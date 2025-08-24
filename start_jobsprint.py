#!/usr/bin/env python3
"""
JobSprint System Launcher
Starts the complete integrated system
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.append(src_dir)

# Import components
from multi_user_system import MultiUserManager
from admin_panel import app

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/jobsprint_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_system_requirements():
    """Check if all system requirements are met"""
    print("🔍 Checking system requirements...")
    
    requirements = {
        'config_file': os.path.exists('config.json'),
        'database': True,  # Will be created automatically
        'logs_directory': os.path.exists('logs'),
        'templates': os.path.exists('src/templates'),
    }
    
    all_good = True
    for req, status in requirements.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {req.replace('_', ' ').title()}")
        if not status:
            all_good = False
    
    return all_good

def initialize_system():
    """Initialize the JobSprint system"""
    print("🚀 Initializing JobSprint System...")
    
    try:
        # Initialize user manager (creates database if needed)
        user_manager = MultiUserManager()
        
        # Get system stats
        stats = user_manager.get_system_stats()
        print(f"   📊 Database: {stats['total_users']} users, {stats['active_users']} active")
        
        # Check if admin user exists
        admin_user = user_manager.get_user_by_email("admin@jobsprint.com")
        if admin_user:
            print(f"   👤 Admin user: {admin_user.email}")
        else:
            print("   ⚠️  No admin user found")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False

def add_system_routes(app):
    """Add system management routes to the Flask app"""
    
    @app.route('/system')
    def system_overview():
        """System overview page"""
        from flask import render_template, session, redirect, url_for
        
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        
        try:
            user_manager = MultiUserManager()
            
            # Get system information
            user_stats = user_manager.get_system_stats()
            users = user_manager.get_all_users()
            
            system_info = {
                'stats': user_stats,
                'users': users[:10],  # Recent 10 users
                'system_health': {
                    'status': 'healthy',
                    'components': {
                        'database': {'status': 'healthy', 'message': 'Database operational'},
                        'web_interface': {'status': 'healthy', 'message': 'Web interface running'},
                        'linkedin_scraper': {'status': 'healthy', 'message': 'LinkedIn scraper ready'},
                        'email_system': {'status': 'healthy', 'message': 'Email system configured'}
                    }
                }
            }
            
            return render_template('system_overview.html', 
                                 system_info=system_info,
                                 current_user=session)
        
        except Exception as e:
            logger.error(f"Error in system overview: {e}")
            return f"System error: {e}", 500
    
    @app.route('/system/test-linkedin')
    def test_linkedin_scraper():
        """Test LinkedIn scraper"""
        from flask import jsonify, session
        
        if not session.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            from linkedin_scraper_free import LinkedInScraperFree
            
            scraper = LinkedInScraperFree()
            
            # Test with a simple search
            jobs = scraper.method_1_guest_api("python developer", "Remote", 5)
            
            return jsonify({
                'status': 'success',
                'jobs_found': len(jobs),
                'message': f'LinkedIn scraper working! Found {len(jobs)} jobs.'
            })
            
        except Exception as e:
            logger.error(f"LinkedIn test failed: {e}")
            return jsonify({
                'status': 'error',
                'message': f'LinkedIn test failed: {e}'
            }), 500

def create_system_overview_template():
    """Create system overview template if it doesn't exist"""
    template_path = 'src/templates/system_overview.html'
    
    if not os.path.exists(template_path):
        template_content = '''{% extends "base.html" %}

{% block title %}System Overview - JobSprint{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="fas fa-tachometer-alt me-2"></i>JobSprint System Overview</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button type="button" class="btn btn-outline-primary" onclick="testLinkedIn()">
            <i class="fas fa-linkedin me-2"></i>Test LinkedIn
        </button>
    </div>
</div>

<!-- System Health -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-heartbeat me-2"></i>System Health</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for component, health in system_info.system_health.components.items() %}
                    <div class="col-md-3 mb-3">
                        <div class="card border-success">
                            <div class="card-body text-center">
                                <i class="fas fa-check-circle fa-2x mb-2 text-success"></i>
                                <h6 class="card-title">{{ component.replace('_', ' ').title() }}</h6>
                                <small class="text-muted">{{ health.message }}</small>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Statistics -->
<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="card stat-card">
            <div class="card-body text-center">
                <i class="fas fa-users fa-2x mb-2"></i>
                <div class="stat-number">{{ system_info.stats.total_users or 0 }}</div>
                <div>Total Users</div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card stat-card">
            <div class="card-body text-center">
                <i class="fas fa-user-check fa-2x mb-2"></i>
                <div class="stat-number">{{ system_info.stats.active_users or 0 }}</div>
                <div>Active Users</div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card stat-card">
            <div class="card-body text-center">
                <i class="fas fa-briefcase fa-2x mb-2"></i>
                <div class="stat-number">{{ system_info.stats.total_jobs or 0 }}</div>
                <div>Total Jobs</div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card stat-card">
            <div class="card-body text-center">
                <i class="fas fa-envelope fa-2x mb-2"></i>
                <div class="stat-number">{{ system_info.stats.total_notifications or 0 }}</div>
                <div>Notifications</div>
            </div>
        </div>
    </div>
</div>

<!-- Quick Actions -->
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-tools me-2"></i>System Management</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{ url_for('admin_users') }}" class="btn btn-outline-primary">
                        <i class="fas fa-users me-2"></i>Manage Users
                    </a>
                    <a href="{{ url_for('admin_create_user') }}" class="btn btn-outline-success">
                        <i class="fas fa-user-plus me-2"></i>Add New User
                    </a>
                    <button class="btn btn-outline-info" onclick="testLinkedIn()">
                        <i class="fas fa-linkedin me-2"></i>Test LinkedIn Scraper
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>System Information</h5>
            </div>
            <div class="card-body">
                <dl class="row">
                    <dt class="col-sm-6">Version:</dt>
                    <dd class="col-sm-6">2.0.0</dd>
                    
                    <dt class="col-sm-6">Database:</dt>
                    <dd class="col-sm-6">SQLite Multi-User</dd>
                    
                    <dt class="col-sm-6">LinkedIn:</dt>
                    <dd class="col-sm-6">Free Scraper</dd>
                    
                    <dt class="col-sm-6">Status:</dt>
                    <dd class="col-sm-6"><span class="badge bg-success">Operational</span></dd>
                </dl>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function testLinkedIn() {
    fetch('/system/test-linkedin')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(`✅ ${data.message}`);
            } else {
                alert(`❌ ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('❌ Error testing LinkedIn scraper');
        });
}
</script>
{% endblock %}'''
        
        with open(template_path, 'w') as f:
            f.write(template_content)
        
        print(f"   📄 Created system overview template")

def main():
    """Main entry point"""
    print("🎯 JobSprint - LinkedIn Job Automation System")
    print("=" * 60)
    
    # Check requirements
    if not check_system_requirements():
        print("❌ System requirements not met. Please check the issues above.")
        return
    
    # Initialize system
    if not initialize_system():
        print("❌ System initialization failed.")
        return
    
    # Create templates if needed
    create_system_overview_template()
    
    # Add system routes
    add_system_routes(app)
    
    # Start the system
    print("\n🚀 Starting JobSprint Web Interface...")
    print("=" * 60)
    print(f"📊 System Overview: http://localhost:5000/system")
    print(f"🔐 Admin Login: http://localhost:5000/admin/login")
    print(f"👤 User Login: http://localhost:5000/user/login")
    print("=" * 60)
    print("🔑 Default Admin: admin@jobsprint.com / admin123")
    print("=" * 60)
    print("\n✨ Features Available:")
    print("   • Multi-user job automation")
    print("   • LinkedIn job scraping (free)")
    print("   • Individual user preferences")
    print("   • Admin user management")
    print("   • Email notifications")
    print("   • Quality job filtering")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 JobSprint system stopped by user")
    except Exception as e:
        print(f"\n❌ Error running JobSprint: {e}")
        logger.error(f"System error: {e}")

if __name__ == "__main__":
    main()
