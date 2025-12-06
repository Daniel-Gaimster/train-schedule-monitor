# Credentials Setup Guide

This project uses different credential storage methods depending on how you're running it:

## For Local Testing (`.env` file)

When testing locally with `test_local.py`, credentials are stored in a `.env` file:

### Setup:
1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   USERNAME=your_rtt_username
   PASSWORD=your_rtt_password
   ```

3. The `.env` file is automatically ignored by git (see `.gitignore`)

## For AppDaemon Deployment (`secrets.yaml` file)

When running in Home Assistant with AppDaemon, credentials are stored in `secrets.yaml`:

### Setup:
1. Create or edit `secrets.yaml` in your AppDaemon configuration directory (same location as `apps.yaml`):
   ```yaml
   # secrets.yaml
   rtt_username: "your_rtt_username"
   rtt_password: "your_rtt_password"
   ```

2. Reference these secrets in your `apps.yaml`:
   ```yaml
   train_monitor:
     module: main
     class: TrainScheduleMonitor
     username: !secret rtt_username
     password: !secret rtt_password
     # ... other config
   ```

3. Never commit `secrets.yaml` to version control!

## Getting RTT API Credentials

1. Go to https://www.realtimetrains.co.uk/about/developer/
2. Create an account or sign in
3. Your credentials will be provided on your account page
4. Use these credentials in either `.env` (local testing) or `secrets.yaml` (AppDaemon)

## Security Checklist

✅ Both `.env` and `secrets.yaml` are in `.gitignore`  
✅ Only commit `.env.example` and `secrets.yaml.example` with placeholder values  
✅ Use `!secret` syntax in AppDaemon configuration files  
✅ Never hardcode credentials in Python files  

## Quick Reference

| Environment | File | Location |
|------------|------|----------|
| Local Testing | `.env` | Project root |
| AppDaemon | `secrets.yaml` | AppDaemon config directory (with `apps.yaml`) |

Both files serve the same purpose but use different formats for their respective environments.
