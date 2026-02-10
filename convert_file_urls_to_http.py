#!/usr/bin/env python3
"""
Convert file:// URLs in config.json to http://localhost:5000/html/ URLs
This allows HTML files to be served via HTTP instead of blocked file:// protocol
"""

import json
from pathlib import Path

CONFIG_FILE = Path('/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json')

# For development/testing
if not CONFIG_FILE.exists():
    CONFIG_FILE = Path('./config.json')

def convert_urls():
    """Convert all file:// URLs to http://localhost:5000/html/ URLs"""
    try:
        # Load config
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        updated = False
        new_urls = []
        
        for url in config.get('urls', []):
            if url.startswith('file:///home/annkiosk/announcements_kiosk/html/'):
                # Extract filename from file:// URL
                filename = url.split('/html/')[-1]
                # Convert to http://localhost URL
                new_url = f'http://localhost:5000/html/{filename}'
                new_urls.append(new_url)
                updated = True
                print(f"Converted: {url}")
                print(f"       to: {new_url}")
            else:
                new_urls.append(url)
        
        if updated:
            # Update config
            config['urls'] = new_urls
            
            # Save config
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✓ Updated {CONFIG_FILE}")
            print(f"✓ Converted {len([u for u in new_urls if 'localhost' in u])} file:// URLs to http://")
            print("\nRestart kiosk service to apply changes:")
            print("  sudo systemctl restart kiosk.service")
        else:
            print("No file:// URLs found in config")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(convert_urls())
