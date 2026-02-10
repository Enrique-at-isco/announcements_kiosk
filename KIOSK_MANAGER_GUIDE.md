# Kiosk Content Manager - User Guide

## Overview
The Kiosk Content Manager allows you to easily create HTML display pages for your Raspberry Pi kiosk system. It supports:
- **Smartsheet embeds**: Display live Smartsheet data with custom titles
- **PDF viewers**: Display PDFs with dual-page view and auto-scrolling
- **Web links**: Any standard web URL (added directly to config.json)

## Quick Start

### 1. Create a Smartsheet Page

```bash
python kiosk_manager.py smartsheet "Weekly Scoreboard" "https://app.smartsheet.com/sheets/YOUR_SHEET_ID"
```

This creates an HTML file that:
- Shows your custom title in the header
- Automatically loads the Smartsheet URL
- Stores the URL in browser localStorage (unique per page)
- Has a settings button to change the URL if needed

**Options:**
- `-o filename` - Custom output filename (default: auto-generated from title)
- `-a` or `--add-to-config` - Automatically add to config.json

**Example with auto-add:**
```bash
python kiosk_manager.py smartsheet "Break Schedule" "https://..." --add-to-config
```

### 2. Create a PDF Viewer Page

```bash
python kiosk_manager.py pdf "Safety Manual" "file:///home/annkiosk/pdfs/safety.pdf"
```

This creates an HTML file that:
- Shows your custom title in the header
- Displays two PDF pages side-by-side
- Auto-scrolls through the PDF at a configurable speed
- Resets to the top when it reaches the end
- Includes controls to pause/resume and reset

**Options:**
- `-o filename` - Custom output filename (default: auto-generated from title)
- `-s SPEED` or `--scroll-speed SPEED` - Scroll speed in pixels/second (default: 50)
- `-a` or `--add-to-config` - Automatically add to config.json

**Example with custom speed:**
```bash
python kiosk_manager.py pdf "Training Manual" "file:///path/to/file.pdf" --scroll-speed 30
```

### 3. List Generated Files

```bash
python kiosk_manager.py list
```

Shows all HTML files in the `html/` directory with their sizes.

### 4. View Current Config

```bash
python kiosk_manager.py config
```

Shows the current config.json contents including all URLs and cycle delay.

## Directory Structure

```
/home/annkiosk/announcements_kiosk/
├── pipiosk_v1/
│   └── config.json                 # Main configuration file
├── html/                           # Generated HTML files
│   ├── weekly_scoreboard.html
│   ├── break_schedule.html
│   ├── safety_manual_pdf.html
│   └── ...
├── dig_bick_kiosk_v25.py          # Main kiosk controller
├── html_generator.py              # HTML generation module
└── kiosk_manager.py               # CLI tool (this)
```

## Configuration

### config.json Format

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

- **urls**: Array of URLs to cycle through (file:// or https://)
- **cycle_delay**: Seconds to display each page before switching

### Adding URLs Manually

You can manually edit `config.json` to:
1. Add web URLs directly (https://...)
2. Reorder pages
3. Change the cycle delay
4. Remove pages

### File Paths

**On Production (Raspberry Pi):**
- Config: `/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json`
- HTML output: `/home/annkiosk/announcements_kiosk/html/`

**On Development (Codespace):**
- Config: `./config.json`
- HTML output: `./html/`

## Workflow Examples

### Adding a New Smartsheet
1. Get your Smartsheet published/embed URL
2. Run: `python kiosk_manager.py smartsheet "Your Title" "URL" --add-to-config`
3. Restart the kiosk: `systemctl restart kiosk` (on Pi)

### Adding a New PDF
1. Upload your PDF to the Pi: `/home/annkiosk/pdfs/`
2. Run: `python kiosk_manager.py pdf "Title" "file:///home/annkiosk/pdfs/file.pdf" --add-to-config`
3. Restart the kiosk

### Adding a Regular Web Link
1. Manually edit `config.json`
2. Add the URL to the "urls" array
3. Restart the kiosk

## Troubleshooting

### PDF Not Loading
- Ensure the PDF path is correct and uses `file://` protocol
- Check file permissions: `chmod 644 /path/to/file.pdf`
- Check the browser console for errors

### Smartsheet Not Loading
- Verify the URL is a published/embed URL from Smartsheet
- Check if the sheet is publicly accessible
- Try the settings button (⚙️) to manually reload

### Changes Not Appearing
- Ensure you restarted the kiosk after editing config.json
- Check if the HTML file was created: `python kiosk_manager.py list`
- Verify the file path in config.json is correct

## Features

### Smartsheet Pages
✅ Custom title per page  
✅ Auto-loads configured URL  
✅ Settings button to change URL  
✅ Unique localStorage per page  
✅ Full-screen display  
✅ No scrollbars  

### PDF Pages
✅ Custom title per page  
✅ Dual-page (book) view  
✅ Auto-scroll with configurable speed  
✅ Auto-reset when reaching end  
✅ Pause/resume controls  
✅ Page counter  
✅ Responsive scaling  

## Next Steps

Future enhancements planned:
- Web-based management interface
- Live URL management without restarts
- Bulk import from CSV
- Preview mode before adding
- Schedule-based display (show different content at different times)

## Support

For issues or questions:
1. Check the logs: `journalctl -u kiosk -f` (on Pi)
2. Verify config: `python kiosk_manager.py config`
3. Test HTML file directly in browser
