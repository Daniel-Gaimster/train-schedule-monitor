# On-Demand Train Check Service

The Train Schedule Monitor now includes an on-demand service that can be called anytime from Home Assistant - no need to wait for the scheduled checks!

## Quick Start

### Check Next Available Train RIGHT NOW

```yaml
service: appdaemon.train_schedule_monitor_check_train
```

That's it! This will:
- Query the API for the next available train on your route
- Fire the appropriate event (`train_delayed`, `train_on_time`, etc.)
- Trigger your automations

### Check a Specific Train

```yaml
service: appdaemon.train_schedule_monitor_check_train
data:
  date: "2025-12-09"
  time: "08:10"
```

## How to Use in Home Assistant

### Method 1: Developer Tools (Testing)

1. Go to **Developer Tools** (in the sidebar, usually at the bottom)
2. Click on the **Actions** tab (previously called "Services")
3. In the search box, type: `appdaemon` or `train`
4. Look for: **Train Schedule Monitor: check_train** or `appdaemon.train_schedule_monitor_check_train`
5. Click **PERFORM ACTION** (or **CALL SERVICE** in older versions)

**If you don't see the service:**
- Check if AppDaemon add-on is running (Settings → Add-ons → AppDaemon)
- Check AppDaemon logs for errors (Settings → Add-ons → AppDaemon → Log tab)
- Look for "Train Schedule Monitor initialized" in the logs
- Make sure you have an `apps.yaml` file configured (see APPDAEMON_SETUP.md)
- Restart the AppDaemon add-on

For next train:
- Just click the button, no data needed!

For specific train:
- Switch to YAML mode
- Add:
  ```yaml
  date: "2025-12-09"
  time: "17:30"
  ```

### Method 2: In an Automation

```yaml
- alias: "Check Train Before Leaving Home"
  trigger:
    - platform: time
      at: "07:45:00"
  action:
    - service: appdaemon.train_schedule_monitor_check_train
      # No data needed - gets next train
```

### Method 3: Button on Dashboard

Add a button card to check train status on demand:

```yaml
type: button
name: Check Next Train
icon: mdi:train
tap_action:
  action: call-service
  service: appdaemon.train_schedule_monitor_check_train
```

### Method 4: Script

Create a script you can call from anywhere:

```yaml
check_my_train:
  alias: "Check My Train"
  sequence:
    - service: appdaemon.train_schedule_monitor_check_train
      data:
        date: "{{ now().strftime('%Y-%m-%d') }}"
        time: "08:10"
```

Then call it:
```yaml
service: script.check_my_train
```

## Examples

### Check Next Train (No Parameters)

**What happens:**
- Queries: `https://api.rtt.io/api/v1/json/search/HYR/to/BFR`
- Returns: The very next train from HYR to BFR
- Fires: Appropriate event based on train status

**Perfect for:**
- "What's the next train?" button on your dashboard
- Checking status right before leaving
- Any time queries without knowing exact times

### Check Specific Train

**What happens:**
- Queries: `https://api.rtt.io/api/v1/json/search/HYR/to/BFR/2025/12/09/0810`
- Returns: The 08:10 train on December 9th
- Fires: Appropriate event based on train status

**Perfect for:**
- Checking your regular commute train
- Planning future journeys
- Historical status checks

## Testing RIGHT NOW (Saturday 16:30)

You can test this immediately without waiting for Monday morning!

### Test 1: Check Next Train
```yaml
service: appdaemon.train_schedule_monitor_check_train
```

This will work even on Saturday - it'll return the next available train service.

### Test 2: Check Monday's 08:10
```yaml
service: appdaemon.train_schedule_monitor_check_train
data:
  date: "2025-12-09"
  time: "08:10"
```

This lets you check Monday's train right now!

## Integration with Automations

The service fires the same events as the scheduled checks, so your existing automations work automatically:

```yaml
# Your existing automation
- alias: "Train Delayed Notification"
  trigger:
    - platform: event
      event_type: train_delayed
  action:
    - service: notify.mobile_app_your_phone
      data:
        message: "Train delayed {{ trigger.event.data.minutes_delayed }} minutes"
```

This automation will trigger whether:
- The scheduled check finds a delay (Monday 07:10-08:10)
- You manually call the service (anytime)
- Someone presses the dashboard button (anytime)

## Dashboard Example

Create a comprehensive train status card:

```yaml
type: vertical-stack
cards:
  - type: button
    name: Check Next Train
    icon: mdi:train
    tap_action:
      action: call-service
      service: appdaemon.train_schedule_monitor_check_train
    
  - type: button
    name: Check Monday 08:10 Train
    icon: mdi:train-variant
    tap_action:
      action: call-service
      service: appdaemon.train_schedule_monitor_check_train
      service_data:
        date: "2025-12-09"
        time: "08:10"
  
  - type: entities
    entities:
      - entity: input_text.train_status
        name: Status
```

## Automation Ideas

### 1. Check Train When You Wake Up
```yaml
- alias: "Morning Train Check"
  trigger:
    - platform: state
      entity_id: binary_sensor.bedroom_motion
      to: "on"
  condition:
    - condition: time
      after: "06:00:00"
      before: "08:00:00"
    - condition: time
      weekday:
        - mon
        - tue
        - wed
        - thu
        - fri
  action:
    - service: appdaemon.train_schedule_monitor_check_train
```

### 2. Check Before Leaving Home
```yaml
- alias: "Check Train When Leaving"
  trigger:
    - platform: state
      entity_id: binary_sensor.front_door
      to: "on"
  condition:
    - condition: time
      after: "07:00:00"
      before: "08:30:00"
  action:
    - service: appdaemon.train_schedule_monitor_check_train
```

### 3. Voice Assistant Integration
```yaml
- alias: "Alexa Check Train"
  trigger:
    - platform: event
      event_type: alexa_actionable_notification
      event_data:
        event_id: check_train
  action:
    - service: appdaemon.train_schedule_monitor_check_train
    - wait_for_trigger:
        - platform: event
          event_type: 
            - train_delayed
            - train_on_time
            - train_cancelled
      timeout: "00:00:10"
    - service: notify.alexa_media
      data:
        message: >
          {% if wait.trigger.event.event_type == 'train_on_time' %}
            Your train is on time.
          {% elif wait.trigger.event.event_type == 'train_delayed' %}
            Your train is delayed by {{ wait.trigger.event.data.minutes_delayed }} minutes.
          {% else %}
            Your train has been cancelled.
          {% endif %}
```

## Troubleshooting

### Service Not Found in Actions Tab

**This usually means AppDaemon hasn't loaded the app yet.**

**Step 1: Check if you've set up the app**
- Do you have an `apps.yaml` file in your AppDaemon `apps` directory?
- If you only have `apps.yaml.example`, you need to create the actual `apps.yaml` file
- See **APPDAEMON_SETUP.md** for setup instructions

**Step 2: Check AppDaemon is running**
- Go to: Settings → Add-ons → AppDaemon
- Status should show "Running"
- If not, click "START"

**Step 3: Check AppDaemon logs**
- In AppDaemon add-on, click the "Log" tab
- Look for: `"Train Schedule Monitor initialized for 08:10 train"`
- If you see this, the app loaded successfully
- If you see errors, they'll tell you what's wrong (missing credentials, wrong config, etc.)

**Step 4: Try restarting AppDaemon**
- Settings → Add-ons → AppDaemon → RESTART
- Wait 10-20 seconds
- Check Actions tab again

**Common Issues:**
- ❌ No `apps.yaml` file → Service won't register
- ❌ Wrong file location → File must be in `/config/appdaemon/apps/apps.yaml`
- ❌ AppDaemon not running → Start the add-on
- ❌ Python file not in apps folder → Copy `train-schedule-monitor.py` to `/config/appdaemon/apps/`

### No Events Fired
- Check AppDaemon logs for errors
- Verify API credentials in secrets.yaml
- Test API with curl command
- Check station codes are correct

### "No services found" Message
- Normal on weekends/late at night when trains aren't running
- Try specifying a specific weekday time
- Check your station codes are valid

## Benefits

✅ **Test anytime** - No need to wait for Monday morning
✅ **On-demand info** - Check status right before leaving
✅ **Dashboard buttons** - One-tap train status
✅ **Voice control** - Ask Alexa/Google to check your train
✅ **Flexible** - Works with or without date/time
✅ **Same events** - Uses existing automations

## Summary

| Service Call | What It Does |
|--------------|--------------|
| No parameters | Gets next available train |
| With date + time | Gets specific train |

Both fire the same events your automations already listen for!
