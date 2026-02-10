# Web Manager Guide

## Overview

The Kiosk Web Manager provides a user-friendly web interface to manage your kiosk display system from any device on your network. No need to SSH or edit files manually!

## Features

- 📋 **Manage URLs** - View, add, remove URLs from slideshow
- 📊 **Add Smartsheets** - Create Smartsheet pages with custom titles
- 📄 **Add PDFs** - Create PDF viewers with auto-scroll
- ⚙️ **Settings** - Change cycle delay and other options
- 🔄 **Service Control** - Restart the kiosk with one click
- 📝 **Logs** - View live kiosk logs
- 🌐 **Remote Access** - Access from any device on same network

## Installation

### 1. Install Dependencies

```bash
cd /home/annkiosk/announcements_kiosk

# Install Flask
pip3 install -r requirements.txt
# or
pip3 install Flask
```

### 2. Configure Sudoers (for service restart)

To allow the web interface to restart the kiosk service without password:

```bash
sudo visudo

# Add these lines at the end:
annkiosk ALL=(ALL) NOPASSWD: /bin/systemctl restart kiosk.service
annkiosk ALL=(ALL) NOPASSWD: /bin/systemctl status kiosk.service
annkiosk ALL=(ALL) NOPASSWD: /bin/journalctl -u kiosk.service *
```

Save and exit (Ctrl+X, Y, Enter).

### 3. Start the Web Manager

```bash
cd /home/annkiosk/announcements_kiosk
python3 web_manager.py
```

The web interface will be available at:
- On Pi: `http://localhost:5000`
- From other devices: `http://<pi-ip-address>:5000`

### 4. Optional: Run as Service (Auto-start)

Create a systemd service for the web manager:

```bash
sudo nano /etc/systemd/system/kiosk-web.service
```

Add:
```ini
[Unit]
Description=Kiosk Web Manager
After=network.target

[Service]
Type=simple
User=annkiosk
WorkingDirectory=/home/annkiosk/announcements_kiosk
ExecStart=/home/annkiosk/announcements_kiosk/venv/bin/python3 /home/annkiosk/announcements_kiosk/web_manager.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kiosk-web.service
sudo systemctl start kiosk-web.service
```

## Usage

### Finding Your Pi's IP Address

```bash
hostname -I
```

Use the first IP address shown (e.g., `192.168.1.100`).

### Accessing from Another Device

1. Open a web browser on your laptop, phone, or tablet
2. Go to: `http://<pi-ip-address>:5000`
3. Example: `http://192.168.1.100:5000`

### Managing URLs

**View Current Slideshow:**
- Click "📋 Manage URLs" tab
- See all current pages in order
- Each page shows its full path

**Remove a URL:**
- Click the 🗑️ Remove button next to any URL
- Confirm the removal
- Changes saved automatically

**Reorder URLs:**
- URLs display in the order they'll be shown
- To reorder, you'll need to remove and re-add them
- (Drag-and-drop coming in future update)

### Adding Smartsheet Pages

1. Click "📊 Add Smartsheet" tab
2. Enter a **Page Title** (e.g., "Weekly Scoreboard")
3. Paste your **Smartsheet Published URL**
4. Check "Add to kiosk slideshow automatically" to add it immediately
5. Click "✨ Create Smartsheet Page"

The system will:
- Generate an HTML file for the Smartsheet
- Save it to the `html/` directory
- Add it to your slideshow (if checked)

### Adding PDF Viewers

1. First, upload your PDF to the Pi:
   ```bash
   scp document.pdf annkiosk@<pi-ip>:/home/annkiosk/pdfs/
   ```

2. Click "📄 Add PDF" tab
3. Enter a **Page Title** (e.g., "Safety Manual")
4. Enter the **PDF File Path**: `file:///home/annkiosk/pdfs/document.pdf`
5. Set **Auto-scroll Speed** (pixels/second, default: 50)
6. Check "Add to kiosk slideshow automatically" to add it immediately
7. Click "✨ Create PDF Viewer"

The system will:
- Generate an HTML file with PDF viewer
- Configure dual-page view and auto-scroll
- Save it to the `html/` directory
- Add it to your slideshow (if checked)

### Changing Settings

1. Click "⚙️ Settings" tab
2. Adjust **Cycle Delay** (seconds per page)
3. Click "💾 Save Settings"
4. Click "🔄 Restart Kiosk" to apply changes

### Viewing Logs

1. Click "📝 Logs" tab
2. View recent kiosk service logs
3. Click "🔄 Refresh Logs" to update
4. Useful for troubleshooting issues

### Restarting the Kiosk

Click the "🔄 Restart Kiosk" button in the header at any time to:
- Apply configuration changes
- Reload updated content
- Recover from errors

## Tips

**Safe to Experiment:**
- All actions can be undone
- Removing a URL doesn't delete the file
- You can always re-add pages
- Backups are in `~/kiosk_migration_backup_*/`

**Network Access:**
- Ensure your device is on the same network as the Pi
- Check firewall isn't blocking port 5000
- Use Pi's local IP, not 127.0.0.1

**Performance:**
- Keep URLs to a reasonable number (< 20 recommended)
- Too many tabs can slow down the Pi
- Monitor logs if experiencing issues

**Security:**
- Web manager has no authentication by default
- Only accessible on local network
- For production, consider adding login

## Troubleshooting

### Can't Access Web Interface

```bash
# Check if web manager is running
ps aux | grep web_manager.py

# Check if port 5000 is listening
sudo netstat -tulpn | grep 5000

# Check firewall
sudo ufw status

# Try starting it manually
cd /home/annkiosk/announcements_kiosk
python3 web_manager.py
```

### "Permission Denied" on Restart

You need to configure sudoers (see Installation step 2).

### Changes Not Appearing in Kiosk

Click "🔄 Restart Kiosk" after making changes. The kiosk needs to reload to show updated configuration.

### Service Status Shows "inactive"

```bash
# Check service status
sudo systemctl status kiosk.service

# View logs for errors
sudo journalctl -u kiosk.service -n 50

# Restart service
sudo systemctl restart kiosk.service
```

## API Reference

For developers wanting to integrate with the web manager:

### GET /api/config
Get current configuration

### POST /api/config/update
Update configuration (requires JSON body)

### POST /api/urls/add
Add URL to slideshow

### POST /api/urls/remove
Remove URL from slideshow

### POST /api/smartsheet/create
Create Smartsheet HTML page

### POST /api/pdf/create
Create PDF viewer HTML page

### POST /api/service/restart
Restart kiosk service

### GET /api/logs
Get recent service logs

See `web_manager.py` for full API documentation.

## Future Enhancements

Planned features:
- [ ] Drag-and-drop URL reordering
- [ ] User authentication
- [ ] File upload for PDFs
- [ ] Preview pages before adding
- [ ] Schedule-based content (show different content at different times)
- [ ] Mobile app
- [ ] Multiple kiosk management

## Support

If you encounter issues:
1. Check the logs tab in the web interface
2. Check systemd service status
3. Review configuration file validity
4. See main troubleshooting guides in DEPLOYMENT_GUIDE.md
