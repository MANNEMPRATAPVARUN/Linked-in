#!/usr/bin/env python3
"""
Vercel Deployment Script for JobSprint Frontend
Automates the deployment process to Vercel
"""

import os
import json
import subprocess
import sys

def check_requirements():
    """Check if all requirements are met for deployment"""
    print("🔍 Checking Vercel deployment requirements...")
    
    # Check if frontend directory exists
    if not os.path.exists('frontend'):
        print("❌ Frontend directory not found")
        return False
    
    # Check if required files exist
    required_files = [
        'frontend/index.html',
        'frontend/dashboard.html',
        'frontend/styles.css',
        'frontend/script.js',
        'frontend/dashboard.js',
        'frontend/vercel.json'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ All requirements met")
    return True

def create_package_json():
    """Create package.json for Vercel deployment"""
    print("📝 Creating package.json for Vercel...")
    
    package_json = {
        "name": "jobsprint-frontend",
        "version": "1.0.0",
        "description": "JobSprint Ultra-Recent Job Automation Frontend",
        "main": "index.html",
        "scripts": {
            "build": "echo 'Static site - no build required'",
            "start": "echo 'Static site - no start command'"
        },
        "keywords": [
            "job-automation",
            "linkedin-scraper",
            "canada-jobs",
            "ultra-recent-filtering",
            "job-search"
        ],
        "author": "JobSprint Team",
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "https://github.com/MANNEMPRATAPVARUN/Linked-in.git"
        }
    }
    
    with open('frontend/package.json', 'w') as f:
        json.dump(package_json, f, indent=2)
    
    print("✅ package.json created")
    return True

def create_readme():
    """Create README for frontend"""
    print("📝 Creating frontend README...")
    
    readme_content = """# JobSprint Frontend

Ultra-recent job automation system frontend built with Bootstrap 5 and vanilla JavaScript.

## Features

- 🚀 Ultra-recent job filtering (5-10 minutes)
- 🇨🇦 Canada-specific location optimization
- 👥 Multi-user dashboard
- 📊 Real-time job discovery
- 📱 Mobile-responsive design
- ⚡ Fast static site deployment

## Deployment

This frontend is deployed on Vercel and connects to the Railway backend API.

### Live URLs

- **Frontend**: https://jobsprint.vercel.app
- **Backend API**: https://jobsprint-api.railway.app

## Local Development

1. Open `index.html` in a web browser
2. For API integration, update `CONFIG.API_BASE_URL` in `script.js`
3. Set `CONFIG.DEMO_MODE = false` when API is ready

## Architecture

```
Frontend (Vercel) → API (Railway) → Database (Supabase)
     ↓                    ↓              ↓
Static Files         Business Logic   Data Storage
Global CDN          Background Jobs   Real-time Updates
Auto HTTPS          Email System     User Management
```

## Technologies

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Deployment**: Vercel
- **CDN**: Global edge network

## Configuration

Update `script.js` with your Railway API URL:

```javascript
const CONFIG = {
    API_BASE_URL: 'https://your-railway-app.railway.app/api',
    DEMO_MODE: false
};
```
"""
    
    with open('frontend/README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.md created")
    return True

def update_api_config():
    """Update API configuration for production"""
    print("🔧 Updating API configuration...")
    
    script_js_path = 'frontend/script.js'
    
    try:
        with open(script_js_path, 'r') as f:
            content = f.read()
        
        # Update the API URL placeholder
        updated_content = content.replace(
            "API_BASE_URL: 'https://your-railway-app.railway.app/api'",
            "API_BASE_URL: 'https://jobsprint-api.railway.app/api'"
        )
        
        with open(script_js_path, 'w') as f:
            f.write(updated_content)
        
        print("✅ API configuration updated")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to update API config: {e}")
        return False

def create_vercel_config():
    """Update Vercel configuration"""
    print("🔧 Updating Vercel configuration...")
    
    vercel_config = {
        "version": 2,
        "name": "jobsprint-frontend",
        "builds": [
            {
                "src": "**/*",
                "use": "@vercel/static"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/$1"
            }
        ],
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {
                        "key": "X-Content-Type-Options",
                        "value": "nosniff"
                    },
                    {
                        "key": "X-Frame-Options",
                        "value": "DENY"
                    },
                    {
                        "key": "X-XSS-Protection",
                        "value": "1; mode=block"
                    },
                    {
                        "key": "Cache-Control",
                        "value": "public, max-age=31536000, immutable"
                    }
                ]
            }
        ],
        "rewrites": [
            {
                "source": "/api/(.*)",
                "destination": "https://jobsprint-api.railway.app/api/$1"
            }
        ]
    }
    
    with open('frontend/vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print("✅ Vercel configuration updated")
    return True

def commit_frontend_files():
    """Commit frontend files to git"""
    print("📦 Committing frontend files...")
    
    try:
        # Add frontend files
        subprocess.run(['git', 'add', 'frontend/', 'deploy_vercel.py'], check=True)
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 
                       '🎨 Add Vercel Frontend Deployment\n\n- Modern responsive frontend with Bootstrap 5\n- Ultra-recent job search interface\n- Canada location optimization UI\n- Real-time dashboard with job management\n- Mobile-responsive design\n- Vercel deployment configuration\n- API integration ready'], 
                      check=True)
        
        print("✅ Frontend files committed to git")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit failed: {e}")
        return False

def display_deployment_instructions():
    """Display step-by-step deployment instructions"""
    print("\n" + "="*60)
    print("🎨 VERCEL FRONTEND DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 STEP 1: DEPLOY TO VERCEL")
    print("1. Go to: https://vercel.com")
    print("2. Sign in with GitHub")
    print("3. Click 'New Project'")
    print("4. Import your 'Linked-in' repository")
    print("5. Set Root Directory to: 'frontend'")
    print("6. Click 'Deploy'")
    
    print("\n📋 STEP 2: CONFIGURE CUSTOM DOMAIN (OPTIONAL)")
    print("1. In Vercel dashboard, go to your project")
    print("2. Click 'Settings' → 'Domains'")
    print("3. Add your custom domain")
    print("4. Follow DNS configuration instructions")
    
    print("\n📋 STEP 3: CONNECT TO RAILWAY API")
    print("1. Get your Railway API URL")
    print("2. Update frontend/script.js:")
    print("   - Change API_BASE_URL to your Railway URL")
    print("   - Set DEMO_MODE to false")
    print("3. Redeploy to Vercel")
    
    print("\n📋 STEP 4: TEST DEPLOYMENT")
    print("1. Visit your Vercel app URL")
    print("2. Test the homepage and navigation")
    print("3. Test login functionality")
    print("4. Test job search (demo mode)")
    
    print("\n🎯 YOUR FRONTEND WILL BE AVAILABLE AT:")
    print("   https://jobsprint-frontend.vercel.app")
    print("   https://your-custom-domain.com (if configured)")
    
    print("\n🔗 ARCHITECTURE OVERVIEW:")
    print("   Frontend (Vercel) → API (Railway) → Database (Supabase)")
    print("   ↓                    ↓              ↓")
    print("   Static Files         Business Logic Data Storage")
    print("   Global CDN          Background Jobs Real-time Updates")
    
    print("\n✅ FRONTEND DEPLOYMENT READY!")
    print("Your JobSprint frontend is ready for Vercel deployment!")

def main():
    """Main deployment preparation function"""
    print("🎨 JobSprint Vercel Frontend Deployment Preparation")
    print("="*55)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements not met. Please fix issues and try again.")
        sys.exit(1)
    
    # Create deployment files
    create_package_json()
    create_readme()
    update_api_config()
    create_vercel_config()
    
    # Commit files
    if commit_frontend_files():
        print("✅ All frontend files prepared and committed")
    else:
        print("⚠️ Files prepared but git commit failed")
    
    # Display instructions
    display_deployment_instructions()
    
    print("\n🎉 Vercel frontend deployment preparation complete!")
    print("Follow the instructions above to deploy to Vercel.")

if __name__ == "__main__":
    main()
