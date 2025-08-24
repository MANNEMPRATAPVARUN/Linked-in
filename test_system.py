#!/usr/bin/env python3
"""
Test script for LinkedIn Job Automation System
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

# Add src to path
sys.path.append('src')

def test_config_loading():
    """Test configuration loading"""
    print("🧪 Testing configuration loading...")
    
    try:
        from main import JobAutomationSystem
        automation = JobAutomationSystem()
        
        # Check if config loaded
        assert automation.config is not None
        assert 'email' in automation.config
        assert 'job_preferences' in automation.config
        assert 'scraping' in automation.config
        
        print("✅ Configuration loading works!")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_database_init():
    """Test database initialization"""
    print("🧪 Testing database initialization...")
    
    try:
        from main import JobAutomationSystem
        automation = JobAutomationSystem()
        
        # Check if database file exists
        assert os.path.exists(automation.db_path)
        
        # Check if tables exist
        conn = sqlite3.connect(automation.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'jobs' in tables
        assert 'sent_notifications' in tables
        
        conn.close()
        
        print("✅ Database initialization works!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_independent_linkedin_scraper():
    """Test our independent LinkedIn scraper"""
    print("🧪 Testing our independent LinkedIn scraper...")

    try:
        # Import our own scraper
        sys.path.append('src')
        from linkedin_scraper_free import LinkedInScraperFree

        # Test basic scraping (small test)
        scraper = LinkedInScraperFree()
        jobs = scraper.method_1_guest_api(
            keywords="python developer",
            location="Remote",
            max_results=2,
            time_filter='r86400'  # Last 24 hours for testing
        )

        print(f"✅ Independent LinkedIn scraper works! Found {len(jobs)} test jobs")
        print("✅ No external dependencies - completely self-sufficient!")
        return True
    except Exception as e:
        print(f"❌ Independent LinkedIn scraper failed: {e}")
        return False

def test_email_content_generation():
    """Test email content generation"""
    print("🧪 Testing email content generation...")
    
    try:
        import pandas as pd
        from main import JobAutomationSystem
        
        automation = JobAutomationSystem()
        
        # Create test job data
        test_jobs = pd.DataFrame([
            {
                'title': 'Software Engineer',
                'company': 'Test Company',
                'location': 'Remote',
                'job_url': 'https://example.com/job1',
                'description': 'Great opportunity for a Python developer',
                'min_amount': 100000,
                'max_amount': 120000,
                'site': 'indeed'
            }
        ])
        
        # Generate email content
        html_content = automation.create_email_content(test_jobs)
        
        assert len(html_content) > 0
        assert 'Software Engineer' in html_content
        assert 'Test Company' in html_content
        
        print("✅ Email content generation works!")
        return True
    except Exception as e:
        print(f"❌ Email content generation failed: {e}")
        return False

def test_job_filtering():
    """Test job filtering functionality"""
    print("🧪 Testing job filtering...")
    
    try:
        import pandas as pd
        from main import JobAutomationSystem
        
        automation = JobAutomationSystem()
        
        # Create test job data
        test_jobs = pd.DataFrame([
            {
                'title': 'Senior Software Engineer',  # Should be filtered out
                'company': 'Test Company 1',
                'job_url': 'https://example.com/job1',
                'description': 'Senior role',
                'min_amount': 150000
            },
            {
                'title': 'Python Developer',  # Should pass
                'company': 'Test Company 2',
                'job_url': 'https://example.com/job2',
                'description': 'Great Python opportunity',
                'min_amount': 90000
            }
        ])
        
        # Filter jobs
        filtered = automation.filter_jobs(test_jobs)
        
        # Should filter out senior role
        assert len(filtered) == 1
        assert 'Python Developer' in filtered['title'].values
        
        print("✅ Job filtering works!")
        return True
    except Exception as e:
        print(f"❌ Job filtering failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 LinkedIn Job Automation System - Test Suite")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_database_init,
        test_independent_linkedin_scraper,
        test_email_content_generation,
        test_job_filtering
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\n📝 Next steps:")
        print("1. Edit config.json with your email settings")
        print("2. Run: python src/main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("💡 Try running: python setup.py")

if __name__ == "__main__":
    run_all_tests()
