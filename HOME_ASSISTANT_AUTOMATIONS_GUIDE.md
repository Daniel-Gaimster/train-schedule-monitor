# Home Assistant Automations Setup Guide

This guide explains how to set up Home Assistant automations to respond to train status events from the TrainScheduleMonitor app.

## Understanding AppDaemon Events

The TrainScheduleMonitor app fires events that Home Assistant can listen to. These events can trigger automations, just like any other Home Assistant event.

### Events Fired by the App

| Event Name | When Fired | Data Available |
|-----------|------------|----------------|
| `train_delayed` | Train is running late | `depart_station`, `arrive_station`, `minutes_delayed` |
| `train_early` | Train is running early | `depart_station`, `arrive_station`, `minutes_early` |
| `train_on_time` | Train is on schedule | `depart_station`, `arrive_station` |
| `train_service_cancelled` | Service is cancelled | `depart_station`, `arrive_station`, `reason_code` |

## Setup Methods

There are **three ways** to add automations in Home Assistant:

### Method 1: Using the UI (Recommended for Beginners)

This is the easiest method and doesn't require editing YAML files.

1. **Go to Settings → Automations & Scenes**
2. **Click "+ CREATE AUTOMATION"**
3. **Click "Create new automation"** (or start from scratch)
4. **Configure the trigger:**
   - Click "Add Trigger"
   - Search for and select "Event"
   - In "Event type", enter: `train_delayed` (or another event)
5. **Add conditions (optional):**
   - Click "Add Condition" → "Template"
   - Example: `{{ trigger.event.data.minutes_delayed > 5 }}`
6. **Configure actions:**
   - Click "Add Action"
   - Choose your action (e.g., "Send a notification")
   - Configure the service and data
7. **Save the automation**

### Method 2: Using automations.yaml

If you prefer YAML, add automations to your `automations.yaml` file:

1. **Open your `automations.yaml` file** (usually in `/config/`)
2. **Add the automation** (see examples below)
3. **Reload automations:**
   - Developer Tools → YAML → Reload Automations

### Method 3: Using configuration.yaml

For more advanced setups:

1. **Edit `configuration.yaml`**
2. **Add or ensure you have:**
   ```yaml
   automation: !include automations.yaml
   ```
3. **Follow Method 2**

## Example Automations

### 1. Send Notification When Train is Delayed

**UI Setup:**
- Trigger: Event → `train_delayed`
- Condition: Template → `{{ trigger.event.data.minutes_delayed > 5 }}`
- Action: Notify → Choose your notification service

**YAML:**
```yaml
- alias: "Notify When Train Delayed"
  trigger:
    - platform: event
      event_type: train_delayed
  condition:
    - condition: template
      value_template: "{{ trigger.event.data.minutes_delayed > 5 }}"
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "🚂 Train Delayed"
        message: >
          Your 08:10 train is delayed by 
          {{ trigger.event.data.minutes_delayed }} minutes.
```

**Important:** Replace `notify.mobile_app_your_phone` with your actual notification service.

### 2. Find Your Notification Service

Your notification service name depends on your setup:

- **Home Assistant Mobile App:** `notify.mobile_app_<device_name>`
  - Find it: Developer Tools → Services → Search "notify"
  - Example: `notify.mobile_app_daniels_iphone`

- **Persistent Notification:** `notify.persistent_notification` (shows in HA UI)

- **Email:** `notify.email_<your_name>`

- **Other services:** Check Developer Tools → Services

**To find your device name:**
```yaml
# Test automation - sends a test notification
- alias: "Test Notification"
  trigger:
    - platform: time
      at: "08:00:00"
  action:
    - service: notify.persistent_notification
      data:
        message: "This is a test notification"
```

### 3. Advanced Notification Example

Send different notifications based on delay severity:

```yaml
- alias: "Train Delay Notifications (Tiered)"
  trigger:
    - platform: event
      event_type: train_delayed
  action:
    - choose:
        # Major delay (>15 minutes)
        - conditions:
            - condition: template
              value_template: "{{ trigger.event.data.minutes_delayed > 15 }}"
          sequence:
            - service: notify.mobile_app_your_phone
              data:
                title: "🚨 Major Train Delay!"
                message: "Train delayed {{ trigger.event.data.minutes_delayed }} minutes. Consider alternative transport!"
                data:
                  priority: high
                  ttl: 0
        # Moderate delay (5-15 minutes)
        - conditions:
            - condition: template
              value_template: "{{ trigger.event.data.minutes_delayed > 5 }}"
          sequence:
            - service: notify.mobile_app_your_phone
              data:
                title: "⚠️ Train Delayed"
                message: "Train delayed {{ trigger.event.data.minutes_delayed }} minutes."
      # Minor delay (<5 minutes) - do nothing
      default: []
```

### 4. Visual Status Light

Control a smart light to show train status:

```yaml
- alias: "Train Status Light - Red for Delayed"
  trigger:
    - platform: event
      event_type: train_delayed
  condition:
    - condition: template
      value_template: "{{ trigger.event.data.minutes_delayed > 5 }}"
  action:
    - service: light.turn_on
      target:
        entity_id: light.bedroom_lamp
      data:
        color_name: red
        brightness_pct: 100

- alias: "Train Status Light - Green for On Time"
  trigger:
    - platform: event
      event_type: train_on_time
  action:
    - service: light.turn_on
      target:
        entity_id: light.bedroom_lamp
      data:
        color_name: green
        brightness_pct: 50

- alias: "Train Status Light - Off When Train Departs"
  trigger:
    - platform: time
      at: "08:15:00"  # 5 minutes after train departure
  action:
    - service: light.turn_off
      target:
        entity_id: light.bedroom_lamp
```

### 5. Cancelled Train with TTS Announcement

Announce through smart speakers:

```yaml
- alias: "Announce Train Cancellation"
  trigger:
    - platform: event
      event_type: train_service_cancelled
  action:
    - service: tts.google_translate_say
      target:
        entity_id: media_player.living_room_speaker
      data:
        message: "Attention! Your morning train has been cancelled. Check for alternative transport."
```

### 6. Set a Helper Entity for Dashboard Display

Create an input_text helper to display train status on your dashboard:

**First, create the helper:**
Settings → Devices & Services → Helpers → Create Helper → Text

Name it: `input_text.train_status`

**Then create automations to update it:**

```yaml
- alias: "Update Train Status Display - Delayed"
  trigger:
    - platform: event
      event_type: train_delayed
  action:
    - service: input_text.set_value
      target:
        entity_id: input_text.train_status
      data:
        value: "Delayed {{ trigger.event.data.minutes_delayed }} min"

- alias: "Update Train Status Display - On Time"
  trigger:
    - platform: event
      event_type: train_on_time
  action:
    - service: input_text.set_value
      target:
        entity_id: input_text.train_status
      data:
        value: "On Time ✓"

- alias: "Update Train Status Display - Cancelled"
  trigger:
    - platform: event
      event_type: train_service_cancelled
  action:
    - service: input_text.set_value
      target:
        entity_id: input_text.train_status
      data:
        value: "CANCELLED ✗"

- alias: "Clear Train Status After Departure"
  trigger:
    - platform: time
      at: "08:15:00"
  action:
    - service: input_text.set_value
      target:
        entity_id: input_text.train_status
      data:
        value: "No updates"
```

**Add to dashboard:**
- Add a card → Entities card
- Select `input_text.train_status`

## Testing Your Automations

### Method 1: Wait for Real Events
Simply wait for the AppDaemon app to check the train and fire events.

### Method 2: Fire Test Events Manually

Use Developer Tools to test your automations:

1. **Go to Developer Tools → Events**
2. **In "Event type", enter:** `train_delayed`
3. **In "Event data", enter:**
   ```json
   {
     "depart_station": "HYR",
     "arrive_station": "BFR",
     "minutes_delayed": 10
   }
   ```
4. **Click "FIRE EVENT"**
5. **Check if your automation triggered**

### Method 3: Check Automation Traces

After an event fires:
1. Go to Settings → Automations & Scenes
2. Click on your automation
3. Click the "Traces" tab
4. See detailed execution logs

## Troubleshooting

### Automation Not Triggering

**Check 1: Is the event being fired?**
- Go to Developer Tools → Events
- Click "LISTEN TO EVENTS"
- Type: `train_delayed` (or the event you're testing)
- Click "START LISTENING"
- Wait for the AppDaemon app to run
- See if the event appears

**Check 2: Is AppDaemon running?**
- Check AppDaemon logs for errors
- Look for: "Train Schedule Monitor initialized"

**Check 3: Event name spelling**
- Event names are case-sensitive
- Must match exactly: `train_delayed`, `train_on_time`, etc.

**Check 4: Condition preventing trigger**
- Remove conditions temporarily to test
- Check template syntax

### Finding Entity IDs

**For lights:**
- Developer Tools → States → Search for your light
- Copy the `entity_id`

**For notifications:**
- Developer Tools → Services → Search "notify"
- See list of available notify services

**For media players:**
- Settings → Devices & Services → Click your integration
- Find your speaker/media player entity

## Complete Working Example

Here's a complete, ready-to-use automation that you can copy:

```yaml
# Simple notification when train is delayed more than 5 minutes
- alias: "Morning Train Alert"
  description: "Notify me about my 08:10 train status"
  trigger:
    - platform: event
      event_type: train_delayed
    - platform: event
      event_type: train_service_cancelled
  action:
    - choose:
        - conditions:
            - condition: template
              value_template: "{{ trigger.event.event_type == 'train_service_cancelled' }}"
          sequence:
            - service: notify.persistent_notification
              data:
                title: "❌ Train Cancelled"
                message: "Your 08:10 train has been cancelled!"
        - conditions:
            - condition: template
              value_template: "{{ trigger.event.event_type == 'train_delayed' }}"
          sequence:
            - service: notify.persistent_notification
              data:
                title: "⚠️ Train Delayed"
                message: "Your 08:10 train is delayed by {{ trigger.event.data.minutes_delayed }} minutes"
  mode: single
```

## Next Steps

1. ✅ Start with a simple notification automation using `notify.persistent_notification`
2. ✅ Test it by firing events manually in Developer Tools
3. ✅ Once working, replace with your actual notification service
4. ✅ Add more advanced automations (lights, TTS, helpers, etc.)
5. ✅ Monitor the automation traces to debug any issues

## Need Help?

- Check AppDaemon logs: `/config/appdaemon/logs/`
- Check Home Assistant logs: Settings → System → Logs
- Use Developer Tools → Events to monitor events
- Use Automation Traces to see execution details
