#!/usr/bin/env python3
"""
🔧 JobSprint CI/CD Setup Helper
Helps collect and verify all required tokens and IDs for automated deployment
"""

import os
import sys
import json
import requests
from typing import Dict, Optional

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class CICDSetup:
    def __init__(self):
        self.secrets = {}
        self.config_file = 'cicd_config.json'
        
    def print_header(self):
        """Print setup header"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}🔧 JobSprint CI/CD Setup Helper{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print("This tool will help you collect all required tokens and IDs")
        print("for automated deployment across Railway, Vercel, and Supabase.\n")

    def get_input(self, prompt: str, secret: bool = False) -> str:
        """Get user input with optional masking"""
        if secret:
            import getpass
            return getpass.getpass(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}")
        else:
            return input(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}")

    def verify_railway_token(self, token: str) -> bool:
        """Verify Railway token is valid"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('https://backboard.railway.app/graphql', 
                                  headers=headers, timeout=10)
            return response.status_code != 401
        except:
            return False

    def verify_vercel_token(self, token: str) -> bool:
        """Verify Vercel token is valid"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('https://api.vercel.com/v2/user', 
                                  headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False

    def verify_supabase_token(self, token: str) -> bool:
        """Verify Supabase token is valid"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('https://api.supabase.com/v1/projects', 
                                  headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False

    def collect_railway_secrets(self):
        """Collect Railway secrets"""
        print(f"\n{Colors.OKBLUE}🚂 Railway Configuration{Colors.ENDC}")
        print("1. Go to https://railway.app/dashboard")
        print("2. Click your profile → Account Settings → Tokens")
        print("3. Create a new token")
        
        token = self.get_input("Enter your Railway token: ", secret=True)
        
        if self.verify_railway_token(token):
            print(f"{Colors.OKGREEN}✅ Railway token verified!{Colors.ENDC}")
            self.secrets['RAILWAY_TOKEN'] = token
        else:
            print(f"{Colors.FAIL}❌ Invalid Railway token{Colors.ENDC}")
            return False
        
        print("\n4. Go to your JobSprint project → Settings")
        project_id = self.get_input("Enter your Railway Project ID: ")
        service_id = self.get_input("Enter your Railway Service ID: ")
        
        self.secrets['RAILWAY_PROJECT_ID'] = project_id
        self.secrets['RAILWAY_SERVICE_ID'] = service_id
        
        return True

    def collect_vercel_secrets(self):
        """Collect Vercel secrets"""
        print(f"\n{Colors.OKBLUE}🌐 Vercel Configuration{Colors.ENDC}")
        print("1. Go to https://vercel.com/dashboard")
        print("2. Settings → Tokens → Create new token")
        
        token = self.get_input("Enter your Vercel token: ", secret=True)
        
        if self.verify_vercel_token(token):
            print(f"{Colors.OKGREEN}✅ Vercel token verified!{Colors.ENDC}")
            self.secrets['VERCEL_TOKEN'] = token
        else:
            print(f"{Colors.FAIL}❌ Invalid Vercel token{Colors.ENDC}")
            return False
        
        print("\n3. Go to your JobSprint project → Settings → General")
        project_id = self.get_input("Enter your Vercel Project ID: ")
        
        print("\n4. Account Settings → Copy Team ID")
        org_id = self.get_input("Enter your Vercel Org/Team ID: ")
        
        self.secrets['VERCEL_PROJECT_ID'] = project_id
        self.secrets['VERCEL_ORG_ID'] = org_id
        
        return True

    def collect_supabase_secrets(self):
        """Collect Supabase secrets"""
        print(f"\n{Colors.OKBLUE}🗄️ Supabase Configuration{Colors.ENDC}")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Account → Access Tokens → Create new token")
        
        token = self.get_input("Enter your Supabase access token: ", secret=True)
        
        if self.verify_supabase_token(token):
            print(f"{Colors.OKGREEN}✅ Supabase token verified!{Colors.ENDC}")
            self.secrets['SUPABASE_ACCESS_TOKEN'] = token
        else:
            print(f"{Colors.FAIL}❌ Invalid Supabase token{Colors.ENDC}")
            return False
        
        print("\n3. Go to your project → Settings → General → Reference ID")
        project_ref = self.get_input("Enter your Supabase Project Reference: ")
        
        self.secrets['SUPABASE_PROJECT_REF'] = project_ref
        
        return True

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.secrets, f, indent=2)
        print(f"\n{Colors.OKGREEN}💾 Configuration saved to {self.config_file}{Colors.ENDC}")

    def generate_github_secrets_guide(self):
        """Generate GitHub secrets setup guide"""
        print(f"\n{Colors.HEADER}📋 GitHub Secrets Setup{Colors.ENDC}")
        print("Copy these secrets to your GitHub repository:")
        print("Go to: Settings → Secrets and variables → Actions → New repository secret\n")
        
        for key, value in self.secrets.items():
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"{Colors.OKCYAN}{key}{Colors.ENDC} = {masked_value}")
        
        print(f"\n{Colors.WARNING}⚠️ Keep these values secure and never commit them to your repository!{Colors.ENDC}")

    def test_deployment_endpoints(self):
        """Test current deployment endpoints"""
        print(f"\n{Colors.OKBLUE}🧪 Testing Current Deployments{Colors.ENDC}")
        
        endpoints = {
            'Frontend': 'https://jobsprint-frontend.vercel.app',
            'Backend': 'https://web-production-f50b3.up.railway.app/health'
        }
        
        for name, url in endpoints.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"  {Colors.OKGREEN}✅ {name}: Healthy{Colors.ENDC}")
                else:
                    print(f"  {Colors.WARNING}⚠️ {name}: Status {response.status_code}{Colors.ENDC}")
            except:
                print(f"  {Colors.FAIL}❌ {name}: Unreachable{Colors.ENDC}")

    def run_setup(self):
        """Run the complete setup process"""
        self.print_header()
        
        # Collect all secrets
        if not self.collect_railway_secrets():
            return False
        
        if not self.collect_vercel_secrets():
            return False
        
        if not self.collect_supabase_secrets():
            return False
        
        # Save configuration
        self.save_config()
        
        # Generate GitHub secrets guide
        self.generate_github_secrets_guide()
        
        # Test current deployments
        self.test_deployment_endpoints()
        
        # Final instructions
        print(f"\n{Colors.HEADER}🎯 Next Steps:{Colors.ENDC}")
        print("1. Add all secrets to your GitHub repository")
        print("2. Push your code to trigger the first automated deployment")
        print("3. Monitor the Actions tab for deployment progress")
        print("4. Use 'python deploy_sync.py' for manual deployments")
        
        print(f"\n{Colors.OKGREEN}🎉 CI/CD setup completed successfully!{Colors.ENDC}")
        return True

def main():
    """Main function"""
    setup = CICDSetup()
    success = setup.run_setup()
    
    if not success:
        print(f"\n{Colors.FAIL}❌ Setup failed. Please try again.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
