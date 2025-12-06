import requests
import json
from datetime import datetime
from appdaemon.plugins.hass import Hass

class TrainScheduleMonitor(Hass):
    
    def initialize(self):
        """Initialize the TrainScheduleMonitor app."""
        # Get configuration from apps.yaml
        self.base_url = self.args.get("base_url", "https://api.rtt.io/api/v1/json")
        self.depart_station_crs = self.args["depart_station_crs"]
        self.arrive_station_crs = self.args["arrive_station_crs"]
        self.username = self.args["username"]
        self.password = self.args["password"]
        
        # Train departure time to monitor (default: 08:10)
        self.train_departure_time = self.args.get("train_departure_time", "08:10")
        
        # How many minutes before departure to start checking (default: 60 minutes)
        self.check_before_departure = self.args.get("check_before_departure", 60)
        
        # How often to check in minutes before departure (default: every 10 minutes)
        self.check_interval_minutes = self.args.get("check_interval_minutes", 10)
        
        # Start monitoring with time-based scheduling
        self.log(f"Train Schedule Monitor initialized for {self.train_departure_time} train")
        
        # Parse the departure time
        depart_hour, depart_minute = map(int, self.train_departure_time.split(':'))
        
        # Calculate when to start checking (e.g., 60 minutes before departure)
        start_minutes = (depart_hour * 60 + depart_minute) - self.check_before_departure
        start_hour = start_minutes // 60
        start_minute = start_minutes % 60
        
        # Schedule checks at intervals leading up to departure
        current_minutes = start_minutes
        end_minutes = depart_hour * 60 + depart_minute
        
        while current_minutes <= end_minutes:
            check_hour = current_minutes // 60
            check_minute = current_minutes % 60
            time_str = f"{check_hour:02d}:{check_minute:02d}:00"
            self.run_daily(self.check_train_status, time_str, constrain_days="mon,tue,wed,thu,fri")
            self.log(f"Scheduled check at {time_str} on weekdays")
            current_minutes += self.check_interval_minutes
    
    def check_train_status(self, cb_args):
        """Callback function to check train status."""
        try:
            now = datetime.now()
            
            s = self.api_session()
            
            # Query the API for the specific train departure time
            date_string = now.strftime("%Y/%m/%d")
            # Use the configured departure time for the query
            date_time_string = f"{date_string}/{self.train_departure_time.replace(':', '')}"
            
            service_details = self.get_service_details(s, date_time_string)
            
            if service_details is None:
                self.log(f"No services found for {self.train_departure_time} departure")
                return
                
            self.log(f"Service details: {json.dumps(service_details, indent=2)}")
            
            self.check_service_health(service_details)
            
        except Exception as e:
            self.log(f"Error checking train status: {str(e)}", level="ERROR")

    def api_session(self):
        """Create and return an authenticated requests session."""
        s = requests.Session()
        s.auth = (self.username, self.password)
        return s

    def get_service_details(self, s, date_time_string):
        """Get service details for the specified date/time.
        
        Args:
            s: Authenticated requests session
            date_time_string: Date/time in format YYYY/MM/DD/HHMM
            
        Returns:
            dict: Service details or None if no services found
        """
        try:
            search_response = s.get(f"{self.base_url}/search/{self.depart_station_crs}/to/{self.arrive_station_crs}/{date_time_string}")
            search_response.raise_for_status()
            
            search_response_json = search_response.json()
            self.log(f"API response: {json.dumps(search_response_json, indent=2)}")
            
            # Return the first available service if any exist
            if 'services' in search_response_json and search_response_json['services']:
                return search_response_json['services'][0]
            
            # If no services found, return None
            return None
            
        except requests.exceptions.RequestException as e:
            self.log(f"API request failed: {str(e)}", level="ERROR")
            return None

    def check_service_health(self, service_details):
        """Check the health/status of a train service.
        
        Args:
            service_details: Dictionary containing service information
        """
        try:
            # Check if service is cancelled
            if 'cancelReasonCode' in service_details.get('locationDetail', {}):
                reason_code = service_details['locationDetail']['cancelReasonCode']
                self.log(f"Service is cancelled. Reason code: {reason_code}", level="WARNING")
                
                # Fire event for Home Assistant automation
                self.fire_event("train_service_cancelled", {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs,
                    "reason_code": reason_code
                })
                return
            
            location_detail = service_details.get('locationDetail', {})
            
            # Check if we have the required time information
            if 'gbttBookedArrival' not in location_detail or 'realtimeArrival' not in location_detail:
                self.log("Missing arrival time information", level="WARNING")
                return
                
            schedule_arrival_time = int(location_detail['gbttBookedArrival'])
            realtime_arrival_time = int(location_detail['realtimeArrival'])
            
            # Positive integer if delayed, negative if early
            minutes_delayed = realtime_arrival_time - schedule_arrival_time
            
            self.log(f"Train status - Minutes delayed: {minutes_delayed}")
            
            # Fire events based on delay status
            if minutes_delayed > 0:
                self.log(f"Train is delayed by {minutes_delayed} minutes", level="WARNING")
                self.fire_event("train_delayed", {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs,
                    "minutes_delayed": minutes_delayed
                })
            elif minutes_delayed < 0:
                self.log(f"Train is early by {abs(minutes_delayed)} minutes")
                self.fire_event("train_early", {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs,
                    "minutes_early": abs(minutes_delayed)
                })
            else:
                self.log("Train is on time")
                self.fire_event("train_on_time", {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs
                })
                
        except (KeyError, ValueError, TypeError) as e:
            self.log(f"Error processing service health data: {str(e)}", level="ERROR")
