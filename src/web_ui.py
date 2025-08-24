#!/usr/bin/env python3
"""
Web UI for LinkedIn Job Automation System
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import threading
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from main import JobAutomationSystem
except ImportError as e:
    print(f"Error importing JobAutomationSystem: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'linkedin-job-automation-secret-key'

# Global automation instance
automation = None
monitoring_thread = None
is_monitoring = False

@app.route('/')
def index():
    """Main dashboard"""
    global automation
    if not automation:
        automation = JobAutomationSystem()
    
    # Get recent jobs from database
    conn = sqlite3.connect(automation.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT title, company, location, site, date_scraped, sent_notification, job_url
        FROM jobs 
        ORDER BY date_scraped DESC 
        LIMIT 20
    ''')
    recent_jobs = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM jobs WHERE sent_notification = 1')
    notifications_sent = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html', 
                         recent_jobs=recent_jobs,
                         total_jobs=total_jobs,
                         notifications_sent=notifications_sent,
                         is_monitoring=is_monitoring,
                         config=automation.config)

@app.route('/config')
def config_page():
    """Advanced configuration page with country-specific settings"""
    global automation
    if not automation:
        automation = JobAutomationSystem()

    # Country-specific job site and location mappings
    country_configs = {
        "Canada": {
            "sites": ["indeed", "glassdoor", "linkedin"],
            "locations": ["Remote", "Toronto, ON", "Vancouver, BC", "Montreal, QC", "Calgary, AB", "Ottawa, ON", "Winnipeg, MB", "Halifax, NS"],
            "currency": "CAD",
            "min_salary_default": 70000,
            "job_sites_info": {
                "indeed": "Indeed Canada - Most popular job site",
                "glassdoor": "Glassdoor Canada - Company reviews + jobs",
                "linkedin": "LinkedIn Canada - Professional network"
            }
        },
        "USA": {
            "sites": ["indeed", "glassdoor", "linkedin", "ziprecruiter"],
            "locations": ["Remote", "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA", "Chicago, IL", "Los Angeles, CA"],
            "currency": "USD",
            "min_salary_default": 80000,
            "job_sites_info": {
                "indeed": "Indeed USA - Largest job board",
                "glassdoor": "Glassdoor USA - Jobs + company insights",
                "linkedin": "LinkedIn USA - Professional networking",
                "ziprecruiter": "ZipRecruiter - Quick apply jobs"
            }
        },
        "UK": {
            "sites": ["indeed", "glassdoor", "linkedin"],
            "locations": ["Remote", "London", "Manchester", "Birmingham", "Edinburgh", "Bristol", "Leeds", "Glasgow"],
            "currency": "GBP",
            "min_salary_default": 50000,
            "job_sites_info": {
                "indeed": "Indeed UK - Top UK job site",
                "glassdoor": "Glassdoor UK - Jobs + reviews",
                "linkedin": "LinkedIn UK - Professional network"
            }
        },
        "Australia": {
            "sites": ["indeed", "glassdoor", "linkedin"],
            "locations": ["Remote", "Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD", "Perth, WA", "Adelaide, SA", "Canberra, ACT"],
            "currency": "AUD",
            "min_salary_default": 90000,
            "job_sites_info": {
                "indeed": "Indeed Australia - Leading job board",
                "glassdoor": "Glassdoor Australia - Jobs + company data",
                "linkedin": "LinkedIn Australia - Professional network"
            }
        }
    }

    return render_template('advanced_config.html',
                         config=automation.config,
                         country_configs=country_configs)

@app.route('/save_config', methods=['POST'])
def save_config():
    """Save configuration with country-specific settings"""
    global automation

    try:
        # Get selected country and apply country-specific defaults
        selected_country = request.form.get('country', 'Canada')

        # Country-specific configurations
        country_defaults = {
            "Canada": {"currency": "CAD", "min_salary": 70000},
            "USA": {"currency": "USD", "min_salary": 80000},
            "UK": {"currency": "GBP", "min_salary": 50000},
            "Australia": {"currency": "AUD", "min_salary": 90000}
        }

        country_info = country_defaults.get(selected_country, country_defaults["Canada"])

        # Get form data
        config = {
            "country": selected_country,
            "currency": country_info["currency"],
            "email": {
                "smtp_server": request.form.get('smtp_server', 'smtp.gmail.com'),
                "smtp_port": int(request.form.get('smtp_port', 587)),
                "sender_email": request.form.get('sender_email', ''),
                "sender_password": request.form.get('sender_password', ''),
                "recipient_emails": [email.strip() for email in request.form.get('recipient_emails', '').split(',') if email.strip()]
            },
            "job_preferences": {
                "keywords": [kw.strip() for kw in request.form.get('keywords', '').split(',') if kw.strip()],
                "locations": (request.form.getlist('locations') +
                            [loc.strip() for loc in request.form.get('custom_locations', '').split(',') if loc.strip()]),
                "job_types": request.form.getlist('job_types'),
                "exclude_keywords": [kw.strip() for kw in request.form.get('exclude_keywords', '').split(',') if kw.strip()],
                "min_salary": int(request.form.get('min_salary', 0)) if request.form.get('min_salary') else 0,
                "max_hours_old": int(request.form.get('max_hours_old', 24))
            },
            "scraping": {
                "sites": request.form.getlist('sites') if request.form.getlist('sites') else ["indeed", "glassdoor"],
                "results_per_site": int(request.form.get('results_per_site', 20)),
                "check_interval_minutes": int(request.form.get('check_interval_minutes', 15)),
                "use_proxies": 'use_proxies' in request.form,
                "proxies": []
            }
        }
        
        # Save to file
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Reload automation system
        automation = JobAutomationSystem()
        
        flash('Configuration saved successfully!', 'success')
        
    except Exception as e:
        flash(f'Error saving configuration: {e}', 'error')
    
    return redirect(url_for('config_page'))

@app.route('/start_monitoring')
def start_monitoring():
    """Start job monitoring"""
    global automation, monitoring_thread, is_monitoring
    
    if not automation:
        automation = JobAutomationSystem()
    
    if not is_monitoring:
        is_monitoring = True
        monitoring_thread = threading.Thread(target=run_monitoring, daemon=True)
        monitoring_thread.start()
        flash('Job monitoring started!', 'success')
    else:
        flash('Job monitoring is already running!', 'info')
    
    return redirect(url_for('index'))

@app.route('/stop_monitoring')
def stop_monitoring():
    """Stop job monitoring"""
    global is_monitoring
    
    is_monitoring = False
    flash('Job monitoring stopped!', 'info')
    
    return redirect(url_for('index'))

@app.route('/test_email')
def test_email():
    """Test email configuration"""
    global automation
    
    if not automation:
        automation = JobAutomationSystem()
    
    try:
        # Create test job data
        import pandas as pd
        test_jobs = pd.DataFrame([{
            'title': 'Test Job - Email Configuration',
            'company': 'LinkedIn Job Automation System',
            'location': 'Remote',
            'job_url': 'https://github.com/MANNEMPRATAPVARUN/linkedin-job-automation',
            'description': 'This is a test email to verify your email configuration is working correctly.',
            'min_amount': 100000,
            'max_amount': 120000,
            'site': 'test'
        }])
        
        automation.send_email_notifications(test_jobs)
        flash('Test email sent successfully!', 'success')
        
    except Exception as e:
        flash(f'Error sending test email: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/run_job_check')
def run_job_check():
    """Run a single job check"""
    global automation
    
    if not automation:
        automation = JobAutomationSystem()
    
    try:
        automation.run_job_check()
        flash('Job check completed!', 'success')
    except Exception as e:
        flash(f'Error running job check: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/test_job_search')
def test_job_search():
    """Test job search with current configuration"""
    global automation
    try:
        if not automation:
            automation = JobAutomationSystem()

        # Run a quick test search
        automation.config['scraping']['results_per_site'] = 3
        jobs = automation.scrape_new_jobs()

        if len(jobs) > 0:
            sample_jobs = []
            for _, job in jobs.head(5).iterrows():
                sample_jobs.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', 'N/A'),
                    'location': job.get('location', 'N/A'),
                    'site': job.get('site', 'N/A'),
                    'url': job.get('job_url', '#')
                })

            result_html = f"""
            <div style="font-family: Arial; padding: 20px;">
                <h1>✅ Job Search Test Successful!</h1>
                <p><strong>Found {len(jobs)} jobs</strong></p>
                <h3>Sample Results:</h3>
                <ul style="list-style-type: none; padding: 0;">
            """

            for job in sample_jobs:
                result_html += f"""
                <li style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px;">
                    <strong style="color: #0077b5;">{job['title']}</strong> at {job['company']}<br>
                    📍 {job['location']} | 🌐 {job['site']}<br>
                    <a href="{job['url']}" target="_blank" style="color: #0077b5;">View Job</a>
                </li>
                """

            result_html += f"""
                </ul>
                <p><strong>✅ Your job automation system is working perfectly!</strong></p>
                <a href='/' style="background: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
            </div>
            """

            return result_html
        else:
            return """
            <div style="font-family: Arial; padding: 20px;">
                <h1>⚠️ No Jobs Found</h1>
                <p>The search completed but no jobs were found. This could be due to:</p>
                <ul>
                    <li>Very specific search criteria</li>
                    <li>Rate limiting from job sites</li>
                    <li>Network restrictions</li>
                </ul>
                <p>Try adjusting your search criteria or try again later.</p>
                <a href='/config' style="background: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Adjust Settings</a>
                <a href='/' style="background: #666; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back</a>
            </div>
            """

    except Exception as e:
        return f"""
        <div style="font-family: Arial; padding: 20px;">
            <h1>❌ Test Failed</h1>
            <p>Error: {str(e)}</p>
            <a href='/config' style="background: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Check Configuration</a>
            <a href='/' style="background: #666; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back</a>
        </div>
        """

def run_monitoring():
    """Background monitoring function"""
    global automation, is_monitoring
    
    while is_monitoring:
        try:
            automation.run_job_check()
            # Wait for the configured interval
            interval_minutes = automation.config["scraping"]["check_interval_minutes"]
            time.sleep(interval_minutes * 60)
        except Exception as e:
            print(f"Error in monitoring: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 LinkedIn Job Automation System - Web UI")
    print("=" * 50)
    print("🌐 Starting web server at http://localhost:5000")
    print("📧 Configure your email settings in the web interface")
    print("🎯 Set your job preferences and start monitoring!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
