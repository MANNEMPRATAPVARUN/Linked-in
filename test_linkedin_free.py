#!/usr/bin/env python3
"""
Test script for the zero-cost LinkedIn scraper
"""

import sys
import os
sys.path.append('src')

from linkedin_scraper_free import LinkedInScraperFree
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_linkedin_scraper():
    """Test the free LinkedIn scraper with your job preferences"""
    
    print("🚀 Testing Zero-Cost LinkedIn Scraper")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = LinkedInScraperFree()
        
        # Test with your actual job preferences
        test_searches = [
            {"keywords": "java developer", "location": "Remote"},
            {"keywords": "full stack developer", "location": "Canada"},
            {"keywords": "software engineer", "location": "Toronto"},
        ]
        
        all_results = []
        
        for search in test_searches:
            print(f"\n🔍 Testing: {search['keywords']} in {search['location']}")
            print("-" * 40)
            
            try:
                # Test with small number first
                jobs_df = scraper.scrape_jobs(
                    keywords=search['keywords'],
                    location=search['location'],
                    max_results=10  # Small test
                )
                
                if len(jobs_df) > 0:
                    print(f"✅ Found {len(jobs_df)} jobs!")
                    
                    # Show sample jobs
                    print("\n📋 Sample Jobs:")
                    for i, job in jobs_df.head(3).iterrows():
                        print(f"  • {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                        print(f"    📍 {job.get('location', 'N/A')}")
                        print(f"    🔗 {job.get('job_url', 'N/A')[:80]}...")
                        print()
                    
                    all_results.append(jobs_df)
                else:
                    print("❌ No jobs found for this search")
                
            except Exception as e:
                print(f"❌ Error in search: {e}")
                continue
        
        # Summary
        total_jobs = sum(len(df) for df in all_results)
        print(f"\n🎉 SUMMARY:")
        print(f"Total jobs found: {total_jobs}")
        print(f"Successful searches: {len(all_results)}/{len(test_searches)}")
        
        if total_jobs > 0:
            print("\n✅ LinkedIn scraper is working!")
            print("🚀 Ready to integrate with your job automation system!")
            return True
        else:
            print("\n⚠️  No jobs found. This could be due to:")
            print("   - LinkedIn rate limiting")
            print("   - Network issues")
            print("   - Search terms too specific")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome browser is installed")
        print("2. Check your internet connection")
        print("3. Try running again (LinkedIn may be rate limiting)")
        return False

def test_method_1_only():
    """Test only the Guest API method (fastest)"""
    print("\n🧪 Testing LinkedIn Guest API Method Only")
    print("=" * 50)
    
    try:
        scraper = LinkedInScraperFree()
        
        # Test guest API method directly
        jobs = scraper.method_1_guest_api(
            keywords="python developer",
            location="Remote",
            max_results=5
        )
        
        if jobs:
            print(f"✅ Guest API method found {len(jobs)} jobs!")
            for job in jobs[:3]:
                print(f"  • {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            return True
        else:
            print("❌ Guest API method found no jobs")
            return False
            
    except Exception as e:
        print(f"❌ Guest API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 LinkedIn Free Scraper Test Suite")
    print("=" * 60)
    
    # Test 1: Guest API only (fastest)
    print("\n1️⃣ Testing Guest API method...")
    api_success = test_method_1_only()
    
    # Test 2: Full scraper (if API works)
    if api_success:
        print("\n2️⃣ Testing full scraper...")
        full_success = test_linkedin_scraper()
        
        if full_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your zero-cost LinkedIn scraper is ready!")
        else:
            print("\n⚠️  Partial success - Guest API works but full scraper needs adjustment")
    else:
        print("\n⚠️  Guest API test failed - LinkedIn may be blocking requests")
        print("Try again in a few minutes or check your network connection")
    
    print("\n" + "=" * 60)
    print("Test complete!")
