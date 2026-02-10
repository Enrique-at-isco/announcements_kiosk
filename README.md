# Announcements Kiosk

A Raspberry Pi-based kiosk system that displays rotating announcements, scoreboards, schedules, and other content on a TV. Supports Smartsheet embeds, PDF documents, and web pages with automatic cycling and refresh.

## Features

- 📊 **Smartsheet Integration**: Display live Smartsheet data with custom titles
- 📄 **PDF Viewer**: Show PDFs with dual-page view and auto-scrolling
- 🌐 **Web Pages**: Display any web content (time, weather, custom sites)
- 🔄 **Auto-Cycling**: Automatically rotate through content at configurable intervals
- 🔧 **Easy Management**: CLI tools to add/remove content without editing code
- 🚀 **Auto-Start**: Runs on boot via systemd service
- 📝 **Config Hot-Reload**: Detects config changes automatically (WIP)

## Quick Start

### Creating Content

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
├── html_generator.py            # HTML page generation module
├── kiosk_manager.py            # CLI tool for content management
├── kiosk.service               # Systemd service file
├── config.json                 # Configuration file
├── html/                       # Generated HTML display pages
│   ├── weekly_scoreboard.html
│   ├── break_schedule.html
│   └── ...
├── KIOSK_MANAGER_GUIDE.md     # User guide for content management
└── DEPLOYMENT_GUIDE.md        # Raspberry Pi deployment guide
```

## Documentation

- **[Kiosk Manager Guide](KIOSK_MANAGER_GUIDE.md)** - How to create and manage content
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Raspberry Pi setup and service management

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
- [ ] Web-based management interface
- [ ] Remote content management over network
- [ ] Schedule-based content switching
- [ ] Content preview before deployment

## License

MIT
