import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import pprint

def main():
    
    s = api_session()
    
    # date_string = datetime.now().strftime("%Y/%m/%d")
    # date_string = "2025/04/14"
    # time_string = "0810"
    # date_time_string = f"{date_string}/{time_string}"
    
    # current date and time for testing
    date_string = datetime.now().strftime("%Y/%m/%d")
    date_time_string = datetime.now().strftime("%Y/%m/%d/%H%M")
    # date_time_string = "2025/04/14/0810"
    date_time_string = "2025/04/09/0810"
    
    service_details = get_service_details(s, date_time_string)
    print(json.dumps(service_details, indent=4))
    
    check_service_health(service_details)
    
    # parse_depart_station_details(service_details)
    

def api_session():
    user = os.getenv("USER")
    pw = os.getenv("PASS")
    
    s = requests.Session()
    s.auth = (user, pw)
    
    return s


def get_service_details(s, date_time_string):
    'Accepts a date_time_string in the format YYYY/MM/DD/HHMM'
    
    search_response = s.get(f"{base_url}/search/{depart_station_crs}/to/{arrive_station_crs}/{date_time_string}")
    search_response.raise_for_status()
    
    search_response_json = search_response.json()
    # print(json.dumps(search_response_json, indent=4))
    
    # Filter down to the service of interest
    for service in search_response_json['services']:
        if service['locationDetail']['gbttBookedArrival'] == '0810':
            return service
    

### Realised that this endpoint is not needed, all necessary data is contained in the search endpoint
# def get_service_details(s, service_uid, date_string):
#     service_response = s.get(f"{base_url}/service/{service_uid}/{date_string}")
#     service_response.raise_for_status()
    
#     service_response_json = service_response.json()
#     # print(json.dumps(service_response_json, indent=4))
    
#     return service_response_json


def check_service_health(service_details):
    # Check if service is cancelled
    if 'cancelReasonCode' in service_details['locationDetail']:
        # Todo: flesh this cancelled logic out
        print("Service is cancelled")
        return
    
    schedule_arrival_time = int(service_details['locationDetail']['gbttBookedArrival'])
    realtime_arrival_time = int(service_details['locationDetail']['realtimeArrival'])
    
    # Positive integer if delayed, negative if early
    minutes_delayed = realtime_arrival_time - schedule_arrival_time
    print(f"Minutes delayed: {minutes_delayed}")


if __name__ == "__main__":
    load_dotenv()
    base_url = 'https://api.rtt.io/api/v1/json'
    depart_station_crs = os.getenv("DEPART_STATION_CRS")
    arrive_station_crs = os.getenv("ARRIVE_STATION_CRS")
    
    main()
