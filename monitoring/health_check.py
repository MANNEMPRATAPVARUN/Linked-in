#!/usr/bin/env python3
"""
🔍 JOBSPRINT PRODUCTION MONITORING
Comprehensive health checks and monitoring for production deployment
"""

import requests
import time
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobSprintMonitor:
    def __init__(self):
        self.backend_url = "https://web-production-f50b3.up.railway.app"
        self.frontend_url = "https://jobsprint-frontend.vercel.app"
        self.admin_credentials = {
            "email": "admin@jobsprint.com",
            "password": "admin123"
        }
        
    def check_backend_health(self):
        """Check backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Backend healthy: {data['service']} - {data['status']}")
                return True
            else:
                logger.error(f"❌ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend check failed: {e}")
            return False
    
    def check_frontend_availability(self):
        """Check frontend availability"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Frontend accessible")
                return True
            else:
                logger.error(f"❌ Frontend error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Frontend check failed: {e}")
            return False
    
    def test_authentication(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('user', {}).get('is_admin'):
                    logger.info("✅ Admin authentication working")
                    return True
            logger.error("❌ Admin authentication failed")
            return False
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return False
    
    def test_job_search(self):
        """Test LinkedIn job search functionality"""
        try:
            # Login first
            session = requests.Session()
            login_response = session.post(
                f"{self.backend_url}/api/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if login_response.status_code != 200:
                logger.error("❌ Login failed for job search test")
                return False
            
            # Test job search
            search_data = {
                "keywords": "software engineer",
                "location": "Toronto, ON",
                "max_results": 1,
                "time_filter": "r86400"
            }
            
            search_response = session.post(
                f"{self.backend_url}/api/jobs/search",
                json=search_data,
                timeout=30
            )
            
            if search_response.status_code == 200:
                data = search_response.json()
                if data.get('success'):
                    job_count = data.get('count', 0)
                    logger.info(f"✅ Job search working: {job_count} jobs found")
                    return True
            
            logger.error("❌ Job search failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Job search test failed: {e}")
            return False
    
    def run_comprehensive_check(self):
        """Run all health checks"""
        logger.info("🔍 Starting comprehensive health check...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'backend_health': self.check_backend_health(),
            'frontend_availability': self.check_frontend_availability(),
            'authentication': self.test_authentication(),
            'job_search': self.test_job_search()
        }
        
        # Calculate overall health
        all_healthy = all(results[key] for key in results if key != 'timestamp')
        
        if all_healthy:
            logger.info("🎉 ALL SYSTEMS HEALTHY!")
            status = "HEALTHY"
        else:
            logger.warning("⚠️ SOME SYSTEMS HAVE ISSUES")
            status = "DEGRADED"
        
        results['overall_status'] = status
        
        # Save results
        with open('monitoring/health_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def monitor_continuously(self, interval_minutes=5):
        """Run continuous monitoring"""
        logger.info(f"🔄 Starting continuous monitoring (every {interval_minutes} minutes)")
        
        while True:
            try:
                results = self.run_comprehensive_check()
                
                if results['overall_status'] != 'HEALTHY':
                    logger.warning("🚨 ALERT: System degraded!")
                    # Here you could add email/Slack notifications
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("👋 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    monitor = JobSprintMonitor()
    
    print("🔍 JobSprint Production Monitor")
    print("=" * 50)
    print("1. Run single health check")
    print("2. Start continuous monitoring")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        results = monitor.run_comprehensive_check()
        print(f"\n📊 Health Check Results:")
        print(f"Overall Status: {results['overall_status']}")
        
    elif choice == '2':
        interval = input("Enter monitoring interval in minutes (default: 5): ").strip()
        interval = int(interval) if interval.isdigit() else 5
        monitor.monitor_continuously(interval)
        
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
