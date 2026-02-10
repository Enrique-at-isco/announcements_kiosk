#!/usr/bin/env python3
"""
Kiosk Content Manager - CLI Tool
Create HTML files for Smartsheets and PDFs for the kiosk system
"""

import sys
import argparse
from pathlib import Path
from html_generator import (
    generate_smartsheet_html,
    generate_pdf_html,
    add_to_config,
    HTML_OUTPUT_DIR,
    CONFIG_FILE
)


def create_smartsheet(args):
    """Create a Smartsheet HTML page"""
    print(f"\n📊 Creating Smartsheet page: {args.title}")
    print(f"   URL: {args.url}")
    
    output_path = generate_smartsheet_html(
        title=args.title,
        smartsheet_url=args.url,
        output_filename=args.output
    )
    
    if args.add_to_config:
        add_to_config(output_path)
    
    print(f"\n✅ Smartsheet page created successfully!")
    print(f"   File: {output_path}")
    return output_path


def create_pdf(args):
    """Create a PDF viewer HTML page"""
    print(f"\n📄 Creating PDF viewer: {args.title}")
    print(f"   PDF: {args.pdf}")
    
    output_path = generate_pdf_html(
        title=args.title,
        pdf_path=args.pdf,
        output_filename=args.output,
        scroll_speed=args.scroll_speed
    )
    
    if args.add_to_config:
        add_to_config(output_path)
    
    print(f"\n✅ PDF viewer created successfully!")
    print(f"   File: {output_path}")
    return output_path


def list_files(args):
    """List all HTML files in the output directory"""
    if not HTML_OUTPUT_DIR.exists():
        print(f"Output directory doesn't exist: {HTML_OUTPUT_DIR}")
        return
    
    html_files = sorted(HTML_OUTPUT_DIR.glob('*.html'))
    
    if not html_files:
        print(f"\nNo HTML files found in {HTML_OUTPUT_DIR}")
        return
    
    print(f"\n📁 HTML files in {HTML_OUTPUT_DIR}:")
    print("=" * 60)
    for i, file in enumerate(html_files, 1):
        size_kb = file.stat().st_size / 1024
        print(f"{i:2d}. {file.name:40s} ({size_kb:.1f} KB)")
    print("=" * 60)
    print(f"Total: {len(html_files)} files\n")


def show_config(args):
    """Show current config.json contents"""
    if not CONFIG_FILE.exists():
        print(f"Config file doesn't exist: {CONFIG_FILE}")
        return
    
    import json
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    print(f"\n⚙️  Current configuration ({CONFIG_FILE}):")
    print("=" * 60)
    print(f"Cycle delay: {config.get('cycle_delay', 'Not set')} seconds")
    print(f"\nURLs ({len(config.get('urls', []))}):")
    for i, url in enumerate(config.get('urls', []), 1):
        print(f"{i:2d}. {url}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Kiosk Content Manager - Create HTML pages for Smartsheets and PDFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create a Smartsheet page
  python kiosk_manager.py smartsheet "Weekly Scoreboard" "https://app.smartsheet.com/..."
  
  # Create a Smartsheet page and add to config
  python kiosk_manager.py smartsheet "Break Schedule" "https://..." --add-to-config
  
  # Create a PDF viewer
  python kiosk_manager.py pdf "Safety Manual" "/path/to/file.pdf"
  
  # Create a PDF viewer with custom scroll speed
  python kiosk_manager.py pdf "Training Doc" "file:///home/user/doc.pdf" --scroll-speed 30
  
  # List all generated HTML files
  python kiosk_manager.py list
  
  # Show current config
  python kiosk_manager.py config
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Smartsheet command
    smartsheet_parser = subparsers.add_parser(
        'smartsheet',
        help='Create a Smartsheet HTML page'
    )
    smartsheet_parser.add_argument('title', help='Page title (e.g., "Weekly Scoreboard")')
    smartsheet_parser.add_argument('url', help='Smartsheet published/embed URL')
    smartsheet_parser.add_argument('-o', '--output', help='Custom output filename (without .html)')
    smartsheet_parser.add_argument('-a', '--add-to-config', action='store_true',
                                   help='Add the generated file to config.json')
    
    # PDF command
    pdf_parser = subparsers.add_parser(
        'pdf',
        help='Create a PDF viewer HTML page'
    )
    pdf_parser.add_argument('title', help='Page title (e.g., "Safety Manual")')
    pdf_parser.add_argument('pdf', help='Path to PDF file (local path or URL)')
    pdf_parser.add_argument('-o', '--output', help='Custom output filename (without .html)')
    pdf_parser.add_argument('-s', '--scroll-speed', type=int, default=50,
                          help='Auto-scroll speed in pixels/second (default: 50)')
    pdf_parser.add_argument('-a', '--add-to-config', action='store_true',
                          help='Add the generated file to config.json')
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List all generated HTML files'
    )
    
    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Show current config.json'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command
    if args.command == 'smartsheet':
        create_smartsheet(args)
    elif args.command == 'pdf':
        create_pdf(args)
    elif args.command == 'list':
        list_files(args)
    elif args.command == 'config':
        show_config(args)


if __name__ == "__main__":
    main()
