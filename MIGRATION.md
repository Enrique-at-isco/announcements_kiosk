# Migration from dig_bick_kiosk_v25.py to kiosk_controller.py

## What Changed

### Main Script: `dig_bick_kiosk_v25.py` → `kiosk_controller.py`

#### Removed Features:
- ❌ Google/Outlook login detection (`click_signin_buttons()`)
- ❌ Sign-in button clicking logic
- ❌ Hard-coded sleep timers for login pages

#### New Features:
- ✅ Config hot-reload detection (auto-detects config.json changes)
- ✅ Better error handling and retry logic
- ✅ Cleaner code structure with docstrings
- ✅ More detailed logging with timestamps
- ✅ Graceful shutdown handling
- ✅ Improved tab refresh on each cycle

#### Still Works The Same:
- ✅ Loads URLs from config.json
- ✅ Opens all URLs in separate tabs
- ✅ Cycles through tabs at configured interval
- ✅ Refreshes each tab when switching to it
- ✅ Runs in kiosk mode with same Chrome options
- ✅ Works as a systemd service

## Migration Steps for Raspberry Pi

### Option 1: Update Service in Place

```bash
# On your Raspberry Pi
cd /home/annkiosk/announcements_kiosk

# Stop current service
sudo systemctl stop kiosk.service

# Pull latest changes
git pull origin main

# Update service file to use new script
sudo cp kiosk.service /etc/systemd/system/kiosk.service

# Or manually edit the service file
sudo nano /etc/systemd/system/kiosk.service
# Change: ExecStart=/usr/bin/python3 /home/annkiosk/announcements_kiosk/kiosk_controller.py

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart kiosk.service

# Check status
sudo systemctl status kiosk.service

# Watch logs to verify it's working
sudo journalctl -u kiosk.service -f
```

### Option 2: Test First, Then Switch

```bash
# Test the new script manually first
cd /home/annkiosk/announcements_kiosk
python3 kiosk_controller.py

# If it works, stop it (Ctrl+C) and update the service
sudo systemctl stop kiosk.service
sudo nano /etc/systemd/system/kiosk.service
# Update ExecStart path
sudo systemctl daemon-reload
sudo systemctl start kiosk.service
```

## Your Current Service File

Your existing service likely looks like this:

```ini
[Service]
ExecStart=/usr/bin/python3 /home/annkiosk/announcements_kiosk/dig_bick_kiosk_v25.py
```

Update it to:

```ini
[Service]
ExecStart=/usr/bin/python3 /home/annkiosk/announcements_kiosk/kiosk_controller.py
```

## Why This Update is Better

1. **No More Login Issues**: Since you're using Smartsheets now, all the Outlook/Google login logic was unnecessary complexity that could cause problems

2. **Cleaner Code**: Easier to maintain and debug

3. **Better Logging**: More informative log messages help troubleshoot issues

4. **Config Hot-Reload**: The new version detects when config.json changes (though you still need to restart for now)

5. **Future-Ready**: The new code structure is ready for the web management interface

## Config File Location

Both scripts use the same config file location:
```
/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json
```

**No changes needed to your config.json!**

## Backwards Compatible

The new script is 100% backwards compatible with your existing setup:
- Same config file format
- Same URLs (file:// or https://)
- Same cycle_delay behavior
- Same Chrome options
- Same systemd service behavior

The only difference is the script filename.

## Rollback Plan

If you need to rollback:

```bash
sudo systemctl stop kiosk.service
sudo nano /etc/systemd/system/kiosk.service
# Change back to: ExecStart=.../dig_bick_kiosk_v25.py
sudo systemctl daemon-reload
sudo systemctl start kiosk.service
```

Both scripts are still in your repository, so switching between them is just a service file change.

## Verification

After migration, verify everything works:

```bash
# Check service is running
sudo systemctl status kiosk.service

# Watch logs
sudo journalctl -u kiosk.service -f

# You should see logs like:
# [2026-02-10 10:30:45] [INFO] Kiosk Controller Starting
# [2026-02-10 10:30:45] [INFO] Loaded 8 URLs with cycle delay of 40s
# [2026-02-10 10:30:48] [INFO] Chrome driver created successfully
# [2026-02-10 10:30:50] [INFO] Successfully opened 8 browser tabs
# [2026-02-10 10:30:50] [INFO] Starting tab cycling...
```

## Questions?

If you run into issues:
1. Check the logs: `sudo journalctl -u kiosk.service -n 100`
2. Try running manually: `python3 kiosk_controller.py`
3. Verify config is valid: `python3 -m json.tool config.json`
4. Compare behavior with old script if needed

Both scripts are functionally equivalent for your use case, so the migration should be seamless!
