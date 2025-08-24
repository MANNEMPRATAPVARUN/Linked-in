#!/usr/bin/env python3
"""
Quick email test for LinkedIn Job Automation
"""

import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email():
    print("🧪 Testing email configuration...")
    
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        email_config = config['email']
        
        print(f"📧 Email: {email_config['sender_email']}")
        print(f"🔑 Password length: {len(email_config['sender_password'])} chars")
        print(f"📬 Recipients: {len(email_config['recipient_emails'])} emails")
        
        # Test SMTP connection
        context = ssl.create_default_context()
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls(context=context)
            print("✅ TLS connection established")
            
            # Test authentication
            server.login(email_config['sender_email'], email_config['sender_password'])
            print("✅ Authentication successful!")
            
            # Send test email
            print("📧 Sending test email...")
            
            msg = MIMEMultipart()
            msg['Subject'] = '🎉 LinkedIn Job Automation - Email Test SUCCESS!'
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['sender_email']
            
            html = """
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #0077b5;">✅ Email Test Successful!</h2>
                <p>Your LinkedIn Job Automation System email is working perfectly!</p>
                <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>🎯 System Status:</h3>
                    <ul>
                        <li>✅ SMTP Connection: Working</li>
                        <li>✅ Authentication: Successful</li>
                        <li>✅ Email Delivery: Functional</li>
                    </ul>
                </div>
                <p><strong>🚀 Your job automation system is ready to send alerts!</strong></p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    This is an automated test from your LinkedIn Job Automation System
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            server.sendmail(
                email_config['sender_email'], 
                [email_config['sender_email']], 
                msg.as_string()
            )
            
            print("🎉 SUCCESS! Test email sent successfully!")
            print(f"📬 Check your inbox: {email_config['sender_email']}")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("🔧 Check your Gmail App Password")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_email()
    if success:
        print("\n🎉 EMAIL SYSTEM IS WORKING PERFECTLY!")
        print("Your LinkedIn job automation system is ready to send notifications!")
    else:
        print("\n❌ Email system needs attention")
        print("Please check your Gmail App Password configuration")
