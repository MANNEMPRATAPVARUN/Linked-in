#!/usr/bin/env python3
"""
Test the database saving fix
"""

import sys
sys.path.append('src')

from continuous_search_engine import ContinuousSearchEngine
from multi_user_system import MultiUserManager

def test_database_saving():
    print("🔧 Testing Database Saving Fix...")
    
    # Create test user
    user_manager = MultiUserManager()
    test_user = user_manager.create_user('testfix@example.com', 'Test Fix User', 'password123', False)
    
    if not test_user:
        print("❌ Could not create test user")
        return False
    
    print("✅ Test user created")
    
    # Set preferences
    preferences = {
        'keywords': ['python developer'],
        'locations': ['Remote'],
        'min_salary': 80000,
        'max_salary': 150000,
        'search_frequency_minutes': 15,
        'linkedin_quality_threshold': 50,
        'max_hours_old': 24,
        'sites_enabled': ['linkedin'],
        'exclude_keywords': []
    }
    
    user_manager.update_user_preferences(test_user.id, preferences)
    print("✅ Preferences set")
    
    # Test search engine
    search_engine = ContinuousSearchEngine()
    print("🔍 Testing fixed search engine...")
    search_engine.search_jobs_for_user(test_user.id)
    
    # Check saved jobs
    from admin_panel import get_user_job_history
    job_history = get_user_job_history(test_user.id, 10)
    print(f"📊 Jobs saved: {len(job_history)}")
    
    success = False
    if job_history:
        print("✅ Database saving is now working!")
        sample_job = job_history[0]
        print(f"Sample job: {sample_job.get('title', 'N/A')} at {sample_job.get('company', 'N/A')}")
        print(f"Quality score: {sample_job.get('quality_score', 0)}/100")
        success = True
    else:
        print("❌ Still not saving to database")
    
    # Clean up
    user_manager.delete_user(test_user.id)
    print("✅ Test user cleaned up")
    
    return success

if __name__ == "__main__":
    success = test_database_saving()
    if success:
        print("\n🎉 DATABASE SAVING FIX SUCCESSFUL!")
    else:
        print("\n❌ Database saving still needs work")
