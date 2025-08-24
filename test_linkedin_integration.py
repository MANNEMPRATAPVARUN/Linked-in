#!/usr/bin/env python3
"""
Test LinkedIn integration with the main system
"""

import sys
import os
sys.path.append('src')

from main import JobAutomationSystem
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_linkedin_integration():
    """Test LinkedIn integration with main system"""
    
    print("🚀 Testing LinkedIn Integration with Main System")
    print("=" * 60)
    
    try:
        # Initialize automation system
        automation = JobAutomationSystem()
        
        print(f"✅ System initialized")
        print(f"📧 Email: {automation.config['email']['sender_email']}")
        print(f"🌐 Sites: {automation.config['scraping']['sites']}")
        print(f"🔧 LinkedIn settings: {automation.config.get('linkedin_settings', {}).get('min_quality_score', 'N/A')}")
        
        # Test LinkedIn scraping specifically
        print("\n🔍 Testing LinkedIn scraping...")
        
        linkedin_jobs = automation.scrape_linkedin_jobs("java developer", "Remote")
        
        if not linkedin_jobs.empty:
            print(f"✅ LinkedIn scraper found {len(linkedin_jobs)} jobs!")
            
            # Show sample with quality scores
            print("\n📋 Sample LinkedIn Jobs with Quality Scores:")
            for i, job in linkedin_jobs.head(3).iterrows():
                quality = job.get('quality_score', 0)
                print(f"  • {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"    📍 {job.get('location', 'N/A')}")
                print(f"    ⭐ Quality Score: {quality:.1f}/100")
                print(f"    🔗 {job.get('job_url', 'N/A')[:80]}...")
                print()
            
            # Test filtering
            filtered_jobs = automation.filter_linkedin_jobs(linkedin_jobs)
            print(f"📊 After quality filtering: {len(filtered_jobs)} jobs")
            
            # Test analytics
            analytics = automation.generate_linkedin_analytics(linkedin_jobs)
            automation.log_linkedin_performance(analytics)
            
            return True
        else:
            print("❌ No LinkedIn jobs found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_integration():
    """Test full system with LinkedIn priority"""
    print("\n🎯 Testing Full System Integration")
    print("=" * 60)
    
    try:
        automation = JobAutomationSystem()
        
        # Test with limited scope
        automation.config['job_preferences']['keywords'] = ['java developer']
        automation.config['job_preferences']['locations'] = ['Remote']
        
        print("🔍 Running full job scraping with LinkedIn priority...")
        
        all_jobs = automation.scrape_new_jobs()
        
        if not all_jobs.empty:
            print(f"✅ Total jobs found: {len(all_jobs)}")
            
            # Show breakdown by site
            site_counts = all_jobs['site'].value_counts()
            print("\n📊 Jobs by site:")
            for site, count in site_counts.items():
                print(f"  • {site}: {count} jobs")
            
            # Show LinkedIn jobs specifically
            linkedin_jobs = all_jobs[all_jobs['site'] == 'linkedin']
            if not linkedin_jobs.empty:
                print(f"\n🎯 LinkedIn jobs: {len(linkedin_jobs)}")
                avg_quality = linkedin_jobs.get('quality_score', pd.Series([0])).mean()
                print(f"   Average quality score: {avg_quality:.1f}/100")
            
            return True
        else:
            print("❌ No jobs found in full integration test")
            return False
            
    except Exception as e:
        print(f"❌ Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 LinkedIn Integration Test Suite")
    print("=" * 70)
    
    # Test 1: LinkedIn scraping only
    print("\n1️⃣ Testing LinkedIn scraping...")
    linkedin_success = test_linkedin_integration()
    
    # Test 2: Full system integration
    if linkedin_success:
        print("\n2️⃣ Testing full system integration...")
        full_success = test_full_integration()
        
        if full_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ LinkedIn integration is working perfectly!")
            print("🚀 Your system now prioritizes LinkedIn jobs with quality scoring!")
        else:
            print("\n⚠️  LinkedIn works but full integration needs adjustment")
    else:
        print("\n⚠️  LinkedIn integration needs debugging")
    
    print("\n" + "=" * 70)
    print("Integration test complete!")
