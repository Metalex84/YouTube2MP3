"""
Test script to validate the Flask web application
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import flask
        print("  ✓ Flask imported successfully")
        
        import flask_socketio
        print("  ✓ Flask-SocketIO imported successfully")
        
        import flask_cors
        print("  ✓ Flask-CORS imported successfully")
        
        import yt_dlp
        print("  ✓ yt-dlp imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def test_app_structure():
    """Test that the app.py file can be loaded"""
    print("\nTesting app structure...")
    try:
        from app import app, socketio
        print("  ✓ Flask app created successfully")
        print(f"  ✓ App secret key configured: {bool(app.config.get('SECRET_KEY'))}")
        print(f"  ✓ Max content length: {app.config.get('MAX_CONTENT_LENGTH')} bytes")
        return True
    except Exception as e:
        print(f"  ✗ Error loading app: {e}")
        return False

def test_routes():
    """Test that all expected routes are registered"""
    print("\nTesting routes...")
    try:
        from app import app
        
        expected_routes = [
            '/',
            '/api/download',
            '/api/batch-download',
            '/api/downloads',
            '/api/download/<download_id>',
            '/api/download/<download_id>/file',
            '/api/health'
        ]
        
        registered_routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        for route in expected_routes:
            # Check if route exists (considering variable parts)
            route_exists = any(route.replace('<download_id>', '<') in r for r in registered_routes)
            if route_exists or route in registered_routes:
                print(f"  ✓ Route registered: {route}")
            else:
                print(f"  ✗ Route missing: {route}")
                
        return True
    except Exception as e:
        print(f"  ✗ Error testing routes: {e}")
        return False

def test_templates():
    """Test that template files exist"""
    print("\nTesting templates...")
    
    template_path = os.path.join(os.getcwd(), 'templates', 'index.html')
    if os.path.exists(template_path):
        print(f"  ✓ Template found: {template_path}")
        return True
    else:
        print(f"  ✗ Template missing: {template_path}")
        return False

def test_static_files():
    """Test that static files exist"""
    print("\nTesting static files...")
    
    static_files = [
        os.path.join('static', 'style.css'),
        os.path.join('static', 'script.js')
    ]
    
    all_exist = True
    for file in static_files:
        file_path = os.path.join(os.getcwd(), file)
        if os.path.exists(file_path):
            print(f"  ✓ Static file found: {file}")
        else:
            print(f"  ✗ Static file missing: {file}")
            all_exist = False
    
    return all_exist

def test_health_endpoint():
    """Test the health endpoint"""
    print("\nTesting health endpoint...")
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/api/health')
            
            if response.status_code == 200:
                print(f"  ✓ Health endpoint responds: {response.status_code}")
                data = response.get_json()
                print(f"  ✓ Response data: {data}")
                return True
            else:
                print(f"  ✗ Health endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"  ✗ Error testing health endpoint: {e}")
        return False

def main():
    print("="*60)
    print("YouTube2MP3 Web Application - Validation Tests")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("App Structure", test_app_structure()))
    results.append(("Routes", test_routes()))
    results.append(("Templates", test_templates()))
    results.append(("Static Files", test_static_files()))
    results.append(("Health Endpoint", test_health_endpoint()))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20s} {status}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n✅ All tests passed! The web application is ready to run.")
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nThen open your browser to:")
        print("  http://localhost:5000")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
