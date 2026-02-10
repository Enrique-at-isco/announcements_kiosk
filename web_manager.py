#!/usr/bin/env python3
"""
Kiosk Web Manager - Flask Web Application
Provides a web interface for managing the kiosk display system
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from html_generator import (
    generate_smartsheet_html,
    generate_pdf_html,
    HTML_OUTPUT_DIR,
    CONFIG_FILE
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kiosk-manager-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# PDF upload directory
PDF_UPLOAD_DIR = Path('/home/annkiosk/pdfs')
if not PDF_UPLOAD_DIR.exists():
    PDF_UPLOAD_DIR = Path('./pdfs')  # Fallback for development

# Ensure directories exist
HTML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_config():
    """Load the current configuration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"urls": [], "cycle_delay": 40, "error": str(e)}


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True, "Configuration saved successfully"
    except Exception as e:
        return False, f"Error saving config: {e}"


def get_service_status():
    """Get kiosk service status"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'kiosk.service'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return "unknown"


def restart_service():
    """Restart the kiosk service"""
    try:
        subprocess.run(
            ['sudo', 'systemctl', 'restart', 'kiosk.service'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return True, "Service restarted successfully"
    except Exception as e:
        return False, f"Error restarting service: {e}"


def get_recent_logs(lines=50):
    """Get recent log entries from the kiosk service"""
    try:
        result = subprocess.run(
            ['journalctl', '-u', 'kiosk.service', '-n', str(lines), '--no-pager'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    except Exception as e:
        return f"Error fetching logs: {e}"


# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/config')
def api_config():
    """Get current configuration"""
    config = load_config()
    config['service_status'] = get_service_status()
    return jsonify(config)


@app.route('/api/config/update', methods=['POST'])
def api_config_update():
    """Update configuration"""
    try:
        new_config = request.json
        success, message = save_config(new_config)
        return jsonify({"success": success, "message": message})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/urls/add', methods=['POST'])
def api_url_add():
    """Add a new URL to the config"""
    try:
        data = request.json
        url = data.get('url')
        position = data.get('position')  # Optional
        
        if not url:
            return jsonify({"success": False, "message": "URL is required"}), 400
        
        config = load_config()
        
        if position is not None and 0 <= position <= len(config['urls']):
            config['urls'].insert(position, url)
        else:
            config['urls'].append(url)
        
        success, message = save_config(config)
        return jsonify({"success": success, "message": message, "config": config})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/urls/remove', methods=['POST'])
def api_url_remove():
    """Remove a URL from the config"""
    try:
        data = request.json
        index = data.get('index')
        
        if index is None:
            return jsonify({"success": False, "message": "Index is required"}), 400
        
        config = load_config()
        
        if 0 <= index < len(config['urls']):
            removed_url = config['urls'].pop(index)
            success, message = save_config(config)
            return jsonify({
                "success": success,
                "message": f"Removed: {removed_url}",
                "config": config
            })
        else:
            return jsonify({"success": False, "message": "Invalid index"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/urls/reorder', methods=['POST'])
def api_url_reorder():
    """Reorder URLs in the config"""
    try:
        data = request.json
        new_order = data.get('urls')
        
        if not new_order or not isinstance(new_order, list):
            return jsonify({"success": False, "message": "Invalid URL list"}), 400
        
        config = load_config()
        config['urls'] = new_order
        
        success, message = save_config(config)
        return jsonify({"success": success, "message": message, "config": config})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/smartsheet/create', methods=['POST'])
def api_smartsheet_create():
    """Create a new Smartsheet HTML page"""
    try:
        data = request.json
        title = data.get('title')
        url = data.get('url')
        add_to_config = data.get('add_to_config', False)
        
        if not title or not url:
            return jsonify({"success": False, "message": "Title and URL are required"}), 400
        
        # Generate HTML file
        output_path = generate_smartsheet_html(title, url)
        file_url = f"file://{output_path}"
        
        # Add to config if requested
        if add_to_config:
            config = load_config()
            config['urls'].append(file_url)
            save_config(config)
        
        return jsonify({
            "success": True,
            "message": f"Created {output_path.name}",
            "file_path": str(output_path),
            "file_url": file_url,
            "added_to_config": add_to_config
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/pdf/create', methods=['POST'])
def api_pdf_create():
    """Create a new PDF viewer HTML page"""
    try:
        data = request.json
        title = data.get('title')
        pdf_path = data.get('pdf_path')
        scroll_speed = data.get('scroll_speed', 50)
        add_to_config = data.get('add_to_config', False)
        
        if not title or not pdf_path:
            return jsonify({"success": False, "message": "Title and PDF path are required"}), 400
        
        # Generate HTML file
        output_path = generate_pdf_html(title, pdf_path, scroll_speed=scroll_speed)
        file_url = f"file://{output_path}"
        
        # Add to config if requested
        if add_to_config:
            config = load_config()
            config['urls'].append(file_url)
            save_config(config)
        
        return jsonify({
            "success": True,
            "message": f"Created {output_path.name}",
            "file_path": str(output_path),
            "file_url": file_url,
            "added_to_config": add_to_config
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/service/status')
def api_service_status():
    """Get kiosk service status"""
    status = get_service_status()
    return jsonify({"status": status})


@app.route('/api/service/restart', methods=['POST'])
def api_service_restart():
    """Restart the kiosk service"""
    success, message = restart_service()
    return jsonify({"success": success, "message": message})


@app.route('/api/logs')
def api_logs():
    """Get recent logs"""
    lines = request.args.get('lines', 50, type=int)
    logs = get_recent_logs(lines)
    return jsonify({"logs": logs})


@app.route('/api/html-files')
def api_html_files():
    """List all HTML files in the html directory"""
    try:
        files = []
        if HTML_OUTPUT_DIR.exists():
            for file in sorted(HTML_OUTPUT_DIR.glob('*.html')):
                files.append({
                    "name": file.name,
                    "path": str(file),
                    "url": f"file://{file}",
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"files": [], "error": str(e)})


@app.route('/api/pdf/upload', methods=['POST'])
def api_pdf_upload():
    """Upload a PDF file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": "Only PDF files are allowed"}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Save the file
        file_path = PDF_UPLOAD_DIR / filename
        file.save(str(file_path))
        
        # Get file info
        file_size = file_path.stat().st_size
        file_url = f"file://{file_path}"
        
        return jsonify({
            "success": True,
            "message": f"Uploaded {filename} successfully",
            "filename": filename,
            "path": str(file_path),
            "url": file_url,
            "size": file_size
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/pdf/list')
def api_pdf_list():
    """List all uploaded PDF files"""
    try:
        files = []
        if PDF_UPLOAD_DIR.exists():
            for file in sorted(PDF_UPLOAD_DIR.glob('*.pdf')):
                files.append({
                    "name": file.name,
                    "path": str(file),
                    "url": f"file://{file}",
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"files": [], "error": str(e)})


if __name__ == '__main__':
    # Run on all network interfaces so it's accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=True)
