#!/usr/bin/env python3
"""
Email Setup and Troubleshooting Tool for LinkedIn Job Automation
"""

import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from setup_logging import setup_comprehensive_logging, log_email_debug_info

def test_email_configuration():
    """Test and diagnose email configuration issues"""
    
    # Setup logging
    setup_comprehensive_logging()
    email_logger = logging.getLogger('email')
    
    print("🔧 LinkedIn Job Automation - Email Configuration Tester")
    print("=" * 60)
    
    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        email_config = config.get('email', {})
        log_email_debug_info(email_config)
        
        print("📧 Current Email Configuration:")
        print(f"   Sender: {email_config.get('sender_email', 'Not configured')}")
        print(f"   Recipients: {len(email_config.get('recipient_emails', []))} emails")
        print(f"   Password: {'✅ Set' if email_config.get('sender_password') else '❌ Not set'}")
        
        # Check password format
        password = email_config.get('sender_password', '')
        if password:
            if 'P@ss' in password or len(password) < 16:
                print("\n⚠️  ISSUE DETECTED: You're using your regular Gmail password!")
                print("🔧 SOLUTION: You need to use a Gmail App Password instead.")
                print("\n📋 How to fix this:")
                print("1. Go to https://myaccount.google.com/security")
                print("2. Enable 2-Step Verification (if not already enabled)")
                print("3. Go to 'App passwords'")
                print("4. Generate a new app password for 'Mail'")
                print("5. Use that 16-character password in config.json")
                print("\n💡 App passwords look like: 'abcd efgh ijkl mnop' (16 characters)")
                
                email_logger.error("Regular Gmail password detected instead of App Password")
                return False
        
        # Test SMTP connection
        print("\n🔌 Testing SMTP connection...")
        email_logger.info("Testing SMTP connection")
        
        smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = email_config.get('smtp_port', 587)
        sender_email = email_config.get('sender_email')
        sender_password = email_config.get('sender_password')
        
        if not all([sender_email, sender_password]):
            print("❌ Email or password not configured")
            email_logger.error("Email or password not configured")
            return False
        
        # Create SMTP connection
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            print("✅ TLS connection established")
            email_logger.info("TLS connection established")
            
            # Test authentication
            try:
                server.login(sender_email, sender_password)
                print("✅ Authentication successful!")
                email_logger.info("SMTP authentication successful")
                
                # Send test email
                print("\n📧 Sending test email...")
                
                message = MIMEMultipart("alternative")
                message["Subject"] = "🧪 LinkedIn Job Automation - Email Test"
                message["From"] = sender_email
                message["To"] = sender_email  # Send to self for testing
                
                html_content = """
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #0077b5;">✅ Email Test Successful!</h2>
                    <p>Your LinkedIn Job Automation System email is working correctly.</p>
                    <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>🎯 System Status:</h3>
                        <ul>
                            <li>✅ SMTP Connection: Working</li>
                            <li>✅ Authentication: Successful</li>
                            <li>✅ Email Delivery: Functional</li>
                        </ul>
                    </div>
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Your email system is ready!</li>
                        <li>Run job searches to get real job alerts</li>
                        <li>Check your inbox for job notifications</li>
                    </ol>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        This is an automated test from your LinkedIn Job Automation System
                    </p>
                </body>
                </html>
                """
                
                part = MIMEText(html_content, "html")
                message.attach(part)
                
                server.sendmail(sender_email, [sender_email], message.as_string())
                print("✅ Test email sent successfully!")
                print(f"📬 Check your inbox: {sender_email}")
                email_logger.info("Test email sent successfully")
                
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ Authentication failed: {e}")
                print("\n🔧 TROUBLESHOOTING:")
                print("1. Make sure you're using a Gmail App Password, not your regular password")
                print("2. Check that 2-Step Verification is enabled on your Google account")
                print("3. Generate a new App Password if needed")
                email_logger.error(f"SMTP authentication failed: {e}")
                return False
                
    except FileNotFoundError:
        print("❌ config.json not found")
        email_logger.error("config.json file not found")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config.json")
        email_logger.error("Invalid JSON in config.json")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        email_logger.error(f"Unexpected error in email test: {e}")
        return False

def create_gmail_app_password_guide():
    """Create a detailed guide for setting up Gmail App Password"""
    
    guide = """
# 📧 Gmail App Password Setup Guide

## Why You Need This:
Gmail requires App Passwords for third-party applications like our job automation system.
Your regular Gmail password won't work for security reasons.

## Step-by-Step Instructions:

### 1. Enable 2-Step Verification
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow the setup process if not already enabled

### 2. Generate App Password
   - In the same security page, look for "App passwords"
   - Click "App passwords"
   - Select "Mail" as the app
   - Select "Other (custom name)" as device
   - Enter "LinkedIn Job Automation" as the name
   - Click "Generate"

### 3. Copy the App Password
   - You'll get a 16-character password like: "abcd efgh ijkl mnop"
   - Copy this EXACT password (including spaces)

### 4. Update config.json
   - Replace your current password with the App Password
   - Example:
     "sender_password": "abcd efgh ijkl mnop"

### 5. Test the Configuration
   - Run: python fix_email_setup.py
   - You should see "✅ Authentication successful!"

## Troubleshooting:
- ❌ "Username and Password not accepted" = Wrong password format
- ❌ "Less secure app access" = Need App Password, not regular password
- ❌ "Authentication failed" = Check 2-Step Verification is enabled

## Security Notes:
- App Passwords are safer than regular passwords
- They only work for the specific app you created them for
- You can revoke them anytime from your Google account
"""
    
    with open('Gmail_App_Password_Guide.md', 'w') as f:
        f.write(guide)
    
    print("📚 Created Gmail_App_Password_Guide.md")
    return guide

def main():
    """Main function to test email and provide guidance"""
    
    print("🚀 Starting Email Configuration Test...")
    
    # Test current configuration
    success = test_email_configuration()
    
    if not success:
        print("\n📚 Creating setup guide...")
        create_gmail_app_password_guide()
        print("\n💡 Please follow the Gmail_App_Password_Guide.md to fix email issues")
    else:
        print("\n🎉 Email configuration is working perfectly!")
        print("Your job automation system is ready to send notifications!")
    
    print(f"\n📁 Detailed logs saved in: logs/")

if __name__ == "__main__":
    main()
