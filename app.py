from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import sys
import threading
from pathlib import Path
import json
from datetime import datetime
import uuid

# Import the existing download functionality
from descargar_audio import descargar_audio_mp3, leer_urls_csv, setup_logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'youtube2mp3-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state to track downloads
downloads = {}
downloads_lock = threading.Lock()

# Configure download directory
DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', os.path.join(os.getcwd(), 'downloads'))
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

class WebProgressHook:
    """Custom progress hook for web interface with SocketIO updates"""
    
    def __init__(self, download_id, socketio_instance):
        self.download_id = download_id
        self.socketio = socketio_instance
        self.last_update = datetime.now()
        
    def __call__(self, d):
        """Hook function called by yt-dlp"""
        now = datetime.now()
        # Throttle updates to every 500ms
        if (now - self.last_update).total_seconds() < 0.5 and d['status'] != 'finished':
            return
            
        self.last_update = now
        
        status_data = {
            'download_id': self.download_id,
            'status': d['status']
        }
        
        if d['status'] == 'downloading':
            status_data.update({
                'percent': d.get('_percent_str', 'N/A'),
                'speed': d.get('_speed_str', 'N/A'),
                'eta': d.get('_eta_str', 'N/A')
            })
        elif d['status'] == 'finished':
            status_data['filename'] = d.get('filename', 'audio.mp3')
            
        # Emit progress update via WebSocket
        self.socketio.emit('download_progress', status_data, namespace='/')

def download_task(download_id, url, output_dir):
    """Background task for downloading audio"""
    with downloads_lock:
        downloads[download_id]['status'] = 'downloading'
        downloads[download_id]['started_at'] = datetime.now().isoformat()
    
    try:
        # Create custom yt-dlp options with web progress hook
        import yt_dlp
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [WebProgressHook(download_id, socketio)],
            'noplaylist': True,
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'audio')
            
            with downloads_lock:
                downloads[download_id]['title'] = title
            
            # Perform download
            ydl.download([url])
            
            # Find the downloaded file
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}.mp3"
            filepath = os.path.join(output_dir, filename)
            
            with downloads_lock:
                downloads[download_id]['status'] = 'completed'
                downloads[download_id]['filename'] = filename
                downloads[download_id]['filepath'] = filepath
                downloads[download_id]['completed_at'] = datetime.now().isoformat()
            
            # Notify completion
            socketio.emit('download_complete', {
                'download_id': download_id,
                'title': title,
                'filename': filename
            }, namespace='/')
            
    except Exception as e:
        with downloads_lock:
            downloads[download_id]['status'] = 'failed'
            downloads[download_id]['error'] = str(e)
            downloads[download_id]['failed_at'] = datetime.now().isoformat()
        
        socketio.emit('download_error', {
            'download_id': download_id,
            'error': str(e)
        }, namespace='/')

@app.route('/')
def index():
    """Render the main web interface"""
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def api_download():
    """API endpoint to start a download"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url'].strip()
    
    # Basic URL validation
    if not (url.startswith('http://') or url.startswith('https://')):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Generate unique download ID
    download_id = str(uuid.uuid4())
    
    # Initialize download tracking
    with downloads_lock:
        downloads[download_id] = {
            'id': download_id,
            'url': url,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
    
    # Start download in background thread
    output_dir = data.get('output_dir', DOWNLOAD_DIR)
    thread = threading.Thread(target=download_task, args=(download_id, url, output_dir))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'download_id': download_id,
        'message': 'Download started'
    }), 202

@app.route('/api/batch-download', methods=['POST'])
def api_batch_download():
    """API endpoint to start batch downloads from CSV or URL list"""
    
    # Check if CSV file was uploaded
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save temporary CSV file
        temp_csv = os.path.join(DOWNLOAD_DIR, f'temp_{uuid.uuid4()}.csv')
        file.save(temp_csv)
        
        # Read URLs from CSV
        urls = leer_urls_csv(temp_csv)
        
        # Clean up temp file
        try:
            os.remove(temp_csv)
        except:
            pass
    
    # Or get URLs from JSON array
    elif request.is_json:
        data = request.get_json()
        urls = data.get('urls', [])
    else:
        return jsonify({'error': 'No URLs or file provided'}), 400
    
    if not urls:
        return jsonify({'error': 'No valid URLs found'}), 400
    
    # Start downloads for each URL
    download_ids = []
    output_dir = request.form.get('output_dir', DOWNLOAD_DIR) if not request.is_json else data.get('output_dir', DOWNLOAD_DIR)
    
    for url in urls:
        download_id = str(uuid.uuid4())
        
        with downloads_lock:
            downloads[download_id] = {
                'id': download_id,
                'url': url,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
        
        thread = threading.Thread(target=download_task, args=(download_id, url, output_dir))
        thread.daemon = True
        thread.start()
        
        download_ids.append(download_id)
    
    return jsonify({
        'success': True,
        'download_ids': download_ids,
        'count': len(download_ids),
        'message': f'Started {len(download_ids)} downloads'
    }), 202

@app.route('/api/downloads', methods=['GET'])
def api_downloads():
    """Get list of all downloads"""
    with downloads_lock:
        return jsonify({
            'downloads': list(downloads.values())
        })

@app.route('/api/download/<download_id>', methods=['GET'])
def api_download_status(download_id):
    """Get status of a specific download"""
    with downloads_lock:
        if download_id not in downloads:
            return jsonify({'error': 'Download not found'}), 404
        return jsonify(downloads[download_id])

@app.route('/api/download/<download_id>/file', methods=['GET'])
def api_download_file(download_id):
    """Download the MP3 file"""
    with downloads_lock:
        if download_id not in downloads:
            return jsonify({'error': 'Download not found'}), 404
        
        download = downloads[download_id]
        
        if download['status'] != 'completed':
            return jsonify({'error': 'Download not completed yet'}), 400
        
        filepath = download.get('filepath')
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True, download_name=download['filename'])

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'downloads_dir': DOWNLOAD_DIR
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to YouTube2MP3 server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    pass

if __name__ == '__main__':
    print("=" * 60)
    print("YouTube2MP3 Web Server")
    print("=" * 60)
    print(f"Download directory: {DOWNLOAD_DIR}")
    print(f"Starting server on http://localhost:5000")
    print("=" * 60)
    
    # Run the Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
