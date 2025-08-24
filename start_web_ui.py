#!/usr/bin/env python3
"""
Simple launcher for the LinkedIn Job Automation Web UI
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("🚀 LinkedIn Job Automation System")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if required files exist
    required_files = [
        "src/main.py",
        "src/web_ui.py", 
        "config.json",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    print("✅ All required files found")
    
    # Start the web UI
    print("🌐 Starting web server...")
    print("📧 Configure your email settings in the web interface")
    print("🎯 Set your job preferences and start monitoring!")
    print("\n" + "=" * 50)
    
    try:
        # Start Flask app
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(script_dir, 'src')
        
        process = subprocess.Popen([
            sys.executable, 
            os.path.join('src', 'web_ui.py')
        ], env=env, cwd=script_dir)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Open browser
        print("🌐 Opening web browser at http://localhost:5000")
        webbrowser.open('http://localhost:5000')
        
        print("\n📝 Instructions:")
        print("1. Configure your email settings (Gmail + App Password)")
        print("2. Set your job preferences (keywords, locations)")
        print("3. Click 'Start Monitoring' to begin finding jobs")
        print("4. Press Ctrl+C to stop the server")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down web server...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

if __name__ == "__main__":
    main()
