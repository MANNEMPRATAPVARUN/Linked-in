#!/usr/bin/env python3
"""
Test script to identify issues with the main module
"""

import os
import sys
import json

print("🧪 Testing LinkedIn Job Automation System Components")
print("=" * 60)

# Test 1: Basic imports
print("1. Testing basic imports...")
try:
    import pandas as pd
    import sqlite3
    import schedule
    import smtplib
    from datetime import datetime
    print("   ✅ Basic imports successful")
except Exception as e:
    print(f"   ❌ Basic imports failed: {e}")
    sys.exit(1)

# Test 2: Our independent LinkedIn scraper import
print("2. Testing our independent LinkedIn scraper...")
try:
    sys.path.append('src')
    from linkedin_scraper_free import LinkedInScraperFree
    print("   ✅ Independent LinkedIn scraper import successful")
except Exception as e:
    print(f"   ❌ LinkedIn scraper import failed: {e}")
    sys.exit(1)

# Test 3: Email imports
print("3. Testing email imports...")
try:
    import email.mime.text
    import email.mime.multipart
    MimeText = email.mime.text.MIMEText
    MimeMultipart = email.mime.multipart.MIMEMultipart
    print("   ✅ Email imports successful")
except Exception as e:
    print(f"   ❌ Email imports failed: {e}")
    sys.exit(1)

# Test 4: Flask import
print("4. Testing Flask import...")
try:
    from flask import Flask
    print("   ✅ Flask import successful")
except Exception as e:
    print(f"   ❌ Flask import failed: {e}")

# Test 5: Configuration loading
print("5. Testing configuration loading...")
try:
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("   ✅ Configuration loaded successfully")
        print(f"   📧 Email configured: {'Yes' if config.get('email', {}).get('sender_email') else 'No'}")
        print(f"   🎯 Keywords: {len(config.get('job_preferences', {}).get('keywords', []))}")
    else:
        print("   ⚠️  config.json not found")
except Exception as e:
    print(f"   ❌ Configuration loading failed: {e}")

# Test 6: Database creation
print("6. Testing database creation...")
try:
    conn = sqlite3.connect('test_jobs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_jobs (
            id INTEGER PRIMARY KEY,
            title TEXT
        )
    ''')
    conn.commit()
    conn.close()
    os.remove('test_jobs.db')
    print("   ✅ Database operations successful")
except Exception as e:
    print(f"   ❌ Database operations failed: {e}")

# Test 7: Simple JobSpy test
print("7. Testing JobSpy functionality...")
try:
    # Very small test
    jobs = scrape_jobs(
        site_name=["indeed"],
        search_term="python",
        location="Remote",
        results_wanted=1,
        verbose=0
    )
    print(f"   ✅ JobSpy test successful - Found {len(jobs)} jobs")
except Exception as e:
    print(f"   ❌ JobSpy test failed: {e}")

print("\n" + "=" * 60)
print("🎉 Component testing completed!")
print("\nIf all tests passed, the system should work correctly.")
print("If any tests failed, those components need to be fixed.")
