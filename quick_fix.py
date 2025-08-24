#!/usr/bin/env python3
"""
🚀 Quick Fix - Immediate Deployment Sync
Fixes current deployment issues by forcing a sync of all services
"""

import os
import sys
import time
import requests
import subprocess
from datetime import datetime

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKBLUE = '\033[94m'
    HEADER = '\033[95m'
    ENDC = '\033[0m'

def print_header():
    print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 JobSprint Quick Fix{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
    print("Fixing deployment sync issues...")
    print()

def run_command(command, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout + result.stderr
    except:
        return False, "Command failed"

def check_health(url, name):
    """Check service health"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"  {Colors.OKGREEN}✅ {name}: Healthy{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.WARNING}⚠️ {name}: Status {response.status_code}{Colors.ENDC}")
            return False
    except:
        print(f"  {Colors.FAIL}❌ {name}: Unreachable{Colors.ENDC}")
        return False

def main():
    print_header()
    
    # Check current status
    print(f"{Colors.OKBLUE}🔍 Checking current status...{Colors.ENDC}")
    frontend_ok = check_health("https://jobsprint-frontend.vercel.app", "Frontend")
    backend_ok = check_health("https://web-production-f50b3.up.railway.app/health", "Backend")
    
    if frontend_ok and backend_ok:
        print(f"\n{Colors.OKGREEN}✅ All services are healthy!{Colors.ENDC}")
        print("Try the Sign Up button now: https://jobsprint-frontend.vercel.app")
        return
    
    print(f"\n{Colors.WARNING}🔧 Issues detected. Attempting fixes...{Colors.ENDC}")
    
    # Method 1: Try GitHub Actions trigger
    print(f"\n{Colors.OKBLUE}📋 Method 1: GitHub Actions{Colors.ENDC}")
    print("1. Go to your GitHub repo → Actions tab")
    print("2. Click 'Deploy JobSprint - Full Stack Sync'")
    print("3. Click 'Run workflow' → 'Run workflow'")
    print("4. Wait 5-10 minutes for completion")
    
    # Method 2: Manual commands
    print(f"\n{Colors.OKBLUE}🛠️ Method 2: Manual Commands{Colors.ENDC}")
    
    # Check if CLIs are available
    vercel_available = run_command("vercel --version")[0]
    railway_available = run_command("railway --version")[0]
    
    if vercel_available:
        print("Frontend (Vercel):")
        print("  cd frontend && vercel --prod")
    else:
        print("Frontend: Install Vercel CLI first: npm i -g vercel")
    
    if railway_available:
        print("Backend (Railway):")
        print("  railway up")
    else:
        print("Backend: Install Railway CLI: curl -fsSL https://railway.app/install.sh | sh")
    
    # Method 3: Direct links
    print(f"\n{Colors.OKBLUE}🔗 Method 3: Direct Dashboard Links{Colors.ENDC}")
    print("Railway: https://railway.app/dashboard → Your project → Deploy")
    print("Vercel: https://vercel.com/dashboard → Your project → Redeploy")
    
    # Quick test
    print(f"\n{Colors.OKBLUE}⚡ Quick Test{Colors.ENDC}")
    print("After any deployment method, test these:")
    print("• Sign Up: https://jobsprint-frontend.vercel.app")
    print("• Admin Login: admin@jobsprint.com / admin123")
    print("• API Health: https://web-production-f50b3.up.railway.app/health")
    
    print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}💡 TIP: Use the full CI/CD setup for automatic syncing!{Colors.ENDC}")
    print("Run: python setup_cicd.py")
    print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")

if __name__ == "__main__":
    main()
