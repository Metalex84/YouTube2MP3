"""
Simple script to check current downloads state
"""
import urllib.request
import json

BASE_URL = "http://localhost:5000"

try:
    # Check downloads
    with urllib.request.urlopen(f"{BASE_URL}/api/downloads") as response:
        data = json.loads(response.read().decode())
        downloads = data.get('downloads', [])
        
        print("=" * 60)
        print(f"Total downloads: {len(downloads)}")
        print("=" * 60)
        
        if not downloads:
            print("No downloads found.")
            print("\nPlease add some downloads using the web interface:")
            print(f"  {BASE_URL}")
        else:
            completed = [d for d in downloads if d['status'] == 'completed']
            pending = [d for d in downloads if d['status'] == 'pending']
            downloading = [d for d in downloads if d['status'] == 'downloading']
            failed = [d for d in downloads if d['status'] == 'failed']
            
            print(f"Completed:   {len(completed)}")
            print(f"Downloading: {len(downloading)}")
            print(f"Pending:     {len(pending)}")
            print(f"Failed:      {len(failed)}")
            print()
            
            if completed:
                print("Completed downloads:")
                for d in completed:
                    title = d.get('title', 'Unknown')
                    filename = d.get('filename', 'N/A')
                    has_file = 'filepath' in d
                    print(f"  - {title}")
                    print(f"    File: {filename}")
                    print(f"    Has filepath: {has_file}")
                    print()
            
            print("=" * 60)
            if len(completed) >= 2:
                print("✓ ZIP download button SHOULD be visible")
                print(f"\nYou can test ZIP download at:")
                print(f"  {BASE_URL}/api/batch-download/zip")
            else:
                print(f"⚠️  Need at least 2 completed downloads (have {len(completed)})")
                print("   ZIP download button will NOT appear yet")
            print("=" * 60)
            
except urllib.error.URLError:
    print("❌ Cannot connect to server at http://localhost:5000")
    print("   Please start the server with: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
