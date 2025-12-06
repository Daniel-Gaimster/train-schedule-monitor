#!/usr/bin/env python3
"""
Local testing script for TrainScheduleMonitor
This simulates the AppDaemon environment for testing
"""

import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os


class MockHass:
    """Mock Hass class to simulate AppDaemon API"""
    
    def __init__(self, args):
        self.args = args
        self.events = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def fire_event(self, event_name, data):
        self.events.append({"event": event_name, "data": data})
        print(f"🔔 EVENT FIRED: {event_name}")
        print(f"   Data: {json.dumps(data, indent=2)}")


class TrainScheduleMonitor(MockHass):
    """Your TrainScheduleMonitor class with minimal modifications for testing"""
    
    def initialize(self):
        """Initialize the TrainScheduleMonitor app."""
        # Get configuration from args
        self.base_url = self.args.get("base_url", "https://api.rtt.io/api/v1/json")
        self.depart_station_crs = self.args["depart_station_crs"]
        self.arrive_station_crs = self.args["arrive_station_crs"]
        self.username = self.args["username"]
        self.password = self.args["password"]
        
        # Train departure time to monitor (default: 08:10)
        self.train_departure_time = self.args.get("train_departure_time", "08:10")
        
        self.log(f"Train Schedule Monitor initialized for {self.train_departure_time} train")
        self.log(f"Route: {self.depart_station_crs} → {self.arrive_station_crs}")

    def check_train_status(self):
        """Check train status (modified for testing)."""
        try:
            date_string = datetime.now().strftime("%Y/%m/%d")
            date_string = '2025/12/08'
            
            # Safety check: only run on weekdays
            if datetime.strptime(date_string, "%Y/%m/%d").weekday() >= 5:  # Saturday=5, Sunday=6
                self.log("Skipping check - not a weekday", level="WARNING")
                return
            
            s = self.api_session()
            
            # Query the API for the specific train departure time
            # Use the configured departure time for the query
            date_time_string = f"{date_string}/{self.train_departure_time.replace(':', '')}"
            
            self.log(f"Querying API for: {date_time_string}")
            
            service_details = self.get_service_details(s, date_time_string)
            
            if service_details is None:
                self.log(f"No services found for {self.train_departure_time} departure", level="WARNING")
                return
                
            self.log(f"✓ Service found!")
            self.log(f"Service details: {json.dumps(service_details, indent=2)}")
            
            self.check_service_health(service_details)
            
        except Exception as e:
            self.log(f"Error checking train status: {str(e)}", level="ERROR")
            import traceback
            traceback.print_exc()

    def api_session(self):
        """Create and return an authenticated requests session."""
        s = requests.Session()
        s.auth = (self.username, self.password)
        return s

    def get_service_details(self, s, date_time_string):
        """Get service details for the specified date/time."""
        try:
            url = f"{self.base_url}/search/{self.depart_station_crs}/to/{self.arrive_station_crs}/{date_time_string}"
            self.log(f"API URL: {url}")
            
            search_response = s.get(url)
            search_response.raise_for_status()
            
            search_response_json = search_response.json()
            
            # Return the first available service if any exist
            if 'services' in search_response_json and search_response_json['services']:
                return search_response_json['services'][0]
            
            # If no services found, return None
            return None
            
        except requests.exceptions.RequestException as e:
            self.log(f"API request failed: {str(e)}", level="ERROR")
            return None

    def check_service_health(self, service_details):
        """Check the health/status of a train service."""
        try:
            # Check if service is cancelled
            if 'cancelReasonCode' in service_details.get('locationDetail', {}):
                reason_code = service_details['locationDetail']['cancelReasonCode']
                self.log(f"❌ Service is cancelled. Reason code: {reason_code}", level="WARNING")
                
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
            
            self.log(f"📊 Train status - Minutes delayed: {minutes_delayed}")
            
            # Fire events based on delay status
            if minutes_delayed > 0:
                self.log(f"⚠️  Train is delayed by {minutes_delayed} minutes", level="WARNING")
                self.fire_event("train_delayed", {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs,
                    "minutes_delayed": minutes_delayed
                })
            elif minutes_delayed < 0:
                self.log(f"✅ Train is early by {abs(minutes_delayed)} minutes")
                self.fire_event("train_early", {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs,
                    "minutes_early": abs(minutes_delayed)
                })
            else:
                self.log("✅ Train is on time")
                self.fire_event("train_on_time", {
                    "depart_station": self.depart_station_crs,
                    "arrive_station": self.arrive_station_crs
                })
                
        except (KeyError, ValueError, TypeError) as e:
            self.log(f"Error processing service health data: {str(e)}", level="ERROR")


def main():
    """Main test function"""
    print("=" * 70)
    print("Train Schedule Monitor - Local Testing")
    print("=" * 70)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Configuration (same as apps.yaml would provide)
    config = {
        "base_url": "https://api.rtt.io/api/v1/json",
        "depart_station_crs": "HYR",
        "arrive_station_crs": "BFR",
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "train_departure_time": "08:10",
        "check_before_departure": 60,
        "check_interval_minutes": 10
    }
    
    # Validate credentials
    if not config["username"] or not config["password"]:
        print("❌ ERROR: USERNAME and PASSWORD must be set in .env file")
        print()
        print("Create a .env file with:")
        print("USERNAME=your_rtt_username")
        print("PASSWORD=your_rtt_password")
        return
    
    # Create and initialize the monitor
    monitor = TrainScheduleMonitor(config)
    monitor.initialize()
    
    print()
    print("-" * 70)
    print("Running check for train status...")
    print("-" * 70)
    print()
    
    # Run a check
    monitor.check_train_status()
    
    print()
    print("=" * 70)
    print("Test completed!")
    print("=" * 70)
    
    # Show summary of events fired
    if monitor.events:
        print()
        print(f"📋 Summary: {len(monitor.events)} event(s) fired during test")
        for event in monitor.events:
            print(f"   - {event['event']}")


if __name__ == "__main__":
    main()
