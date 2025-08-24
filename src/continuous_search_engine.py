#!/usr/bin/env python3
"""
Continuous Search Engine for Multi-User Job Automation
Handles background job searching, scheduling, and notifications
"""

import os
import sys
import time
import json
import logging
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import sqlite3
import uuid

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from multi_user_system import MultiUserManager, User, UserPreferences
from linkedin_scraper_free import LinkedInScraperFree

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/continuous_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContinuousSearchEngine:
    """Manages continuous job searching for all users"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.user_manager = MultiUserManager()
        self.linkedin_scraper = LinkedInScraperFree()
        self.is_running = False
        self.search_threads = {}
        self.last_search_times = {}
        
        # Rate limiting
        self.linkedin_requests_per_minute = 10
        self.linkedin_last_requests = []
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        logger.info("🚀 Continuous Search Engine initialized")
    
    def load_config(self) -> Dict:
        """Load email configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def start_continuous_search(self):
        """Start the continuous search engine"""
        if self.is_running:
            logger.warning("Search engine is already running")
            return
        
        self.is_running = True
        logger.info("🔄 Starting continuous search engine...")
        
        # Schedule user searches
        self.schedule_user_searches()
        
        # Start the scheduler thread
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Continuous search engine started")
    
    def stop_continuous_search(self):
        """Stop the continuous search engine"""
        self.is_running = False
        schedule.clear()
        logger.info("🛑 Continuous search engine stopped")
    
    def schedule_user_searches(self):
        """Schedule searches for all active users"""
        users = self.user_manager.get_all_users()
        active_users = [user for user in users if user.is_active]
        
        logger.info(f"📅 Scheduling searches for {len(active_users)} active users")
        
        for user in active_users:
            preferences = self.user_manager.get_user_preferences(user.id)
            if preferences:
                # Schedule based on user's preferred frequency
                frequency = preferences.search_frequency_minutes
                
                # Stagger user searches to avoid overwhelming the system
                delay_minutes = hash(user.id) % frequency
                
                schedule.every(frequency).minutes.do(
                    self.search_jobs_for_user, 
                    user_id=user.id
                ).tag(f"user_{user.id}")
                
                logger.info(f"📋 Scheduled search for {user.email} every {frequency} minutes")
    
    def run_scheduler(self):
        """Run the background scheduler"""
        logger.info("⏰ Scheduler thread started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait longer on error
        
        logger.info("⏰ Scheduler thread stopped")
    
    def search_jobs_for_user(self, user_id: str):
        """Search jobs for a specific user"""
        try:
            user = self.user_manager.get_user_by_id(user_id)
            if not user or not user.is_active:
                logger.warning(f"User {user_id} not found or inactive")
                return

            preferences = self.user_manager.get_user_preferences(user_id)
            if not preferences:
                logger.warning(f"No preferences found for user {user.email}")
                return

            logger.info(f"🔍 STARTING JOB SEARCH for {user.email}")
            logger.info(f"   📋 Keywords: {preferences.keywords}")
            logger.info(f"   📍 Locations: {preferences.locations}")
            logger.info(f"   💰 Salary: ${preferences.min_salary:,} - ${preferences.max_salary:,}")
            logger.info(f"   ⭐ Quality threshold: {preferences.linkedin_quality_threshold}/100")

            # Check rate limiting
            if not self.check_rate_limit():
                logger.warning(f"⚠️  RATE LIMIT EXCEEDED - Skipping search for {user.email}")
                return

            all_jobs = []
            
            # Search for each keyword/location combination
            total_searches = 0
            for keyword in preferences.keywords[:3]:  # Limit to 3 keywords to avoid rate limits
                for location in preferences.locations[:2]:  # Limit to 2 locations
                    total_searches += 1
                    try:
                        logger.info(f"🔍 SEARCHING: '{keyword}' in '{location}' for {user.email}")

                        # LinkedIn search (primary) with ultra-recent filtering
                        if 'linkedin' in preferences.sites_enabled:
                            # Determine time filter based on user preferences
                            time_filter = getattr(preferences, 'time_filter', 'r3600')
                            work_type = getattr(preferences, 'work_type', '2')

                            # Ultra-recent mode for first applicant advantage
                            if getattr(preferences, 'ultra_recent_mode', False):
                                time_filter = 'r600'  # Last 10 minutes
                                logger.info(f"🚨 ULTRA-RECENT MODE: Searching jobs from last 10 minutes!")

                            if getattr(preferences, 'first_applicant_mode', False):
                                time_filter = 'r300'  # Last 5 minutes
                                logger.info(f"🔥 FIRST APPLICANT MODE: Searching jobs from last 5 minutes!")

                            # Use the direct method with ultra-recent filtering
                            linkedin_jobs_list = self.linkedin_scraper.method_1_guest_api(
                                keywords=keyword,
                                location=location,
                                max_results=10,  # Smaller batches for continuous search
                                time_filter=time_filter,
                                work_type=work_type
                            )

                            logger.info(f"📊 RAW RESULTS: Found {len(linkedin_jobs_list)} jobs from LinkedIn API")

                            if linkedin_jobs_list:
                                # Convert to DataFrame-like structure for filtering
                                import pandas as pd
                                linkedin_jobs = pd.DataFrame(linkedin_jobs_list)

                                # Add user context
                                linkedin_jobs['user_id'] = user_id
                                linkedin_jobs['search_keyword'] = keyword
                                linkedin_jobs['search_location'] = location

                                # Add quality scores
                                linkedin_jobs['quality_score'] = linkedin_jobs.apply(
                                    lambda row: self.calculate_quality_score(row, preferences), axis=1
                                )

                                # Filter by user preferences
                                filtered_jobs = self.filter_jobs_for_user(linkedin_jobs, preferences)
                                all_jobs.append(filtered_jobs)

                                logger.info(f"✅ FILTERED RESULTS: {len(filtered_jobs)} jobs passed quality filters")

                                # Log sample job for verification
                                if len(filtered_jobs) > 0:
                                    sample_job = filtered_jobs.iloc[0]
                                    logger.info(f"📝 SAMPLE JOB: '{sample_job.get('title', 'N/A')}' at '{sample_job.get('company', 'N/A')}' (Quality: {sample_job.get('quality_score', 0)}/100)")
                            else:
                                logger.warning(f"❌ NO JOBS FOUND for '{keyword}' in '{location}'")

                        # Rate limiting delay
                        logger.info(f"⏳ Waiting 5 seconds before next search...")
                        time.sleep(5)

                    except Exception as e:
                        logger.error(f"❌ ERROR searching '{keyword}' in '{location}' for {user.email}: {e}")
                        continue

            logger.info(f"🔍 COMPLETED {total_searches} searches for {user.email}")
            
            # Combine and process jobs
            if all_jobs:
                combined_jobs = pd.concat(all_jobs, ignore_index=True)
                
                # Remove duplicates
                combined_jobs = combined_jobs.drop_duplicates(subset=['job_url'], keep='first')
                
                # Save jobs to database
                logger.info(f"💾 SAVING {len(combined_jobs)} jobs to database for {user.email}")
                new_jobs = self.save_jobs_for_user(user_id, combined_jobs)

                if len(new_jobs) > 0:
                    logger.info(f"💾 SUCCESSFULLY SAVED {len(new_jobs)} jobs to database")
                    # Send notifications for new jobs
                    self.send_job_notifications(user, new_jobs)
                    logger.info(f"✅ Found {len(new_jobs)} new jobs for {user.email}")
                else:
                    logger.warning(f"📭 No new jobs saved to database for {user.email} (might be duplicates)")
            else:
                logger.info(f"📭 No jobs found for {user.email}")
            
            # Update last search time
            self.last_search_times[user_id] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in job search for user {user_id}: {e}")
    
    def check_rate_limit(self) -> bool:
        """Check if we're within LinkedIn rate limits"""
        now = datetime.now()
        
        # Remove requests older than 1 minute
        self.linkedin_last_requests = [
            req_time for req_time in self.linkedin_last_requests
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check if we can make another request
        if len(self.linkedin_last_requests) >= self.linkedin_requests_per_minute:
            return False
        
        # Record this request
        self.linkedin_last_requests.append(now)
        return True
    
    def calculate_quality_score(self, job_row, preferences: UserPreferences) -> float:
        """Calculate quality score for a job based on user preferences"""
        try:
            score = 50  # Base score

            title = str(job_row.get('title', '')).lower()
            company = str(job_row.get('company', '')).lower()
            location = str(job_row.get('location', '')).lower()

            # Keyword matching (30 points)
            keyword_matches = 0
            for keyword in preferences.keywords:
                if keyword.lower() in title:
                    keyword_matches += 1

            if keyword_matches > 0:
                score += min(30, keyword_matches * 10)

            # Location preference (20 points)
            for pref_location in preferences.locations:
                if pref_location.lower() in location:
                    score += 20
                    break

            # Company reputation (basic check) (10 points)
            reputable_companies = ['google', 'microsoft', 'amazon', 'apple', 'meta', 'netflix', 'uber', 'airbnb']
            if any(comp in company for comp in reputable_companies):
                score += 10

            # Job freshness (10 points)
            posted_date = job_row.get('posted_date')
            if posted_date:
                try:
                    from datetime import datetime, timedelta
                    if isinstance(posted_date, str):
                        job_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                        days_old = (datetime.now() - job_date.replace(tzinfo=None)).days
                        if days_old <= 1:
                            score += 10
                        elif days_old <= 3:
                            score += 5
                except:
                    pass

            # Exclude keywords penalty
            for exclude_keyword in preferences.exclude_keywords:
                if exclude_keyword.lower() in title:
                    score -= 20

            return min(100, max(0, score))

        except Exception as e:
            logger.warning(f"Error calculating quality score: {e}")
            return 50

    def filter_jobs_for_user(self, jobs_df: pd.DataFrame, preferences: UserPreferences) -> pd.DataFrame:
        """Filter jobs based on user preferences"""
        if jobs_df.empty:
            return jobs_df
        
        filtered_jobs = jobs_df.copy()
        
        # Quality score filter (LinkedIn)
        if 'quality_score' in filtered_jobs.columns:
            filtered_jobs = filtered_jobs[
                filtered_jobs['quality_score'] >= preferences.linkedin_quality_threshold
            ]
        
        # Salary filter (if salary_min column exists)
        if preferences.min_salary > 0 and 'salary_min' in filtered_jobs.columns:
            filtered_jobs = filtered_jobs[
                (filtered_jobs['salary_min'].isna()) |
                (filtered_jobs['salary_min'] >= preferences.min_salary)
            ]
        
        # Exclude keywords filter
        if preferences.exclude_keywords:
            exclude_pattern = '|'.join(preferences.exclude_keywords)
            filtered_jobs = filtered_jobs[
                ~filtered_jobs['title'].str.contains(exclude_pattern, case=False, na=False)
            ]
        
        # Job age filter (if available)
        if preferences.max_hours_old and 'posted_date' in filtered_jobs.columns:
            cutoff_time = datetime.now() - timedelta(hours=preferences.max_hours_old)
            # This would need proper date parsing - simplified for now
        
        return filtered_jobs
    
    def save_jobs_for_user(self, user_id: str, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Save jobs and return only new ones"""
        if jobs_df.empty:
            logger.warning(f"No jobs to save for user {user_id}")
            return pd.DataFrame()

        logger.info(f"💾 Processing {len(jobs_df)} jobs for user {user_id}")
        new_jobs = []

        for _, job in jobs_df.iterrows():
            try:
                job_url = job.get('job_url', '')
                if not job_url:
                    logger.warning(f"Skipping job without URL: {job.get('title', 'Unknown')}")
                    continue

                # Check if job already exists for this user
                existing_status = self.user_manager.get_user_job_status(user_id, job_url)

                if not existing_status:
                    logger.info(f"💾 Saving new job: '{job.get('title', 'Unknown')}' at '{job.get('company', 'Unknown')}'")

                    # This is a new job for this user
                    job_data = {
                        'external_id': job_url,
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', ''),
                        'salary_min': job.get('salary_min'),
                        'salary_max': job.get('salary_max'),
                        'job_url': job_url,
                        'description': job.get('description', ''),
                        'site_source': job.get('site_source', 'linkedin'),
                        'quality_score': job.get('quality_score', 0),
                        'posted_date': job.get('posted_date'),
                    }

                    # Save job to database
                    job_id = self.save_job_to_db(job_data)

                    if job_id:
                        # Create user-job relationship
                        relationship_created = self.create_user_job_relationship(
                            user_id, job_id, job.get('quality_score', 0)
                        )

                        if relationship_created:
                            new_jobs.append(job)
                            logger.info(f"✅ Successfully saved job {job_id} for user {user_id}")
                        else:
                            logger.error(f"❌ Failed to create user-job relationship for job {job_id}")
                    else:
                        logger.error(f"❌ Failed to save job to database: {job.get('title', 'Unknown')}")
                else:
                    logger.debug(f"Skipping duplicate job: {job.get('title', 'Unknown')}")

            except Exception as e:
                logger.error(f"Error saving job for user {user_id}: {e}")
                continue

        logger.info(f"💾 Saved {len(new_jobs)} new jobs for user {user_id}")
        return pd.DataFrame(new_jobs) if new_jobs else pd.DataFrame()
    
    def save_job_to_db(self, job_data: Dict) -> Optional[str]:
        """Save job to database"""
        try:
            conn = sqlite3.connect(self.user_manager.db_path)
            cursor = conn.cursor()

            job_id = str(uuid.uuid4())

            cursor.execute('''
                INSERT OR IGNORE INTO jobs
                (id, external_id, title, company, location, salary_min, salary_max,
                 job_url, description, site_source, quality_score, posted_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                job_data.get('external_id', ''),
                job_data.get('title', ''),
                job_data.get('company', ''),
                job_data.get('location', ''),
                job_data.get('salary_min'),
                job_data.get('salary_max'),
                job_data.get('job_url', ''),
                job_data.get('description', ''),
                job_data.get('site_source', 'linkedin'),
                job_data.get('quality_score', 0),
                job_data.get('posted_date')
            ))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if success:
                logger.debug(f"Saved job to database with ID: {job_id}")
                return job_id
            else:
                logger.warning(f"Job already exists in database: {job_data.get('title', 'Unknown')}")
                # Return existing job ID
                return self.get_existing_job_id(job_data.get('job_url', ''))

        except Exception as e:
            logger.error(f"Error saving job to database: {e}")
            return None

    def get_existing_job_id(self, job_url: str) -> Optional[str]:
        """Get existing job ID by URL"""
        try:
            conn = sqlite3.connect(self.user_manager.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM jobs WHERE job_url = ?', (job_url,))
            result = cursor.fetchone()
            conn.close()

            return result[0] if result else None

        except Exception as e:
            logger.error(f"Error getting existing job ID: {e}")
            return None

    def create_user_job_relationship(self, user_id: str, job_id: str, match_score: float = 0) -> bool:
        """Create relationship between user and job"""
        try:
            conn = sqlite3.connect(self.user_manager.db_path)
            cursor = conn.cursor()

            relationship_id = str(uuid.uuid4())

            cursor.execute('''
                INSERT OR IGNORE INTO user_jobs
                (id, user_id, job_id, match_score, is_notified, is_applied, is_saved, is_hidden)
                VALUES (?, ?, ?, ?, 0, 0, 0, 0)
            ''', (relationship_id, user_id, job_id, match_score))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if success:
                logger.debug(f"Created user-job relationship: {user_id} -> {job_id}")
            else:
                logger.debug(f"User-job relationship already exists: {user_id} -> {job_id}")

            return True  # Return True even if relationship already exists

        except Exception as e:
            logger.error(f"Error creating user-job relationship: {e}")
            return False
    
    def send_job_notifications(self, user: User, jobs_df: pd.DataFrame):
        """Send email notifications for new jobs"""
        if jobs_df.empty:
            return
        
        try:
            email_config = self.config.get('email', {})
            if not email_config.get('sender_email'):
                logger.warning("Email not configured, skipping notifications")
                return
            
            # Create email content
            subject = f"🎯 {len(jobs_df)} New Job Opportunities Found!"
            
            html_content = self.create_job_email_html(user, jobs_df)
            
            # Send email
            self.send_email(user.email, subject, html_content, email_config)
            
            # Mark jobs as notified
            for _, job in jobs_df.iterrows():
                # In full implementation, would mark in database
                pass
            
            logger.info(f"📧 Sent notification to {user.email} for {len(jobs_df)} jobs")
            
        except Exception as e:
            logger.error(f"Error sending notifications to {user.email}: {e}")
    
    def create_job_email_html(self, user: User, jobs_df: pd.DataFrame) -> str:
        """Create HTML email content for job notifications"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">🎯 New Job Opportunities for {user.name}</h2>
                <p>We found <strong>{len(jobs_df)}</strong> new jobs matching your preferences:</p>
        """
        
        for _, job in jobs_df.head(10).iterrows():  # Limit to 10 jobs in email
            quality_score = job.get('quality_score', 0)
            quality_color = '#28a745' if quality_score >= 80 else '#ffc107' if quality_score >= 60 else '#dc3545'
            
            html += f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0; background: #f9f9f9;">
                <h3 style="margin: 0 0 10px 0; color: #333;">
                    <a href="{job.get('job_url', '#')}" style="text-decoration: none; color: #667eea;">
                        {job.get('title', 'N/A')}
                    </a>
                </h3>
                <p style="margin: 5px 0;"><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Location:</strong> {job.get('location', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Source:</strong> {job.get('site', 'LinkedIn').title()}</p>
                <p style="margin: 5px 0;">
                    <strong>Quality Score:</strong> 
                    <span style="color: {quality_color}; font-weight: bold;">{quality_score:.0f}/100</span>
                </p>
            </div>
            """
        
        html += f"""
                <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 8px;">
                    <p style="margin: 0;"><strong>JobSprint Automation</strong></p>
                    <p style="margin: 5px 0; font-size: 14px; color: #666;">
                        This search was performed automatically based on your preferences. 
                        <a href="http://localhost:5001/user/preferences">Update your preferences</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, recipient: str, subject: str, html_content: str, email_config: Dict):
        """Send HTML email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config['sender_email']
            msg['To'] = recipient
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                server.send_message(msg)
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {e}")
            raise
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        users = self.user_manager.get_all_users()
        active_users = [user for user in users if user.is_active]
        
        status = {
            'is_running': self.is_running,
            'total_users': len(users),
            'active_users': len(active_users),
            'scheduled_searches': len(schedule.jobs),
            'last_search_times': {
                user_id: time_str.isoformat() if isinstance(time_str, datetime) else str(time_str)
                for user_id, time_str in self.last_search_times.items()
            },
            'rate_limit_status': {
                'requests_last_minute': len(self.linkedin_last_requests),
                'limit': self.linkedin_requests_per_minute
            }
        }
        
        return status

def test_continuous_search():
    """Test the continuous search engine"""
    print("🧪 Testing Continuous Search Engine...")
    
    try:
        engine = ContinuousSearchEngine()
        
        # Test system status
        status = engine.get_system_status()
        print(f"✅ System status: {status['total_users']} users, {status['active_users']} active")
        
        # Test single user search (if users exist)
        users = engine.user_manager.get_all_users()
        if users:
            test_user = users[0]
            print(f"🔍 Testing search for user: {test_user.email}")
            
            # Run a single search
            engine.search_jobs_for_user(test_user.id)
            print("✅ Single user search completed")
        
        print("🎉 Continuous search engine test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Continuous search engine test failed: {e}")
        return False

if __name__ == "__main__":
    test_continuous_search()
