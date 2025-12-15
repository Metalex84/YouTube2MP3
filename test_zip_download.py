"""
Test script to verify ZIP download functionality
This script simulates completed downloads and tests the ZIP endpoint
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_zip_download():
    """Test the batch ZIP download endpoint"""
    
    # First, check if there are any completed downloads
    print("1. Checking for completed downloads...")
    response = requests.get(f"{BASE_URL}/api/downloads")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to get downloads: {response.status_code}")
        return False
    
    data = response.json()
    downloads = data.get('downloads', [])
    completed = [d for d in downloads if d['status'] == 'completed']
    
    print(f"   ✓ Found {len(completed)} completed downloads out of {len(downloads)} total")
    
    if len(completed) < 2:
        print("   ⚠️  Need at least 2 completed downloads to test ZIP functionality")
        print("   Please complete some downloads first using the UI")
        return False
    
    # Try to download the ZIP
    print("\n2. Requesting ZIP download...")
    response = requests.get(f"{BASE_URL}/api/batch-download/zip")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to download ZIP: {response.status_code}")
        if response.headers.get('Content-Type') == 'application/json':
            print(f"   Error: {response.json()}")
        return False
    
    # Check if response is a ZIP file
    content_type = response.headers.get('Content-Type', '')
    content_disposition = response.headers.get('Content-Disposition', '')
    
    print(f"   ✓ Response received")
    print(f"   Content-Type: {content_type}")
    print(f"   Content-Disposition: {content_disposition}")
    print(f"   Size: {len(response.content)} bytes")
    
    if 'zip' not in content_type and 'zip' not in content_disposition:
        print("   ⚠️  Response doesn't appear to be a ZIP file")
        return False
    
    # Verify it's a valid ZIP file
    import zipfile
    import io
    
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        files = zip_file.namelist()
        print(f"\n3. ZIP file contents:")
        for filename in files:
            file_info = zip_file.getinfo(filename)
            print(f"   - {filename} ({file_info.file_size} bytes)")
        
        print(f"\n✓ Success! ZIP contains {len(files)} file(s)")
        return True
        
    except zipfile.BadZipFile:
        print("   ❌ Invalid ZIP file")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing ZIP Download Functionality")
    print("=" * 60)
    
    try:
        success = test_zip_download()
        print("\n" + "=" * 60)
        if success:
            print("✓ All tests passed!")
        else:
            print("❌ Tests failed or incomplete")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server at http://localhost:5000")
        print("   Please make sure the Flask app is running:")
        print("   python app.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
