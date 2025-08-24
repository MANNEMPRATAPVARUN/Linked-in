#!/usr/bin/env python3
"""
Multi-User System for Job Automation
Supports both SQLite (current) and Supabase (future) backends
"""

import os
import json
import sqlite3
import hashlib
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class User:
    id: str
    email: str
    name: str
    is_active: bool = True
    is_admin: bool = False
    subscription_tier: str = 'free'
    created_at: str = None

@dataclass
class UserPreferences:
    """User job search preferences with ultra-recent filtering"""
    user_id: str
    keywords: List[str]
    exclude_keywords: List[str]
    locations: List[str]
    min_salary: int = 80000
    max_salary: int = 200000
    job_types: List[str] = None
    sites_enabled: List[str] = None
    search_frequency_minutes: int = 15
    linkedin_quality_threshold: int = 65
    max_hours_old: int = 24
    # New ultra-recent filtering fields
    time_filter: str = 'r3600'  # r300=5min, r600=10min, r1800=30min, r3600=1hr
    work_type: str = '2'  # 1=on-site, 2=remote, 3=hybrid
    country_focus: str = 'canada'  # canada, usa, india, etc.
    ultra_recent_mode: bool = False  # Enable 5-10 minute searches
    first_applicant_mode: bool = False  # Ultra-aggressive mode

class MultiUserManager:
    """Manages multi-user functionality with SQLite backend"""
    
    def __init__(self, db_path: str = "multi_user_jobs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with multi-user schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                subscription_tier TEXT DEFAULT 'free',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                keywords TEXT, -- JSON string
                exclude_keywords TEXT, -- JSON string
                locations TEXT, -- JSON string
                min_salary INTEGER DEFAULT 80000,
                max_salary INTEGER DEFAULT 200000,
                job_types TEXT, -- JSON string
                sites_enabled TEXT, -- JSON string
                search_frequency_minutes INTEGER DEFAULT 15,
                linkedin_quality_threshold INTEGER DEFAULT 65,
                max_hours_old INTEGER DEFAULT 24,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                external_id TEXT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                job_url TEXT NOT NULL,
                description TEXT,
                site_source TEXT NOT NULL,
                quality_score REAL DEFAULT 0,
                posted_date TEXT,
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(external_id, site_source)
            )
        ''')
        
        # User jobs relationship table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_jobs (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                job_id TEXT REFERENCES jobs(id) ON DELETE CASCADE,
                is_notified BOOLEAN DEFAULT 0,
                is_applied BOOLEAN DEFAULT 0,
                is_saved BOOLEAN DEFAULT 0,
                is_hidden BOOLEAN DEFAULT 0,
                match_score REAL DEFAULT 0,
                notified_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, job_id)
            )
        ''')
        
        # Admin settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_settings (
                id TEXT PRIMARY KEY,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL, -- JSON string
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_site_source ON jobs(site_source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_quality_score ON jobs(quality_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_jobs_user_id ON user_jobs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_jobs_notified ON user_jobs(is_notified)')
        
        conn.commit()
        conn.close()
        
        # Create default admin user if not exists
        self.create_default_admin()

        # Run database migrations
        self.run_migrations()

    def run_migrations(self):
        """Run database migrations for new features"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if new columns exist, if not add them
            cursor.execute("PRAGMA table_info(user_preferences)")
            columns = [column[1] for column in cursor.fetchall()]

            # Add ultra-recent filtering columns
            if 'time_filter' not in columns:
                cursor.execute('ALTER TABLE user_preferences ADD COLUMN time_filter TEXT DEFAULT "r3600"')
                logger.info("Added time_filter column to user_preferences")

            if 'work_type' not in columns:
                cursor.execute('ALTER TABLE user_preferences ADD COLUMN work_type TEXT DEFAULT "2"')
                logger.info("Added work_type column to user_preferences")

            if 'country_focus' not in columns:
                cursor.execute('ALTER TABLE user_preferences ADD COLUMN country_focus TEXT DEFAULT "canada"')
                logger.info("Added country_focus column to user_preferences")

            if 'ultra_recent_mode' not in columns:
                cursor.execute('ALTER TABLE user_preferences ADD COLUMN ultra_recent_mode BOOLEAN DEFAULT 0')
                logger.info("Added ultra_recent_mode column to user_preferences")

            if 'first_applicant_mode' not in columns:
                cursor.execute('ALTER TABLE user_preferences ADD COLUMN first_applicant_mode BOOLEAN DEFAULT 0')
                logger.info("Added first_applicant_mode column to user_preferences")

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error running migrations: {e}")

    def create_default_admin(self):
        """Create default admin user"""
        try:
            admin_email = "admin@jobsprint.com"
            if not self.get_user_by_email(admin_email):
                self.create_user(
                    email=admin_email,
                    name="System Administrator",
                    password="admin123",  # Change this!
                    is_admin=True
                )
                logger.info("✅ Default admin user created: admin@jobsprint.com / admin123")
        except Exception as e:
            logger.error(f"Error creating default admin: {e}")
    
    # User Management Methods
    def create_user(self, email: str, name: str, password: str, is_admin: bool = False) -> Optional[User]:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user_id = str(uuid.uuid4())
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (id, email, name, password_hash, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, email, name, password_hash, is_admin))
            
            conn.commit()
            conn.close()
            
            # Create default preferences
            self.create_default_preferences(user_id)
            
            logger.info(f"✅ User created: {email}")
            return self.get_user_by_id(user_id)
            
        except sqlite3.IntegrityError:
            logger.error(f"User with email {email} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, email, name, is_active, is_admin, subscription_tier, created_at FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(*row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, email, name, is_active, is_admin, subscription_tier, created_at FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(*row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin function)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, email, name, is_active, is_admin, subscription_tier, created_at FROM users ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [User(*row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                SELECT id, email, name, is_active, is_admin, subscription_tier, created_at 
                FROM users 
                WHERE email = ? AND password_hash = ? AND is_active = 1
            ''', (email, password_hash))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(*row)
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ['name', 'is_active', 'is_admin', 'subscription_tier']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user and all associated data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            success = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    # User Preferences Methods
    def create_default_preferences(self, user_id: str) -> bool:
        """Create default preferences for a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            prefs_id = str(uuid.uuid4())
            default_prefs = {
                'keywords': ['software engineer', 'python developer', 'java developer'],
                'exclude_keywords': ['senior', 'lead'],
                'locations': ['Remote', 'San Francisco', 'New York'],
                'job_types': ['full-time', 'remote'],
                'sites_enabled': ['linkedin', 'indeed', 'glassdoor']
            }
            
            cursor.execute('''
                INSERT INTO user_preferences 
                (id, user_id, keywords, exclude_keywords, locations, job_types, sites_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                prefs_id, user_id,
                json.dumps(default_prefs['keywords']),
                json.dumps(default_prefs['exclude_keywords']),
                json.dumps(default_prefs['locations']),
                json.dumps(default_prefs['job_types']),
                json.dumps(default_prefs['sites_enabled'])
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating default preferences for user {user_id}: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Parse JSON fields
                keywords = json.loads(row[2]) if row[2] else []
                exclude_keywords = json.loads(row[3]) if row[3] else []
                locations = json.loads(row[4]) if row[4] else []
                job_types = json.loads(row[7]) if row[7] else ['full-time']
                sites_enabled = json.loads(row[8]) if row[8] else ['linkedin', 'indeed']

                # Handle new columns (may not exist in older databases)
                time_filter = row[12] if len(row) > 12 and row[12] else 'r3600'
                work_type = row[13] if len(row) > 13 and row[13] else '2'
                country_focus = row[14] if len(row) > 14 and row[14] else 'canada'
                ultra_recent_mode = bool(row[15]) if len(row) > 15 and row[15] is not None else False
                first_applicant_mode = bool(row[16]) if len(row) > 16 and row[16] is not None else False

                return UserPreferences(
                    user_id=row[1],
                    keywords=keywords,
                    exclude_keywords=exclude_keywords,
                    locations=locations,
                    min_salary=row[5] or 80000,
                    max_salary=row[6] or 200000,
                    job_types=job_types,
                    sites_enabled=sites_enabled,
                    search_frequency_minutes=row[9] or 15,
                    linkedin_quality_threshold=row[10] or 65,
                    max_hours_old=row[11] or 24,
                    time_filter=time_filter,
                    work_type=work_type,
                    country_focus=country_focus,
                    ultra_recent_mode=ultra_recent_mode,
                    first_applicant_mode=first_applicant_mode
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query
            updates = []
            values = []
            
            if 'keywords' in preferences:
                updates.append('keywords = ?')
                values.append(json.dumps(preferences['keywords']))
            
            if 'exclude_keywords' in preferences:
                updates.append('exclude_keywords = ?')
                values.append(json.dumps(preferences['exclude_keywords']))
            
            if 'locations' in preferences:
                updates.append('locations = ?')
                values.append(json.dumps(preferences['locations']))
            
            for field in ['min_salary', 'max_salary', 'search_frequency_minutes', 'linkedin_quality_threshold', 'max_hours_old']:
                if field in preferences:
                    updates.append(f'{field} = ?')
                    values.append(preferences[field])
            
            if 'job_types' in preferences:
                updates.append('job_types = ?')
                values.append(json.dumps(preferences['job_types']))
            
            if 'sites_enabled' in preferences:
                updates.append('sites_enabled = ?')
                values.append(json.dumps(preferences['sites_enabled']))
            
            if not updates:
                return False
            
            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(user_id)
            
            query = f"UPDATE user_preferences SET {', '.join(updates)} WHERE user_id = ?"
            cursor.execute(query, values)
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False
    
    def get_user_job_status(self, user_id: str, job_url: str) -> Optional[Dict]:
        """Check if a job already exists for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT uj.* FROM user_jobs uj
                JOIN jobs j ON uj.job_id = j.id
                WHERE uj.user_id = ? AND j.job_url = ?
            ''', (user_id, job_url))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'job_id': row[2],
                    'is_notified': row[3],
                    'is_applied': row[4],
                    'is_saved': row[5],
                    'is_hidden': row[6],
                    'match_score': row[7],
                    'notified_at': row[8],
                    'created_at': row[9]
                }
            return None

        except Exception as e:
            logger.error(f"Error checking user job status: {e}")
            return None

    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats = {}

            cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            stats['active_users'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM jobs')
            stats['total_jobs'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM user_jobs WHERE is_notified = 1')
            stats['total_notifications'] = cursor.fetchone()[0]

            conn.close()
            return stats

        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}

def test_multi_user_system():
    """Test the multi-user system"""
    print("🧪 Testing Multi-User System...")
    
    try:
        manager = MultiUserManager("test_multi_user.db")
        
        # Test user creation
        user = manager.create_user("test@example.com", "Test User", "password123")
        if user:
            print(f"✅ User created: {user.email}")
            
            # Test authentication
            auth_user = manager.authenticate_user("test@example.com", "password123")
            if auth_user:
                print("✅ User authentication successful")
                
                # Test preferences
                prefs = manager.get_user_preferences(user.id)
                if prefs:
                    print(f"✅ User preferences loaded: {len(prefs.keywords)} keywords")
                
                # Test stats
                stats = manager.get_system_stats()
                print(f"✅ System stats: {stats}")
                
                # Cleanup
                manager.delete_user(user.id)
                os.remove("test_multi_user.db")
                
                print("🎉 Multi-user system test passed!")
                return True
        
        print("❌ Multi-user system test failed")
        return False
        
    except Exception as e:
        print(f"❌ Multi-user system test failed: {e}")
        return False

if __name__ == "__main__":
    test_multi_user_system()
