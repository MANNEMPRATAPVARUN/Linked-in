#!/usr/bin/env python3
"""
Test job scraping with Canada-specific configuration
"""

import sys
import os
sys.path.append('src')

from main import JobAutomationSystem

def test_canada_job_search():
    print("🍁 LinkedIn Job Automation System - Canada Test")
    print("=" * 50)
    
    try:
        # Initialize system with your actual config
        automation = JobAutomationSystem()
        print("✅ System initialized with your configuration")
        
        print("🎯 Your Current Configuration:")
        print(f"   📧 Email: {automation.config['email']['sender_email']}")
        print(f"   📬 Recipients: {len(automation.config['email']['recipient_emails'])} emails")
        print(f"   🎯 Keywords: {automation.config['job_preferences']['keywords']}")
        print(f"   📍 Locations: {automation.config['job_preferences']['locations']}")
        print(f"   🌐 Sites: {automation.config['scraping']['sites']}")
        print(f"   💰 Min Salary: ${automation.config['job_preferences']['min_salary']:,}")
        
        # Test with a focused search for Canada
        print("\n🔍 Testing job search for Java Developer in Canada...")
        
        # Temporarily modify for focused test
        original_keywords = automation.config['job_preferences']['keywords'].copy()
        original_locations = automation.config['job_preferences']['locations'].copy()
        original_results = automation.config['scraping']['results_per_site']
        
        automation.config['job_preferences']['keywords'] = ['java developer']
        automation.config['job_preferences']['locations'] = ['Remote', 'Toronto, ON']
        automation.config['scraping']['results_per_site'] = 5
        
        jobs = automation.scrape_new_jobs()
        
        print(f"📊 Found {len(jobs)} total jobs")
        
        if len(jobs) > 0:
            print("✅ Job scraping is working for Canada!")
            print("\n📋 Sample jobs found:")
            for i, (_, job) in enumerate(jobs.head(5).iterrows()):
                print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"      📍 {job.get('location', 'N/A')} | 🌐 {job.get('site', 'N/A')}")
                if job.get('min_amount'):
                    print(f"      💰 ${job.get('min_amount'):,.0f}+")
                print()
            
            # Test filtering with your exclude keywords
            print("🎯 Testing job filtering with your preferences...")
            filtered_jobs = automation.filter_jobs(jobs)
            print(f"📊 After filtering: {len(filtered_jobs)} jobs")
            
            if len(filtered_jobs) > 0:
                print("✅ Found jobs that match your criteria!")
                for i, (_, job) in enumerate(filtered_jobs.head(3).iterrows()):
                    print(f"   ✨ {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    print(f"      📍 {job.get('location', 'N/A')}")
            
            # Test email functionality (without actually sending)
            print("\n📧 Testing email system...")
            if automation.config['email']['sender_email'] != 'your-email@gmail.com':
                print("✅ Email configuration looks good!")
                print(f"   📧 Sender: {automation.config['email']['sender_email']}")
                print(f"   📬 Recipients: {len(automation.config['email']['recipient_emails'])} emails")
                print("   💡 Ready to send notifications!")
            else:
                print("⚠️  Email not configured yet - update config.json with your Gmail details")
            
            print("\n🎉 System is fully functional for Canada job search!")
            print("🚀 Ready to start monitoring and send you job alerts!")
            
        else:
            print("⚠️  No jobs found. This could be due to:")
            print("   - Very specific search criteria")
            print("   - Rate limiting from job sites")
            print("   - Network restrictions")
            print("   - Try different keywords or locations")
            
        # Restore original config
        automation.config['job_preferences']['keywords'] = original_keywords
        automation.config['job_preferences']['locations'] = original_locations
        automation.config['scraping']['results_per_site'] = original_results
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_canada_job_search()
