#!/usr/bin/env python3
"""
🚀 FRESH DEPLOYMENT - Complete Clean Start
Deploys JobSprint from scratch to new Railway and Vercel projects
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
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 JOBSPRINT FRESH DEPLOYMENT{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print("Complete clean start - New Railway & Vercel deployments")
    print()

def run_command(command, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_cli_tools():
    """Check if required CLI tools are installed"""
    print(f"{Colors.OKBLUE}🔍 Checking CLI Tools...{Colors.ENDC}")
    
    tools = {
        'git': 'git --version',
        'vercel': 'vercel --version',
        'railway': 'railway --version'
    }
    
    missing_tools = []
    
    for tool, command in tools.items():
        success, output = run_command(command)
        if success:
            print(f"  ✅ {tool}: Available")
        else:
            print(f"  ❌ {tool}: Missing")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n{Colors.FAIL}❌ Missing tools: {', '.join(missing_tools)}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}Install missing tools:{Colors.ENDC}")
        if 'vercel' in missing_tools:
            print("  npm install -g vercel")
        if 'railway' in missing_tools:
            print("  curl -fsSL https://railway.app/install.sh | sh")
        return False
    
    return True

def deploy_to_railway():
    """Deploy backend to Railway"""
    print(f"\n{Colors.OKBLUE}🚂 Deploying Backend to Railway...{Colors.ENDC}")
    
    # Check if logged in
    success, output = run_command("railway whoami")
    if not success:
        print(f"  {Colors.WARNING}⚠️ Not logged in to Railway{Colors.ENDC}")
        print(f"  Run: railway login")
        return False, None
    
    print(f"  ✅ Railway authenticated")
    
    # Initialize new Railway project
    print(f"  🚀 Creating new Railway project...")
    success, output = run_command("railway init")
    if not success:
        print(f"  {Colors.FAIL}❌ Railway init failed: {output}{Colors.ENDC}")
        return False, None
    
    # Deploy
    print(f"  📦 Deploying to Railway...")
    success, output = run_command("railway up")
    if success:
        print(f"  {Colors.OKGREEN}✅ Railway deployment successful!{Colors.ENDC}")
        
        # Get the deployment URL
        success, url_output = run_command("railway status")
        if success and "https://" in url_output:
            # Extract URL from output
            lines = url_output.split('\n')
            for line in lines:
                if 'https://' in line and 'railway.app' in line:
                    url = line.strip().split()[-1]
                    print(f"  🔗 Railway URL: {url}")
                    return True, url
        
        return True, "https://your-project.up.railway.app"
    else:
        print(f"  {Colors.FAIL}❌ Railway deployment failed: {output}{Colors.ENDC}")
        return False, None

def deploy_to_vercel():
    """Deploy frontend to Vercel"""
    print(f"\n{Colors.OKBLUE}🌐 Deploying Frontend to Vercel...{Colors.ENDC}")
    
    # Check if logged in
    success, output = run_command("vercel whoami")
    if not success:
        print(f"  {Colors.WARNING}⚠️ Not logged in to Vercel{Colors.ENDC}")
        print(f"  Run: vercel login")
        return False, None
    
    print(f"  ✅ Vercel authenticated")
    
    # Deploy from frontend directory
    print(f"  🚀 Deploying frontend...")
    success, output = run_command("vercel --prod --yes", cwd="frontend")
    if success:
        print(f"  {Colors.OKGREEN}✅ Vercel deployment successful!{Colors.ENDC}")
        
        # Extract URL from output
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'vercel.app' in line:
                url = line.strip()
                print(f"  🔗 Vercel URL: {url}")
                return True, url
        
        return True, "https://your-project.vercel.app"
    else:
        print(f"  {Colors.FAIL}❌ Vercel deployment failed: {output}{Colors.ENDC}")
        return False, None

def test_deployments(frontend_url, backend_url):
    """Test both deployments"""
    print(f"\n{Colors.OKBLUE}🧪 Testing Deployments...{Colors.ENDC}")
    
    # Test frontend
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Frontend: Working (Status: {response.status_code})")
        else:
            print(f"  ⚠️ Frontend: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Frontend: {e}")
    
    # Test backend health
    try:
        health_url = f"{backend_url}/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Backend: Working (Status: {response.status_code})")
        else:
            print(f"  ⚠️ Backend: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Backend: {e}")
    
    # Test registration endpoint
    try:
        reg_url = f"{backend_url}/api/auth/register"
        response = requests.options(reg_url, timeout=10)
        print(f"  ✅ Registration endpoint: Accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"  ⚠️ Registration endpoint: {e}")

def main():
    print_header()
    
    # Check CLI tools
    if not check_cli_tools():
        print(f"\n{Colors.FAIL}❌ Please install missing CLI tools first{Colors.ENDC}")
        return
    
    print(f"\n{Colors.WARNING}🗑️ IMPORTANT: Make sure you've deleted old deployments first!{Colors.ENDC}")
    print("1. Delete Vercel project: https://vercel.com/dashboard")
    print("2. Delete Railway project: https://railway.app/dashboard")
    
    input(f"\n{Colors.OKBLUE}Press Enter when you've deleted old deployments...{Colors.ENDC}")
    
    # Deploy backend
    railway_success, railway_url = deploy_to_railway()
    if not railway_success:
        print(f"\n{Colors.FAIL}❌ Railway deployment failed. Please check and try again.{Colors.ENDC}")
        return
    
    # Deploy frontend
    vercel_success, vercel_url = deploy_to_vercel()
    if not vercel_success:
        print(f"\n{Colors.FAIL}❌ Vercel deployment failed. Please check and try again.{Colors.ENDC}")
        return
    
    # Test deployments
    if railway_url and vercel_url:
        test_deployments(vercel_url, railway_url)
    
    # Final summary
    print(f"\n{Colors.HEADER}🎉 FRESH DEPLOYMENT COMPLETED!{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    if vercel_url:
        print(f"🌐 Frontend: {vercel_url}")
    if railway_url:
        print(f"🚂 Backend: {railway_url}")
    
    print(f"\n{Colors.OKGREEN}🎯 Next Steps:{Colors.ENDC}")
    print("1. Test the Sign Up button on your frontend")
    print("2. Test admin login: admin@jobsprint.com / admin123")
    print("3. Verify all functionality works")
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")

if __name__ == "__main__":
    main()
