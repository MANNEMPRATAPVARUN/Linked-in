#!/usr/bin/env python3
"""
Enhanced logging setup for LinkedIn Job Automation System
"""

import logging
import os
from datetime import datetime
import sys

def setup_comprehensive_logging():
    """Set up comprehensive logging with multiple handlers"""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create timestamp for log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 1. Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # 2. Main log file (DEBUG and above)
    main_log_file = os.path.join(logs_dir, f"job_automation_{timestamp}.log")
    file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # 3. Error log file (ERROR and above)
    error_log_file = os.path.join(logs_dir, f"errors_{timestamp}.log")
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # 4. Email log file (for email-specific issues)
    email_log_file = os.path.join(logs_dir, f"email_{timestamp}.log")
    email_handler = logging.FileHandler(email_log_file, encoding='utf-8')
    email_handler.setLevel(logging.DEBUG)
    email_handler.setFormatter(detailed_formatter)
    
    # Create email logger
    email_logger = logging.getLogger('email')
    email_logger.addHandler(email_handler)
    email_logger.setLevel(logging.DEBUG)
    
    # 5. Job scraping log file
    jobs_log_file = os.path.join(logs_dir, f"job_scraping_{timestamp}.log")
    jobs_handler = logging.FileHandler(jobs_log_file, encoding='utf-8')
    jobs_handler.setLevel(logging.DEBUG)
    jobs_handler.setFormatter(detailed_formatter)
    
    # Create jobs logger
    jobs_logger = logging.getLogger('jobs')
    jobs_logger.addHandler(jobs_handler)
    jobs_logger.setLevel(logging.DEBUG)
    
    # Log the setup
    logging.info("=" * 60)
    logging.info("🚀 LinkedIn Job Automation System - Enhanced Logging Started")
    logging.info("=" * 60)
    logging.info(f"📁 Main log: {main_log_file}")
    logging.info(f"❌ Error log: {error_log_file}")
    logging.info(f"📧 Email log: {email_log_file}")
    logging.info(f"🔍 Jobs log: {jobs_log_file}")
    logging.info("=" * 60)
    
    return {
        'main_log': main_log_file,
        'error_log': error_log_file,
        'email_log': email_log_file,
        'jobs_log': jobs_log_file
    }

def log_system_info():
    """Log system information for debugging"""
    import platform
    import sys
    
    logging.info("🖥️ System Information:")
    logging.info(f"   OS: {platform.system()} {platform.release()}")
    logging.info(f"   Python: {sys.version}")
    logging.info(f"   Working Directory: {os.getcwd()}")
    
def log_email_debug_info(config):
    """Log email configuration for debugging (without sensitive info)"""
    email_logger = logging.getLogger('email')
    
    email_logger.info("📧 Email Configuration Debug:")
    email_logger.info(f"   SMTP Server: {config.get('smtp_server', 'Not set')}")
    email_logger.info(f"   SMTP Port: {config.get('smtp_port', 'Not set')}")
    email_logger.info(f"   Sender Email: {config.get('sender_email', 'Not set')}")
    email_logger.info(f"   Password Length: {len(config.get('sender_password', '')) if config.get('sender_password') else 0} characters")
    email_logger.info(f"   Recipients: {len(config.get('recipient_emails', []))} configured")
    
    # Check if password looks like an app password
    password = config.get('sender_password', '')
    if password:
        if len(password) == 16 and password.replace(' ', '').isalnum():
            email_logger.info("   ✅ Password format looks like Gmail App Password")
        else:
            email_logger.warning("   ⚠️ Password might not be Gmail App Password format")
            email_logger.warning("   💡 Gmail App Passwords are 16 characters, letters and numbers only")

if __name__ == "__main__":
    # Test the logging setup
    log_files = setup_comprehensive_logging()
    log_system_info()
    
    # Test different log levels
    logging.debug("🔧 Debug message test")
    logging.info("ℹ️ Info message test")
    logging.warning("⚠️ Warning message test")
    logging.error("❌ Error message test")
    
    # Test email logger
    email_logger = logging.getLogger('email')
    email_logger.info("📧 Email logger test")
    
    # Test jobs logger
    jobs_logger = logging.getLogger('jobs')
    jobs_logger.info("🔍 Jobs logger test")
    
    print("✅ Logging setup complete!")
    print(f"📁 Log files created in: {os.path.abspath('logs')}")
    for log_type, log_file in log_files.items():
        print(f"   {log_type}: {log_file}")
