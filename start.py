#!/usr/bin/env python3
"""
Startup script for Railway deployment
Ensures proper path setup and Gunicorn launch
"""

import os
import sys
import subprocess

def main():
    """Main startup function"""
    print("🚀 Starting MevzuatAI deployment...")
    
    # Set working directory to project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Get port from environment
    port = os.environ.get('PORT', '8000')
    print(f"🌐 Port: {port}")
    
    # Verify frontend directory exists
    frontend_path = os.path.join(project_root, 'frontend')
    if not os.path.exists(frontend_path):
        print(f"❌ Frontend directory not found: {frontend_path}")
        sys.exit(1)
    
    app_file = os.path.join(frontend_path, 'app.py')
    if not os.path.exists(app_file):
        print(f"❌ App file not found: {app_file}")
        sys.exit(1)
    
    print(f"✅ Frontend path verified: {frontend_path}")
    
    # Build Gunicorn command
    gunicorn_cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        '--timeout', '300',
        '--worker-class', 'sync',
        '--max-requests', '1000',
        '--preload',
        '--chdir', 'frontend',
        'app:app'
    ]
    
    print(f"🚀 Starting Gunicorn: {' '.join(gunicorn_cmd)}")
    
    try:
        # Start Gunicorn
        subprocess.run(gunicorn_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed: {e}")
        print("🔄 Falling back to Flask development server...")
        
        # Fallback to Flask
        sys.path.insert(0, frontend_path)
        os.chdir(frontend_path)
        
        from app import app
        app.run(host='0.0.0.0', port=int(port))
    except FileNotFoundError:
        print("❌ Gunicorn not found, using Flask development server...")
        
        # Fallback to Flask
        sys.path.insert(0, frontend_path)
        os.chdir(frontend_path)
        
        from app import app
        app.run(host='0.0.0.0', port=int(port))

if __name__ == '__main__':
    main()