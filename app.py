#!/usr/bin/env python3
"""
JobSprint Unified Application
Flask app serving both API and static files for Railway deployment
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, session, render_template, send_from_directory
import hashlib
import uuid

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our modules
from supabase_manager import SupabaseManager
from linkedin_scraper_free import LinkedInScraperFree
from location_manager import LocationManager
from email_system import EmailSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with static and template folders
app = Flask(__name__, 
           static_folder='frontend',
           static_url_path='',
           template_folder='frontend')

app.secret_key = os.environ.get('SECRET_KEY', 'jobsprint-unified-secret-key-2024')

# Initialize managers
try:
    supabase_manager = SupabaseManager()
    linkedin_scraper = LinkedInScraperFree()
    location_manager = LocationManager()
    email_system = EmailSystem()
    logger.info("✅ All managers initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing managers: {e}")
    # Continue anyway for local development

# Local test users (for development without Supabase)
LOCAL_USERS = {
    'admin@jobsprint.com': {
        'id': 'admin-001',
        'email': 'admin@jobsprint.com',
        'name': 'JobSprint Admin',
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'is_admin': True
    },
    'test@jobsprint.com': {
        'id': 'test-001',
        'email': 'test@jobsprint.com',
        'name': 'Test User',
        'password_hash': hashlib.sha256('test123'.encode()).hexdigest(),
        'is_admin': False
    }
}

# ============================================================================
# STATIC FILE ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory('frontend', 'index.html')

@app.route('/dashboard.html')
def dashboard():
    """Serve the dashboard page"""
    return send_from_directory('frontend', 'dashboard.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files from frontend directory"""
    return send_from_directory('frontend', filename)

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'JobSprint API',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Hash password for comparison
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Try Supabase first, fallback to local users
        user = None
        try:
            user = supabase_manager.get_user_by_email(email)
        except Exception as e:
            logger.warning(f"Supabase unavailable, using local auth: {e}")
        
        # If Supabase failed or returned None, use local users
        if user is None:
            logger.info(f"Using local authentication for {email}")
            user = LOCAL_USERS.get(email)
        
        if user and user.get('password_hash') == password_hash:
            session['user_id'] = user['id']
            session['is_admin'] = user.get('is_admin', False)
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'is_admin': user.get('is_admin', False)
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not email or not name or not password:
            return jsonify({'error': 'Email, name, and password required'}), 400
        
        # Check if user already exists (local or Supabase)
        existing_user = None
        try:
            existing_user = supabase_manager.get_user_by_email(email)
        except Exception:
            # Check local users
            existing_user = LOCAL_USERS.get(email)
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        # Try Supabase first, fallback to local users
        user = None
        try:
            user = supabase_manager.create_user(email, name, password, is_admin=False)
        except Exception as e:
            logger.warning(f"Supabase unavailable, simulating registration: {e}")
        
        # If Supabase failed or returned None, use local users
        if user is None:
            logger.info(f"Using local registration for {email}")
            # Simulate user creation for local development
            user_id = f"user-{len(LOCAL_USERS) + 1:03d}"
            user = {
                'id': user_id,
                'email': email,
                'name': name,
                'password_hash': hashlib.sha256(password.encode()).hexdigest(),
                'is_admin': False
            }
            # Add to local users (in memory only)
            LOCAL_USERS[email] = user
        
        if user:
            # Auto-login the new user
            session['user_id'] = user['id']
            session['is_admin'] = user.get('is_admin', False)

            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'is_admin': user.get('is_admin', False)
                }
            })
        else:
            return jsonify({'error': 'Registration failed'}), 500

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    try:
        # Check if user is admin
        if 'user_id' not in session or not session.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403

        # Return local users (in production, this would query the database)
        users = []
        for email, user_data in LOCAL_USERS.items():
            users.append({
                'id': user_data['id'],
                'email': user_data['email'],
                'name': user_data['name'],
                'is_admin': user_data.get('is_admin', False)
            })

        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        })

    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({'error': 'Failed to get users'}), 500

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        # Check if user is admin
        if 'user_id' not in session or not session.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403

        # Find and remove user from local users
        user_to_delete = None
        for email, user_data in LOCAL_USERS.items():
            if user_data['id'] == user_id:
                user_to_delete = email
                break

        if user_to_delete:
            if LOCAL_USERS[user_to_delete].get('is_admin', False):
                return jsonify({'error': 'Cannot delete admin user'}), 400

            del LOCAL_USERS[user_to_delete]
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            })
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500

@app.route('/api/admin/system/status', methods=['GET'])
def system_status():
    """Get system status (admin only)"""
    try:
        # Check if user is admin
        if 'user_id' not in session or not session.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403

        return jsonify({
            'success': True,
            'status': {
                'api': 'healthy',
                'linkedin_scraper': 'active',
                'database': 'connected',
                'users_count': len(LOCAL_USERS),
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"System status error: {e}")
        return jsonify({'error': 'Failed to get system status'}), 500

# Job search endpoints
@app.route('/api/jobs/search', methods=['POST'])
def search_jobs():
    """Search for jobs using LinkedIn scraper"""
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        keywords = data.get('keywords', '')
        location = data.get('location', 'Canada')
        max_results = data.get('max_results', 10)
        time_filter = data.get('time_filter', 'r86400')  # Default: 24 hours
        work_type = data.get('work_type', 2)  # Default: Remote
        
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        logger.info(f"🔍 Job search request: {keywords} in {location}")
        
        # Perform job search
        jobs_df = linkedin_scraper.scrape_jobs(
            keywords=keywords,
            location=location,
            max_results=max_results,
            time_filter=time_filter,
            work_type=work_type
        )
        
        if jobs_df is not None and not jobs_df.empty:
            # Convert DataFrame to list of dictionaries
            jobs_list = jobs_df.to_dict('records')
            
            # Store jobs for the user (if Supabase is available)
            user_id = session['user_id']
            for job in jobs_list:
                try:
                    supabase_manager.store_job(job, user_id)
                except Exception as e:
                    logger.warning(f"Could not store job: {e}")
            
            return jsonify({
                'success': True,
                'count': len(jobs_list),
                'jobs': jobs_list,
                'search_params': {
                    'keywords': keywords,
                    'location': location,
                    'time_filter': time_filter
                }
            })
        else:
            return jsonify({
                'success': True,
                'count': 0,
                'jobs': [],
                'message': 'No jobs found matching your criteria'
            })
            
    except Exception as e:
        logger.error(f"Job search error: {e}")
        return jsonify({'error': 'Job search failed'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting JobSprint Unified App on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
