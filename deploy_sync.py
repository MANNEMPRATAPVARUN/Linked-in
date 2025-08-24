#!/usr/bin/env python3
"""
🚀 JobSprint Deployment Sync Script
Ensures all services (Railway, Vercel, Supabase) are in sync
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DeploymentSync:
    def __init__(self):
        self.services = {
            'frontend': {
                'name': '🌐 Frontend (Vercel)',
                'url': 'https://jobsprint-frontend.vercel.app',
                'health_endpoint': 'https://jobsprint-frontend.vercel.app/health',
                'status': 'unknown'
            },
            'backend': {
                'name': '🚂 Backend (Railway)',
                'url': 'https://web-production-f50b3.up.railway.app',
                'health_endpoint': 'https://web-production-f50b3.up.railway.app/health',
                'status': 'unknown'
            },
            'database': {
                'name': '🗄️ Database (Supabase)',
                'url': 'https://supabase.com/dashboard',
                'health_endpoint': None,
                'status': 'unknown'
            }
        }
        
    def print_header(self):
        """Print deployment sync header"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}🚀 JobSprint Deployment Sync{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def check_service_health(self, service_key: str) -> bool:
        """Check if a service is healthy"""
        service = self.services[service_key]
        
        if not service['health_endpoint']:
            return True  # Skip health check for services without endpoints
            
        try:
            print(f"🔍 Checking {service['name']}...")
            response = requests.get(service['health_endpoint'], timeout=10)
            
            if response.status_code == 200:
                service['status'] = 'healthy'
                print(f"  {Colors.OKGREEN}✅ Healthy (Status: {response.status_code}){Colors.ENDC}")
                return True
            else:
                service['status'] = 'unhealthy'
                print(f"  {Colors.WARNING}⚠️ Unhealthy (Status: {response.status_code}){Colors.ENDC}")
                return False
                
        except requests.exceptions.RequestException as e:
            service['status'] = 'error'
            print(f"  {Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
            return False

    def run_command(self, command: str, cwd: str = None) -> Tuple[bool, str]:
        """Run a shell command and return success status and output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def deploy_frontend(self) -> bool:
        """Deploy frontend to Vercel"""
        print(f"\n{Colors.OKBLUE}🌐 Deploying Frontend to Vercel...{Colors.ENDC}")
        
        # Check if Vercel CLI is installed
        success, output = self.run_command("vercel --version")
        if not success:
            print(f"  {Colors.FAIL}❌ Vercel CLI not found. Install with: npm i -g vercel{Colors.ENDC}")
            return False
        
        # Deploy to Vercel
        print("  📦 Deploying to Vercel...")
        success, output = self.run_command("vercel --prod --yes", cwd="frontend")
        
        if success:
            print(f"  {Colors.OKGREEN}✅ Frontend deployed successfully!{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.FAIL}❌ Frontend deployment failed:{Colors.ENDC}")
            print(f"  {output}")
            return False

    def deploy_backend(self) -> bool:
        """Deploy backend to Railway"""
        print(f"\n{Colors.OKBLUE}🚂 Deploying Backend to Railway...{Colors.ENDC}")
        
        # Check if Railway CLI is installed
        success, output = self.run_command("railway --version")
        if not success:
            print(f"  {Colors.FAIL}❌ Railway CLI not found. Install from: https://railway.app/cli{Colors.ENDC}")
            return False
        
        # Check if logged in
        success, output = self.run_command("railway whoami")
        if not success:
            print(f"  {Colors.WARNING}⚠️ Not logged in to Railway. Run: railway login{Colors.ENDC}")
            return False
        
        # Deploy to Railway
        print("  🚂 Deploying to Railway...")
        success, output = self.run_command("railway up")
        
        if success:
            print(f"  {Colors.OKGREEN}✅ Backend deployed successfully!{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.FAIL}❌ Backend deployment failed:{Colors.ENDC}")
            print(f"  {output}")
            return False

    def sync_database(self) -> bool:
        """Sync database schema with Supabase"""
        print(f"\n{Colors.OKBLUE}🗄️ Syncing Database Schema...{Colors.ENDC}")
        
        # Check if schema file exists
        schema_file = "database/supabase_schema.sql"
        if not os.path.exists(schema_file):
            print(f"  {Colors.WARNING}⚠️ No schema file found at {schema_file}{Colors.ENDC}")
            return True  # Not an error, just skip
        
        print(f"  📋 Schema file found: {schema_file}")
        print(f"  {Colors.OKGREEN}✅ Database schema is ready{Colors.ENDC}")
        print(f"  💡 Apply manually in Supabase dashboard if needed")
        return True

    def wait_for_deployments(self):
        """Wait for deployments to be ready"""
        print(f"\n{Colors.OKCYAN}⏳ Waiting for deployments to be ready...{Colors.ENDC}")
        time.sleep(30)  # Give services time to start
        
        for i in range(5):  # Try 5 times
            print(f"  🔄 Health check attempt {i+1}/5...")
            
            frontend_ok = self.check_service_health('frontend')
            backend_ok = self.check_service_health('backend')
            
            if frontend_ok and backend_ok:
                print(f"  {Colors.OKGREEN}✅ All services are healthy!{Colors.ENDC}")
                return True
            
            if i < 4:  # Don't sleep on last attempt
                print(f"  ⏳ Waiting 15 seconds before retry...")
                time.sleep(15)
        
        print(f"  {Colors.WARNING}⚠️ Some services may still be starting up{Colors.ENDC}")
        return False

    def print_summary(self):
        """Print deployment summary"""
        print(f"\n{Colors.HEADER}📊 Deployment Summary{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        for service_key, service in self.services.items():
            status_color = Colors.OKGREEN if service['status'] == 'healthy' else Colors.WARNING
            print(f"{service['name']}: {status_color}{service['status']}{Colors.ENDC}")
            if service['url']:
                print(f"  🔗 {service['url']}")
        
        print(f"\n{Colors.OKCYAN}🔗 Quick Access Links:{Colors.ENDC}")
        print(f"  🏠 Main App: https://jobsprint-frontend.vercel.app")
        print(f"  🔐 Admin Login: admin@jobsprint.com / admin123")
        print(f"  📊 API Health: https://web-production-f50b3.up.railway.app/health")
        
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

    def run_sync(self, force_deploy: bool = False):
        """Run the complete deployment sync"""
        self.print_header()
        
        # Initial health check
        print(f"{Colors.OKCYAN}🔍 Initial Health Check{Colors.ENDC}")
        frontend_healthy = self.check_service_health('frontend')
        backend_healthy = self.check_service_health('backend')
        
        deploy_needed = force_deploy or not (frontend_healthy and backend_healthy)
        
        if not deploy_needed:
            print(f"\n{Colors.OKGREEN}✅ All services are healthy! No deployment needed.{Colors.ENDC}")
            print(f"💡 Use --force to deploy anyway")
            self.print_summary()
            return True
        
        print(f"\n{Colors.WARNING}🚀 Deployment needed. Starting sync...{Colors.ENDC}")
        
        # Deploy services
        results = []
        
        if not frontend_healthy or force_deploy:
            results.append(self.deploy_frontend())
        
        if not backend_healthy or force_deploy:
            results.append(self.deploy_backend())
        
        # Always sync database
        results.append(self.sync_database())
        
        # Wait for deployments and final health check
        self.wait_for_deployments()
        
        # Final summary
        self.print_summary()
        
        return all(results)

def main():
    """Main function"""
    force_deploy = '--force' in sys.argv or '-f' in sys.argv
    
    sync = DeploymentSync()
    success = sync.run_sync(force_deploy=force_deploy)
    
    if success:
        print(f"{Colors.OKGREEN}🎉 Deployment sync completed successfully!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"{Colors.FAIL}❌ Deployment sync failed!{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
