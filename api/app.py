#!/usr/bin/env python3
"""
JobSprint Production API
Flask backend for Railway deployment with Supabase integration
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import hashlib
import uuid

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

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

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS for frontend
CORS(app, origins=[
    'https://*.vercel.app',
    'https://*.railway.app', 
    'http://localhost:3000',
    'http://localhost:5000'
])

# Initialize managers
try:
    supabase_manager = SupabaseManager(
        supabase_url=os.environ.get('SUPABASE_URL'),
        supabase_key=os.environ.get('SUPABASE_SERVICE_KEY')
    )
    linkedin_scraper = LinkedInScraperFree()
    location_manager = LocationManager()
    email_system = EmailSystem()
    logger.info("✅ All managers initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize managers: {e}")
    raise

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check for Railway deployment"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'JobSprint API',
        'version': '1.0.0'
    }

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
        
        # Get user from Supabase
        user = supabase_manager.get_user_by_email(email)
        
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

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True})

# User management endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        users = supabase_manager.get_all_users()
        return jsonify({'users': users})
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({'error': 'Failed to get users'}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user (admin only)"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password', 'defaultpass123')
        
        if not email or not name:
            return jsonify({'error': 'Email and name required'}), 400
        
        user = supabase_manager.create_user(email, name, password)
        
        if user:
            # Send welcome email
            try:
                email_system.send_enrollment_email(email, name, password)
            except Exception as e:
                logger.warning(f"Failed to send welcome email: {e}")
            
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        logger.error(f"Create user error: {e}")
        return jsonify({'error': 'Failed to create user'}), 500

# Job search endpoints
@app.route('/api/jobs/search', methods=['POST'])
def search_jobs():
    """Search for jobs using LinkedIn scraper"""
    if not session.get('user_id'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        keywords = data.get('keywords', '')
        location = data.get('location', 'Canada Remote')
        max_results = data.get('max_results', 25)
        time_filter = data.get('time_filter', 'r3600')  # Default 1 hour
        
        # Use LinkedIn scraper
        jobs_df = linkedin_scraper.scrape_jobs(
            keywords=keywords,
            location=location,
            max_results=max_results,
            time_filter=time_filter
        )
        
        # Convert to list of dictionaries
        jobs = jobs_df.to_dict('records') if not jobs_df.empty else []
        
        # Store jobs in Supabase
        user_id = session['user_id']
        for job in jobs:
            try:
                supabase_manager.store_job(job, user_id)
            except Exception as e:
                logger.warning(f"Failed to store job: {e}")
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs),
            'search_params': {
                'keywords': keywords,
                'location': location,
                'time_filter': time_filter
            }
        })
        
    except Exception as e:
        logger.error(f"Job search error: {e}")
        return jsonify({'error': 'Job search failed'}), 500

# User preferences endpoints
@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    if not session.get('user_id'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        preferences = supabase_manager.get_user_preferences(user_id)
        return jsonify({'preferences': preferences})
    except Exception as e:
        logger.error(f"Get preferences error: {e}")
        return jsonify({'error': 'Failed to get preferences'}), 500

@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    """Update user preferences"""
    if not session.get('user_id'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        success = supabase_manager.update_user_preferences(user_id, data)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to update preferences'}), 500
            
    except Exception as e:
        logger.error(f"Update preferences error: {e}")
        return jsonify({'error': 'Failed to update preferences'}), 500

# Location endpoints
@app.route('/api/locations/canada', methods=['GET'])
def get_canada_locations():
    """Get optimized Canada locations"""
    try:
        locations = location_manager.get_canada_locations()
        return jsonify({'locations': locations})
    except Exception as e:
        logger.error(f"Get locations error: {e}")
        return jsonify({'error': 'Failed to get locations'}), 500

# Admin dashboard endpoints
@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        stats = supabase_manager.get_admin_dashboard_stats()
        return jsonify({'stats': stats})
    except Exception as e:
        logger.error(f"Get admin stats error: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting JobSprint API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
