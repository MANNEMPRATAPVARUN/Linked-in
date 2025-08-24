#!/usr/bin/env python3
"""
Setup script for LinkedIn Job Automation System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    
    return True

def setup_chrome_driver():
    """Setup Chrome driver for Selenium"""
    print("🌐 Setting up Chrome driver...")
    
    try:
        # Install webdriver-manager for automatic driver management
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
        print("✅ Chrome driver setup completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ["logs", "data"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    return True

def main():
    """Main setup function"""
    print("🚀 LinkedIn Job Automation System Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation")
        return
    
    # Setup Chrome driver
    if not setup_chrome_driver():
        print("❌ Setup failed during Chrome driver setup")
        return
    
    # Create directories
    if not create_directories():
        print("❌ Setup failed during directory creation")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit config.json with your email settings and job preferences")
    print("2. For Gmail, create an App Password: https://support.google.com/accounts/answer/185833")
    print("3. Run: python src/main.py")
    print("\n⚡ Your job automation system will be ready to find opportunities!")

if __name__ == "__main__":
    main()
