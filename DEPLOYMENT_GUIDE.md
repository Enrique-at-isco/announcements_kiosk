# Deployment Guide - Raspberry Pi Kiosk

## Initial Setup on Raspberry Pi

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Chromium and ChromeDriver
sudo apt install -y chromium-browser chromium-chromedriver

# Install Python dependencies
sudo apt install -y python3-pip python3-venv
pip3 install selenium
```

### 2. Deploy Files

```bash
# Create directory structure
mkdir -p /home/annkiosk/announcements_kiosk/pipiosk_v1
mkdir -p /home/annkiosk/announcements_kiosk/html

# Copy files from repository
# - kiosk_controller.py
# - html_generator.py
# - kiosk_manager.py
# - config.json (to pipiosk_v1/)
```

### 3. Install Systemd Service

```bash
# Copy service file
sudo cp kiosk.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable kiosk.service

# Start service
sudo systemctl start kiosk.service
```

## Service Management Commands

### Check Status
```bash
sudo systemctl status kiosk.service
```

### View Logs (Live)
```bash
# Follow logs in real-time
sudo journalctl -u kiosk.service -f

# View last 50 lines
sudo journalctl -u kiosk.service -n 50

# View logs since boot
sudo journalctl -u kiosk.service -b
```

### Restart Service
```bash
# Restart (stops and starts)
sudo systemctl restart kiosk.service

# Reload config without full restart
# (Note: config changes are auto-detected, but restart ensures clean state)
sudo systemctl restart kiosk.service
```

### Stop/Start Service
```bash
# Stop
sudo systemctl stop kiosk.service

# Start
sudo systemctl start kiosk.service

# Disable (prevent auto-start on boot)
sudo systemctl disable kiosk.service
```

## Updating the System

### Update Code
```bash
cd /home/annkiosk/announcements_kiosk

# Pull latest changes
git pull origin main

# Restart service to apply changes
sudo systemctl restart kiosk.service
```

### Add New Content

**Add Smartsheet Page:**
```bash
cd /home/annkiosk/announcements_kiosk

# Create the HTML page
python3 kiosk_manager.py smartsheet "Page Title" "https://..." --add-to-config

# Restart kiosk to load new page
sudo systemctl restart kiosk.service
```

**Add PDF Viewer:**
```bash
# Upload PDF to Pi
# Create the HTML page
python3 kiosk_manager.py pdf "PDF Title" "file:///home/annkiosk/pdfs/file.pdf" --add-to-config

# Restart kiosk
sudo systemctl restart kiosk.service
```

**Add Web URL:**
```bash
# Manually edit config
nano /home/annkiosk/announcements_kiosk/pipiosk_v1/config.json

# Add URL to "urls" array
# Restart kiosk
sudo systemctl restart kiosk.service
```

## Configuration Changes

### Edit Cycle Delay
```bash
# Edit config
nano /home/annkiosk/announcements_kiosk/pipiosk_v1/config.json

# Change "cycle_delay" value (in seconds)
# Restart kiosk
sudo systemctl restart kiosk.service
```

### Reorder Pages
```bash
# Edit config
nano /home/annkiosk/announcements_kiosk/pipiosk_v1/config.json

# Reorder URLs in the "urls" array
# Restart kiosk
sudo systemctl restart kiosk.service
```

## Troubleshooting

### Kiosk Not Starting
```bash
# Check service status
sudo systemctl status kiosk.service

# Check for errors in logs
sudo journalctl -u kiosk.service -n 50

# Common issues:
# 1. Config file missing or invalid JSON
# 2. ChromeDriver not installed
# 3. Display not available (DISPLAY=:0)
# 4. Permissions issues
```

### Browser Crashes
```bash
# Check system resources
free -h
top

# Chromium may crash on low memory
# Consider reducing number of tabs or cycle delay
```

### Pages Not Loading
```bash
# Check URLs in config
cat /home/annkiosk/announcements_kiosk/pipiosk_v1/config.json

# Test URLs manually
chromium-browser <url>

# Check file:// paths exist
ls -l /home/annkiosk/announcements_kiosk/html/
```

### Config Changes Not Applied
```bash
# Restart service
sudo systemctl restart kiosk.service

# Verify config is valid JSON
python3 -m json.tool /home/annkiosk/announcements_kiosk/pipiosk_v1/config.json
```

## Remote Access (SSH)

### Connect via SSH
```bash
ssh annkiosk@<pi-ip-address>
```

### Restart Kiosk Remotely
```bash
ssh annkiosk@<pi-ip-address> "sudo systemctl restart kiosk.service"
```

### View Logs Remotely
```bash
ssh annkiosk@<pi-ip-address> "sudo journalctl -u kiosk.service -f"
```

## Performance Tips

1. **Reduce tabs**: Fewer tabs = less memory usage
2. **Increase cycle delay**: Gives browser more time to stabilize
3. **Disable GPU acceleration**: Already done in kiosk_controller.py
4. **Close other applications**: Maximize resources for kiosk
5. **Use swap file**: If RAM is limited

## Auto-Start on Boot

The service is configured to start automatically on boot via systemd.

To verify:
```bash
sudo systemctl is-enabled kiosk.service
# Should output: enabled
```

To disable auto-start:
```bash
sudo systemctl disable kiosk.service
```

To re-enable:
```bash
sudo systemctl enable kiosk.service
```

## File Locations Reference

| Location | Purpose |
|----------|---------|
| `/home/annkiosk/announcements_kiosk/kiosk_controller.py` | Main kiosk script |
| `/home/annkiosk/announcements_kiosk/kiosk_manager.py` | Content management CLI |
| `/home/annkiosk/announcements_kiosk/html_generator.py` | HTML generation module |
| `/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json` | Configuration file |
| `/home/annkiosk/announcements_kiosk/html/` | Generated HTML files |
| `/etc/systemd/system/kiosk.service` | Systemd service file |
| `/usr/bin/chromedriver` | ChromeDriver binary |
| `/usr/bin/chromium-browser` | Chromium browser |

## Next Steps: Web Management Interface

When the web management interface is developed, it will need to:

1. **Read config**: Display current URLs and settings
2. **Modify config**: Add/remove/reorder URLs
3. **Restart service**: Execute `sudo systemctl restart kiosk.service`
4. **View logs**: Display recent log entries

For the web interface to restart the service without password, add to sudoers:
```bash
sudo visudo

# Add this line:
annkiosk ALL=(ALL) NOPASSWD: /bin/systemctl restart kiosk.service
annkiosk ALL=(ALL) NOPASSWD: /bin/systemctl status kiosk.service
annkiosk ALL=(ALL) NOPASSWD: /bin/journalctl -u kiosk.service *
```
