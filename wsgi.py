"""
WSGI entry point for YouTube2MP3 application
This file is used by Apache mod_wsgi, Gunicorn, and other WSGI servers
"""
import sys
import os
from pathlib import Path

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_path = project_dir / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Import the Flask application
from app import app, socketio

# For standard WSGI servers (Apache mod_wsgi, Gunicorn without SocketIO)
application = app

# For SocketIO-enabled servers (Gunicorn with eventlet/gevent)
# Use: gunicorn --worker-class eventlet -w 1 wsgi:application
