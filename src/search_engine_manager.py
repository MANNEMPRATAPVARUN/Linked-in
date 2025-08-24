#!/usr/bin/env python3
"""
Search Engine Manager - Web interface for managing continuous search
"""

import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from continuous_search_engine import ContinuousSearchEngine
from multi_user_system import MultiUserManager

app = Flask(__name__, template_folder=os.path.join(current_dir, 'templates'))
app.secret_key = 'search-engine-manager-secret-key'

# Global instances
search_engine = None
user_manager = MultiUserManager()
engine_thread = None

def init_search_engine():
    """Initialize the search engine"""
    global search_engine
    if search_engine is None:
        search_engine = ContinuousSearchEngine()
    return search_engine

@app.route('/search-manager')
def search_manager_dashboard():
    """Search engine management dashboard"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    engine = init_search_engine()
    status = engine.get_system_status()
    
    return render_template('search_manager_dashboard.html', 
                         status=status,
                         current_user=session)

@app.route('/search-manager/start', methods=['POST'])
def start_search_engine():
    """Start the continuous search engine"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        engine = init_search_engine()
        
        if not engine.is_running:
            # Start in a separate thread
            global engine_thread
            engine_thread = threading.Thread(target=engine.start_continuous_search, daemon=True)
            engine_thread.start()
            
            flash('Search engine started successfully!', 'success')
        else:
            flash('Search engine is already running', 'info')
        
        return redirect(url_for('search_manager_dashboard'))
        
    except Exception as e:
        flash(f'Error starting search engine: {e}', 'error')
        return redirect(url_for('search_manager_dashboard'))

@app.route('/search-manager/stop', methods=['POST'])
def stop_search_engine():
    """Stop the continuous search engine"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        engine = init_search_engine()
        engine.stop_continuous_search()
        
        flash('Search engine stopped successfully!', 'success')
        return redirect(url_for('search_manager_dashboard'))
        
    except Exception as e:
        flash(f'Error stopping search engine: {e}', 'error')
        return redirect(url_for('search_manager_dashboard'))

@app.route('/search-manager/test-user/<user_id>', methods=['POST'])
def test_user_search(user_id):
    """Test search for a specific user"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        engine = init_search_engine()
        
        # Run search in background thread
        def run_test_search():
            engine.search_jobs_for_user(user_id)
        
        test_thread = threading.Thread(target=run_test_search, daemon=True)
        test_thread.start()
        
        flash('Test search started for user', 'info')
        return redirect(url_for('search_manager_dashboard'))
        
    except Exception as e:
        flash(f'Error running test search: {e}', 'error')
        return redirect(url_for('search_manager_dashboard'))

@app.route('/search-manager/api/status')
def api_search_status():
    """API endpoint for search engine status"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        engine = init_search_engine()
        status = engine.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search-manager/api/users')
def api_search_users():
    """API endpoint for user search status"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        users = user_manager.get_all_users()
        engine = init_search_engine()
        
        user_data = []
        for user in users:
            if user.is_active:
                preferences = user_manager.get_user_preferences(user.id)
                last_search = engine.last_search_times.get(user.id)
                
                user_data.append({
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'search_frequency': preferences.search_frequency_minutes if preferences else 15,
                    'last_search': last_search.isoformat() if last_search else None,
                    'keywords_count': len(preferences.keywords) if preferences else 0,
                    'locations_count': len(preferences.locations) if preferences else 0
                })
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search-manager/logs')
def view_search_logs():
    """View search engine logs"""
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        log_file = 'logs/continuous_search.log'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 100 lines
                logs = lines[-100:] if len(lines) > 100 else lines
                logs.reverse()  # Show newest first
        
        return render_template('search_logs.html', 
                             logs=logs,
                             current_user=session)
        
    except Exception as e:
        flash(f'Error reading logs: {e}', 'error')
        return redirect(url_for('search_manager_dashboard'))

# Integration with admin panel
@app.route('/admin/search-engine')
def admin_search_engine():
    """Admin search engine page"""
    return redirect(url_for('search_manager_dashboard'))

def create_integrated_app():
    """Create integrated app with admin panel"""
    from admin_panel import app as admin_app
    
    # Add search manager routes to admin app
    for rule in app.url_map.iter_rules():
        admin_app.add_url_rule(
            rule.rule,
            rule.endpoint,
            app.view_functions[rule.endpoint],
            methods=rule.methods
        )
    
    return admin_app

if __name__ == '__main__':
    print("🚀 Starting Search Engine Manager...")
    print("📊 Dashboard: http://localhost:5002/search-manager")
    
    app.run(debug=True, port=5002, host='0.0.0.0')
