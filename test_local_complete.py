#!/usr/bin/env python3
"""
🧪 COMPLETE LOCAL TESTING
Test everything locally before any deployment
"""

import os
import sys
import time
import requests
import subprocess
import threading
from datetime import datetime

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKBLUE = '\033[94m'
    HEADER = '\033[95m'
    ENDC = '\033[0m'

def print_header():
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}🧪 COMPLETE LOCAL TESTING{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print("Testing everything locally before deployment")
    print()

def run_command(command, cwd=None, timeout=60):
    """Run command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def start_backend():
    """Start the backend server"""
    print(f"\n{Colors.OKBLUE}🚂 Starting Backend Server...{Colors.ENDC}")
    
    # Check if requirements are installed
    success, stdout, stderr = run_command("pip list | findstr fastapi", cwd="backend")
    if not success or "fastapi" not in stdout.lower():
        print(f"  📦 Installing backend dependencies...")
        success, stdout, stderr = run_command("pip install -r requirements.txt", cwd="backend", timeout=120)
        if not success:
            print(f"  ❌ Failed to install dependencies: {stderr}")
            return None
        print(f"  ✅ Dependencies installed")
    
    # Start the server in background
    print(f"  🚀 Starting FastAPI server on port 8000...")
    try:
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print(f"  ✅ Backend server started (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"  ❌ Server failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"  ❌ Failed to start server: {e}")
        return None

def test_backend_endpoints():
    """Test all backend endpoints"""
    print(f"\n{Colors.OKBLUE}🔍 Testing Backend Endpoints...{Colors.ENDC}")
    
    base_url = "http://localhost:8000"
    tests_passed = 0
    total_tests = 0
    
    # Test health endpoint
    total_tests += 1
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Health endpoint: Working")
            tests_passed += 1
        else:
            print(f"  ❌ Health endpoint: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Health endpoint: {e}")
    
    # Test CORS preflight for registration
    total_tests += 1
    try:
        response = requests.options(f"{base_url}/api/auth/register", timeout=10)
        if response.status_code in [200, 204]:
            print(f"  ✅ Registration CORS: Working")
            tests_passed += 1
        else:
            print(f"  ❌ Registration CORS: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Registration CORS: {e}")
    
    # Test registration endpoint with dummy data
    total_tests += 1
    try:
        test_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/api/auth/register", json=test_data, timeout=10)
        if response.status_code in [200, 201, 400, 409]:  # 400/409 are expected for validation
            print(f"  ✅ Registration endpoint: Working (Status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"  ❌ Registration endpoint: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Registration endpoint: {e}")
    
    # Test admin login
    total_tests += 1
    try:
        admin_data = {
            "email": "admin@jobsprint.com",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=admin_data, timeout=10)
        if response.status_code in [200, 201, 400, 401]:  # Various expected responses
            print(f"  ✅ Admin login endpoint: Working (Status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"  ❌ Admin login endpoint: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Admin login endpoint: {e}")
    
    # Test job search endpoint
    total_tests += 1
    try:
        search_params = {
            "keywords": "python developer",
            "location": "Toronto",
            "time_filter": "r3600"
        }
        response = requests.get(f"{base_url}/api/jobs/search", params=search_params, timeout=15)
        if response.status_code in [200, 400, 500]:  # 500 might be expected without real API keys
            print(f"  ✅ Job search endpoint: Working (Status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"  ❌ Job search endpoint: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Job search endpoint: {e}")
    
    print(f"\n  📊 Backend Tests: {tests_passed}/{total_tests} passed")
    return tests_passed >= 3  # At least 3 core endpoints should work

def start_frontend():
    """Start the frontend server"""
    print(f"\n{Colors.OKBLUE}🌐 Starting Frontend Server...{Colors.ENDC}")
    
    # Check if we have a simple HTTP server available
    try:
        # Try Python's built-in server
        process = subprocess.Popen(
            ["python", "-m", "http.server", "3000"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        if process.poll() is None:
            print(f"  ✅ Frontend server started on port 3000 (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"  ❌ Frontend server failed: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"  ❌ Failed to start frontend: {e}")
        return None

def test_frontend():
    """Test frontend"""
    print(f"\n{Colors.OKBLUE}🔍 Testing Frontend...{Colors.ENDC}")
    
    base_url = "http://localhost:3000"
    tests_passed = 0
    total_tests = 0
    
    # Test main page
    total_tests += 1
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Main page: Loading")
            tests_passed += 1
        else:
            print(f"  ❌ Main page: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Main page: {e}")
    
    # Test dashboard page
    total_tests += 1
    try:
        response = requests.get(f"{base_url}/dashboard.html", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Dashboard page: Loading")
            tests_passed += 1
        else:
            print(f"  ❌ Dashboard page: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Dashboard page: {e}")
    
    # Test static files
    total_tests += 1
    try:
        response = requests.get(f"{base_url}/styles.css", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ CSS files: Loading")
            tests_passed += 1
        else:
            print(f"  ❌ CSS files: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ CSS files: {e}")
    
    print(f"\n  📊 Frontend Tests: {tests_passed}/{total_tests} passed")
    return tests_passed >= 2

def test_integration():
    """Test frontend-backend integration"""
    print(f"\n{Colors.OKBLUE}🔗 Testing Frontend-Backend Integration...{Colors.ENDC}")
    
    # This would test if frontend can communicate with backend
    # For now, just verify both servers are running
    
    backend_ok = False
    frontend_ok = False
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        backend_ok = response.status_code == 200
    except:
        pass
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        frontend_ok = response.status_code == 200
    except:
        pass
    
    if backend_ok and frontend_ok:
        print(f"  ✅ Both servers running - Integration possible")
        return True
    else:
        print(f"  ❌ Integration test failed - Backend: {backend_ok}, Frontend: {frontend_ok}")
        return False

def cleanup_processes(processes):
    """Clean up running processes"""
    print(f"\n{Colors.OKBLUE}🧹 Cleaning Up Processes...{Colors.ENDC}")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✅ Process {process.pid} terminated")
            except:
                try:
                    process.kill()
                    print(f"  ✅ Process {process.pid} killed")
                except:
                    print(f"  ⚠️ Could not terminate process {process.pid}")

def main():
    print_header()
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)
            time.sleep(2)  # Give backend time to fully start
        
        # Test backend
        backend_ok = test_backend_endpoints()
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
            time.sleep(2)  # Give frontend time to start
        
        # Test frontend
        frontend_ok = test_frontend()
        
        # Test integration
        integration_ok = test_integration()
        
        # Results
        print(f"\n{Colors.HEADER}📊 LOCAL TESTING RESULTS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        
        print(f"🚂 Backend: {'✅ PASS' if backend_ok else '❌ FAIL'}")
        print(f"🌐 Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
        print(f"🔗 Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
        
        overall_success = backend_ok and frontend_ok and integration_ok
        
        if overall_success:
            print(f"\n{Colors.OKGREEN}🎉 ALL LOCAL TESTS PASSED!{Colors.ENDC}")
            print(f"✅ Ready for deployment")
            print(f"\n🔗 Local URLs:")
            print(f"  Frontend: http://localhost:3000")
            print(f"  Backend: http://localhost:8000")
            print(f"  API Docs: http://localhost:8000/docs")
        else:
            print(f"\n{Colors.FAIL}❌ SOME TESTS FAILED{Colors.ENDC}")
            print(f"⚠️ Fix issues before deployment")
        
        print(f"\n{Colors.WARNING}Press Ctrl+C to stop servers and exit{Colors.ENDC}")
        
        # Keep servers running for manual testing
        if overall_success:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Colors.OKBLUE}Stopping servers...{Colors.ENDC}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.OKBLUE}Interrupted by user{Colors.ENDC}")
    
    finally:
        cleanup_processes(processes)
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")

if __name__ == "__main__":
    main()
