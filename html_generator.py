#!/usr/bin/env python3
"""
HTML Generator for Kiosk Display Pages
Generates HTML files for Smartsheet embeds and PDF viewers
"""

import os
import json
from pathlib import Path

# Default paths
HTML_OUTPUT_DIR = Path('/home/annkiosk/announcements_kiosk/html')
CONFIG_FILE = Path('/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json')

# For development/testing in codespace
if not CONFIG_FILE.exists():
    HTML_OUTPUT_DIR = Path('./html')
    CONFIG_FILE = Path('./config.json')


def generate_smartsheet_html(title, smartsheet_url, output_filename=None):
    """
    Generate an HTML file for embedding a Smartsheet.
    
    Args:
        title (str): The title to display in the header
        smartsheet_url (str): The Smartsheet published/embed URL
        output_filename (str): Optional custom filename (without .html extension)
        
    Returns:
        Path: Path to the generated HTML file
    """
    if output_filename is None:
        # Generate filename from title
        output_filename = title.lower().replace(' ', '_').replace('-', '_')
    
    # Ensure .html extension
    if not output_filename.endswith('.html'):
        output_filename += '.html'
    
    # Create unique localStorage key from filename
    storage_key = output_filename.replace('.html', '_url').replace('/', '_')
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}

        .header {{
            background-color: #41a3db;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 32px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .config-section {{
            padding: 15px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .config-section.hidden {{
            display: none;
        }}

        .config-section label {{
            display: inline-block;
            margin-right: 10px;
            font-weight: bold;
        }}

        .config-section input {{
            width: 70%;
            max-width: 600px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-right: 10px;
        }}

        .config-section button {{
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}

        .config-section button:hover {{
            background-color: #0056b3;
        }}

        .iframe-container {{
            flex: 1;
            width: 100%;
            overflow: hidden;
            background-color: white;
            position: relative;
        }}

        .iframe-container iframe {{
            width: 100%;
            height: 100%;
            border: none;
            transform-origin: center center;
        }}

        #message {{
            display: none;
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 18px;
        }}

        .toggle-config {{
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            background-color: rgba(0, 123, 255, 0.8);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            z-index: 1000;
        }}

        .toggle-config:hover {{
            background-color: rgba(0, 86, 179, 0.9);
        }}
    </style>
</head>
<body>
    <div class="header">{title.upper()}</div>
    
    <div class="config-section hidden" id="configSection">
        <label for="iframeUrl">Smartsheet Embed URL:</label>
        <input type="text" id="iframeUrl" placeholder="Paste your Smartsheet published URL here">
        <button onclick="loadIframe()">Load Sheet</button>
    </div>

    <div id="message">Please enter a Smartsheet published URL and click "Load Sheet"</div>

    <div class="iframe-container" id="iframeContainer" style="display: none;">
        <button class="toggle-config" onclick="toggleConfig()">⚙️ Settings</button>
        <iframe id="smartsheetFrame" allowfullscreen scrolling="no"></iframe>
    </div>

    <script>
        const STORAGE_KEY = '{storage_key}';
        const DEFAULT_URL = '{smartsheet_url}';

        // Load URL from localStorage or use default
        window.addEventListener('DOMContentLoaded', () => {{
            const savedUrl = localStorage.getItem(STORAGE_KEY) || DEFAULT_URL;
            
            if (savedUrl) {{
                document.getElementById('iframeUrl').value = savedUrl;
                loadIframe();
            }} else {{
                document.getElementById('message').style.display = 'block';
            }}
        }});

        function loadIframe() {{
            const url = document.getElementById('iframeUrl').value.trim();
            
            if (!url) {{
                alert('Please enter a Smartsheet published URL');
                document.getElementById('message').style.display = 'block';
                document.getElementById('iframeContainer').style.display = 'none';
                return;
            }}

            // Validate URL format
            if (!url.startsWith('http://') && !url.startsWith('https://')) {{
                alert('Please enter a valid URL starting with http:// or https://');
                return;
            }}

            // Save URL
            localStorage.setItem(STORAGE_KEY, url);

            // Load iframe
            document.getElementById('smartsheetFrame').src = url;
            document.getElementById('message').style.display = 'none';
            document.getElementById('iframeContainer').style.display = 'block';
            
            // Hide config section after loading
            document.getElementById('configSection').classList.add('hidden');
        }}

        function toggleConfig() {{
            const configSection = document.getElementById('configSection');
            configSection.classList.toggle('hidden');
        }}
    </script>
</body>
</html>'''
    
    # Create output directory if it doesn't exist
    HTML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write the file
    output_path = HTML_OUTPUT_DIR / output_filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Generated Smartsheet HTML: {output_path}")
    return output_path


def generate_pdf_html(title, pdf_path, output_filename=None, scroll_speed=50):
    """
    Generate an HTML file for displaying a PDF with dual-page view and auto-scroll.
    
    Args:
        title (str): The title to display in the header
        pdf_path (str): Path to the PDF file (can be local file:// or URL)
        output_filename (str): Optional custom filename (without .html extension)
        scroll_speed (int): Pixels per second to scroll (default: 50)
        
    Returns:
        Path: Path to the generated HTML file
    """
    if output_filename is None:
        # Generate filename from title
        output_filename = title.lower().replace(' ', '_').replace('-', '_') + '_pdf'
    
    # Ensure .html extension
    if not output_filename.endswith('.html'):
        output_filename += '.html'
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background-color: #525659;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}

        .header {{
            background-color: #41a3db;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 32px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .pdf-container {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 20px;
            scroll-behavior: smooth;
        }}

        .pages-wrapper {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            max-width: 1800px;
        }}

        .page-pair {{
            display: flex;
            gap: 20px;
            justify-content: center;
        }}

        .page-canvas {{
            background: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}

        .controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.7);
            padding: 15px;
            border-radius: 8px;
            color: white;
            z-index: 1000;
        }}

        .controls button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 4px;
            cursor: pointer;
        }}

        .controls button:hover {{
            background: #0056b3;
        }}

        #loading {{
            text-align: center;
            color: white;
            padding: 40px;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="header">{title.upper()}</div>
    
    <div id="loading">Loading PDF...</div>
    
    <div class="pdf-container" id="pdfContainer" style="display: none;">
        <div class="pages-wrapper" id="pagesWrapper"></div>
    </div>

    <div class="controls">
        <div>
            <button onclick="toggleAutoScroll()">⏯ Toggle Scroll</button>
            <button onclick="resetScroll()">⏮ Reset</button>
        </div>
        <div style="margin-top: 10px; font-size: 12px;">
            <span id="pageInfo">Page 1-2 of ?</span>
        </div>
    </div>

    <script>
        const PDF_URL = '{pdf_path}';
        const SCROLL_SPEED = {scroll_speed}; // pixels per second
        
        let pdfDoc = null;
        let totalPages = 0;
        let isAutoScrolling = false;
        let scrollInterval = null;
        
        // Set up PDF.js worker
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

        async function loadPDF() {{
            try {{
                pdfDoc = await pdfjsLib.getDocument(PDF_URL).promise;
                totalPages = pdfDoc.numPages;
                
                console.log(`PDF loaded: ${{totalPages}} pages`);
                
                await renderAllPages();
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('pdfContainer').style.display = 'flex';
                
                // Start auto-scrolling after a short delay
                setTimeout(() => {{
                    startAutoScroll();
                }}, 2000);
                
            }} catch (error) {{
                console.error('Error loading PDF:', error);
                document.getElementById('loading').textContent = 'Error loading PDF: ' + error.message;
            }}
        }}

        async function renderAllPages() {{
            const wrapper = document.getElementById('pagesWrapper');
            
            // Render pages in pairs
            for (let pageNum = 1; pageNum <= totalPages; pageNum += 2) {{
                const pairDiv = document.createElement('div');
                pairDiv.className = 'page-pair';
                
                // Render left page
                const canvas1 = await renderPage(pageNum);
                pairDiv.appendChild(canvas1);
                
                // Render right page if it exists
                if (pageNum + 1 <= totalPages) {{
                    const canvas2 = await renderPage(pageNum + 1);
                    pairDiv.appendChild(canvas2);
                }}
                
                wrapper.appendChild(pairDiv);
            }}
            
            updatePageInfo();
        }}

        async function renderPage(pageNum) {{
            const page = await pdfDoc.getPage(pageNum);
            const viewport = page.getViewport({{ scale: 1.5 }});
            
            const canvas = document.createElement('canvas');
            canvas.className = 'page-canvas';
            const context = canvas.getContext('2d');
            
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            
            await page.render({{
                canvasContext: context,
                viewport: viewport
            }}).promise;
            
            return canvas;
        }}

        function startAutoScroll() {{
            if (isAutoScrolling) return;
            
            isAutoScrolling = true;
            const container = document.getElementById('pdfContainer');
            
            scrollInterval = setInterval(() => {{
                if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {{
                    // Reached the bottom, reset to top
                    container.scrollTop = 0;
                }} else {{
                    container.scrollTop += SCROLL_SPEED / 60; // 60 FPS
                }}
                updatePageInfo();
            }}, 1000 / 60); // 60 FPS
        }}

        function stopAutoScroll() {{
            isAutoScrolling = false;
            if (scrollInterval) {{
                clearInterval(scrollInterval);
                scrollInterval = null;
            }}
        }}

        function toggleAutoScroll() {{
            if (isAutoScrolling) {{
                stopAutoScroll();
            }} else {{
                startAutoScroll();
            }}
        }}

        function resetScroll() {{
            const container = document.getElementById('pdfContainer');
            container.scrollTop = 0;
            updatePageInfo();
        }}

        function updatePageInfo() {{
            const container = document.getElementById('pdfContainer');
            const scrollPercent = container.scrollTop / (container.scrollHeight - container.clientHeight);
            const estimatedPage = Math.floor(scrollPercent * totalPages) + 1;
            const nextPage = Math.min(estimatedPage + 1, totalPages);
            
            document.getElementById('pageInfo').textContent = 
                `Page ${{estimatedPage}}-${{nextPage}} of ${{totalPages}}`;
        }}

        // Load PDF on page load
        window.addEventListener('DOMContentLoaded', loadPDF);
        
        // Pause scrolling when user manually scrolls
        document.getElementById('pdfContainer').addEventListener('wheel', () => {{
            if (isAutoScrolling) {{
                stopAutoScroll();
            }}
        }});
    </script>
</body>
</html>'''
    
    # Create output directory if it doesn't exist
    HTML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write the file
    output_path = HTML_OUTPUT_DIR / output_filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Generated PDF HTML: {output_path}")
    return output_path


def add_to_config(file_path, position=None):
    """
    Add a generated HTML file to the config.json URLs list.
    
    Args:
        file_path (Path or str): Path to the HTML file
        position (int): Optional position to insert at (default: append to end)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert to file:// URL
        file_url = f"file://{file_path}"
        
        # Load config
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Add URL
        if 'urls' not in config:
            config['urls'] = []
        
        if position is not None:
            config['urls'].insert(position, file_url)
        else:
            config['urls'].append(file_url)
        
        # Save config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Added to config: {file_url}")
        return True
        
    except Exception as e:
        print(f"✗ Error adding to config: {e}")
        return False


if __name__ == "__main__":
    print("HTML Generator Module")
    print("Import this module to use generate_smartsheet_html() and generate_pdf_html()")
