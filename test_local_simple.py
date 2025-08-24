#!/usr/bin/env python3
"""
🧪 SIMPLE LOCAL TESTING
Test the actual project structure locally
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
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}🧪 LOCAL TESTING - JOBSPRINT{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")

def test_backend_files():
    """Check if backend files exist"""
    print(f"\n{Colors.OKBLUE}📁 Checking Backend Files...{Colors.ENDC}")
    
    files_to_check = [
        "api/app.py",
        "requirements.txt",
        "src/main.py",
        "Procfile"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def test_frontend_files():
    """Check if frontend files exist"""
    print(f"\n{Colors.OKBLUE}📁 Checking Frontend Files...{Colors.ENDC}")
    
    files_to_check = [
        "frontend/index.html",
        "frontend/dashboard.html",
        "frontend/script.js",
        "frontend/styles.css",
        "frontend/vercel.json"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def start_backend_server():
    """Start the backend server"""
    print(f"\n{Colors.OKBLUE}🚂 Starting Backend Server...{Colors.ENDC}")
    
    # Check which backend file to use
    if os.path.exists("api/app.py"):
        backend_file = "api.app:app"
        print(f"  📁 Using FastAPI backend: api/app.py")
    elif os.path.exists("src/main.py"):
        backend_file = "src.main:app"
        print(f"  📁 Using main backend: src/main.py")
    else:
        print(f"  ❌ No backend file found")
        return None
    
    try:
        # Start uvicorn server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", backend_file,
            "--host", "127.0.0.1", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print(f"  ⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"  ✅ Backend server started on http://127.0.0.1:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"  ❌ Server failed to start")
            print(f"     Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"  ❌ Failed to start server: {e}")
        return None

def test_backend_endpoints():
    """Test backend endpoints"""
    print(f"\n{Colors.OKBLUE}🔍 Testing Backend Endpoints...{Colors.ENDC}")
    
    base_url = "http://127.0.0.1:8000"
    tests = []
    
    # Test root endpoint
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Root endpoint: Working")
            tests.append(True)
        else:
            print(f"  ⚠️ Root endpoint: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ Root endpoint: {e}")
        tests.append(False)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Health endpoint: Working")
            tests.append(True)
        else:
            print(f"  ⚠️ Health endpoint: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ Health endpoint: {e}")
        tests.append(False)
    
    # Test API docs
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ API docs: Working")
            tests.append(True)
        else:
            print(f"  ⚠️ API docs: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ API docs: {e}")
        tests.append(False)
    
    return sum(tests) >= 2

def start_frontend_server():
    """Start frontend server"""
    print(f"\n{Colors.OKBLUE}🌐 Starting Frontend Server...{Colors.ENDC}")
    
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd="frontend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)
        
        if process.poll() is None:
            print(f"  ✅ Frontend server started on http://127.0.0.1:3000")
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
    
    base_url = "http://127.0.0.1:3000"
    tests = []
    
    # Test main page
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Main page: Loading")
            tests.append(True)
        else:
            print(f"  ❌ Main page: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ Main page: {e}")
        tests.append(False)
    
    # Test dashboard
    try:
        response = requests.get(f"{base_url}/dashboard.html", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Dashboard: Loading")
            tests.append(True)
        else:
            print(f"  ❌ Dashboard: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ Dashboard: {e}")
        tests.append(False)
    
    return sum(tests) >= 1

def cleanup_processes(processes):
    """Clean up processes"""
    print(f"\n{Colors.OKBLUE}🧹 Cleaning Up...{Colors.ENDC}")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✅ Process terminated")
            except:
                try:
                    process.kill()
                    print(f"  ✅ Process killed")
                except:
                    print(f"  ⚠️ Could not stop process")

def main():
    print_header()
    
    processes = []
    
    try:
        # Check files
        backend_files_ok = test_backend_files()
        frontend_files_ok = test_frontend_files()
        
        if not backend_files_ok:
            print(f"\n{Colors.FAIL}❌ Backend files missing - cannot proceed{Colors.ENDC}")
            return
        
        if not frontend_files_ok:
            print(f"\n{Colors.FAIL}❌ Frontend files missing - cannot proceed{Colors.ENDC}")
            return
        
        # Start backend
        backend_process = start_backend_server()
        if backend_process:
            processes.append(backend_process)
        
        # Test backend
        backend_ok = test_backend_endpoints() if backend_process else False
        
        # Start frontend
        frontend_process = start_frontend_server()
        if frontend_process:
            processes.append(frontend_process)
        
        # Test frontend
        frontend_ok = test_frontend() if frontend_process else False
        
        # Results
        print(f"\n{Colors.HEADER}📊 LOCAL TEST RESULTS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        print(f"📁 Backend Files: {'✅' if backend_files_ok else '❌'}")
        print(f"📁 Frontend Files: {'✅' if frontend_files_ok else '❌'}")
        print(f"🚂 Backend Server: {'✅' if backend_ok else '❌'}")
        print(f"🌐 Frontend Server: {'✅' if frontend_ok else '❌'}")
        
        if backend_ok and frontend_ok:
            print(f"\n{Colors.OKGREEN}🎉 ALL LOCAL TESTS PASSED!{Colors.ENDC}")
            print(f"\n🔗 Local URLs:")
            print(f"  Frontend: http://127.0.0.1:3000")
            print(f"  Backend: http://127.0.0.1:8000")
            print(f"  API Docs: http://127.0.0.1:8000/docs")
            
            print(f"\n{Colors.WARNING}✅ READY FOR DEPLOYMENT!{Colors.ENDC}")
            print(f"Press Ctrl+C to stop servers")
            
            # Keep running for manual testing
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Colors.OKBLUE}Stopping...{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}❌ SOME TESTS FAILED{Colors.ENDC}")
            print(f"Fix issues before deployment")
    
    except KeyboardInterrupt:
        print(f"\n{Colors.OKBLUE}Interrupted{Colors.ENDC}")
    
    finally:
        cleanup_processes(processes)

if __name__ == "__main__":
    main()
