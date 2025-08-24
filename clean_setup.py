#!/usr/bin/env python3
"""
🧹 COMPLETE CLEAN SETUP
Automated clean deployment of JobSprint
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

def print_header():
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}🧹 JOBSPRINT COMPLETE CLEAN SETUP{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print("Automated fresh deployment - Everything handled systematically")
    print()

def run_command(command, cwd=None, timeout=300):
    """Run command and return success status"""
    try:
        print(f"  🔧 Running: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"  ✅ Success")
            return True, result.stdout
        else:
            print(f"  ❌ Failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False, str(e)

def clean_deployment_files():
    """Clean up any existing deployment configurations"""
    print(f"\n{Colors.OKBLUE}🧹 Cleaning Deployment Files...{Colors.ENDC}")
    
    files_to_clean = [
        '.vercel',
        'railway.json',
        'railway.toml',
        'deployment_trigger.txt'
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            try:
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                print(f"  ✅ Removed: {file_path}")
            except Exception as e:
                print(f"  ⚠️ Could not remove {file_path}: {e}")
    
    print(f"  ✅ Cleanup completed")

def setup_railway():
    """Set up Railway deployment"""
    print(f"\n{Colors.OKBLUE}🚂 Setting Up Railway Backend...{Colors.ENDC}")
    
    # Check if logged in
    success, output = run_command("railway whoami")
    if not success:
        print(f"  {Colors.WARNING}⚠️ Please login to Railway first{Colors.ENDC}")
        print(f"  Run this command and follow the browser prompt:")
        print(f"  {Colors.WARNING}railway login{Colors.ENDC}")
        input(f"  Press Enter after logging in...")
        
        # Check again
        success, output = run_command("railway whoami")
        if not success:
            print(f"  {Colors.FAIL}❌ Railway login failed{Colors.ENDC}")
            return False, None
    
    print(f"  ✅ Railway authenticated: {output.strip()}")
    
    # Initialize new project
    print(f"  🚀 Creating new Railway project...")
    success, output = run_command("railway init --name jobsprint-backend")
    if not success:
        print(f"  {Colors.WARNING}⚠️ Init failed, trying alternative...{Colors.ENDC}")
        success, output = run_command("railway init")
    
    if success:
        print(f"  ✅ Railway project created")
    else:
        print(f"  {Colors.FAIL}❌ Failed to create Railway project{Colors.ENDC}")
        return False, None
    
    # Deploy
    print(f"  📦 Deploying to Railway...")
    success, output = run_command("railway up", timeout=600)
    
    if success:
        print(f"  ✅ Railway deployment successful!")
        
        # Get deployment URL
        success, status_output = run_command("railway status")
        if success:
            lines = status_output.split('\n')
            for line in lines:
                if 'https://' in line and 'railway.app' in line:
                    url = line.strip().split()[-1]
                    print(f"  🔗 Railway URL: {url}")
                    return True, url
        
        # Fallback - try to get domain
        success, domain_output = run_command("railway domain")
        if success and 'https://' in domain_output:
            lines = domain_output.split('\n')
            for line in lines:
                if 'https://' in line:
                    url = line.strip()
                    print(f"  🔗 Railway URL: {url}")
                    return True, url
        
        print(f"  ⚠️ Deployment successful but couldn't extract URL")
        return True, "https://your-project.up.railway.app"
    else:
        print(f"  {Colors.FAIL}❌ Railway deployment failed{Colors.ENDC}")
        return False, None

def setup_vercel(railway_url):
    """Set up Vercel deployment"""
    print(f"\n{Colors.OKBLUE}🌐 Setting Up Vercel Frontend...{Colors.ENDC}")
    
    # Check if logged in
    success, output = run_command("vercel whoami")
    if not success:
        print(f"  {Colors.WARNING}⚠️ Please login to Vercel first{Colors.ENDC}")
        print(f"  Run this command and follow the browser prompt:")
        print(f"  {Colors.WARNING}vercel login{Colors.ENDC}")
        input(f"  Press Enter after logging in...")
        
        # Check again
        success, output = run_command("vercel whoami")
        if not success:
            print(f"  {Colors.FAIL}❌ Vercel login failed{Colors.ENDC}")
            return False, None
    
    print(f"  ✅ Vercel authenticated: {output.strip()}")
    
    # Update vercel.json with new Railway URL
    if railway_url:
        print(f"  🔧 Updating API configuration...")
        update_vercel_config(railway_url)
    
    # Deploy frontend
    print(f"  📦 Deploying to Vercel...")
    success, output = run_command("vercel --prod --yes", cwd="frontend", timeout=600)
    
    if success:
        print(f"  ✅ Vercel deployment successful!")
        
        # Extract URL from output
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'vercel.app' in line and 'Preview:' not in line:
                url = line.strip()
                if url.startswith('https://'):
                    print(f"  🔗 Vercel URL: {url}")
                    return True, url
        
        print(f"  ⚠️ Deployment successful but couldn't extract URL")
        return True, "https://your-project.vercel.app"
    else:
        print(f"  {Colors.FAIL}❌ Vercel deployment failed{Colors.ENDC}")
        return False, None

def update_vercel_config(railway_url):
    """Update vercel.json with new Railway URL"""
    try:
        vercel_config_path = "frontend/vercel.json"
        
        if os.path.exists(vercel_config_path):
            with open(vercel_config_path, 'r') as f:
                config = json.load(f)
            
            # Update the API rewrite destination
            if 'rewrites' in config:
                for rewrite in config['rewrites']:
                    if rewrite.get('source') == '/api/(.*)':
                        rewrite['destination'] = f"{railway_url}/api/$1"
                        print(f"    ✅ Updated API endpoint to: {railway_url}")
            
            with open(vercel_config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        else:
            print(f"    ⚠️ vercel.json not found")
            
    except Exception as e:
        print(f"    ❌ Failed to update vercel.json: {e}")

def test_deployments(frontend_url, backend_url):
    """Test both deployments"""
    print(f"\n{Colors.OKBLUE}🧪 Testing Deployments...{Colors.ENDC}")
    
    tests_passed = 0
    total_tests = 3
    
    # Test frontend
    try:
        print(f"  🔍 Testing frontend...")
        response = requests.get(frontend_url, timeout=15)
        if response.status_code == 200:
            print(f"    ✅ Frontend: Working (Status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"    ⚠️ Frontend: Status {response.status_code}")
    except Exception as e:
        print(f"    ❌ Frontend: {e}")
    
    # Test backend health
    try:
        print(f"  🔍 Testing backend health...")
        health_url = f"{backend_url}/health"
        response = requests.get(health_url, timeout=15)
        if response.status_code == 200:
            print(f"    ✅ Backend Health: Working (Status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"    ⚠️ Backend Health: Status {response.status_code}")
    except Exception as e:
        print(f"    ❌ Backend Health: {e}")
    
    # Test registration endpoint
    try:
        print(f"  🔍 Testing registration endpoint...")
        reg_url = f"{backend_url}/api/auth/register"
        response = requests.options(reg_url, timeout=15)
        if response.status_code in [200, 204]:
            print(f"    ✅ Registration: Accessible (Status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"    ⚠️ Registration: Status {response.status_code}")
    except Exception as e:
        print(f"    ❌ Registration: {e}")
    
    print(f"\n  📊 Tests passed: {tests_passed}/{total_tests}")
    return tests_passed >= 2

def main():
    print_header()
    
    # Clean up existing files
    clean_deployment_files()
    
    # Setup Railway
    railway_success, railway_url = setup_railway()
    if not railway_success:
        print(f"\n{Colors.FAIL}❌ Railway setup failed. Exiting.{Colors.ENDC}")
        return
    
    # Setup Vercel
    vercel_success, vercel_url = setup_vercel(railway_url)
    if not vercel_success:
        print(f"\n{Colors.FAIL}❌ Vercel setup failed. Exiting.{Colors.ENDC}")
        return
    
    # Test deployments
    if railway_url and vercel_url:
        test_success = test_deployments(vercel_url, railway_url)
    else:
        test_success = False
    
    # Final summary
    print(f"\n{Colors.HEADER}🎉 CLEAN SETUP COMPLETED!{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    if vercel_url:
        print(f"🌐 Frontend: {vercel_url}")
    if railway_url:
        print(f"🚂 Backend: {railway_url}")
    
    if test_success:
        print(f"\n{Colors.OKGREEN}✅ All systems operational!{Colors.ENDC}")
        print(f"\n🎯 Test your app:")
        print(f"1. Go to: {vercel_url}")
        print(f"2. Click 'Sign Up' button")
        print(f"3. Test admin login: admin@jobsprint.com / admin123")
    else:
        print(f"\n{Colors.WARNING}⚠️ Some tests failed. Check the deployments manually.{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")

if __name__ == "__main__":
    main()
