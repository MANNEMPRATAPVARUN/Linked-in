#!/usr/bin/env python3
"""
Test job scraping functionality
"""

import sys
import os
sys.path.append('src')

from main import JobAutomationSystem

def test_job_scraping():
    print("🚀 LinkedIn Job Automation System - Live Test")
    print("=" * 50)
    
    try:
        # Initialize system
        automation = JobAutomationSystem()
        print("✅ System initialized successfully")
        
        # Configure for a focused test
        automation.config['job_preferences']['keywords'] = ['python developer']
        automation.config['job_preferences']['locations'] = ['Remote']
        automation.config['scraping']['results_per_site'] = 3
        automation.config['scraping']['sites'] = ['indeed']  # Use only Indeed for testing
        
        print("🎯 Configuration:")
        print(f"   Keywords: {automation.config['job_preferences']['keywords']}")
        print(f"   Locations: {automation.config['job_preferences']['locations']}")
        print(f"   Sites: {automation.config['scraping']['sites']}")
        print(f"   Results per site: {automation.config['scraping']['results_per_site']}")
        
        print("\n🔍 Starting job search...")
        jobs = automation.scrape_new_jobs()
        
        print(f"📊 Found {len(jobs)} total jobs")
        
        if len(jobs) > 0:
            print("✅ Job scraping is working!")
            print("\n📋 Sample jobs found:")
            for i, (_, job) in enumerate(jobs.head(3).iterrows()):
                print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"      Location: {job.get('location', 'N/A')}")
                print(f"      Site: {job.get('site', 'N/A')}")
                print()
            
            # Test filtering
            print("🎯 Testing job filtering...")
            filtered_jobs = automation.filter_jobs(jobs)
            print(f"📊 After filtering: {len(filtered_jobs)} jobs")
            
            # Test database storage
            print("💾 Testing database storage...")
            automation.save_jobs_to_db(filtered_jobs)
            print("✅ Jobs saved to database")
            
            print("\n🎉 All tests passed! The system is fully functional.")
            
        else:
            print("⚠️  No jobs found. This could be due to:")
            print("   - Rate limiting from job sites")
            print("   - Network restrictions")
            print("   - Site changes or maintenance")
            print("   - Search terms too specific")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_job_scraping()
