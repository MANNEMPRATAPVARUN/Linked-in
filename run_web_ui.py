#!/usr/bin/env python3
"""
Simple script to run the web UI with error handling
"""

import os
import sys
import traceback

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

print("🚀 LinkedIn Job Automation System - Web UI")
print("=" * 50)
print(f"📁 Current directory: {current_dir}")
print(f"🐍 Python path: {sys.path[:3]}...")

try:
    print("📦 Importing Flask...")
    from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
    print("✅ Flask imported successfully")
    
    print("📦 Importing main module...")
    from main import JobAutomationSystem
    print("✅ Main module imported successfully")
    
    print("🌐 Starting Flask application...")
    
    app = Flask(__name__, template_folder='src/templates')
    app.secret_key = 'linkedin-job-automation-secret-key'
    
    # Global automation instance
    automation = None
    
    @app.route('/')
    def index():
        """Simple test page"""
        return """
        <html>
        <head>
            <title>LinkedIn Job Automation System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #0077b5; margin-bottom: 30px; }
                .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
                .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
                .btn { background: #0077b5; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; text-decoration: none; display: inline-block; }
                .btn:hover { background: #005885; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 LinkedIn Job Automation System</h1>
                    <p>Your personal job hunting assistant</p>
                </div>
                
                <div class="status success">
                    ✅ <strong>System Status:</strong> Web UI is running successfully!
                </div>
                
                <div class="status info">
                    📋 <strong>Next Steps:</strong>
                    <ol>
                        <li>Configure your email settings in config.json</li>
                        <li>Set your job preferences (keywords, locations)</li>
                        <li>Test the email functionality</li>
                        <li>Start monitoring for jobs</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/config" class="btn">⚙️ Configuration</a>
                    <a href="/test" class="btn">🧪 Test System</a>
                    <a href="/start" class="btn">▶️ Start Monitoring</a>
                </div>
                
                <div style="text-align: center; margin-top: 20px; color: #666;">
                    <p>🌐 Web UI running at <strong>http://localhost:5000</strong></p>
                    <p>Press <strong>Ctrl+C</strong> to stop the server</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.route('/config')
    def config():
        return "<h1>Configuration Page</h1><p>Configuration interface will be here</p><a href='/'>← Back</a>"
    
    @app.route('/test')
    def test():
        global automation
        try:
            if not automation:
                automation = JobAutomationSystem()
            return "<h1>✅ Test Successful</h1><p>JobAutomationSystem initialized successfully!</p><a href='/'>← Back</a>"
        except Exception as e:
            return f"<h1>❌ Test Failed</h1><p>Error: {str(e)}</p><a href='/'>← Back</a>"
    
    @app.route('/start')
    def start():
        return "<h1>Start Monitoring</h1><p>Monitoring functionality will be here</p><a href='/'>← Back</a>"
    
    print("🌐 Starting web server on http://localhost:5000")
    print("📧 Configure your settings and start monitoring!")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"❌ Error starting web UI: {e}")
    print("\n🔍 Full error traceback:")
    traceback.print_exc()
    print("\n💡 Troubleshooting tips:")
    print("1. Make sure all dependencies are installed: py -m pip install -r requirements.txt")
    print("2. Check if config.json exists and is valid")
    print("3. Verify all files are in the correct locations")
    input("\nPress Enter to exit...")
