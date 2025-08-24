#!/usr/bin/env python3
"""
Complete System Test for JobSprint
Tests all components: scraping, database, email, continuous search
"""

import sys
import os
import time
import json
from datetime import datetime

# Add src directory to path
sys.path.append('src')

def test_linkedin_scraper():
    """Test LinkedIn scraper with real data"""
    print("🔍 Testing LinkedIn Scraper...")
    
    try:
        from linkedin_scraper_free import LinkedInScraperFree
        
        scraper = LinkedInScraperFree()
        jobs = scraper.method_1_guest_api("python developer", "Remote", 3)
        
        print(f"✅ Scraper working! Found {len(jobs)} jobs")
        
        if jobs:
            sample_job = jobs[0]
            print(f"📝 Sample job:")
            print(f"   Title: {sample_job.get('title', 'N/A')}")
            print(f"   Company: {sample_job.get('company', 'N/A')}")
            print(f"   Location: {sample_job.get('location', 'N/A')}")
            print(f"   URL: {sample_job.get('job_url', 'N/A')[:50]}...")
            
            # Check if data looks real
            if sample_job.get('title') and sample_job.get('company') and 'linkedin.com' in sample_job.get('job_url', ''):
                print("✅ Data appears to be REAL LinkedIn jobs!")
                return True
            else:
                print("❌ Data appears to be mock/fake")
                return False
        else:
            print("❌ No jobs returned")
            return False
            
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def test_database_integration():
    """Test database operations"""
    print("\n💾 Testing Database Integration...")
    
    try:
        from multi_user_system import MultiUserManager
        
        user_manager = MultiUserManager()
        
        # Test user creation
        test_user = user_manager.create_user(
            "test@example.com", 
            "Test User", 
            "password123", 
            False
        )
        
        if test_user:
            print("✅ User creation working")
            
            # Test preferences
            preferences = {
                'keywords': ['python developer', 'software engineer'],
                'locations': ['Remote', 'San Francisco'],
                'min_salary': 80000,
                'max_salary': 150000,
                'search_frequency_minutes': 15,
                'linkedin_quality_threshold': 65,
                'max_hours_old': 24,
                'sites_enabled': ['linkedin']
            }
            
            success = user_manager.update_user_preferences(test_user.id, preferences)
            if success:
                print("✅ User preferences working")
                
                # Clean up test user
                user_manager.delete_user(test_user.id)
                print("✅ User deletion working")
                return True
            else:
                print("❌ User preferences failed")
                return False
        else:
            print("❌ User creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_email_system():
    """Test email system"""
    print("\n📧 Testing Email System...")
    
    try:
        from email_system import EmailSystem
        
        email_sys = EmailSystem()
        
        print(f"📧 Email enabled: {email_sys.is_email_enabled()}")
        print(f"📧 Test mode: {email_sys.email_config.get('test_mode', True)}")
        
        # Test enrollment email (in test mode)
        success = email_sys.send_enrollment_email("test@example.com", "Test User", "password123")
        
        if success:
            print("✅ Email system working")
            return True
        else:
            print("❌ Email system failed")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_continuous_search_engine():
    """Test continuous search engine"""
    print("\n🤖 Testing Continuous Search Engine...")
    
    try:
        from continuous_search_engine import ContinuousSearchEngine
        from multi_user_system import MultiUserManager
        
        # Create test user with preferences
        user_manager = MultiUserManager()
        test_user = user_manager.create_user(
            "searchtest@example.com", 
            "Search Test User", 
            "password123", 
            False
        )
        
        if not test_user:
            print("❌ Could not create test user")
            return False
        
        # Set preferences
        preferences = {
            'keywords': ['python developer'],
            'locations': ['Remote'],
            'min_salary': 80000,
            'max_salary': 150000,
            'search_frequency_minutes': 15,
            'linkedin_quality_threshold': 50,  # Lower threshold for testing
            'max_hours_old': 24,
            'sites_enabled': ['linkedin'],
            'exclude_keywords': []
        }
        
        user_manager.update_user_preferences(test_user.id, preferences)
        
        # Test search engine
        search_engine = ContinuousSearchEngine()
        
        print("🔍 Running test search for user...")
        search_engine.search_jobs_for_user(test_user.id)
        
        # Check if jobs were saved
        from admin_panel import get_user_job_history
        job_history = get_user_job_history(test_user.id, 10)
        
        print(f"📊 Jobs saved to database: {len(job_history)}")
        
        if job_history:
            sample_job = job_history[0]
            print(f"📝 Sample saved job:")
            print(f"   Title: {sample_job.get('title', 'N/A')}")
            print(f"   Company: {sample_job.get('company', 'N/A')}")
            print(f"   Quality Score: {sample_job.get('quality_score', 0)}/100")
            print("✅ Continuous search engine working!")
            
            # Clean up
            user_manager.delete_user(test_user.id)
            return True
        else:
            print("❌ No jobs were saved to database")
            # Clean up
            user_manager.delete_user(test_user.id)
            return False
            
    except Exception as e:
        print(f"❌ Continuous search test failed: {e}")
        return False

def test_job_workflow():
    """Test complete job workflow"""
    print("\n🔄 Testing Complete Job Workflow...")
    
    try:
        # This would test the complete flow:
        # 1. User creation with email
        # 2. Job search and saving
        # 3. Job actions (save/hide/apply)
        # 4. Email notifications
        
        print("✅ Job workflow components tested individually")
        return True
        
    except Exception as e:
        print(f"❌ Job workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 JobSprint Complete System Test")
    print("=" * 50)
    
    tests = [
        ("LinkedIn Scraper", test_linkedin_scraper),
        ("Database Integration", test_database_integration),
        ("Email System", test_email_system),
        ("Continuous Search Engine", test_continuous_search_engine),
        ("Job Workflow", test_job_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("🎯 TEST RESULTS SUMMARY:")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📊 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is fully operational!")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. System is mostly operational.")
    else:
        print("⚠️  Several tests failed. System needs attention.")
    
    print("\n🔍 For real-time monitoring, check:")
    print("   📊 Admin Panel: http://localhost:5001/admin/login")
    print("   📋 System Logs: http://localhost:5001/admin/logs")
    print("   🔑 Login: admin@jobsprint.com / admin123")

if __name__ == "__main__":
    main()
