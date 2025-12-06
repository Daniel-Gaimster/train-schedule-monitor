# Train Schedule Monitor

Monitor UK train schedules and get real-time updates through Home Assistant using AppDaemon.

Data sourced from the [Real Time Trains API](https://www.realtimetrains.co.uk/about/developer/pull/docs/)

## Features

- 🚂 Monitor a specific train service (e.g., your daily 08:10 commute)
- ⏰ Automatic checks on weekday mornings leading up to departure
- 🎯 **On-demand checks** - Call anytime to check next train or specific train
- 📱 Real-time notifications about delays and cancellations
- 💡 Control smart lights based on train status
- 🔊 TTS announcements through smart speakers
- 📊 Dashboard display of current train status

## Quick Start

### Test It RIGHT NOW! 🚀

No need to wait for Monday morning - test the service immediately:

```yaml
# Developer Tools → Services
service: appdaemon.train_schedule_monitor_check_train
```

This checks the **next available train** on your route and fires events to trigger your automations!

See **[ON_DEMAND_SERVICE.md](ON_DEMAND_SERVICE.md)** for dashboard buttons, voice control, and more examples.

### Full Setup

### 1️⃣ Get Started
See **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** for a visual overview of the system and setup checklist.

### 2️⃣ Test Locally
See **[TESTING.md](TESTING.md)** for instructions on testing the app on your computer before deploying.

### 3️⃣ Deploy to AppDaemon
See **[APPDAEMON_SETUP.md](APPDAEMON_SETUP.md)** for complete deployment instructions.

### 4️⃣ Set Up Automations
See **[HOME_ASSISTANT_AUTOMATIONS_GUIDE.md](HOME_ASSISTANT_AUTOMATIONS_GUIDE.md)** for detailed automation setup with examples.

## Documentation

| Guide | Description |
|-------|-------------|
| [ON_DEMAND_SERVICE.md](ON_DEMAND_SERVICE.md) | 🎯 **Check trains anytime** (recommended starting point!) |
| [HOW_IT_WORKS.md](HOW_IT_WORKS.md) | 📋 System overview, flow diagram, and checklist |
| [TESTING.md](TESTING.md) | 🧪 Local testing guide |
| [APPDAEMON_SETUP.md](APPDAEMON_SETUP.md) | 🚀 AppDaemon deployment guide |
| [HOME_ASSISTANT_AUTOMATIONS_GUIDE.md](HOME_ASSISTANT_AUTOMATIONS_GUIDE.md) | 🤖 Complete automation setup guide |
| [PRODUCTION_TESTING.md](PRODUCTION_TESTING.md) | 🔧 Testing in production Home Assistant |
| [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) | 🔐 Credentials configuration |
| [quick_start_automation.yaml](quick_start_automation.yaml) | ⚡ Ready-to-use test automation |

## What It Does

The app monitors your configured train service on weekday mornings:

1. **Scheduled Checks**: Automatically checks train status starting 60 minutes before departure
2. **Status Monitoring**: Tracks delays, cancellations, and on-time status
3. **Event Firing**: Sends events to Home Assistant with train status information
4. **Automation Triggers**: Your Home Assistant automations respond to these events

### Events Available

- `train_delayed` - Train is running late (includes minutes delayed)
- `train_on_time` - Train is on schedule
- `train_early` - Train is running early
- `train_service_cancelled` - Service has been cancelled

## Example Use Cases

- 📱 **Get notified** when your morning train is delayed
- 💡 **Visual indicators** with smart lights (red = delayed, green = on time)
- 🔊 **Voice announcements** if train is cancelled
- 📊 **Dashboard cards** showing current train status
- 🚗 **Trigger actions** like starting car heating if train is delayed

## Configuration

```yaml
train_monitor:
  module: main
  class: TrainScheduleMonitor
  depart_station_crs: "HYR"       # Your departure station
  arrive_station_crs: "BFR"        # Your arrival station
  username: !secret rtt_username   # RTT API credentials
  password: !secret rtt_password
  train_departure_time: "08:10"    # Train to monitor
```

## Requirements

- Home Assistant with AppDaemon
- Real Time Trains API account (free)
- Python 3.13+

## Installation

See [APPDAEMON_SETUP.md](APPDAEMON_SETUP.md) for detailed instructions.

## Support

- Check [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for troubleshooting
- Review AppDaemon logs: `/config/appdaemon/logs/`
- Test events manually in Home Assistant Developer Tools

## License

This project is for personal use. Please respect the [Real Time Trains API terms of service](https://www.realtimetrains.co.uk/about/developer/).