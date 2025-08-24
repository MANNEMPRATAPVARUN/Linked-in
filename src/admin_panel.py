#!/usr/bin/env python3
"""
Admin Panel for Multi-User Job Automation System
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import logging

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from multi_user_system import MultiUserManager
from email_system import email_system
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder=os.path.join(current_dir, 'templates'))
app.secret_key = 'admin-panel-secret-key-change-this'

# Global manager instances
user_manager = MultiUserManager()
continuous_search_engine = None
search_engine_thread = None

@app.route('/')
def index():
    """Redirect to admin login"""
    if 'user_id' in session and session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = user_manager.authenticate_user(email, password)
        
        if user and user.is_admin:
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials or insufficient permissions', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    # Get system statistics
    stats = user_manager.get_system_stats()
    
    # Get recent users
    users = user_manager.get_all_users()
    recent_users = users[:10]  # Last 10 users
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         current_user=session)

@app.route('/admin/users')
def admin_users():
    """User management page"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    users = user_manager.get_all_users()
    return render_template('admin_users.html', users=users, current_user=session)

@app.route('/admin/users/create', methods=['GET', 'POST'])
def admin_create_user():
    """Create new user"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        if email and name and password:
            user = user_manager.create_user(email, name, password, is_admin)
            if user:
                # Send enrollment email
                try:
                    email_sent = email_system.send_enrollment_email(email, name, password)
                    if email_sent:
                        flash(f'User {email} created successfully! Enrollment email sent.', 'success')
                    else:
                        flash(f'User {email} created successfully! (Email notification failed - check email config)', 'warning')
                except Exception as e:
                    logger.error(f"Error sending enrollment email: {e}")
                    flash(f'User {email} created successfully! (Email notification failed)', 'warning')

                return redirect(url_for('admin_users'))
            else:
                flash('Failed to create user. Email might already exist.', 'error')
        else:
            flash('All fields are required', 'error')
    
    return render_template('admin_create_user.html', current_user=session)

@app.route('/admin/users/<user_id>/edit', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    """Edit user"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    user = user_manager.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        updates = {}
        
        if 'name' in request.form:
            updates['name'] = request.form['name']
        
        updates['is_active'] = request.form.get('is_active') == 'on'
        updates['is_admin'] = request.form.get('is_admin') == 'on'
        
        if 'subscription_tier' in request.form:
            updates['subscription_tier'] = request.form['subscription_tier']
        
        if user_manager.update_user(user_id, updates):
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('Failed to update user', 'error')
    
    return render_template('admin_edit_user.html', user=user, current_user=session)

@app.route('/admin/users/<user_id>/preferences')
def admin_user_preferences(user_id):
    """View/edit user preferences"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    user = user_manager.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin_users'))
    
    preferences = user_manager.get_user_preferences(user_id)
    
    return render_template('admin_user_preferences.html', 
                         user=user, 
                         preferences=preferences, 
                         current_user=session)

@app.route('/admin/users/<user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    """Delete user"""
    # Check admin access with proper session validation
    if not session.get('user_id') or not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))

    # Prevent admin from deleting themselves
    if user_id == session.get('user_id'):
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin_users'))

    try:
        user = user_manager.get_user_by_id(user_id)
        if user:
            if user_manager.delete_user(user_id):
                flash(f'User {user.email} deleted successfully', 'success')
                logger.info(f"Admin {session.get('user_email')} deleted user {user.email}")
            else:
                flash('Failed to delete user', 'error')
                logger.error(f"Failed to delete user {user_id}")
        else:
            flash('User not found', 'error')
            logger.warning(f"Attempt to delete non-existent user {user_id}")
    except Exception as e:
        flash(f'Error deleting user: {e}', 'error')
        logger.error(f"Error deleting user {user_id}: {e}")

    return redirect(url_for('admin_users'))

@app.route('/admin/api/stats')
def admin_api_stats():
    """API endpoint for dashboard stats"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = user_manager.get_system_stats()
    return jsonify(stats)

@app.route('/admin/api/users')
def admin_api_users():
    """API endpoint for users list"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = user_manager.get_all_users()
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'subscription_tier': user.subscription_tier,
            'created_at': user.created_at
        })
    
    return jsonify(users_data)

# User-facing routes (for individual users)
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = user_manager.authenticate_user(email, password)
        
        if user:
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            
            flash('Login successful!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('user_login.html')

@app.route('/user/dashboard')
def user_dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    user = user_manager.get_user_by_id(user_id)
    preferences = user_manager.get_user_preferences(user_id)
    
    return render_template('user_dashboard.html', 
                         user=user, 
                         preferences=preferences,
                         current_user=session)

@app.route('/user/preferences', methods=['GET', 'POST'])
def user_preferences():
    """User preferences page"""
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Update preferences
        preferences = {}
        
        # Parse form data
        keywords = request.form.get('keywords', '').split(',')
        keywords = [k.strip() for k in keywords if k.strip()]
        
        exclude_keywords = request.form.get('exclude_keywords', '').split(',')
        exclude_keywords = [k.strip() for k in exclude_keywords if k.strip()]
        
        locations = request.form.get('locations', '').split(',')
        locations = [l.strip() for l in locations if l.strip()]
        
        preferences.update({
            'keywords': keywords,
            'exclude_keywords': exclude_keywords,
            'locations': locations,
            'min_salary': int(request.form.get('min_salary', 80000)),
            'max_salary': int(request.form.get('max_salary', 200000)),
            'search_frequency_minutes': int(request.form.get('search_frequency_minutes', 15)),
            'linkedin_quality_threshold': int(request.form.get('linkedin_quality_threshold', 65)),
            'max_hours_old': int(request.form.get('max_hours_old', 24)),
            # New ultra-recent filtering fields
            'time_filter': request.form.get('time_filter', 'r3600'),
            'work_type': request.form.get('work_type', '2'),
            'country_focus': request.form.get('country_focus', 'canada'),
            'ultra_recent_mode': bool(request.form.get('ultra_recent_mode')),
            'first_applicant_mode': bool(request.form.get('first_applicant_mode'))
        })
        
        if user_manager.update_user_preferences(user_id, preferences):
            flash('Preferences updated successfully!', 'success')
        else:
            flash('Failed to update preferences', 'error')
        
        return redirect(url_for('user_preferences'))
    
    user = user_manager.get_user_by_id(user_id)
    preferences = user_manager.get_user_preferences(user_id)
    
    return render_template('user_preferences.html', 
                         user=user, 
                         preferences=preferences,
                         current_user=session)

@app.route('/user/logout')
def user_logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('user_login'))

@app.route('/user/test-search', methods=['POST'])
def user_test_search():
    """Test job search for current user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        user_id = session['user_id']
        user = user_manager.get_user_by_id(user_id)
        preferences = user_manager.get_user_preferences(user_id)

        if not preferences:
            return jsonify({'success': False, 'message': 'No preferences set. Please configure your preferences first.'})

        # Import and run a test search
        from linkedin_scraper_free import LinkedInScraperFree
        scraper = LinkedInScraperFree()

        # Test with first keyword and location
        test_keyword = preferences.keywords[0] if preferences.keywords else "software engineer"
        test_location = preferences.locations[0] if preferences.locations else "Remote"

        # Run a small test search
        jobs = scraper.method_1_guest_api(test_keyword, test_location, 3)

        # Save jobs to database
        saved_jobs = 0
        for job in jobs:
            try:
                job_data = {
                    'external_id': job.get('job_url', ''),
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'salary_min': job.get('salary_min'),
                    'salary_max': job.get('salary_max'),
                    'job_url': job.get('job_url', ''),
                    'description': job.get('description', ''),
                    'site_source': 'linkedin',
                    'quality_score': job.get('quality_score', 0),
                    'posted_date': job.get('posted_date')
                }

                # Save job and create user-job relationship
                job_id = save_job_to_database(job_data)
                if job_id:
                    create_user_job_relationship(user_id, job_id, job.get('quality_score', 0))
                    saved_jobs += 1

            except Exception as e:
                logger.error(f"Error saving test job: {e}")

        logger.info(f"Test search for user {user.email}: {len(jobs)} jobs found, {saved_jobs} saved")

        return jsonify({
            'success': True,
            'message': f'Found {len(jobs)} jobs for "{test_keyword}" in "{test_location}". Saved {saved_jobs} to database.',
            'jobs_count': len(jobs),
            'saved_count': saved_jobs,
            'keyword': test_keyword,
            'location': test_location
        })

    except Exception as e:
        logger.error(f"Error in test search for user {session.get('user_id')}: {e}")
        return jsonify({'success': False, 'message': f'Test search failed: {str(e)}'})

@app.route('/user/job-history')
def user_job_history():
    """View user's job history"""
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    user = user_manager.get_user_by_id(user_id)

    # Get real job history from database
    job_history = get_user_job_history(user_id)

    return render_template('user_job_history.html',
                         user=user,
                         job_history=job_history,
                         current_user=session)

@app.route('/admin/test-user-search/<user_id>', methods=['POST'])
def admin_test_user_search(user_id):
    """Admin test search for specific user"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Admin access required'}), 401

    try:
        user = user_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})

        preferences = user_manager.get_user_preferences(user_id)
        if not preferences:
            return jsonify({'success': False, 'message': 'User has no preferences set'})

        # Import and run a test search
        from linkedin_scraper_free import LinkedInScraperFree
        scraper = LinkedInScraperFree()

        # Test with first keyword and location
        test_keyword = preferences.keywords[0] if preferences.keywords else "software engineer"
        test_location = preferences.locations[0] if preferences.locations else "Remote"

        # Run a small test search
        jobs = scraper.method_1_guest_api(test_keyword, test_location, 3)

        logger.info(f"Admin test search for user {user.email}: {len(jobs)} jobs found")

        return jsonify({
            'success': True,
            'message': f'Found {len(jobs)} jobs for user {user.name}',
            'jobs_count': len(jobs),
            'keyword': test_keyword,
            'location': test_location
        })

    except Exception as e:
        logger.error(f"Error in admin test search for user {user_id}: {e}")
        return jsonify({'success': False, 'message': f'Test search failed: {str(e)}'})

@app.route('/user/job/<job_id>/save', methods=['POST'])
def save_job(job_id):
    """Save a job for later"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        user_id = session['user_id']

        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE user_jobs
            SET is_saved = 1
            WHERE user_id = ? AND job_id = ?
        ''', (user_id, job_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            return jsonify({'success': True, 'message': 'Job saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Job not found'})

    except Exception as e:
        logger.error(f"Error saving job {job_id} for user {user_id}: {e}")
        return jsonify({'success': False, 'message': 'Error saving job'})

@app.route('/user/job/<job_id>/hide', methods=['POST'])
def hide_job(job_id):
    """Hide a job"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        user_id = session['user_id']

        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE user_jobs
            SET is_hidden = 1
            WHERE user_id = ? AND job_id = ?
        ''', (user_id, job_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            return jsonify({'success': True, 'message': 'Job hidden successfully'})
        else:
            return jsonify({'success': False, 'message': 'Job not found'})

    except Exception as e:
        logger.error(f"Error hiding job {job_id} for user {user_id}: {e}")
        return jsonify({'success': False, 'message': 'Error hiding job'})

@app.route('/user/job/<job_id>/apply', methods=['POST'])
def mark_job_applied(job_id):
    """Mark job as applied"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        user_id = session['user_id']

        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE user_jobs
            SET is_applied = 1
            WHERE user_id = ? AND job_id = ?
        ''', (user_id, job_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            return jsonify({'success': True, 'message': 'Job marked as applied'})
        else:
            return jsonify({'success': False, 'message': 'Job not found'})

    except Exception as e:
        logger.error(f"Error marking job {job_id} as applied for user {user_id}: {e}")
        return jsonify({'success': False, 'message': 'Error updating job status'})

@app.route('/admin/search-engine/start', methods=['POST'])
def start_continuous_search():
    """Start the continuous search engine"""
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))

    try:
        global continuous_search_engine, search_engine_thread

        if continuous_search_engine and continuous_search_engine.is_running:
            flash('Search engine is already running', 'info')
            return redirect(url_for('admin_dashboard'))

        # Import and initialize search engine
        from continuous_search_engine import ContinuousSearchEngine
        continuous_search_engine = ContinuousSearchEngine()

        # Start in background thread
        def run_search_engine():
            continuous_search_engine.start_continuous_search()

        search_engine_thread = threading.Thread(target=run_search_engine, daemon=True)
        search_engine_thread.start()

        flash('Continuous search engine started successfully!', 'success')
        logger.info(f"Admin {session.get('user_email')} started continuous search engine")

    except Exception as e:
        flash(f'Error starting search engine: {e}', 'error')
        logger.error(f"Error starting continuous search engine: {e}")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/search-engine/stop', methods=['POST'])
def stop_continuous_search():
    """Stop the continuous search engine"""
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))

    try:
        global continuous_search_engine

        if continuous_search_engine and continuous_search_engine.is_running:
            continuous_search_engine.stop_continuous_search()
            flash('Continuous search engine stopped successfully!', 'success')
            logger.info(f"Admin {session.get('user_email')} stopped continuous search engine")
        else:
            flash('Search engine is not running', 'info')

    except Exception as e:
        flash(f'Error stopping search engine: {e}', 'error')
        logger.error(f"Error stopping continuous search engine: {e}")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/search-engine/status')
def search_engine_status():
    """Get search engine status"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 401

    try:
        global continuous_search_engine

        if continuous_search_engine:
            status = continuous_search_engine.get_system_status()
        else:
            status = {
                'is_running': False,
                'total_users': 0,
                'active_users': 0,
                'scheduled_searches': 0,
                'last_search_times': {},
                'rate_limit_status': {'requests_last_minute': 0, 'limit': 10}
            }

        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting search engine status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/logs')
def admin_logs():
    """View system logs"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    return render_template('admin_logs.html', current_user=session)

@app.route('/admin/logs/api')
def admin_logs_api():
    """API endpoint for real-time logs"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 401

    try:
        logs = []
        log_files = [
            'logs/continuous_search.log',
            'logs/jobsprint_system.log',
            'logs/integrated_system.log'
        ]

        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        # Get last 50 lines from each log file
                        recent_lines = lines[-50:] if len(lines) > 50 else lines

                        for line in recent_lines:
                            if line.strip():
                                logs.append({
                                    'file': os.path.basename(log_file),
                                    'content': line.strip(),
                                    'timestamp': datetime.now().isoformat()
                                })
                except Exception as e:
                    logger.error(f"Error reading {log_file}: {e}")

        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x['content'][:19] if len(x['content']) > 19 else x['timestamp'], reverse=True)

        return jsonify(logs[:100])  # Return last 100 log entries

    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/test-scraper')
def admin_test_scraper():
    """Test the LinkedIn scraper directly"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    try:
        from linkedin_scraper_free import LinkedInScraperFree
        scraper = LinkedInScraperFree()

        # Test with simple search
        jobs = scraper.method_1_guest_api("python developer", "Remote", 3)

        result = {
            'success': True,
            'jobs_found': len(jobs),
            'jobs': jobs[:3],  # Return first 3 jobs
            'message': f'LinkedIn scraper working! Found {len(jobs)} real jobs.'
        }

        logger.info(f"Admin scraper test: Found {len(jobs)} jobs")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Admin scraper test failed: {e}")
        return jsonify({
            'success': False,
            'message': f'Scraper test failed: {str(e)}'
        }), 500

def save_job_to_database(job_data):
    """Save job to database and return job ID"""
    try:
        import sqlite3
        import uuid

        conn = sqlite3.connect(user_manager.db_path)
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

        return job_id if success else None

    except Exception as e:
        logger.error(f"Error saving job to database: {e}")
        return None

def create_user_job_relationship(user_id, job_id, match_score=0):
    """Create relationship between user and job"""
    try:
        import sqlite3
        import uuid

        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()

        relationship_id = str(uuid.uuid4())

        cursor.execute('''
            INSERT OR IGNORE INTO user_jobs
            (id, user_id, job_id, match_score, is_notified, is_applied, is_saved, is_hidden)
            VALUES (?, ?, ?, ?, 0, 0, 0, 0)
        ''', (relationship_id, user_id, job_id, match_score))

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    except Exception as e:
        logger.error(f"Error creating user-job relationship: {e}")
        return False

def get_user_job_history(user_id, limit=50):
    """Get job history for a user"""
    try:
        import sqlite3

        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT j.*, uj.is_notified, uj.is_applied, uj.is_saved, uj.is_hidden,
                   uj.match_score, uj.notified_at, uj.created_at as user_job_created
            FROM jobs j
            JOIN user_jobs uj ON j.id = uj.job_id
            WHERE uj.user_id = ?
            ORDER BY uj.created_at DESC
            LIMIT ?
        ''', (user_id, limit))

        rows = cursor.fetchall()
        conn.close()

        jobs = []
        for row in rows:
            jobs.append({
                'id': row[0],
                'external_id': row[1],
                'title': row[2],
                'company': row[3],
                'location': row[4],
                'salary_min': row[5],
                'salary_max': row[6],
                'job_url': row[7],
                'description': row[8],
                'site_source': row[9],
                'quality_score': row[10],
                'posted_date': row[11],
                'scraped_at': row[12],
                'created_at': row[13],
                'is_notified': row[14],
                'is_applied': row[15],
                'is_saved': row[16],
                'is_hidden': row[17],
                'match_score': row[18],
                'notified_at': row[19],
                'user_job_created': row[20]
            })

        return jobs

    except Exception as e:
        logger.error(f"Error getting user job history: {e}")
        return []

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(current_dir, 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        logger.info(f"Created templates directory: {templates_dir}")
    
    print("🚀 Starting Admin Panel...")
    print("📊 Admin Login: http://localhost:5001/admin/login")
    print("👤 User Login: http://localhost:5001/user/login")
    print("🔑 Default Admin: admin@jobsprint.com / admin123")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
