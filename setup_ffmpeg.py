"""
FFmpeg Setup Script for YouTube2MP3
Downloads and configures FFmpeg for Windows
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path
import shutil

def download_ffmpeg_windows():
    """Download FFmpeg for Windows and extract to project directory"""
    
    project_dir = Path(__file__).parent
    ffmpeg_dir = project_dir / "ffmpeg"
    ffmpeg_bin = ffmpeg_dir / "bin"
    
    # Check if already installed
    if (ffmpeg_bin / "ffmpeg.exe").exists():
        print("✅ FFmpeg already installed!")
        print(f"Location: {ffmpeg_bin}")
        return str(ffmpeg_bin)
    
    print("=" * 60)
    print("FFmpeg Setup for YouTube2MP3")
    print("=" * 60)
    print("\nFFmpeg is required to convert audio to MP3 format.")
    print("This script will download FFmpeg (essentials build) from gyan.dev\n")
    
    # FFmpeg download URL (essentials build - smaller size)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    print(f"Downloading FFmpeg from: {ffmpeg_url}")
    print("This may take a few minutes (size: ~70 MB)...\n")
    
    try:
        # Create ffmpeg directory
        ffmpeg_dir.mkdir(exist_ok=True)
        
        # Download file
        zip_path = ffmpeg_dir / "ffmpeg.zip"
        
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '-' * (bar_length - filled)
            print(f'\r[{bar}] {percent:.1f}%', end='', flush=True)
        
        urllib.request.urlretrieve(ffmpeg_url, zip_path, show_progress)
        print("\n✅ Download complete!")
        
        # Extract zip file
        print("\nExtracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get the top-level directory name in the zip
            zip_contents = zip_ref.namelist()
            top_dir = zip_contents[0].split('/')[0]
            
            # Extract all
            zip_ref.extractall(ffmpeg_dir)
        
        # Move files from extracted directory to ffmpeg/bin
        extracted_dir = ffmpeg_dir / top_dir
        extracted_bin = extracted_dir / "bin"
        
        if extracted_bin.exists():
            # Copy bin directory contents
            if ffmpeg_bin.exists():
                shutil.rmtree(ffmpeg_bin)
            shutil.copytree(extracted_bin, ffmpeg_bin)
            
            # Clean up
            shutil.rmtree(extracted_dir)
        
        # Remove zip file
        zip_path.unlink()
        
        print(f"✅ FFmpeg installed successfully!")
        print(f"Location: {ffmpeg_bin}")
        print("\n" + "=" * 60)
        
        # Verify installation
        ffmpeg_exe = ffmpeg_bin / "ffmpeg.exe"
        if ffmpeg_exe.exists():
            print("✅ Verification: ffmpeg.exe found")
            return str(ffmpeg_bin)
        else:
            print("⚠️ Warning: ffmpeg.exe not found in expected location")
            return None
            
    except Exception as e:
        print(f"\n❌ Error downloading/installing FFmpeg: {e}")
        print("\nManual installation instructions:")
        print("1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/")
        print("2. Extract the zip file")
        print("3. Copy the 'bin' folder contents to: ffmpeg/bin/")
        print("   Or add FFmpeg to your system PATH")
        return None

def create_env_file(ffmpeg_path):
    """Create or update .env file with FFmpeg location"""
    project_dir = Path(__file__).parent
    env_file = project_dir / ".env"
    
    ffmpeg_location = ffmpeg_path.replace("\\", "\\\\")
    
    env_content = f"""# YouTube2MP3 Environment Configuration
# FFmpeg location
FFMPEG_LOCATION={ffmpeg_location}

# Download directory (optional, defaults to ./downloads)
# DOWNLOAD_DIR=C:\\\\path\\\\to\\\\downloads

# Logs directory (optional, defaults to current directory)
# LOGS_DIR=C:\\\\path\\\\to\\\\logs
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Created .env file with FFmpeg configuration")
    print(f"Location: {env_file}")

def main():
    print("\n🎵 YouTube2MP3 - FFmpeg Setup\n")
    
    # Download and install FFmpeg
    ffmpeg_path = download_ffmpeg_windows()
    
    if ffmpeg_path:
        # Create .env file
        create_env_file(ffmpeg_path)
        
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("  python app.py")
        print("\nOr use the CLI:")
        print('  python descargar_audio.py "https://youtube.com/watch?v=..."')
        print("\n")
    else:
        print("\n❌ Setup failed. Please install FFmpeg manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()
