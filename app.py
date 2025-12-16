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
import zipfile
import tempfile

# Load .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Import the existing download functionality
from descargar_audio import descargar_audio_mp3, leer_urls_csv, setup_logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'youtube2mp3-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload
CORS(app)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False
)

# Global state to track downloads
downloads = {}
downloads_lock = threading.Lock()

# Track batch operations
batches = {}
batches_lock = threading.Lock()

# Configure download directory
DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', os.path.join(os.getcwd(), 'downloads'))
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Configure FFmpeg location
def find_ffmpeg():
    """Find FFmpeg location from environment or local installation"""
    import shutil
    
    # Check environment variable first
    if os.environ.get('FFMPEG_LOCATION'):
        return os.environ.get('FFMPEG_LOCATION')
    
    # Check local ffmpeg/bin directory first (portable, relative to project)
    local_ffmpeg = Path(__file__).parent / 'ffmpeg' / 'bin'
    if (local_ffmpeg / 'ffmpeg.exe').exists() and (local_ffmpeg / 'ffprobe.exe').exists():
        return str(local_ffmpeg.resolve())  # Return absolute path for yt-dlp
    
    # Fallback to system PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        # Return the directory containing ffmpeg
        return str(Path(ffmpeg_path).parent)
    
    return None

FFMPEG_LOCATION = find_ffmpeg()
print(f"[DEBUG] FFMPEG_LOCATION set to: {FFMPEG_LOCATION}")

class WebProgressHook:
    """Custom progress hook for web interface with SocketIO updates"""
    
    def __init__(self, download_id, socketio_instance):
        self.download_id = download_id
        self.socketio = socketio_instance
        self.last_update = datetime.now()
        self.final_filename = None
        
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
            self.final_filename = d.get('filename')
            
        # Emit progress update via WebSocket
        self.socketio.emit('download_progress', status_data, namespace='/')

def check_batch_completion(batch_id):
    """Check if all downloads in a batch are complete and create ZIP if so"""
    with batches_lock:
        if batch_id not in batches:
            return
        
        batch = batches[batch_id]
        download_ids = batch['download_ids']
    
    # Check status of all downloads in batch
    with downloads_lock:
        all_downloads = [downloads.get(did) for did in download_ids if did in downloads]
        completed = [d for d in all_downloads if d and d['status'] == 'completed']
        failed = [d for d in all_downloads if d and d['status'] == 'failed']
        in_progress = [d for d in all_downloads if d and d['status'] in ('pending', 'downloading')]
    
    # If there are still downloads in progress, don't create ZIP yet
    if in_progress:
        print(f"[DEBUG] Batch {batch_id}: {len(in_progress)} downloads still in progress")
        return
    
    # All downloads are done (completed or failed)
    if not completed:
        print(f"[DEBUG] Batch {batch_id}: No successful downloads to zip")
        with batches_lock:
            batches[batch_id]['status'] = 'failed'
        return
    
    # Create ZIP file with all completed downloads
    print(f"[DEBUG] Batch {batch_id}: All downloads complete, creating ZIP...")
    
    try:
        zip_filename = f'youtube2mp3_batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        zip_path = os.path.join(DOWNLOAD_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for download in completed:
                filepath = download.get('filepath')
                filename = download.get('filename')
                
                if filepath and os.path.exists(filepath):
                    print(f"[DEBUG] Adding to batch ZIP: {filename}")
                    zipf.write(filepath, arcname=filename)
        
        # Update batch status
        with batches_lock:
            batches[batch_id]['status'] = 'completed'
            batches[batch_id]['zip_filename'] = zip_filename
            batches[batch_id]['zip_path'] = zip_path
            batches[batch_id]['completed_at'] = datetime.now().isoformat()
            batches[batch_id]['total_files'] = len(completed)
        
        print(f"[DEBUG] Batch {batch_id}: ZIP created successfully - {zip_filename}")
        
        # Notify via WebSocket
        socketio.emit('batch_complete', {
            'batch_id': batch_id,
            'zip_filename': zip_filename,
            'total_files': len(completed),
            'failed_files': len(failed)
        }, namespace='/')
        
    except Exception as e:
        print(f"[ERROR] Failed to create batch ZIP: {e}")
        import traceback
        traceback.print_exc()
        
        with batches_lock:
            batches[batch_id]['status'] = 'failed'
            batches[batch_id]['error'] = str(e)

def download_task(download_id, url, output_dir):
    """Background task for downloading audio"""
    print(f"[DEBUG] Starting download task for {download_id}: {url}")
    print(f"[DEBUG] Output directory: {output_dir}")
    
    with downloads_lock:
        downloads[download_id]['status'] = 'downloading'
        downloads[download_id]['started_at'] = datetime.now().isoformat()
    
    try:
        # Create custom yt-dlp options with web progress hook
        import yt_dlp
        print(f"[DEBUG] yt-dlp imported successfully")
        
        progress_hook = WebProgressHook(download_id, socketio)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'quiet': True,
            'socket_timeout': 30,  # 30 seconds socket timeout
            'retries': 3,  # Retry 3 times on failure
            'fragment_retries': 3,  # Retry fragments
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            'no_warnings': True,  # Suppress yt-dlp warnings
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        if FFMPEG_LOCATION:
            ydl_opts['ffmpeg_location'] = FFMPEG_LOCATION
            print(f"[DEBUG] Using ffmpeg location: {FFMPEG_LOCATION}")
        else:
            print(f"[WARNING] FFMPEG_LOCATION is None - ffmpeg may not be found!")
        
        print(f"[DEBUG] Creating YoutubeDL with options: {ydl_opts}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[DEBUG] Extracting info for: {url}")
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'audio')
            print(f"[DEBUG] Video title: {title}")
            
            with downloads_lock:
                downloads[download_id]['title'] = title
            
            # Perform download
            print(f"[DEBUG] Starting download...")
            ydl.download([url])
            print(f"[DEBUG] Download completed")
            
            # Get the actual downloaded file from progress hook
            filepath = None
            filename = None
            
            if progress_hook.final_filename:
                # The progress hook captured the final filename (before post-processing)
                # But post-processing changes the extension to .mp3
                base_path = os.path.splitext(progress_hook.final_filename)[0]
                filepath = f"{base_path}.mp3"
                filename = os.path.basename(filepath)
                print(f"[DEBUG] Filepath from progress hook: {filepath}")
            else:
                # Fallback: search for the most recently created .mp3 file
                print(f"[DEBUG] Progress hook didn't capture filename, searching directory...")
                import glob
                mp3_files = glob.glob(os.path.join(output_dir, "*.mp3"))
                if mp3_files:
                    filepath = max(mp3_files, key=os.path.getctime)
                    filename = os.path.basename(filepath)
                    print(f"[DEBUG] Found most recent file: {filepath}")
            
            print(f"[DEBUG] Final filepath: {filepath}")
            print(f"[DEBUG] File exists: {os.path.exists(filepath) if filepath else False}")
            
            if not filepath or not os.path.exists(filepath):
                raise FileNotFoundError(f"Downloaded file not found. Expected: {filepath}")
            
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
            
            # Check if this download is part of a batch
            batch_id = downloads[download_id].get('batch_id')
            if batch_id:
                # Check if all downloads in batch are complete
                check_batch_completion(batch_id)
            
    except Exception as e:
        print(f"[ERROR] Download failed for {download_id}: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        with downloads_lock:
            downloads[download_id]['status'] = 'failed'
            downloads[download_id]['error'] = str(e)
            downloads[download_id]['failed_at'] = datetime.now().isoformat()
        
        socketio.emit('download_error', {
            'download_id': download_id,
            'error': str(e)
        }, namespace='/')
        
        # Check if this download is part of a batch
        batch_id = downloads[download_id].get('batch_id')
        if batch_id:
            # Check if all downloads in batch are complete (or failed)
            check_batch_completion(batch_id)

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
    
    # Create a batch to track this group of downloads
    batch_id = str(uuid.uuid4())
    
    with batches_lock:
        batches[batch_id] = {
            'id': batch_id,
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'total_urls': len(urls),
            'download_ids': []
        }
    
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
                'batch_id': batch_id,  # Associate with batch
                'created_at': datetime.now().isoformat()
            }
        
        thread = threading.Thread(target=download_task, args=(download_id, url, output_dir))
        thread.daemon = True
        thread.start()
        
        download_ids.append(download_id)
    
    # Update batch with download IDs
    with batches_lock:
        batches[batch_id]['download_ids'] = download_ids
    
    return jsonify({
        'success': True,
        'batch_id': batch_id,
        'download_ids': download_ids,
        'count': len(download_ids),
        'message': f'Started {len(download_ids)} downloads'
    }), 202

@app.route('/api/downloads', methods=['GET'])
def api_downloads():
    """Get list of all downloads"""
    with downloads_lock:
        downloads_list = list(downloads.values())
    
    with batches_lock:
        batches_list = list(batches.values())
    
    return jsonify({
        'downloads': downloads_list,
        'batches': batches_list
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
    print(f"[DEBUG] File download requested for: {download_id}")
    
    with downloads_lock:
        if download_id not in downloads:
            print(f"[DEBUG] Download ID not found: {download_id}")
            return jsonify({'error': 'Download not found'}), 404
        
        download = downloads[download_id]
        print(f"[DEBUG] Download status: {download['status']}")
        
        if download['status'] != 'completed':
            return jsonify({'error': 'Download not completed yet'}), 400
        
        filepath = download.get('filepath')
        filename = download.get('filename')
        
        print(f"[DEBUG] Filepath: {filepath}")
        print(f"[DEBUG] Filename: {filename}")
        print(f"[DEBUG] File exists: {os.path.exists(filepath) if filepath else False}")
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'File not found', 'filepath': filepath}), 404
    
    try:
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='audio/mpeg')
    except Exception as e:
        print(f"[ERROR] Failed to send file: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to send file: {str(e)}'}), 500

@app.route('/api/batch/<batch_id>/zip', methods=['GET'])
def api_batch_zip(batch_id):
    """Download the ZIP file for a completed batch"""
    print(f"[DEBUG] Batch ZIP download requested for: {batch_id}")
    
    with batches_lock:
        if batch_id not in batches:
            return jsonify({'error': 'Batch not found'}), 404
        
        batch = batches[batch_id]
        
        if batch['status'] != 'completed':
            return jsonify({'error': f"Batch not completed yet (status: {batch['status']})"}), 400
        
        zip_path = batch.get('zip_path')
        zip_filename = batch.get('zip_filename')
        
        if not zip_path or not os.path.exists(zip_path):
            return jsonify({'error': 'ZIP file not found'}), 404
    
    try:
        return send_file(zip_path, as_attachment=True, download_name=zip_filename, mimetype='application/zip')
    except Exception as e:
        print(f"[ERROR] Failed to send batch ZIP: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to send ZIP file: {str(e)}'}), 500

@app.route('/api/batch-download/zip', methods=['GET'])
def api_batch_download_zip():
    """Download all completed files as a ZIP archive"""
    print(f"[DEBUG] ZIP download requested")
    
    # Get all completed downloads (release lock immediately)
    with downloads_lock:
        completed = [d.copy() for d in downloads.values() if d['status'] == 'completed' and 'filepath' in d]
    
    if not completed:
        print(f"[DEBUG] No completed downloads found")
        return jsonify({'error': 'No completed downloads available'}), 404
    
    print(f"[DEBUG] Found {len(completed)} completed downloads")
    
    # Create a temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip_path = temp_zip.name
    temp_zip.close()
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for download in completed:
                filepath = download.get('filepath')
                filename = download.get('filename')
                
                if filepath and os.path.exists(filepath):
                    print(f"[DEBUG] Adding to zip: {filename}")
                    zipf.write(filepath, arcname=filename)
                else:
                    print(f"[WARNING] File not found: {filepath}")
        
        # Send the ZIP file
        zip_filename = f'youtube2mp3_batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        print(f"[DEBUG] Sending ZIP file: {zip_filename}")
        
        def cleanup_temp_file():
            """Clean up temporary file after sending"""
            try:
                os.unlink(temp_zip_path)
                print(f"[DEBUG] Cleaned up temp zip: {temp_zip_path}")
            except Exception as e:
                print(f"[WARNING] Failed to cleanup temp zip: {e}")
        
        response = send_file(
            temp_zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
        
        # Schedule cleanup after response is sent
        response.call_on_close(cleanup_temp_file)
        
        return response
        
    except Exception as e:
        print(f"[ERROR] Failed to create ZIP: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        try:
            os.unlink(temp_zip_path)
        except:
            pass
        
        return jsonify({'error': f'Failed to create ZIP: {str(e)}'}), 500

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
    print(f"[DEBUG] Client connected")
    emit('connected', {'message': 'Connected to YouTube2MP3 server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"[DEBUG] Client disconnected")

@socketio.on('ping')
def handle_ping():
    """Handle ping from client"""
    emit('pong')

if __name__ == '__main__':
    print("=" * 60)
    print("YouTube2MP3 Web Server")
    print("=" * 60)
    print(f"Download directory: {DOWNLOAD_DIR}")
    
    if FFMPEG_LOCATION:
        print(f"FFmpeg location: {FFMPEG_LOCATION}")
    else:
        print("⚠️  WARNING: FFmpeg not found!")
        print("   Please run: python setup_ffmpeg.py")
        print("   Or install FFmpeg and add to PATH")
    
    print(f"Starting server on http://localhost:5000")
    print("=" * 60)
    
    # Run the Flask-SocketIO server
    # In production/Docker, allow_unsafe_werkzeug=True is needed
    # For production deployment, consider using gunicorn with eventlet worker
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False,  # Disable debug in production
        use_reloader=False, 
        log_output=True,
        allow_unsafe_werkzeug=True  # Required for Flask-SocketIO with newer Werkzeug
    )
