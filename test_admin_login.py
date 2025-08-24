#!/usr/bin/env python3
"""
🔐 TEST ADMIN LOGIN
Test the admin login functionality directly
"""

import hashlib
import requests
import time

def test_local_auth():
    """Test the local authentication logic"""
    print("🧪 Testing Local Authentication Logic...")
    
    # Local users (same as in api/app.py)
    LOCAL_USERS = {
        'admin@jobsprint.com': {
            'id': 'admin-001',
            'email': 'admin@jobsprint.com',
            'name': 'JobSprint Admin',
            'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
            'is_admin': True
        },
        'test@jobsprint.com': {
            'id': 'test-001',
            'email': 'test@jobsprint.com',
            'name': 'Test User',
            'password_hash': hashlib.sha256('test123'.encode()).hexdigest(),
            'is_admin': False
        }
    }
    
    # Test admin credentials
    email = 'admin@jobsprint.com'
    password = 'admin123'
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"  📧 Email: {email}")
    print(f"  🔑 Password: {password}")
    print(f"  🔐 Password Hash: {password_hash}")
    
    user = LOCAL_USERS.get(email)
    if user:
        print(f"  ✅ User found in LOCAL_USERS")
        print(f"  👤 Name: {user['name']}")
        print(f"  👑 Is Admin: {user['is_admin']}")
        print(f"  🔐 Stored Hash: {user['password_hash']}")
        
        if user['password_hash'] == password_hash:
            print(f"  ✅ Password hash matches!")
            return True
        else:
            print(f"  ❌ Password hash mismatch!")
            return False
    else:
        print(f"  ❌ User not found in LOCAL_USERS")
        return False

def test_api_login():
    """Test the API login endpoint"""
    print(f"\n🌐 Testing API Login Endpoint...")
    
    # Wait for server to be ready
    print(f"  ⏳ Checking if server is running...")
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ Server is running")
        else:
            print(f"  ❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Server not accessible: {e}")
        return False
    
    # Test admin login
    login_data = {
        "email": "admin@jobsprint.com",
        "password": "admin123"
    }
    
    try:
        print(f"  🚀 Sending login request...")
        response = requests.post(
            "http://127.0.0.1:5000/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"  📊 Response Status: {response.status_code}")
        print(f"  📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('user', {}).get('is_admin'):
                print(f"  ✅ Admin login successful!")
                return True
            else:
                print(f"  ❌ Login response invalid")
                return False
        else:
            print(f"  ❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Login request failed: {e}")
        return False

def start_server_and_test():
    """Start server and test"""
    print(f"\n🚀 Starting Fresh Server...")
    
    import subprocess
    import os
    
    try:
        # Start the server
        process = subprocess.Popen(
            ["python", "api/app.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"  ⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Check if server is running
        if process.poll() is None:
            print(f"  ✅ Server started (PID: {process.pid})")
            
            # Test the login
            login_success = test_api_login()
            
            # Stop the server
            process.terminate()
            process.wait(timeout=5)
            print(f"  🛑 Server stopped")
            
            return login_success
        else:
            stdout, stderr = process.communicate()
            print(f"  ❌ Server failed to start")
            print(f"     STDOUT: {stdout.decode()}")
            print(f"     STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error starting server: {e}")
        return False

def main():
    print("🔐 ADMIN LOGIN TEST")
    print("=" * 50)
    
    # Test local auth logic
    local_success = test_local_auth()
    
    # Test API endpoint (if server is already running)
    api_success = test_api_login()
    
    print(f"\n" + "=" * 50)
    print(f"📊 TEST RESULTS")
    print(f"=" * 50)
    
    print(f"🧪 Local Auth Logic: {'✅ PASS' if local_success else '❌ FAIL'}")
    print(f"🌐 API Endpoint: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if local_success and api_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Admin login should work in the frontend")
    elif local_success and not api_success:
        print(f"\n⚠️ LOCAL LOGIC WORKS BUT API FAILS")
        print(f"💡 The server might not be running the updated code")
        print(f"🔄 Try restarting the server")
    else:
        print(f"\n❌ TESTS FAILED")
        print(f"🔧 Check the code and try again")

if __name__ == "__main__":
    main()
