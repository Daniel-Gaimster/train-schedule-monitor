#!/usr/bin/env fish
# Deploys train-schedule-monitor.py to the AppDaemon add-on on the Home Assistant Yellow
# and restarts the add-on so the change takes effect.
#
# Requires: SSH key at ~/.ssh/ha_yellow authorized on the Yellow's SSH add-on
# (Settings > Add-ons > Terminal & SSH > Configuration > authorized_keys),
# and HA-MCP connected in this session to trigger the AppDaemon restart.

set -l REMOTE hassio@homeassistant.local
set -l REMOTE_PATH /addon_configs/a0d7b954_appdaemon/apps/train-schedule-monitor.py
set -l KEY ~/.ssh/ha_yellow

echo "Copying train-schedule-monitor.py to $REMOTE:$REMOTE_PATH ..."
scp -i $KEY train-schedule-monitor.py $REMOTE:$REMOTE_PATH
if test $status -ne 0
    echo "Copy failed." >&2
    exit 1
end

echo "Copied. Restart the AppDaemon add-on (slug a0d7b954_appdaemon) via Claude/HA-MCP, or manually in Settings > Add-ons > AppDaemon."
