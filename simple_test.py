#!/usr/bin/env python3
"""
Simple test to verify Flask works
"""

print("🧪 Testing Flask...")

try:
    from flask import Flask
    print("✅ Flask imported successfully")
    
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return """
        <html>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>🎉 SUCCESS!</h1>
            <h2>LinkedIn Job Automation System</h2>
            <p>Flask web server is working correctly!</p>
            <p>The system is ready to run.</p>
            <hr>
            <p><strong>Next steps:</strong></p>
            <ol style="text-align: left; max-width: 400px; margin: 0 auto;">
                <li>Configure your email settings in config.json</li>
                <li>Set your job preferences</li>
                <li>Start monitoring for jobs</li>
            </ol>
        </body>
        </html>
        """
    
    print("🌐 Starting Flask test server on http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
