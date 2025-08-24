#!/usr/bin/env python3
"""
Simple Web UI for LinkedIn Job Automation System
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash
import sys
import os
sys.path.append('src')

from main import JobAutomationSystem

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Global automation instance
automation = None

@app.route('/')
def index():
    """Main dashboard"""
    global automation
    if not automation:
        automation = JobAutomationSystem()
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🍁 LinkedIn Job Automation - Canada Edition</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #0077b5; margin-bottom: 30px; }
            .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
            .btn { background: #0077b5; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; text-decoration: none; display: inline-block; }
            .btn:hover { background: #005885; }
            .btn-success { background: #28a745; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-danger { background: #dc3545; }
            .config-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
            .config-item { background: #f8f9fa; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍁 LinkedIn Job Automation System</h1>
                <h3>Canada Edition - Your Personal Job Hunter</h3>
            </div>
            
            <div class="status success">
                <strong>✅ System Status:</strong> Ready and operational!<br>
                <strong>📧 Email:</strong> {{ config.email.sender_email }}<br>
                <strong>🎯 Keywords:</strong> {{ config.job_preferences.keywords|length }} configured<br>
                <strong>📍 Locations:</strong> {{ config.job_preferences.locations|length }} configured<br>
                <strong>💰 Min Salary:</strong> ${{ "{:,}".format(config.job_preferences.min_salary) }}
            </div>
            
            <div class="config-grid">
                <div class="config-item">
                    <h4>🎯 Your Job Preferences</h4>
                    <strong>Keywords:</strong><br>
                    {% for keyword in config.job_preferences.keywords %}
                        <span style="background: #0077b5; color: white; padding: 2px 8px; border-radius: 3px; margin: 2px; display: inline-block;">{{ keyword }}</span>
                    {% endfor %}
                    <br><br>
                    <strong>Exclude:</strong> {{ config.job_preferences.exclude_keywords|join(', ') }}
                </div>
                
                <div class="config-item">
                    <h4>📍 Target Locations</h4>
                    {% for location in config.job_preferences.locations %}
                        <div>📍 {{ location }}</div>
                    {% endfor %}
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="/test_jobs" class="btn btn-success">🔍 Test Job Search</a>
                <a href="/test_email" class="btn btn-warning">📧 Test Email</a>
                <a href="/run_search" class="btn">🚀 Find Jobs Now</a>
                <a href="/config" class="btn" style="background: #6c757d;">⚙️ Settings</a>
            </div>
            
            <div class="status info">
                <strong>🚀 Quick Start:</strong><br>
                1. Click "Test Job Search" to verify job scraping works<br>
                2. Click "Test Email" to verify email notifications work<br>
                3. Click "Find Jobs Now" to start finding opportunities!<br>
                4. Check your email for job alerts
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template, config=automation.config)

@app.route('/test_jobs')
def test_jobs():
    """Test job search functionality"""
    global automation
    try:
        if not automation:
            automation = JobAutomationSystem()
        
        # Run focused test for Canada
        automation.config['scraping']['results_per_site'] = 5
        jobs = automation.scrape_new_jobs()
        
        if len(jobs) > 0:
            filtered_jobs = automation.filter_jobs(jobs)
            
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>🔍 Job Search Test Results</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .job-item { border: 1px solid #ddd; margin: 15px 0; padding: 20px; border-radius: 8px; background: #f8f9fa; }
                    .job-title { color: #0077b5; font-size: 18px; font-weight: bold; }
                    .job-company { color: #666; font-size: 16px; margin: 5px 0; }
                    .job-location { color: #28a745; font-size: 14px; }
                    .job-site { background: #0077b5; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
                    .btn { background: #0077b5; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; text-decoration: none; display: inline-block; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔍 Job Search Test Results</h1>
                    <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>✅ Success!</strong> Found {{ total_jobs }} jobs, {{ filtered_jobs }} match your criteria
                    </div>
                    
                    <h3>📋 Jobs That Match Your Preferences:</h3>
                    {% for job in sample_jobs %}
                    <div class="job-item">
                        <div class="job-title">{{ job.title }}</div>
                        <div class="job-company">🏢 {{ job.company }}</div>
                        <div class="job-location">📍 {{ job.location }}</div>
                        <div style="margin-top: 10px;">
                            <span class="job-site">{{ job.site }}</span>
                            {% if job.salary %}
                            <span style="color: #28a745; margin-left: 10px;">💰 {{ job.salary }}</span>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="/" class="btn">← Back to Dashboard</a>
                        <a href="/run_search" class="btn" style="background: #28a745;">🚀 Start Real Job Hunt</a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            sample_jobs = []
            for _, job in filtered_jobs.head(10).iterrows():
                sample_jobs.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', 'N/A'),
                    'location': job.get('location', 'N/A'),
                    'site': job.get('site', 'N/A'),
                    'salary': f"${job.get('min_amount', 0):,.0f}+" if job.get('min_amount') and job.get('min_amount') > 0 else None
                })
            
            return render_template_string(template, 
                                        total_jobs=len(jobs),
                                        filtered_jobs=len(filtered_jobs),
                                        sample_jobs=sample_jobs)
        else:
            return """
            <h1>⚠️ No Jobs Found</h1>
            <p>Try adjusting your search criteria or try again later.</p>
            <a href="/" style="background: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back</a>
            """
            
    except Exception as e:
        return f"""
        <h1>❌ Test Failed</h1>
        <p>Error: {str(e)}</p>
        <a href="/" style="background: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back</a>
        """

@app.route('/test_email')
def test_email():
    """Test email functionality"""
    global automation
    try:
        if not automation:
            automation = JobAutomationSystem()
        
        # Create a test job for email
        test_jobs = [{
            'title': 'Senior Java Developer',
            'company': 'Tech Company Canada',
            'location': 'Toronto, ON (Remote)',
            'job_url': 'https://example.com/job',
            'site': 'indeed',
            'date_posted': '2025-08-23'
        }]
        
        # Try to send test email
        import pandas as pd
        test_jobs_df = pd.DataFrame(test_jobs)
        automation.send_email_notifications(test_jobs_df)
        
        return """
        <div style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>✅ Email Test Successful!</h1>
            <p>Test email sent successfully to your configured recipients.</p>
            <p>Check your inbox for the test job notification.</p>
            <a href="/" style="background: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
        </div>
        """
        
    except Exception as e:
        return f"""
        <div style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>❌ Email Test Failed</h1>
            <p>Error: {str(e)}</p>
            <p>Please check your email configuration in config.json</p>
            <a href="/" style="background: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">← Back</a>
        </div>
        """

@app.route('/run_search')
def run_search():
    """Run actual job search and send notifications"""
    global automation
    try:
        if not automation:
            automation = JobAutomationSystem()
        
        jobs = automation.scrape_new_jobs()
        filtered_jobs = automation.filter_jobs(jobs)
        
        if len(filtered_jobs) > 0:
            # Save to database
            automation.save_jobs_to_db(filtered_jobs)
            
            # Send email notification
            job_list = []
            for _, job in filtered_jobs.iterrows():
                job_list.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', 'N/A'),
                    'location': job.get('location', 'N/A'),
                    'job_url': job.get('job_url', '#'),
                    'site': job.get('site', 'N/A'),
                    'date_posted': job.get('date_posted', 'N/A')
                })
            
            automation.send_email_notifications(filtered_jobs)
            
            return f"""
            <div style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>🎉 Job Search Complete!</h1>
                <p><strong>Found {len(filtered_jobs)} jobs that match your criteria!</strong></p>
                <p>✅ Jobs saved to database</p>
                <p>📧 Email notifications sent</p>
                <p>Check your email for the job opportunities!</p>
                <a href="/" style="background: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
            </div>
            """
        else:
            return """
            <div style="font-family: Arial; padding: 40px; text-align: center;">
                <h1>📭 No New Jobs Found</h1>
                <p>No jobs found matching your criteria at this time.</p>
                <p>Try again later or adjust your search preferences.</p>
                <a href="/" style="background: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">← Back</a>
            </div>
            """
            
    except Exception as e:
        return f"""
        <div style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>❌ Search Failed</h1>
            <p>Error: {str(e)}</p>
            <a href="/" style="background: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">← Back</a>
        </div>
        """

@app.route('/config')
def config():
    """Simple configuration display"""
    global automation
    if not automation:
        automation = JobAutomationSystem()
    
    return f"""
    <div style="font-family: Arial; padding: 40px;">
        <h1>⚙️ Current Configuration</h1>
        <p><strong>Email:</strong> {automation.config['email']['sender_email']}</p>
        <p><strong>Recipients:</strong> {', '.join(automation.config['email']['recipient_emails'])}</p>
        <p><strong>Keywords:</strong> {', '.join(automation.config['job_preferences']['keywords'])}</p>
        <p><strong>Locations:</strong> {', '.join(automation.config['job_preferences']['locations'])}</p>
        <p><strong>Min Salary:</strong> ${automation.config['job_preferences']['min_salary']:,}</p>
        <p><strong>Job Sites:</strong> {', '.join(automation.config['scraping']['sites'])}</p>
        <br>
        <p><em>To modify settings, edit the config.json file directly.</em></p>
        <a href="/" style="background: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">← Back</a>
    </div>
    """

if __name__ == '__main__':
    print("🍁 Starting LinkedIn Job Automation System - Canada Edition")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    app.run(debug=False, host='0.0.0.0', port=5000)
