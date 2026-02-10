# Announcements Kiosk

A Raspberry Pi-based kiosk system that displays rotating announcements, scoreboards, schedules, and other content on a TV. Supports Smartsheet embeds, PDF documents, and web pages with automatic cycling and refresh.

## Features

- 🌐 **Web-Based Management**: Full control from any device on your network
- 📊 **Smartsheet Integration**: Display live Smartsheet data with custom titles
- 📄 **PDF Viewer**: Show PDFs with dual-page view and auto-scrolling
- 🌐 **Web Pages**: Display any web content (time, weather, custom sites)
- 🔄 **Auto-Cycling**: Automatically rotate through content at configurable intervals
- 🔧 **Easy Management**: Web UI + CLI tools - no manual file editing needed
- 🚀 **Auto-Start**: Runs on boot via systemd service
- 📝 **Live Logs**: Monitor kiosk status in real-time

## Quick Start

### Web Manager (Recommended)

**Start the web interface:**
```bash
cd /home/annkiosk/announcements_kiosk
pip3 install flask
python3 web_manager.py
```

**Access from any device on your network:**
- Open browser: `http://<pi-ip-address>:5000`
- Add/remove content with visual interface
- Restart kiosk with one click
- View live logs

See [WEB_MANAGER_GUIDE.md](WEB_MANAGER_GUIDE.md) for details.

### Command Line (Alternative)

**Add a Smartsheet:**
```bash
python3 kiosk_manager.py smartsheet "Weekly Scoreboard" "https://app.smartsheet.com/..." --add-to-config
```

**Add a PDF:**
```bash
python3 kiosk_manager.py pdf "Safety Manual" "file:///home/annkiosk/pdfs/safety.pdf" --add-to-config
```

**View all content:**
```bash
python3 kiosk_manager.py list
python3 kiosk_manager.py config
```

### On Raspberry Pi

**Restart kiosk:**
```bash
sudo systemctl restart kiosk.service
```

**View logs:**
```bash
sudo journalctl -u kiosk.service -f
```

## Project Structure

```
announcements_kiosk/
├── kiosk_controller.py          # Main kiosk controller (runs as service)
├── web_manager.py               # 🌐 Web management interface (Flask app)
├── html_generator.py            # HTML page generation module
├── kiosk_manager.py             # CLI tool for content management
├── kiosk.service                # Systemd service file
├── config.json                  # Configuration file (example)
├── requirements.txt             # Python dependencies
├── templates/                   # Web UI templates
│   └── index.html
├── html/                        # Generated HTML display pages
│   ├── weekly_scoreboard.html
│   ├── break_schedule.html
│   └── ...
├── WEB_MANAGER_GUIDE.md        # Web interface user guide
├── KIOSK_MANAGER_GUIDE.md      # CLI tool user guide
├── DEPLOYMENT_GUIDE.md         # Raspberry Pi deployment guide
└── MIGRATION.md                # Migration from old versions
```

## Documentation

- **[Web Manager Guide](WEB_MANAGER_GUIDE.md)** - Web interface for managing content (recommended!)
- **[Kiosk Manager Guide](KIOSK_MANAGER_GUIDE.md)** - CLI tool for content management
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Raspberry Pi setup and service management
- **[Migration Guide](MIGRATION.md)** - Upgrading from older versions

## Configuration

Edit `config.json` (or use `kiosk_manager.py --add-to-config`):

```json
{
  "urls": [
    "file:///home/annkiosk/announcements_kiosk/html/weekly_scoreboard.html",
    "file:///home/annkiosk/announcements_kiosk/html/break_schedule.html",
    "https://time.is/clock",
    "https://www.windy.com/..."
  ],
  "cycle_delay": 40
}
```

- **urls**: List of pages to display (local HTML or web URLs)
- **cycle_delay**: Seconds to show each page before switching

## Requirements

- Raspberry Pi 5 (or compatible)
- Chromium Browser
- Python 3.7+
- Selenium WebDriver
- ChromeDriver

## Installation

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete setup instructions.

## Roadmap

- [x] Smartsheet HTML generator
- [x] PDF viewer with auto-scroll
- [x] CLI content management tool
- [x] Systemd service integration
- [x] Web-based management interface
- [x] Remote content management over network
- [ ] Drag-and-drop URL reordering in web UI
- [ ] Schedule-based content switching
- [ ] Content preview before deployment
- [ ] User authentication for web interface
- [ ] Mobile app

## License

MIT
