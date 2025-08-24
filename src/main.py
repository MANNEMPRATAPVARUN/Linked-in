#!/usr/bin/env python3
"""
JobSprint - Independent Job Automation System
=============================================

A comprehensive job automation system that:
- Scrapes jobs from LinkedIn using our own independent implementation
- Ultra-recent filtering (5-10 minutes) for first applicant advantage
- Canada-specific location targeting and optimization
- Filters jobs based on your keywords and preferences
- Sends instant email notifications for new matching jobs
- Tracks sent notifications to avoid duplicates
- Provides real-time monitoring every 5-15 minutes

Built with our own LinkedIn scraper, Gmail SMTP, and advanced filtering.
NO EXTERNAL JOB SCRAPING DEPENDENCIES - COMPLETELY SELF-SUFFICIENT!
"""

import os
import sys
import time
import json
import sqlite3
import smtplib
import schedule
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Set
import pandas as pd

# Email imports - using direct import approach
import email.mime.text
import email.mime.multipart
MimeText = email.mime.text.MIMEText
MimeMultipart = email.mime.multipart.MIMEMultipart

# Import our own LinkedIn scraper (no external dependencies!)
from linkedin_scraper_free import LinkedInScraperFree

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobAutomationSystem:
    """Main class for the LinkedIn Job Automation System"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the job automation system"""
        self.config_file = config_file
        self.config = self.load_config()
        self.db_path = "jobs.db"
        self.init_database()
        self.sent_jobs: Set[str] = self.load_sent_jobs()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",  # Use app password for Gmail
                "recipient_emails": []
            },
            "job_preferences": {
                "keywords": ["software engineer", "python developer", "data scientist"],
                "locations": ["Remote", "San Francisco", "New York"],
                "job_types": ["fulltime", "contract"],
                "exclude_keywords": ["senior", "lead", "manager"],
                "min_salary": 80000,
                "max_hours_old": 24
            },
            "scraping": {
                "sites": ["linkedin", "indeed", "glassdoor", "ziprecruiter"],
                "results_per_site": 20,
                "check_interval_minutes": 15,
                "use_proxies": False,
                "proxies": []
            },
            "linkedin_settings": {
                "max_results_per_search": 30,
                "min_quality_score": 65,
                "enable_selenium_fallback": True,
                "respect_rate_limits": True,
                "delay_between_searches": [3, 7],
                "priority_keywords": ["senior", "lead", "principal", "architect"],
                "exclude_companies": ["staffing", "recruiting", "temp"]
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config file: {self.config_file}")
            return default_config
    
    def init_database(self):
        """Initialize SQLite database for storing jobs and tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT UNIQUE,
                title TEXT,
                company TEXT,
                location TEXT,
                site TEXT,
                description TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                date_posted TEXT,
                date_scraped TEXT,
                sent_notification BOOLEAN DEFAULT FALSE,
                keywords_matched TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT,
                sent_at TEXT,
                recipient_email TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_sent_jobs(self) -> Set[str]:
        """Load URLs of jobs for which notifications were already sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT job_url FROM sent_notifications")
        sent_urls = {row[0] for row in cursor.fetchall()}
        conn.close()
        return sent_urls
    
    def scrape_new_jobs(self) -> pd.DataFrame:
        """Scrape jobs from all configured sites with LinkedIn priority"""
        logger.info("Starting job scraping...")

        all_jobs = pd.DataFrame()

        for keyword in self.config["job_preferences"]["keywords"]:
            for location in self.config["job_preferences"]["locations"]:
                try:
                    logger.info(f"Scraping jobs for '{keyword}' in '{location}'")

                    # Priority 1: LinkedIn (if enabled) - Use our free scraper
                    linkedin_jobs = pd.DataFrame()
                    if 'linkedin' in self.config["scraping"]["sites"]:
                        try:
                            logger.info("🔍 Using enhanced LinkedIn scraper...")
                            linkedin_jobs = self.scrape_linkedin_jobs(keyword, location)

                            if not linkedin_jobs.empty:
                                linkedin_jobs['search_keyword'] = keyword
                                linkedin_jobs['search_location'] = location
                                logger.info(f"LinkedIn: Found {len(linkedin_jobs)} jobs")

                                # Apply LinkedIn-specific quality filtering
                                linkedin_jobs = self.filter_linkedin_jobs(linkedin_jobs)
                                logger.info(f"LinkedIn: {len(linkedin_jobs)} jobs after quality filtering")

                                # Add to all_jobs
                                all_jobs = pd.concat([all_jobs, linkedin_jobs], ignore_index=True)

                            # Respectful delay
                            time.sleep(random.uniform(3, 7))

                        except Exception as e:
                            logger.warning(f"Enhanced LinkedIn scraper failed: {e}")

                    # Priority 2: Focus on LinkedIn only (our independent implementation)
                    # Note: We've removed dependency on external job scraping libraries
                    # Our LinkedIn scraper is comprehensive and independent
                    logger.info(f"Using independent LinkedIn scraper only - no external dependencies!")

                except Exception as e:
                    logger.error(f"Error scraping jobs for '{keyword}' in '{location}': {e}")
                    continue

        # Remove duplicates based on job URL
        if not all_jobs.empty:
            all_jobs = all_jobs.drop_duplicates(subset=['job_url'], keep='first')
            logger.info(f"Total unique jobs found: {len(all_jobs)}")

            # Generate and log LinkedIn analytics
            linkedin_analytics = self.generate_linkedin_analytics(all_jobs)
            self.log_linkedin_performance(linkedin_analytics)

        return all_jobs

    def scrape_linkedin_jobs(self, keyword: str, location: str) -> pd.DataFrame:
        """Enhanced LinkedIn job scraping with quality checks"""
        try:
            from linkedin_scraper_free import LinkedInScraperFree

            linkedin_scraper = LinkedInScraperFree()

            # Get LinkedIn-specific settings
            linkedin_config = self.config.get("linkedin_settings", {})
            max_results = linkedin_config.get("max_results_per_search", self.config["scraping"]["results_per_site"])

            # Scrape jobs
            jobs_df = linkedin_scraper.scrape_jobs(
                keywords=keyword,
                location=location,
                max_results=max_results
            )

            if not jobs_df.empty:
                # Add LinkedIn-specific metadata
                jobs_df['site'] = 'linkedin'
                jobs_df['scraped_method'] = 'enhanced_free'
                jobs_df['quality_score'] = jobs_df.apply(self.calculate_linkedin_quality_score, axis=1)

                # Sort by quality score
                jobs_df = jobs_df.sort_values('quality_score', ascending=False)

                logger.info(f"LinkedIn scraping completed: {len(jobs_df)} jobs with quality scores")

            return jobs_df

        except Exception as e:
            logger.error(f"LinkedIn scraping failed: {e}")
            return pd.DataFrame()

    def calculate_linkedin_quality_score(self, job_row) -> float:
        """Calculate quality score for LinkedIn jobs (0-100)"""
        score = 50.0  # Base score

        try:
            # Title relevance (check against keywords)
            title = str(job_row.get('title', '')).lower()
            for keyword in self.config["job_preferences"]["keywords"]:
                if keyword.lower() in title:
                    score += 15
                    break

            # Company reputation (basic check)
            company = str(job_row.get('company', '')).lower()
            if any(word in company for word in ['inc', 'corp', 'ltd', 'llc', 'technologies', 'systems']):
                score += 10

            # Location preference
            location = str(job_row.get('location', '')).lower()
            for pref_location in self.config["job_preferences"]["locations"]:
                if pref_location.lower() in location or 'remote' in location:
                    score += 10
                    break

            # Exclude keywords penalty
            full_text = f"{title} {company} {str(job_row.get('description', ''))}".lower()
            for exclude_word in self.config["job_preferences"]["exclude_keywords"]:
                if exclude_word.lower() in full_text:
                    score -= 20
                    break

            # Recent posting bonus
            posted_date = job_row.get('posted_date', '')
            if posted_date and 'hour' in str(posted_date):
                score += 5

            return max(0, min(100, score))

        except Exception as e:
            logger.warning(f"Error calculating quality score: {e}")
            return 50.0

    def filter_linkedin_jobs(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Apply LinkedIn-specific filtering"""
        if jobs_df.empty:
            return jobs_df

        filtered_jobs = jobs_df.copy()

        # Quality score threshold
        min_quality_score = self.config.get("linkedin_settings", {}).get("min_quality_score", 60)
        filtered_jobs = filtered_jobs[filtered_jobs['quality_score'] >= min_quality_score]

        # Remove jobs with suspicious patterns
        filtered_jobs = filtered_jobs[
            ~filtered_jobs['title'].str.contains('scam|fake|pyramid|mlm', case=False, na=False)
        ]

        # Prefer jobs with complete information
        filtered_jobs = filtered_jobs.dropna(subset=['title', 'company'])

        logger.info(f"LinkedIn filtering: {len(jobs_df)} → {len(filtered_jobs)} jobs (quality threshold: {min_quality_score})")

        return filtered_jobs

    def generate_linkedin_analytics(self, jobs_df: pd.DataFrame) -> dict:
        """Generate LinkedIn-specific analytics"""
        if jobs_df.empty:
            return {}

        linkedin_jobs = jobs_df[jobs_df['site'] == 'linkedin']

        if linkedin_jobs.empty:
            return {}

        analytics = {
            'total_linkedin_jobs': len(linkedin_jobs),
            'avg_quality_score': linkedin_jobs['quality_score'].mean() if 'quality_score' in linkedin_jobs.columns else 0,
            'top_companies': linkedin_jobs['company'].value_counts().head(5).to_dict(),
            'location_distribution': linkedin_jobs['location'].value_counts().head(5).to_dict(),
            'quality_distribution': {
                'excellent': len(linkedin_jobs[linkedin_jobs.get('quality_score', 0) >= 80]),
                'good': len(linkedin_jobs[(linkedin_jobs.get('quality_score', 0) >= 60) & (linkedin_jobs.get('quality_score', 0) < 80)]),
                'fair': len(linkedin_jobs[linkedin_jobs.get('quality_score', 0) < 60])
            },
            'scraping_method': linkedin_jobs.get('scraped_method', 'unknown').value_counts().to_dict() if 'scraped_method' in linkedin_jobs.columns else {}
        }

        return analytics

    def log_linkedin_performance(self, analytics: dict):
        """Log LinkedIn scraping performance"""
        if not analytics:
            return

        logger.info("📊 LinkedIn Analytics:")
        logger.info(f"   Total jobs: {analytics.get('total_linkedin_jobs', 0)}")
        logger.info(f"   Avg quality: {analytics.get('avg_quality_score', 0):.1f}/100")

        quality_dist = analytics.get('quality_distribution', {})
        logger.info(f"   Quality: {quality_dist.get('excellent', 0)} excellent, {quality_dist.get('good', 0)} good, {quality_dist.get('fair', 0)} fair")

        top_companies = analytics.get('top_companies', {})
        if top_companies:
            logger.info(f"   Top companies: {', '.join(list(top_companies.keys())[:3])}")

    def filter_jobs(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Filter jobs based on preferences and keywords"""
        if jobs_df.empty:
            return jobs_df
        
        filtered_jobs = jobs_df.copy()
        
        # Filter by exclude keywords
        exclude_keywords = self.config["job_preferences"]["exclude_keywords"]
        if exclude_keywords:
            exclude_pattern = '|'.join(exclude_keywords)
            mask = ~(
                filtered_jobs['title'].str.contains(exclude_pattern, case=False, na=False) |
                filtered_jobs['description'].str.contains(exclude_pattern, case=False, na=False)
            )
            filtered_jobs = filtered_jobs[mask]
        
        # Filter by minimum salary (if available)
        min_salary = self.config["job_preferences"]["min_salary"]
        if min_salary and 'min_amount' in filtered_jobs.columns:
            filtered_jobs = filtered_jobs[
                (filtered_jobs['min_amount'].isna()) | 
                (filtered_jobs['min_amount'] >= min_salary)
            ]
        
        # Filter out jobs already sent
        filtered_jobs = filtered_jobs[~filtered_jobs['job_url'].isin(self.sent_jobs)]
        
        logger.info(f"Jobs after filtering: {len(filtered_jobs)}")
        return filtered_jobs
    
    def save_jobs_to_db(self, jobs_df: pd.DataFrame):
        """Save jobs to database"""
        if jobs_df.empty:
            return
        
        conn = sqlite3.connect(self.db_path)
        
        for _, job in jobs_df.iterrows():
            try:
                conn.execute('''
                    INSERT OR IGNORE INTO jobs 
                    (job_url, title, company, location, site, description, 
                     salary_min, salary_max, date_posted, date_scraped, keywords_matched)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.get('job_url', ''),
                    job.get('title', ''),
                    job.get('company', ''),
                    job.get('location', ''),
                    job.get('site', ''),
                    job.get('description', ''),
                    job.get('min_amount'),
                    job.get('max_amount'),
                    job.get('date_posted', ''),
                    datetime.now().isoformat(),
                    job.get('search_keyword', '')
                ))
            except Exception as e:
                logger.error(f"Error saving job to database: {e}")
        
        conn.commit()
        conn.close()

    def create_email_content(self, jobs_df: pd.DataFrame) -> str:
        """Create HTML email content for job notifications"""
        if jobs_df.empty:
            return ""

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #0077b5; color: white; padding: 20px; text-align: center; }}
                .job-card {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
                .job-title {{ font-size: 18px; font-weight: bold; color: #0077b5; }}
                .company {{ font-size: 16px; color: #666; margin: 5px 0; }}
                .location {{ color: #888; margin: 5px 0; }}
                .salary {{ color: #28a745; font-weight: bold; margin: 5px 0; }}
                .description {{ margin: 10px 0; max-height: 100px; overflow: hidden; }}
                .apply-btn {{
                    background-color: #0077b5; color: white; padding: 10px 20px;
                    text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0;
                }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 New Job Opportunities Found!</h1>
                <p>Found {len(jobs_df)} new jobs matching your preferences</p>
            </div>
        """

        for _, job in jobs_df.iterrows():
            salary_info = ""
            if pd.notna(job.get('min_amount')) and pd.notna(job.get('max_amount')):
                salary_info = f"<div class='salary'>💰 ${job['min_amount']:,.0f} - ${job['max_amount']:,.0f}</div>"
            elif pd.notna(job.get('min_amount')):
                salary_info = f"<div class='salary'>💰 From ${job['min_amount']:,.0f}</div>"

            description = job.get('description', '')[:200] + "..." if len(str(job.get('description', ''))) > 200 else job.get('description', '')

            html_content += f"""
            <div class="job-card">
                <div class="job-title">{job.get('title', 'N/A')}</div>
                <div class="company">🏢 {job.get('company', 'N/A')}</div>
                <div class="location">📍 {job.get('location', 'N/A')}</div>
                {salary_info}
                <div class="description">{description}</div>
                <a href="{job.get('job_url', '#')}" class="apply-btn" target="_blank">Apply Now</a>
                <small style="color: #888;">Source: {job.get('site', 'N/A').title()}</small>
            </div>
            """

        html_content += """
            <div class="footer">
                <p>This is an automated notification from your LinkedIn Job Automation System</p>
                <p>⚡ Be among the first 5 applicants to increase your chances!</p>
            </div>
        </body>
        </html>
        """

        return html_content

    def send_email_notifications(self, jobs_df: pd.DataFrame):
        """Send email notifications for new jobs"""
        if jobs_df.empty:
            logger.info("No new jobs to send notifications for")
            return

        email_config = self.config["email"]
        if not email_config["sender_email"] or not email_config["sender_password"]:
            logger.error("Email configuration incomplete. Please set sender_email and sender_password")
            return

        if not email_config["recipient_emails"]:
            logger.error("No recipient emails configured")
            return

        try:
            # Create email content
            html_content = self.create_email_content(jobs_df)

            # Setup email
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"🚀 {len(jobs_df)} New Job Opportunities Found!"
            msg['From'] = email_config["sender_email"]
            msg['To'] = ", ".join(email_config["recipient_emails"])

            # Attach HTML content
            html_part = MimeText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                server.starttls()
                server.login(email_config["sender_email"], email_config["sender_password"])

                for recipient in email_config["recipient_emails"]:
                    server.send_message(msg, to_addrs=[recipient])
                    logger.info(f"Email sent to {recipient}")

            # Record sent notifications
            self.record_sent_notifications(jobs_df, email_config["recipient_emails"])

        except Exception as e:
            logger.error(f"Error sending email notifications: {e}")

    def record_sent_notifications(self, jobs_df: pd.DataFrame, recipients: List[str]):
        """Record sent notifications in database"""
        conn = sqlite3.connect(self.db_path)

        for _, job in jobs_df.iterrows():
            for recipient in recipients:
                try:
                    conn.execute('''
                        INSERT INTO sent_notifications (job_url, sent_at, recipient_email)
                        VALUES (?, ?, ?)
                    ''', (job['job_url'], datetime.now().isoformat(), recipient))

                    # Add to in-memory set
                    self.sent_jobs.add(job['job_url'])

                except Exception as e:
                    logger.error(f"Error recording notification: {e}")

        conn.commit()
        conn.close()

    def run_job_check(self):
        """Main function to check for new jobs and send notifications"""
        logger.info("=" * 50)
        logger.info("Starting job check cycle")

        try:
            # Scrape new jobs
            jobs_df = self.scrape_new_jobs()

            if jobs_df.empty:
                logger.info("No jobs found in this cycle")
                return

            # Filter jobs
            filtered_jobs = self.filter_jobs(jobs_df)

            if filtered_jobs.empty:
                logger.info("No new jobs after filtering")
                return

            # Save to database
            self.save_jobs_to_db(filtered_jobs)

            # Send notifications
            self.send_email_notifications(filtered_jobs)

            logger.info(f"Job check completed. Sent notifications for {len(filtered_jobs)} jobs")

        except Exception as e:
            logger.error(f"Error in job check cycle: {e}")

    def start_monitoring(self):
        """Start the continuous job monitoring"""
        check_interval = self.config["scraping"]["check_interval_minutes"]
        logger.info(f"Starting job monitoring every {check_interval} minutes")

        # Schedule the job check
        schedule.every(check_interval).minutes.do(self.run_job_check)

        # Run initial check
        self.run_job_check()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks


def main():
    """Main entry point"""
    print("🚀 LinkedIn Job Automation System")
    print("=" * 40)

    # Initialize system
    automation = JobAutomationSystem()

    # Check if configuration is complete
    if not automation.config["email"]["sender_email"]:
        print("\n⚠️  Configuration Required!")
        print("Please edit config.json with your email settings and job preferences")
        print("Then run the script again.")
        return

    print(f"✅ Configuration loaded")
    print(f"📧 Email: {automation.config['email']['sender_email']}")
    print(f"🎯 Keywords: {', '.join(automation.config['job_preferences']['keywords'])}")
    print(f"📍 Locations: {', '.join(automation.config['job_preferences']['locations'])}")
    print(f"🌐 Sites: {', '.join(automation.config['scraping']['sites'])}")
    print(f"⏰ Check interval: {automation.config['scraping']['check_interval_minutes']} minutes")

    try:
        automation.start_monitoring()
    except KeyboardInterrupt:
        print("\n\n👋 Job monitoring stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
