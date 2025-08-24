#!/usr/bin/env python3
"""
Integrated JobSprint System
Combines all components: LinkedIn scraping, multi-user system, continuous search, and web UI
"""

import os
import sys
import json
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from multi_user_system import MultiUserManager
from continuous_search_engine import ContinuousSearchEngine
from admin_panel import app as admin_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/integrated_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedJobSprintSystem:
    """Main system that integrates all components"""
    
    def __init__(self):
        self.user_manager = MultiUserManager()
        self.search_engine = ContinuousSearchEngine()
        self.web_app = self.create_integrated_app()
        self.is_running = False
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        logger.info("🚀 Integrated JobSprint System initialized")
    
    def create_integrated_app(self):
        """Create integrated Flask app with all features"""
        app = Flask(__name__, template_folder=os.path.join(current_dir, 'templates'))
        app.secret_key = 'jobsprint-integrated-system-secret-key'
        
        # Import all routes from admin panel
        from admin_panel import *
        
        # Add search engine management routes
        @app.route('/system/dashboard')
        def system_dashboard():
            """Main system dashboard"""
            if not session.get('is_admin'):
                return redirect(url_for('admin_login'))
            
            # Get system statistics
            user_stats = self.user_manager.get_system_stats()
            search_status = self.search_engine.get_system_status()
            
            system_info = {
                'users': user_stats,
                'search_engine': search_status,
                'system_health': self.get_system_health()
            }
            
            return render_template('system_dashboard.html', 
                                 system_info=system_info,
                                 current_user=session)
        
        @app.route('/system/search-engine/start', methods=['POST'])
        def start_integrated_search():
            """Start the integrated search engine"""
            if not session.get('is_admin'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            try:
                if not self.search_engine.is_running:
                    # Start in background thread
                    search_thread = threading.Thread(
                        target=self.search_engine.start_continuous_search, 
                        daemon=True
                    )
                    search_thread.start()
                    
                    flash('Continuous search engine started!', 'success')
                else:
                    flash('Search engine is already running', 'info')
                
                return redirect(url_for('system_dashboard'))
                
            except Exception as e:
                flash(f'Error starting search engine: {e}', 'error')
                return redirect(url_for('system_dashboard'))
        
        @app.route('/system/search-engine/stop', methods=['POST'])
        def stop_integrated_search():
            """Stop the integrated search engine"""
            if not session.get('is_admin'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            try:
                self.search_engine.stop_continuous_search()
                flash('Search engine stopped!', 'success')
                return redirect(url_for('system_dashboard'))
                
            except Exception as e:
                flash(f'Error stopping search engine: {e}', 'error')
                return redirect(url_for('system_dashboard'))
        
        @app.route('/system/api/health')
        def system_health_api():
            """System health API endpoint"""
            if not session.get('is_admin'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            health = self.get_system_health()
            return jsonify(health)
        
        @app.route('/system/test-search/<user_id>', methods=['POST'])
        def test_user_search_integrated(user_id):
            """Test search for a specific user"""
            if not session.get('is_admin'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            try:
                # Run search in background
                def run_test():
                    self.search_engine.search_jobs_for_user(user_id)
                
                test_thread = threading.Thread(target=run_test, daemon=True)
                test_thread.start()
                
                flash('Test search started for user', 'info')
                return redirect(url_for('system_dashboard'))
                
            except Exception as e:
                flash(f'Error running test search: {e}', 'error')
                return redirect(url_for('system_dashboard'))
        
        # Override the default index route
        @app.route('/')
        def integrated_index():
            """Main landing page"""
            if 'user_id' in session:
                if session.get('is_admin'):
                    return redirect(url_for('system_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            return redirect(url_for('user_login'))
        
        return app
    
    def get_system_health(self):
        """Get overall system health status"""
        try:
            health = {
                'status': 'healthy',
                'components': {
                    'database': self.check_database_health(),
                    'search_engine': self.check_search_engine_health(),
                    'linkedin_scraper': self.check_linkedin_health(),
                    'email_system': self.check_email_health()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Overall status based on components
            if any(comp['status'] == 'error' for comp in health['components'].values()):
                health['status'] = 'error'
            elif any(comp['status'] == 'warning' for comp in health['components'].values()):
                health['status'] = 'warning'
            
            return health
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_database_health(self):
        """Check database health"""
        try:
            users = self.user_manager.get_all_users()
            return {
                'status': 'healthy',
                'message': f'Database operational with {len(users)} users'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database error: {e}'
            }
    
    def check_search_engine_health(self):
        """Check search engine health"""
        try:
            status = self.search_engine.get_system_status()
            if status['is_running']:
                return {
                    'status': 'healthy',
                    'message': f'Search engine running with {status["active_users"]} active users'
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Search engine is stopped'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Search engine error: {e}'
            }
    
    def check_linkedin_health(self):
        """Check LinkedIn scraper health"""
        try:
            # Simple test - create scraper instance
            from linkedin_scraper_free import LinkedInScraperFree
            scraper = LinkedInScraperFree()
            
            return {
                'status': 'healthy',
                'message': 'LinkedIn scraper operational'
            }
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'LinkedIn scraper issue: {e}'
            }
    
    def check_email_health(self):
        """Check email system health"""
        try:
            config_file = 'config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                email_config = config.get('email', {})
                if email_config.get('sender_email') and email_config.get('sender_password'):
                    return {
                        'status': 'healthy',
                        'message': 'Email system configured'
                    }
                else:
                    return {
                        'status': 'warning',
                        'message': 'Email system not fully configured'
                    }
            else:
                return {
                    'status': 'warning',
                    'message': 'Configuration file not found'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Email system error: {e}'
            }
    
    def start_system(self, host='0.0.0.0', port=5000, debug=False):
        """Start the integrated system"""
        try:
            self.is_running = True
            
            print("🚀 Starting JobSprint Integrated System...")
            print("=" * 60)
            print(f"📊 System Dashboard: http://localhost:{port}/system/dashboard")
            print(f"👤 User Login: http://localhost:{port}/user/login")
            print(f"🔐 Admin Login: http://localhost:{port}/admin/login")
            print("=" * 60)
            print("🔑 Default Admin: admin@jobsprint.com / admin123")
            print("=" * 60)
            
            logger.info("🎉 JobSprint Integrated System started successfully")
            
            # Start the web application
            self.web_app.run(host=host, port=port, debug=debug)
            
        except Exception as e:
            logger.error(f"Error starting integrated system: {e}")
            raise
    
    def stop_system(self):
        """Stop the integrated system"""
        try:
            self.is_running = False
            
            # Stop search engine if running
            if self.search_engine.is_running:
                self.search_engine.stop_continuous_search()
            
            logger.info("🛑 JobSprint Integrated System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping integrated system: {e}")

def main():
    """Main entry point"""
    try:
        # Create and start the integrated system
        system = IntegratedJobSprintSystem()
        system.start_system(port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down JobSprint System...")
        if 'system' in locals():
            system.stop_system()
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        logger.error(f"System startup error: {e}")

if __name__ == "__main__":
    main()
