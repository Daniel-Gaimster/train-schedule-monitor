import requests
import json
from datetime import datetime, time
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
        
        # Listen for Home Assistant events for on-demand train checks
        self.listen_event(self.service_check_train, "check_train_schedule")
        
        # Listen for test events to simulate train statuses
        self.listen_event(self.test_train_status, "check_train_schedule_test")
    
    def service_check_train(self, event_name, data, **kwargs):
        """Event callback to check train status on demand.
        
        Can be called from Home Assistant with optional date/time parameters.
        If no parameters provided, returns the next available train.
        
        Args:
            event_name: Name of the event (will be "check_train_schedule")
            data: Event data dictionary containing optional date/time
            **kwargs: Additional keyword arguments
        
        Example calls from HA:
            # Get next train
            service: event.fire
            data:
              event_type: check_train_schedule
            
            # Get specific train
            service: event.fire
            data:
              event_type: check_train_schedule
              event_data:
                date: "2025-12-09"
                time: "08:10"
        """
        try:
            date_param = data.get("date")
            time_param = data.get("time")
            
            s = self.api_session()
            
            if date_param and time_param:
                # Check specific date/time
                # Convert date format from YYYY-MM-DD to YYYY/MM/DD
                date_string = date_param.replace("-", "/")
                time_string = time_param.replace(":", "")
                date_time_string = f"{date_string}/{time_string}"
                self.log(f"On-demand check for specific train: {date_time_string}")
            elif time_param:
                # Check specific time today
                date_string = datetime.now().strftime("%Y/%m/%d")
                time_string = time_param.replace(":", "")
                date_time_string = f"{date_string}/{time_string}"
                self.log(f"On-demand check for specific time today: {date_time_string}")
            else:
                # Get next available train (no date/time in URL)
                date_time_string = None
                self.log("On-demand check for next available train")
            
            service_details = self.get_service_details(s, date_time_string)
            
            if service_details is None:
                self.log("No services found", level="WARNING")
                event_data = {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs
                }
                self.fire_event("train_check_no_service", **event_data)
                return
            
            self.log(f"Service details: {json.dumps(service_details, indent=2)}")
            self.check_service_health(service_details)
            
        except Exception as e:
            self.log(f"Error in on-demand train check: {str(e)}", level="ERROR")
    
    def test_train_status(self, event_name, data, **kwargs):
        """Test event callback to simulate train statuses for automation testing.
        
        This allows you to fire test events to verify your Home Assistant automations
        work correctly without waiting for real train delays or cancellations.
        
        Args:
            event_name: Name of the event (will be "check_train_schedule_test")
            data: Event data dictionary containing test parameters
            **kwargs: Additional keyword arguments
        
        Example calls from HA:
            # Test cancelled train
            service: event.fire
            data:
              event_type: check_train_schedule_test
              event_data:
                status: cancelled
                reason_code: "123"
            
            # Test delayed train
            service: event.fire
            data:
              event_type: check_train_schedule_test
              event_data:
                status: delayed
                scheduled_time: "08:10"
                actual_time: "08:25"
                minutes_delayed: 15
            
            # Test early train
            service: event.fire
            data:
              event_type: check_train_schedule_test
              event_data:
                status: early
                scheduled_time: "08:10"
                actual_time: "08:05"
                minutes_early: 5
            
            # Test on-time train
            service: event.fire
            data:
              event_type: check_train_schedule_test
              event_data:
                status: on_time
                scheduled_time: "08:10"
                actual_time: "08:10"
        """
        try:
            status = data.get("status", "").lower()
            
            if not status:
                self.log("Test event requires 'status' parameter", level="ERROR")
                return
            
            # Prepare base event data
            event_data = {
                "depart_station": self.depart_station_crs,
                "arrive_station": self.arrive_station_crs
            }
            
            if status == "cancelled":
                # Test cancelled train
                reason_code = data.get("reason_code", "000")
                event_data["status"] = "cancelled"
                event_data["reason_code"] = str(reason_code)
                self.log(f"TEST: Simulating cancelled train (reason: {reason_code})")
                
            elif status == "delayed":
                # Test delayed train
                scheduled_time = data.get("scheduled_time", "08:10")
                actual_time = data.get("actual_time", "08:25")
                minutes_delayed = data.get("minutes_delayed", 15)
                
                event_data["status"] = "delayed"
                event_data["scheduled_time"] = scheduled_time
                event_data["actual_time"] = actual_time
                event_data["minutes_delayed"] = int(minutes_delayed)
                event_data["minutes_difference"] = int(minutes_delayed)
                
                self.log(f"TEST: Simulating delayed train - Scheduled: {scheduled_time}, "
                        f"Actual: {actual_time}, Delay: {minutes_delayed} minutes")
                
            elif status == "early":
                # Test early train
                scheduled_time = data.get("scheduled_time", "08:10")
                actual_time = data.get("actual_time", "08:05")
                minutes_early = data.get("minutes_early", 5)
                
                event_data["status"] = "early"
                event_data["scheduled_time"] = scheduled_time
                event_data["actual_time"] = actual_time
                event_data["minutes_early"] = int(minutes_early)
                event_data["minutes_difference"] = -int(minutes_early)
                
                self.log(f"TEST: Simulating early train - Scheduled: {scheduled_time}, "
                        f"Actual: {actual_time}, Early by: {minutes_early} minutes")
                
            elif status == "on_time":
                # Test on-time train
                scheduled_time = data.get("scheduled_time", "08:10")
                actual_time = data.get("actual_time", scheduled_time)
                
                event_data["status"] = "on_time"
                event_data["scheduled_time"] = scheduled_time
                event_data["actual_time"] = actual_time
                event_data["minutes_difference"] = 0
                
                self.log(f"TEST: Simulating on-time train - Time: {scheduled_time}")
                
            else:
                self.log(f"Unknown test status: {status}. Valid options: cancelled, delayed, early, on_time", 
                        level="ERROR")
                return
            
            # Fire the train_status event with test data
            self.fire_event("train_status", **event_data)
            self.log(f"TEST: Fired train_status event with data: {json.dumps(event_data, indent=2)}")
            
        except Exception as e:
            self.log(f"Error in test train status: {str(e)}", level="ERROR")
    
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

    def get_service_details(self, s, date_time_string=None):
        """Get service details for the specified date/time.
        
        Args:
            s: Authenticated requests session
            date_time_string: Optional date/time in format YYYY/MM/DD/HHMM
                            If None, gets the next available train
            
        Returns:
            dict: Service details or None if no services found
        """
        try:
            # Build URL based on whether date/time is provided
            if date_time_string:
                url = f"{self.base_url}/search/{self.depart_station_crs}/to/{self.arrive_station_crs}/{date_time_string}"
            else:
                # No date/time = get next available train
                url = f"{self.base_url}/search/{self.depart_station_crs}/to/{self.arrive_station_crs}"
            
            self.log(f"Querying API: {url}")
            search_response = s.get(url)
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
            location_detail = service_details.get('locationDetail', {})
            
            # Prepare common event data
            event_data = {
                "depart_station": self.depart_station_crs,
                "arrive_station": self.arrive_station_crs
            }
            
            # Check if service is cancelled
            if 'cancelReasonCode' in location_detail:
                reason_code = location_detail['cancelReasonCode']
                self.log(f"Service is cancelled. Reason code: {reason_code}", level="WARNING")
                event_data["status"] = "cancelled"
                event_data["reason_code"] = str(reason_code)
                self.fire_event("train_status", **event_data)
                return
            
            # Check if we have the required time information
            if 'gbttBookedArrival' not in location_detail or 'realtimeArrival' not in location_detail:
                self.log("Missing arrival time information", level="WARNING")
                return
            
            # Times are in HHMM format (e.g., "1740" = 17:40)
            # Convert to time objects for comparison
            booked_time_str = str(location_detail['gbttBookedArrival']).zfill(4)  # Ensure 4 digits
            realtime_time_str = str(location_detail['realtimeArrival']).zfill(4)
            
            # Parse HHMM format into time objects
            booked_time = time(
                hour=int(booked_time_str[:2]),
                minute=int(booked_time_str[2:])
            )
            realtime_time = time(
                hour=int(realtime_time_str[:2]),
                minute=int(realtime_time_str[2:])
            )
            
            # Convert to minutes since midnight for difference calculation
            booked_minutes = booked_time.hour * 60 + booked_time.minute
            realtime_minutes = realtime_time.hour * 60 + realtime_time.minute
            
            # Calculate delay in minutes (positive = delayed, negative = early)
            minutes_delayed = realtime_minutes - booked_minutes
            
            self.log(f"Train status - Scheduled: {booked_time.strftime('%H:%M')}, "
                    f"Actual: {realtime_time.strftime('%H:%M')}, "
                    f"Difference: {minutes_delayed} minutes")
            
            # Add time information to event data
            event_data["scheduled_time"] = booked_time.strftime('%H:%M')
            event_data["actual_time"] = realtime_time.strftime('%H:%M')
            event_data["minutes_difference"] = int(minutes_delayed)
            
            # Determine status and add status-specific data
            if minutes_delayed > 0:
                self.log(f"Train is delayed by {minutes_delayed} minutes", level="WARNING")
                event_data["status"] = "delayed"
                event_data["minutes_delayed"] = int(minutes_delayed)
            elif minutes_delayed < 0:
                self.log(f"Train is early by {abs(minutes_delayed)} minutes")
                event_data["status"] = "early"
                event_data["minutes_early"] = int(abs(minutes_delayed))
            else:
                self.log("Train is on time")
                event_data["status"] = "on_time"
            
            # Fire single event with all status information
            self.fire_event("train_status", **event_data)
                
        except (KeyError, ValueError, TypeError) as e:
            self.log(f"Error processing service health data: {str(e)}", level="ERROR")
