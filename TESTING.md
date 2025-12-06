# Local Testing Guide

## Quick Start

### 1. Set up your environment

First, make sure you have your dependencies installed:

```bash
# If using uv (recommended, already in your pyproject.toml)
uv sync

# Or with pip
pip install -r requirements.txt
```

### 2. Configure your credentials

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your RTT API credentials:

```
USERNAME=your_rtt_username
PASSWORD=your_rtt_password
```

**Get RTT API credentials**: Sign up at https://www.realtimetrains.co.uk/about/developer/

### 3. Run the test

```bash
python test_local.py
```

Or with uv:

```bash
uv run test_local.py
```

## What the test does

The test script:
1. ✅ Loads your credentials from `.env`
2. ✅ Creates a mock AppDaemon environment
3. ✅ Initializes the TrainScheduleMonitor
4. ✅ Makes a real API call to check the 08:10 train
5. ✅ Shows all logs and events that would be fired
6. ✅ Displays service details and delay information

## Customizing the test

Edit `test_local.py` to change:

```python
config = {
    "depart_station_crs": "HYR",      # Your departure station
    "arrive_station_crs": "BFR",       # Your arrival station
    "train_departure_time": "08:10",   # Train time to check
    # ... other settings
}
```

## Testing different scenarios

### Test a different time
```python
"train_departure_time": "17:45",  # Evening train
```

### Test a specific date (modify the code)
In `test_local.py`, you can change the `check_train_status` method to use a specific date:

```python
# Instead of:
date_string = now.strftime("%Y/%m/%d")

# Use a specific date:
date_string = "2025/12/09"  # Monday
```

### Test weekend behavior
The script will automatically detect weekends and skip checks (as designed).

## Expected Output

### Successful check:
```
======================================================================
Train Schedule Monitor - Local Testing
======================================================================

[10:30:45] INFO: Train Schedule Monitor initialized for 08:10 train
[10:30:45] INFO: Route: HYR → BFR

----------------------------------------------------------------------
Running check for train status...
----------------------------------------------------------------------

[10:30:45] INFO: Querying API for: 2025/12/06/0810
[10:30:45] INFO: API URL: https://api.rtt.io/api/v1/json/search/HYR/to/BFR/2025/12/06/0810
[10:30:46] INFO: ✓ Service found!
[10:30:46] INFO: 📊 Train status - Minutes delayed: 5
[10:30:46] WARNING: ⚠️  Train is delayed by 5 minutes
🔔 EVENT FIRED: train_delayed
   Data: {
     "depart_station": "HYR",
     "arrive_station": "BFR",
     "minutes_delayed": 5
   }

======================================================================
Test completed!
======================================================================

📋 Summary: 1 event(s) fired during test
   - train_delayed
```

### When train is on time:
```
[10:30:46] INFO: ✅ Train is on time
🔔 EVENT FIRED: train_on_time
```

### When service is cancelled:
```
[10:30:46] WARNING: ❌ Service is cancelled. Reason code: 123
🔔 EVENT FIRED: train_service_cancelled
```

## Troubleshooting

### "Import 'hassapi' could not be resolved"
This is normal when testing locally. The `test_local.py` script uses a mock Hass class instead.

### "API request failed: 401"
Your credentials are incorrect. Check your `.env` file.

### "No services found"
- Check your station codes are correct (CRS codes)
- Try a different time (some trains only run on certain days)
- The train might not exist at that time

### "Missing arrival time information"
The API returned data but it's incomplete. This might happen if:
- The train hasn't reached the destination yet
- Data is not available for that service

## Next Steps

Once local testing works:
1. Copy `main.py` to your AppDaemon `apps/` directory
2. Configure `apps.yaml` with the same settings that worked in testing
3. Restart AppDaemon
4. Check AppDaemon logs to confirm it's working

## Viewing Full API Response

To see the complete API response, uncomment this line in `test_local.py`:

```python
# In get_service_details method, add:
print(json.dumps(search_response_json, indent=2))
```
