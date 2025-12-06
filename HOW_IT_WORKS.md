# How It All Works Together

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRAIN MONITORING SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

1. SCHEDULE (Weekday Mornings)
   ┌──────────────────────────────────────────┐
   │ 07:10, 07:20, 07:30, 07:40, 07:50,      │
   │ 08:00, 08:10 (every 10 minutes)          │
   └──────────────────────────────────────────┘
                      ↓
                      
2. APPDAEMON APP (main.py)
   ┌──────────────────────────────────────────┐
   │ TrainScheduleMonitor runs automatically  │
   │ → Queries RTT API for 08:10 train       │
   │ → Checks delay/cancellation status       │
   └──────────────────────────────────────────┘
                      ↓
                      
3. FIRES EVENTS TO HOME ASSISTANT
   ┌──────────────────────────────────────────┐
   │ ✓ train_on_time                          │
   │ ⚠ train_delayed (+ minutes_delayed)      │
   │ ❌ train_service_cancelled               │
   │ 🚀 train_early (+ minutes_early)         │
   └──────────────────────────────────────────┘
                      ↓
                      
4. HOME ASSISTANT AUTOMATIONS LISTEN
   ┌──────────────────────────────────────────┐
   │ Your automations are triggered by these  │
   │ events and perform actions...            │
   └──────────────────────────────────────────┘
                      ↓
                      
5. ACTIONS YOU CONFIGURE
   ┌──────────────────┬───────────────────┬──────────────────┐
   │  📱 Notifications │  💡 Smart Lights  │  🔊 Announcements │
   ├──────────────────┼───────────────────┼──────────────────┤
   │ "Train delayed   │ Turn light red    │ "Your train has  │
   │  10 minutes!"    │ if delayed        │  been cancelled" │
   └──────────────────┴───────────────────┴──────────────────┘
```

## Example Timeline: Monday Morning

```
Time     What Happens
─────────────────────────────────────────────────────────────
07:10    ✓ App checks 08:10 train → On time
         ✓ Fires: train_on_time
         💡 Green light turns on

07:20    ✓ App checks 08:10 train → Still on time
         ✓ Fires: train_on_time
         💡 Light stays green

07:30    ⚠ App checks 08:10 train → 5 min delay detected!
         ⚠ Fires: train_delayed (minutes_delayed: 5)
         💡 Light turns orange
         📱 Notification: "Train delayed 5 minutes"

07:40    ⚠ App checks 08:10 train → Now 12 min delay!
         ⚠ Fires: train_delayed (minutes_delayed: 12)
         💡 Light turns red (>10 min delay)
         📱 Notification: "Major delay - 12 minutes"

07:50    ⚠ App checks 08:10 train → Still 12 min delay
         ⚠ Fires: train_delayed (minutes_delayed: 12)
         (No new notification - same status)

08:00    ⚠ App checks 08:10 train → Delay improved to 8 min
         ⚠ Fires: train_delayed (minutes_delayed: 8)
         💡 Light turns orange (<10 min delay)
         📱 Notification: "Delay reduced to 8 minutes"

08:10    ⚠ Final check before departure
         ⚠ Fires: train_delayed (minutes_delayed: 8)

08:15    💡 Light turns off (after departure time)
```

## Files You Need to Set Up

### On Your Computer (Local Testing)
```
train-schedule-monitor/
├── main.py                    ← The AppDaemon app code
├── test_local.py              ← Local test script
└── .env                       ← Your API credentials (for testing)
```

### In Home Assistant / AppDaemon
```
/config/appdaemon/
├── apps/
│   ├── apps.yaml              ← App configuration
│   └── main.py                ← Copy your app here
├── secrets.yaml               ← Your API credentials
└── logs/                      ← Check here for errors
```

### In Home Assistant (Automations)
```
/config/
├── automations.yaml           ← Add your automations here
└── configuration.yaml         ← Should include: automation: !include automations.yaml
```

## Quick Setup Checklist

### ✅ Step 1: Local Testing
- [ ] Create `.env` file with RTT credentials
- [ ] Run `python test_local.py` to verify API access
- [ ] Confirm you see train data in the output

### ✅ Step 2: Deploy to AppDaemon
- [ ] Copy `main.py` to `/config/appdaemon/apps/`
- [ ] Create `/config/appdaemon/secrets.yaml` with credentials
- [ ] Add configuration to `/config/appdaemon/apps/apps.yaml`
- [ ] Restart AppDaemon
- [ ] Check logs: `/config/appdaemon/logs/`

### ✅ Step 3: Create Home Assistant Automations
- [ ] Copy `quick_start_automation.yaml` to test
- [ ] Test by firing manual events (Developer Tools)
- [ ] Verify notification appears in HA
- [ ] Customize automations for your needs

### ✅ Step 4: Monitor & Enjoy
- [ ] Check that automations trigger during scheduled times
- [ ] Review AppDaemon logs for any errors
- [ ] Adjust notification thresholds as needed

## Getting Help

### Check These First:
1. **AppDaemon Logs:** `/config/appdaemon/logs/error.log`
2. **Home Assistant Logs:** Settings → System → Logs
3. **Automation Traces:** Settings → Automations → Your automation → Traces tab

### Common Issues:

**"No events firing"**
→ Check AppDaemon is running and app initialized
→ Verify it's a weekday during monitoring hours (07:10-08:10)

**"Automation not triggering"**
→ Test by manually firing event in Developer Tools
→ Check automation conditions aren't blocking execution

**"API errors in logs"**
→ Verify credentials in secrets.yaml
→ Check station codes are valid CRS codes

## Need More Help?

- 📖 [APPDAEMON_SETUP.md](APPDAEMON_SETUP.md) - Full deployment guide
- 🤖 [HOME_ASSISTANT_AUTOMATIONS_GUIDE.md](HOME_ASSISTANT_AUTOMATIONS_GUIDE.md) - Detailed automation examples
- 🧪 [TESTING.md](TESTING.md) - Local testing guide
- 🔐 [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) - Credentials configuration
