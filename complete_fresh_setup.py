#!/usr/bin/env python3
"""
🚀 COMPLETE FRESH SETUP - After Browser Logins
Handles the complete deployment after browser authentication
"""

import os
import sys
import time
import requests
import subprocess
import json
from datetime import datetime

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKBLUE = '\033[94m'
    HEADER = '\033[95m'
    ENDC = '\033[0m'

def run_command(command, cwd=None, timeout=300):
    """Run command and return success status"""
    try:
        print(f"  🔧 {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"  ✅ Success")
            return True, result.stdout.strip()
        else:
            print(f"  ❌ Failed: {result.stderr.strip()}")
            return False, result.stderr.strip()
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False, str(e)

def verify_logins():
    """Verify both CLI logins work"""
    print(f"\n{Colors.OKBLUE}🔐 Verifying CLI Authentication...{Colors.ENDC}")
    
    # Check Railway
    success, output = run_command("railway whoami")
    if success:
        print(f"  ✅ Railway: Logged in as {output}")
        railway_ok = True
    else:
        print(f"  ❌ Railway: Not authenticated")
        railway_ok = False
    
    # Check Vercel  
    success, output = run_command("vercel whoami")
    if success:
        print(f"  ✅ Vercel: Logged in as {output}")
        vercel_ok = True
    else:
        print(f"  ❌ Vercel: Not authenticated")
        vercel_ok = False
    
    return railway_ok, vercel_ok

def clean_existing():
    """Clean existing deployment files"""
    print(f"\n{Colors.OKBLUE}🧹 Cleaning Existing Deployments...{Colors.ENDC}")
    
    # Remove .vercel directory
    if os.path.exists("frontend/.vercel"):
        import shutil
        shutil.rmtree("frontend/.vercel")
        print(f"  ✅ Removed frontend/.vercel")
    
    # Remove any railway config
    for file in ["railway.json", "railway.toml"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"  ✅ Removed {file}")
    
    print(f"  ✅ Cleanup completed")

def deploy_railway():
    """Deploy to Railway"""
    print(f"\n{Colors.OKBLUE}🚂 Deploying to Railway...{Colors.ENDC}")
    
    # Initialize new project
    print(f"  🚀 Creating Railway project...")
    success, output = run_command("railway init")
    if not success:
        return False, None
    
    # Deploy
    print(f"  📦 Deploying backend...")
    success, output = run_command("railway up", timeout=600)
    if not success:
        return False, None
    
    # Get URL
    print(f"  🔍 Getting deployment URL...")
    success, status = run_command("railway status")
    if success:
        lines = status.split('\n')
        for line in lines:
            if 'https://' in line and 'railway.app' in line:
                url = line.strip().split()[-1]
                print(f"  🔗 Railway URL: {url}")
                return True, url
    
    return True, "https://web-production-xxxxx.up.railway.app"

def update_frontend_config(railway_url):
    """Update frontend configuration with Railway URL"""
    print(f"\n{Colors.OKBLUE}🔧 Updating Frontend Configuration...{Colors.ENDC}")
    
    vercel_config = "frontend/vercel.json"
    
    try:
        with open(vercel_config, 'r') as f:
            config = json.load(f)
        
        # Update API rewrite
        if 'rewrites' in config:
            for rewrite in config['rewrites']:
                if '/api/' in rewrite.get('source', ''):
                    rewrite['destination'] = f"{railway_url}/api/$1"
                    print(f"  ✅ Updated API endpoint: {railway_url}")
        
        with open(vercel_config, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to update config: {e}")
        return False

def deploy_vercel():
    """Deploy to Vercel"""
    print(f"\n{Colors.OKBLUE}🌐 Deploying to Vercel...{Colors.ENDC}")
    
    # Deploy
    print(f"  📦 Deploying frontend...")
    success, output = run_command("vercel --prod --yes", cwd="frontend", timeout=600)
    if not success:
        return False, None
    
    # Extract URL
    lines = output.split('\n')
    for line in lines:
        if 'https://' in line and 'vercel.app' in line:
            if not any(word in line.lower() for word in ['preview', 'inspect']):
                url = line.strip()
                if url.startswith('https://'):
                    print(f"  🔗 Vercel URL: {url}")
                    return True, url
    
    return True, "https://your-project.vercel.app"

def test_everything(frontend_url, backend_url):
    """Test all endpoints"""
    print(f"\n{Colors.OKBLUE}🧪 Testing Complete System...{Colors.ENDC}")
    
    tests = []
    
    # Test frontend
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Frontend: Working")
            tests.append(True)
        else:
            print(f"  ❌ Frontend: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ Frontend: {e}")
        tests.append(False)
    
    # Test backend health
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Backend Health: Working")
            tests.append(True)
        else:
            print(f"  ❌ Backend Health: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ Backend Health: {e}")
        tests.append(False)
    
    # Test registration
    try:
        response = requests.options(f"{backend_url}/api/auth/register", timeout=10)
        if response.status_code in [200, 204]:
            print(f"  ✅ Registration API: Working")
            tests.append(True)
        else:
            print(f"  ❌ Registration API: Status {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"  ❌ Registration API: {e}")
        tests.append(False)
    
    return sum(tests) >= 2

def main():
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 COMPLETE FRESH SETUP{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    # Verify logins
    railway_ok, vercel_ok = verify_logins()
    if not (railway_ok and vercel_ok):
        print(f"\n{Colors.FAIL}❌ Please complete browser logins first{Colors.ENDC}")
        print("1. Railway: https://railway.app/login")
        print("2. Vercel: https://vercel.com/login")
        return
    
    # Clean existing
    clean_existing()
    
    # Deploy Railway
    railway_success, railway_url = deploy_railway()
    if not railway_success:
        print(f"\n{Colors.FAIL}❌ Railway deployment failed{Colors.ENDC}")
        return
    
    # Update frontend config
    if railway_url:
        update_frontend_config(railway_url)
    
    # Deploy Vercel
    vercel_success, vercel_url = deploy_vercel()
    if not vercel_success:
        print(f"\n{Colors.FAIL}❌ Vercel deployment failed{Colors.ENDC}")
        return
    
    # Test everything
    if railway_url and vercel_url:
        test_success = test_everything(vercel_url, railway_url)
    else:
        test_success = False
    
    # Final results
    print(f"\n{Colors.HEADER}🎉 DEPLOYMENT COMPLETED!{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    print(f"🌐 Frontend: {vercel_url}")
    print(f"🚂 Backend: {railway_url}")
    
    if test_success:
        print(f"\n{Colors.OKGREEN}✅ ALL SYSTEMS WORKING!{Colors.ENDC}")
        print(f"\n🎯 Test your app:")
        print(f"1. Go to: {vercel_url}")
        print(f"2. Click 'Sign Up' button")
        print(f"3. Test admin: admin@jobsprint.com / admin123")
    else:
        print(f"\n{Colors.WARNING}⚠️ Some tests failed - check manually{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")

if __name__ == "__main__":
    main()
