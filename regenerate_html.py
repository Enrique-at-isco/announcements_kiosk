#!/usr/bin/env python3
"""
Regenerate existing HTML files to use HTTP URLs for both PDFs and Smartsheets
This fixes the file:// URL blocking issue in Chrome
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from html_generator import generate_smartsheet_html, generate_pdf_html

def regenerate_html_files():
    """Regenerate known HTML files with proper HTTP URLs"""
    
    print("Regenerating HTML files with HTTP support...\n")
    
    # Regenerate Weekly Scoreboard Smartsheet with 80% zoom (to fix cutoff)
    print("1. Weekly Scoreboard (Smartsheet)")
    try:
        output = generate_smartsheet_html(
            title="Weekly Scoreboard",
            smartsheet_url="https://publish.smartsheet.com/fc2e49dfa071477fa5b15a00cc062dbc",
            output_filename="weekly_scoreboard.html",
            zoom=0.8  # 80% zoom to prevent cutoff
        )
        print(f"   ✓ Created: {output}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Regenerate Florida Flash PDF viewer
    print("2. Florida Flash PDF")
    try:
        # This will auto-convert to http://localhost:5000/pdfs/florida_flash_feb_26.pdf
        output = generate_pdf_html(
            title="Florida Flash",
            pdf_path="file:///home/annkiosk/pdfs/florida_flash_feb_26.pdf",
            output_filename="florida_flash_pdf.html",
            scroll_speed=50
        )
        print(f"   ✓ Created: {output}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("HTML files regenerated!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python3 convert_file_urls_to_http.py")
    print("2. Run: sudo systemctl restart kiosk-web.service")
    print("3. Run: sudo systemctl restart kiosk.service")
    print()

if __name__ == '__main__':
    regenerate_html_files()
