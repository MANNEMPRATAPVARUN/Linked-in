#!/usr/bin/env python3
"""
🚀 MANUAL FRESH DEPLOYMENT GUIDE
Step-by-step guide for fresh deployment
"""

import os
import sys
import time
import requests

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKBLUE = '\033[94m'
    HEADER = '\033[95m'
    ENDC = '\033[0m'

def print_header():
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 JOBSPRINT MANUAL FRESH DEPLOYMENT{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print("Step-by-step guide for complete fresh start")
    print()

def print_step(step_num, title, commands, notes=None):
    print(f"\n{Colors.OKBLUE}STEP {step_num}: {title}{Colors.ENDC}")
    print("-" * 50)
    
    for i, command in enumerate(commands, 1):
        print(f"{i}. {Colors.WARNING}{command}{Colors.ENDC}")
    
    if notes:
        print(f"\n{Colors.OKGREEN}📝 Notes:{Colors.ENDC}")
        for note in notes:
            print(f"   • {note}")
    
    input(f"\n{Colors.OKBLUE}Press Enter when completed...{Colors.ENDC}")

def test_deployment(frontend_url, backend_url):
    """Test deployments"""
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
    
    # Test backend
    try:
        health_url = f"{backend_url}/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Backend: Working (Status: {response.status_code})")
        else:
            print(f"  ⚠️ Backend: Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Backend: {e}")

def main():
    print_header()
    
    # Step 1: Delete old deployments
    print_step(1, "DELETE OLD DEPLOYMENTS", [
        "Go to https://vercel.com/dashboard",
        "Find your JobSprint project → Settings → General → Delete Project",
        "Go to https://railway.app/dashboard", 
        "Find your JobSprint project → Settings → Danger → Delete Project"
    ], [
        "Make sure both old deployments are completely deleted",
        "This prevents conflicts with new deployments"
    ])
    
    # Step 2: Login to services
    print_step(2, "LOGIN TO SERVICES", [
        "vercel login",
        "railway login"
    ], [
        "Follow the browser prompts to authenticate",
        "Make sure both logins are successful"
    ])
    
    # Step 3: Deploy backend to Railway
    print_step(3, "DEPLOY BACKEND TO RAILWAY", [
        "railway init",
        "railway up"
    ], [
        "This creates a new Railway project and deploys your backend",
        "Note down the Railway URL that appears after deployment",
        "It should look like: https://web-production-xxxxx.up.railway.app"
    ])
    
    # Get Railway URL
    railway_url = input(f"\n{Colors.OKBLUE}Enter your Railway URL: {Colors.ENDC}")
    if not railway_url.startswith('http'):
        railway_url = f"https://{railway_url}"
    
    # Step 4: Deploy frontend to Vercel
    print_step(4, "DEPLOY FRONTEND TO VERCEL", [
        "cd frontend",
        "vercel --prod"
    ], [
        "This creates a new Vercel project and deploys your frontend",
        "Note down the Vercel URL that appears after deployment",
        "It should look like: https://your-project.vercel.app"
    ])
    
    # Get Vercel URL
    vercel_url = input(f"\n{Colors.OKBLUE}Enter your Vercel URL: {Colors.ENDC}")
    if not vercel_url.startswith('http'):
        vercel_url = f"https://{vercel_url}"
    
    # Step 5: Update frontend API configuration
    print_step(5, "UPDATE API CONFIGURATION", [
        f"Update frontend/vercel.json - Change API destination to: {railway_url}",
        "git add .",
        "git commit -m 'Update API endpoint for new Railway deployment'",
        "git push origin main",
        "vercel --prod (redeploy frontend with new API endpoint)"
    ], [
        "This connects your frontend to the new backend",
        "The frontend needs to know the new Railway URL"
    ])
    
    # Test deployments
    if railway_url and vercel_url:
        test_deployment(vercel_url, railway_url)
    
    # Final summary
    print(f"\n{Colors.HEADER}🎉 FRESH DEPLOYMENT COMPLETED!{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    print(f"🌐 Frontend: {vercel_url}")
    print(f"🚂 Backend: {railway_url}")
    
    print(f"\n{Colors.OKGREEN}🎯 Test Your App:{Colors.ENDC}")
    print(f"1. Go to: {vercel_url}")
    print("2. Click 'Sign Up' button")
    print("3. Try admin login: admin@jobsprint.com / admin123")
    
    print(f"\n{Colors.WARNING}📝 Save These URLs:{Colors.ENDC}")
    print(f"Frontend: {vercel_url}")
    print(f"Backend: {railway_url}")
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")

if __name__ == "__main__":
    main()
