#!/usr/bin/env python3
"""
Railway Deployment Script for JobSprint API
Automates the deployment process to Railway
"""

import os
import json
import subprocess
import sys

def check_requirements():
    """Check if all requirements are met for deployment"""
    print("🔍 Checking deployment requirements...")
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        print("❌ Git repository not initialized")
        return False
    
    # Check if required files exist
    required_files = [
        'api/app.py',
        'Procfile',
        'railway.json',
        'requirements.txt',
        'production.env.example'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ All requirements met")
    return True

def create_railway_env_vars():
    """Create environment variables configuration for Railway"""
    print("📝 Creating Railway environment variables...")
    
    env_vars = {
        "FLASK_ENV": "production",
        "FLASK_DEBUG": "False",
        "SECRET_KEY": "CHANGE_THIS_SECRET_KEY_IN_RAILWAY_DASHBOARD",
        "SUPABASE_URL": "https://eazuowqlkqijpmcimkcz.supabase.co",
        "SUPABASE_ANON_KEY": "GET_FROM_SUPABASE_DASHBOARD",
        "SUPABASE_SERVICE_KEY": "GET_FROM_SUPABASE_DASHBOARD",
        "EMAIL_SMTP_SERVER": "smtp.gmail.com",
        "EMAIL_SMTP_PORT": "587",
        "EMAIL_USERNAME": "your_gmail@gmail.com",
        "EMAIL_PASSWORD": "your_gmail_app_password",
        "SYSTEM_NAME": "JobSprint Ultra-Recent Automation",
        "ULTRA_RECENT_MODE": "true",
        "CANADA_OPTIMIZATION": "true",
        "DEFAULT_SEARCH_FREQUENCY": "5",
        "LINKEDIN_RATE_LIMIT": "10",
        "EMAIL_RATE_LIMIT": "50",
        "LOG_LEVEL": "INFO"
    }
    
    # Save to file for reference
    with open('railway_env_vars.json', 'w') as f:
        json.dump(env_vars, f, indent=2)
    
    print("✅ Environment variables configuration saved to railway_env_vars.json")
    print("\n📋 IMPORTANT: Set these environment variables in Railway dashboard:")
    for key, value in env_vars.items():
        print(f"   {key}={value}")
    
    return env_vars

def prepare_deployment():
    """Prepare files for Railway deployment"""
    print("🔧 Preparing deployment files...")
    
    # Create .railwayignore file
    railwayignore_content = """
# Railway ignore file
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/

# Local development files
.env
*.db
*.sqlite
*.sqlite3
logs/
test_*.py
*_test.py

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# External repositories
JobSpy/
Job-apply-AI-agent/

# Local config files
config.json
supabase_config.json
"""
    
    with open('.railwayignore', 'w') as f:
        f.write(railwayignore_content.strip())
    
    print("✅ Created .railwayignore file")
    
    # Create runtime.txt for Python version
    with open('runtime.txt', 'w') as f:
        f.write('python-3.11.0')
    
    print("✅ Created runtime.txt file")
    
    return True

def commit_deployment_files():
    """Commit deployment files to git"""
    print("📦 Committing deployment files...")
    
    try:
        # Add deployment files
        subprocess.run(['git', 'add', 'api/', 'Procfile', 'railway.json', 
                       'requirements.txt', 'production.env.example', 
                       'deploy_railway.py', '.railwayignore', 'runtime.txt',
                       'railway_env_vars.json'], check=True)
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 
                       '🚀 Add Railway deployment configuration\n\n- Flask API backend ready for production\n- Supabase integration configured\n- Environment variables template\n- Railway deployment files'], 
                      check=True)
        
        print("✅ Deployment files committed to git")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit failed: {e}")
        return False

def display_deployment_instructions():
    """Display step-by-step deployment instructions"""
    print("\n" + "="*60)
    print("🚀 RAILWAY DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 STEP 1: PREPARE SUPABASE API KEYS")
    print("1. Go to: https://supabase.com/dashboard/project/eazuowqlkqijpmcimkcz/settings/api")
    print("2. Copy the 'anon public' key")
    print("3. Copy the 'service_role' key (keep this secret!)")
    
    print("\n📋 STEP 2: DEPLOY TO RAILWAY")
    print("1. Go to: https://railway.app")
    print("2. Sign in with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Select your 'Linked-in' repository")
    print("5. Railway will auto-detect Python and deploy")
    
    print("\n📋 STEP 3: SET ENVIRONMENT VARIABLES")
    print("1. In Railway dashboard, go to your project")
    print("2. Click 'Variables' tab")
    print("3. Add these environment variables:")
    
    # Read the env vars we created
    if os.path.exists('railway_env_vars.json'):
        with open('railway_env_vars.json', 'r') as f:
            env_vars = json.load(f)
        
        for key, value in env_vars.items():
            if 'GET_FROM_SUPABASE' in value or 'CHANGE_THIS' in value:
                print(f"   🔑 {key}=<REPLACE_WITH_ACTUAL_VALUE>")
            else:
                print(f"   ✅ {key}={value}")
    
    print("\n📋 STEP 4: VERIFY DEPLOYMENT")
    print("1. Check Railway logs for successful startup")
    print("2. Visit your Railway app URL")
    print("3. Test /health endpoint")
    print("4. Test API endpoints")
    
    print("\n🎯 YOUR API WILL BE AVAILABLE AT:")
    print("   https://your-app-name.railway.app")
    print("   https://your-app-name.railway.app/health")
    print("   https://your-app-name.railway.app/api/locations/canada")
    
    print("\n✅ DEPLOYMENT READY!")
    print("Your JobSprint API backend is ready for Railway deployment!")

def main():
    """Main deployment preparation function"""
    print("🚀 JobSprint Railway Deployment Preparation")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements not met. Please fix issues and try again.")
        sys.exit(1)
    
    # Create environment variables
    create_railway_env_vars()
    
    # Prepare deployment files
    prepare_deployment()
    
    # Commit files
    if commit_deployment_files():
        print("✅ All deployment files prepared and committed")
    else:
        print("⚠️ Files prepared but git commit failed")
    
    # Display instructions
    display_deployment_instructions()
    
    print("\n🎉 Railway deployment preparation complete!")
    print("Follow the instructions above to deploy to Railway.")

if __name__ == "__main__":
    main()
