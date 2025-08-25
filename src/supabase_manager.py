#!/usr/bin/env python3
"""
Supabase Database Manager for Multi-User Job Automation System
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import hashlib
import uuid

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages all Supabase database operations for the job automation system"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize Supabase client"""
        # Use environment variables or provided values
        self.supabase_url = supabase_url or "https://eazuowqlkqijpmcimkcz.supabase.co"
        self.supabase_key = supabase_key or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVhenVvd3Fsa3FpanBtY2lta2N6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUwNTU5NzQsImV4cCI6MjA1MDYzMTk3NH0.Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8"
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def create_database_schema(self):
        """Create the database schema for multi-user system"""
        try:
            # Note: In production, you would run these SQL commands through Supabase dashboard
            # or migration scripts. For now, we'll assume the schema exists.
            logger.info("📊 Database schema should be created through Supabase dashboard")
            logger.info("   Tables needed: users, user_preferences, jobs, user_jobs, admin_settings")
            return True
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            return False
    
    # User Management Methods
    def create_user(self, email: str, name: str, password: str, is_admin: bool = False) -> Optional[Dict]:
        """Create a new user"""
        try:
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user_data = {
                'email': email,
                'name': name,
                'password_hash': password_hash,
                'is_admin': is_admin,
                'subscription_tier': 'free',
                'is_active': True
            }
            
            result = self.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                user = result.data[0]
                logger.info(f"✅ User created: {email}")
                
                # Create default preferences
                self.create_default_preferences(user['id'])
                
                return user
            else:
                logger.error(f"Failed to create user: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            result = self.supabase.table('users').select('*').eq('email', email).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {email}: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin function)"""
        try:
            result = self.supabase.table('users').select('id, email, name, is_active, subscription_tier, created_at').execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user information"""
        try:
            result = self.supabase.table('users').update(updates).eq('id', user_id).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user and all associated data"""
        try:
            # Delete user (cascading will handle related data)
            result = self.supabase.table('users').delete().eq('id', user_id).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    # User Preferences Methods
    def create_default_preferences(self, user_id: str) -> bool:
        """Create default preferences for a new user"""
        try:
            default_prefs = {
                'user_id': user_id,
                'keywords': ['software engineer', 'python developer', 'java developer'],
                'exclude_keywords': ['senior', 'lead'],
                'locations': ['Remote', 'San Francisco', 'New York'],
                'min_salary': 80000,
                'max_salary': 200000,
                'job_types': ['full-time', 'remote'],
                'sites_enabled': ['linkedin', 'indeed', 'glassdoor'],
                'search_frequency_minutes': 15,
                'linkedin_quality_threshold': 65,
                'max_hours_old': 24
            }
            
            result = self.supabase.table('user_preferences').insert(default_prefs).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error creating default preferences for user {user_id}: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        try:
            result = self.supabase.table('user_preferences').select('*').eq('user_id', user_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            result = self.supabase.table('user_preferences').update(preferences).eq('user_id', user_id).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False
    
    # Job Management Methods
    def save_job(self, job_data: Dict) -> Optional[str]:
        """Save a job to the database"""
        try:
            # Create unique external_id if not provided
            if 'external_id' not in job_data:
                job_data['external_id'] = str(uuid.uuid4())
            
            result = self.supabase.table('jobs').upsert(job_data, on_conflict='external_id,site_source').execute()
            
            if result.data:
                return result.data[0]['id']
            return None
            
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            return None
    
    def get_jobs_for_user(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get jobs relevant to a user based on their preferences"""
        try:
            # Get user preferences first
            prefs = self.get_user_preferences(user_id)
            if not prefs:
                return []
            
            # Query jobs with user-specific filtering
            query = self.supabase.table('jobs').select('''
                id, title, company, location, salary_min, salary_max, 
                job_url, site_source, quality_score, posted_date, scraped_at
            ''')
            
            # Filter by quality score if LinkedIn
            if prefs.get('linkedin_quality_threshold'):
                query = query.gte('quality_score', prefs['linkedin_quality_threshold'])
            
            # Filter by salary
            if prefs.get('min_salary'):
                query = query.gte('salary_min', prefs['min_salary'])
            
            # Order by quality score and recency
            query = query.order('quality_score', desc=True).order('scraped_at', desc=True)
            
            result = query.limit(limit).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting jobs for user {user_id}: {e}")
            return []
    
    def mark_job_notified(self, user_id: str, job_id: str) -> bool:
        """Mark a job as notified for a user"""
        try:
            user_job_data = {
                'user_id': user_id,
                'job_id': job_id,
                'is_notified': True,
                'notified_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('user_jobs').upsert(user_job_data, on_conflict='user_id,job_id').execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error marking job {job_id} as notified for user {user_id}: {e}")
            return False
    
    def get_user_job_status(self, user_id: str, job_id: str) -> Optional[Dict]:
        """Get user-specific job status"""
        try:
            result = self.supabase.table('user_jobs').select('*').eq('user_id', user_id).eq('job_id', job_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting job status for user {user_id}, job {job_id}: {e}")
            return None
    
    # Job Storage Methods
    def store_job(self, job_data: Dict, user_id: str) -> bool:
        """Store job data for a user"""
        try:
            # For local development, just log the job storage
            logger.info(f"📝 Storing job for user {user_id}: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")

            # In production, this would store to Supabase
            # For now, just return success
            return True

        except Exception as e:
            logger.error(f"Error storing job: {e}")
            return False

    # Admin Methods
    def get_system_stats(self) -> Dict:
        """Get system statistics for admin dashboard"""
        try:
            stats = {}
            
            # User stats
            users_result = self.supabase.table('users').select('id', count='exact').execute()
            stats['total_users'] = users_result.count or 0
            
            # Active users (users with recent activity)
            active_users_result = self.supabase.table('users').select('id', count='exact').eq('is_active', True).execute()
            stats['active_users'] = active_users_result.count or 0
            
            # Job stats
            jobs_result = self.supabase.table('jobs').select('id', count='exact').execute()
            stats['total_jobs'] = jobs_result.count or 0
            
            # Notification stats
            notifications_result = self.supabase.table('user_jobs').select('id', count='exact').eq('is_notified', True).execute()
            stats['total_notifications'] = notifications_result.count or 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return None
            
            # Check password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash and user['is_active']:
                # Remove password hash from returned data
                user.pop('password_hash', None)
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None

def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    try:
        print("🧪 Testing Supabase connection...")
        
        manager = SupabaseManager()
        
        # Test basic connection
        stats = manager.get_system_stats()
        print(f"✅ Connection successful! System stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
