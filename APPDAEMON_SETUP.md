# AppDaemon Installation and Configuration Guide

## Overview
This train schedule monitor has been converted to work with Home Assistant AppDaemon. It monitors train services and fires events that can trigger Home Assistant automations.

## Installation

### 1. AppDaemon Setup
Make sure you have AppDaemon installed and configured in your Home Assistant setup. If not, follow the [official AppDaemon installation guide](https://appdaemon.readthedocs.io/en/latest/INSTALL.html).

### 2. Copy the App
Copy `main.py` to your AppDaemon `apps/` directory (usually `/config/appdaemon/apps/`).

### 3. Set Up Secrets
AppDaemon uses a `secrets.yaml` file to store sensitive information like API credentials.

Create or edit `secrets.yaml` in your AppDaemon configuration directory (same location as `apps.yaml`):

```yaml
# secrets.yaml
rtt_username: "your_actual_rtt_username"
rtt_password: "your_actual_rtt_password"
```

**Important**: Never commit `secrets.yaml` to version control!

### 4. Configuration
Add the configuration to your `apps/apps.yaml` file:

```yaml
train_monitor:
  module: main
  class: TrainScheduleMonitor
  
  # Required configuration
  depart_station_crs: "HYR"          # Your departure station CRS code
  arrive_station_crs: "BFR"          # Your arrival station CRS code
  username: !secret rtt_username      # References secrets.yaml
  password: !secret rtt_password      # References secrets.yaml
  
  # Optional configuration
  train_departure_time: "08:10"       # The specific train departure time (default: 08:10)
  check_before_departure: 60          # Start checking X minutes before departure (default: 60)
  check_interval_minutes: 10          # Check every X minutes (default: 10)
```

**Note**: The `!secret` tags tell AppDaemon to load those values from your `secrets.yaml` file.

### 5. Get RTT API Credentials
1. Register at [Realtime Trains](https://www.realtimetrains.co.uk/about/developer/)
2. Obtain your API credentials
3. Update the `rtt_username` and `rtt_password` in your `secrets.yaml` file

### 6. Update Station Codes
Replace `"HYR"` and `"BFR"` with the appropriate CRS codes for your journey:
- Find station codes at [National Rail Enquiries](https://www.nationalrail.co.uk/stations_destinations/48541.aspx)

## Security Note

⚠️ **Never commit sensitive credentials to version control!**

The `secrets.yaml` file contains your API credentials and should be kept secure:
- Add `secrets.yaml` to your `.gitignore` file
- Only store `secrets.yaml.example` (with placeholder values) in version control
- Use AppDaemon's `!secret` syntax to reference credentials in `apps.yaml`

Example `.gitignore` entry:
```
secrets.yaml
.env
```

## Features

### Events Fired
The app fires the following events that can be used in Home Assistant automations:

- `train_delayed`: When train is running late
  - Data: `depart_station`, `arrive_station`, `minutes_delayed`
- `train_early`: When train is running early
  - Data: `depart_station`, `arrive_station`, `minutes_early`
- `train_on_time`: When train is punctual
  - Data: `depart_station`, `arrive_station`
- `train_service_cancelled`: When service is cancelled
  - Data: `depart_station`, `arrive_station`, `reason_code`

### Logging
The app logs all activities to AppDaemon logs. Check your AppDaemon logs for monitoring information and any errors.

## Home Assistant Integration

The app fires events that Home Assistant can respond to with automations. This allows you to:
- 📱 Send notifications when trains are delayed or cancelled
- 💡 Control lights based on train status
- 🔊 Make announcements through smart speakers
- 📊 Display train status on your dashboard
- 🚗 Trigger other actions (e.g., start car heating if train is delayed)

### Setting Up Automations

📚 **See the [HOME_ASSISTANT_AUTOMATIONS_GUIDE.md](HOME_ASSISTANT_AUTOMATIONS_GUIDE.md) for complete setup instructions**, including:
- Step-by-step UI setup guide
- Multiple automation examples (notifications, lights, TTS, dashboards)
- How to find your notification service names
- Testing and troubleshooting tips
- Ready-to-use YAML examples

**Quick Example:**
```yaml
- alias: "Notify When Train Delayed"
  trigger:
    - platform: event
      event_type: train_delayed
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "🚂 Train Delayed"
        message: "Train delayed {{ trigger.event.data.minutes_delayed }} minutes"
```

Also see `home_assistant_automations.yaml.example` for more quick examples.

## Troubleshooting

1. **Import Error**: Make sure AppDaemon is properly installed
2. **Authentication Issues**: Verify your RTT API credentials
3. **No Data**: Check that your station CRS codes are correct
4. **Events Not Firing**: Check AppDaemon logs for errors

## Monitoring Schedule
By default, the app monitors the **08:10 train on weekdays (Monday-Friday)**, checking every **10 minutes** starting **60 minutes before departure**. This means it will check at:
- 07:10, 07:20, 07:30, 07:40, 07:50, 08:00, 08:10

This can be customized in the configuration:

- `train_departure_time`: The specific train time to monitor (e.g., "08:10", "17:45")
- `check_before_departure`: How many minutes before departure to start checking (default: 60)
- `check_interval_minutes`: How often to check in minutes (default: 10)

The app always queries the API for the same train departure time, regardless of when the check runs. This ensures you're tracking the status of your specific train throughout the morning.
