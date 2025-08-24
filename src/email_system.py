#!/usr/bin/env python3
"""
Email System for JobSprint
Handles all email notifications including enrollment, job alerts, and system notifications
"""

import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSystem:
    """Handles all email functionality for JobSprint"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.email_config = self.config.get('email', {})
        
        # Create default config if it doesn't exist
        if not os.path.exists(config_file):
            self.create_default_config()
    
    def load_config(self) -> Dict:
        """Load email configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "email": {
                "sender_email": "your-email@gmail.com",
                "sender_password": "your-app-password",
                "sender_name": "JobSprint Automation",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "enabled": False,
                "test_mode": True
            },
            "system": {
                "name": "JobSprint",
                "version": "2.0.0",
                "admin_email": "admin@jobsprint.com"
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            logger.info(f"✅ Created default config file: {self.config_file}")
            logger.info("📧 Please update email settings in config.json to enable notifications")
            
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
    
    def is_email_enabled(self) -> bool:
        """Check if email system is enabled and configured"""
        return (
            self.email_config.get('enabled', False) and
            self.email_config.get('sender_email') and
            self.email_config.get('sender_password') and
            '@' in self.email_config.get('sender_email', '')
        )
    
    def send_enrollment_email(self, user_email: str, user_name: str, password: str) -> bool:
        """Send welcome email when user enrolls"""
        if not self.is_email_enabled():
            logger.warning("Email system not configured - enrollment email not sent")
            return False
        
        try:
            subject = "🎉 Welcome to JobSprint - Your Job Automation is Ready!"
            
            html_content = self.create_enrollment_email_html(user_name, user_email, password)
            
            success = self.send_email(user_email, subject, html_content)
            
            if success:
                logger.info(f"📧 Enrollment email sent to {user_email}")
            else:
                logger.error(f"❌ Failed to send enrollment email to {user_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending enrollment email to {user_email}: {e}")
            return False
    
    def create_enrollment_email_html(self, user_name: str, user_email: str, password: str) -> str:
        """Create HTML content for enrollment email"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">
                    <span style="font-size: 32px;">🎉</span> Welcome to JobSprint!
                </h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Your Personal Job Automation System</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #667eea; margin-top: 0;">Hello {user_name}! 👋</h2>
                <p>Your JobSprint account has been created successfully! You now have access to our powerful job automation system that will help you find the perfect opportunities.</p>
            </div>
            
            <div style="background: white; border: 2px solid #667eea; border-radius: 8px; padding: 25px; margin-bottom: 25px;">
                <h3 style="color: #667eea; margin-top: 0;">🔐 Your Login Credentials</h3>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace;">
                    <p style="margin: 5px 0;"><strong>Email:</strong> {user_email}</p>
                    <p style="margin: 5px 0;"><strong>Password:</strong> {password}</p>
                    <p style="margin: 5px 0;"><strong>Login URL:</strong> <a href="http://localhost:5001/user/login" style="color: #667eea;">http://localhost:5001/user/login</a></p>
                </div>
                <p style="margin-top: 15px; font-size: 14px; color: #666;">
                    <strong>Security Note:</strong> Please change your password after your first login for security.
                </p>
            </div>
            
            <div style="background: #e8f4fd; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 25px;">
                <h3 style="color: #667eea; margin-top: 0;">🚀 What's Next?</h3>
                <ol style="margin: 0; padding-left: 20px;">
                    <li style="margin-bottom: 10px;"><strong>Login</strong> to your account using the credentials above</li>
                    <li style="margin-bottom: 10px;"><strong>Set up your preferences</strong> - keywords, locations, salary range</li>
                    <li style="margin-bottom: 10px;"><strong>Configure quality settings</strong> to get the best job matches</li>
                    <li style="margin-bottom: 10px;"><strong>Test your job search</strong> to see the system in action</li>
                    <li style="margin-bottom: 10px;"><strong>Relax</strong> while JobSprint finds opportunities for you!</li>
                </ol>
            </div>
            
            <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 25px;">
                <h3 style="color: #667eea; margin-top: 0;">✨ JobSprint Features</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <p style="margin: 5px 0;"><strong>🔍 LinkedIn Integration</strong><br>
                        <small style="color: #666;">Free job scraping with quality filtering</small></p>
                        
                        <p style="margin: 5px 0;"><strong>📧 Smart Notifications</strong><br>
                        <small style="color: #666;">Get notified only about quality matches</small></p>
                    </div>
                    <div>
                        <p style="margin: 5px 0;"><strong>⚙️ Personal Preferences</strong><br>
                        <small style="color: #666;">Customize keywords, locations, salary</small></p>
                        
                        <p style="margin: 5px 0;"><strong>🤖 Continuous Search</strong><br>
                        <small style="color: #666;">24/7 automated job discovery</small></p>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5001/user/login" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                    🚀 Login to JobSprint
                </a>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; color: #666; font-size: 14px;">
                <p style="margin: 0;">Need help? Contact your administrator or check the system documentation.</p>
                <p style="margin: 5px 0 0 0;">This is an automated message from JobSprint Job Automation System.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_job_notification_email(self, user_email: str, user_name: str, jobs: List[Dict]) -> bool:
        """Send job notification email"""
        if not self.is_email_enabled():
            logger.warning("Email system not configured - job notification not sent")
            return False
        
        try:
            subject = f"🎯 {len(jobs)} New Job Opportunities Found!"
            
            html_content = self.create_job_notification_html(user_name, jobs)
            
            success = self.send_email(user_email, subject, html_content)
            
            if success:
                logger.info(f"📧 Job notification email sent to {user_email} for {len(jobs)} jobs")
            else:
                logger.error(f"❌ Failed to send job notification email to {user_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending job notification email to {user_email}: {e}")
            return False
    
    def create_job_notification_html(self, user_name: str, jobs: List[Dict]) -> str:
        """Create HTML content for job notification email"""
        jobs_html = ""
        
        for job in jobs[:10]:  # Limit to 10 jobs in email
            quality_color = '#28a745' if job.get('quality_score', 0) >= 80 else '#ffc107' if job.get('quality_score', 0) >= 60 else '#dc3545'
            
            jobs_html += f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0; background: #f9f9f9;">
                <h3 style="margin: 0 0 10px 0; color: #333;">
                    <a href="{job.get('job_url', '#')}" style="text-decoration: none; color: #667eea;">
                        {job.get('title', 'N/A')}
                    </a>
                </h3>
                <p style="margin: 5px 0;"><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Location:</strong> {job.get('location', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Source:</strong> {job.get('site_source', 'LinkedIn').title()}</p>
                <p style="margin: 5px 0;">
                    <strong>Quality Score:</strong> 
                    <span style="color: {quality_color}; font-weight: bold;">{job.get('quality_score', 0):.0f}/100</span>
                </p>
            </div>
            """
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">🎯 New Job Opportunities!</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Found {len(jobs)} jobs matching your preferences</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #667eea; margin-top: 0;">Hello {user_name}! 👋</h2>
                <p>Great news! JobSprint found <strong>{len(jobs)} new job opportunities</strong> that match your preferences. Here are the details:</p>
            </div>
            
            {jobs_html}
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5001/user/job-history" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                    📋 View All Jobs
                </a>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; color: #666; font-size: 14px;">
                <p style="margin: 0;">This search was performed automatically based on your preferences.</p>
                <p style="margin: 5px 0 0 0;">
                    <a href="http://localhost:5001/user/preferences" style="color: #667eea;">Update your preferences</a> | 
                    <a href="http://localhost:5001/user/dashboard" style="color: #667eea;">Dashboard</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, recipient: str, subject: str, html_content: str) -> bool:
        """Send HTML email"""
        if not self.is_email_enabled():
            if self.email_config.get('test_mode', True):
                logger.info(f"📧 TEST MODE - Email would be sent to {recipient}: {subject}")
                return True
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.email_config.get('sender_name', 'JobSprint')} <{self.email_config['sender_email']}>"
            msg['To'] = recipient
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {e}")
            return False
    
    def test_email_system(self, test_email: str) -> bool:
        """Test email system configuration"""
        try:
            subject = "🧪 JobSprint Email Test"
            html_content = """
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">📧 Email System Test</h2>
                <p>If you're reading this, your JobSprint email system is working correctly!</p>
                <p><strong>Test completed:</strong> {}</p>
            </body>
            </html>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            return self.send_email(test_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Email system test failed: {e}")
            return False

# Global email system instance
email_system = EmailSystem()

def test_email_system():
    """Test the email system"""
    print("🧪 Testing Email System...")
    
    try:
        email_sys = EmailSystem()
        
        print(f"📧 Email enabled: {email_sys.is_email_enabled()}")
        print(f"📧 Test mode: {email_sys.email_config.get('test_mode', True)}")
        
        # Test enrollment email
        success = email_sys.send_enrollment_email("test@example.com", "Test User", "password123")
        print(f"📧 Enrollment email test: {'✅ Success' if success else '❌ Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email system test failed: {e}")
        return False

if __name__ == "__main__":
    test_email_system()
