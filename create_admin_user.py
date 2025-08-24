#!/usr/bin/env python3
"""
🔐 CREATE ADMIN USER
Initialize the admin user in the database
"""

import os
import sys
import hashlib
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from supabase_manager import SupabaseManager

def create_admin_user():
    """Create the admin user"""
    print("🔐 Creating Admin User...")
    
    try:
        # Initialize Supabase manager
        supabase_manager = SupabaseManager()
        
        # Admin credentials
        admin_email = "admin@jobsprint.com"
        admin_password = "admin123"
        admin_name = "JobSprint Admin"
        
        # Check if admin already exists
        existing_admin = supabase_manager.get_user_by_email(admin_email)
        if existing_admin:
            print(f"  ✅ Admin user already exists: {admin_email}")
            print(f"  🔑 Password: {admin_password}")
            return True
        
        # Create admin user
        print(f"  🚀 Creating admin user: {admin_email}")
        admin_user = supabase_manager.create_user(
            email=admin_email,
            name=admin_name,
            password=admin_password,
            is_admin=True
        )
        
        if admin_user:
            print(f"  ✅ Admin user created successfully!")
            print(f"  📧 Email: {admin_email}")
            print(f"  🔑 Password: {admin_password}")
            print(f"  👑 Admin privileges: Yes")
            return True
        else:
            print(f"  ❌ Failed to create admin user")
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating admin user: {e}")
        return False

def create_test_user():
    """Create a test regular user"""
    print("\n👤 Creating Test User...")
    
    try:
        supabase_manager = SupabaseManager()
        
        # Test user credentials
        test_email = "test@jobsprint.com"
        test_password = "test123"
        test_name = "Test User"
        
        # Check if test user already exists
        existing_user = supabase_manager.get_user_by_email(test_email)
        if existing_user:
            print(f"  ✅ Test user already exists: {test_email}")
            print(f"  🔑 Password: {test_password}")
            return True
        
        # Create test user
        print(f"  🚀 Creating test user: {test_email}")
        test_user = supabase_manager.create_user(
            email=test_email,
            name=test_name,
            password=test_password,
            is_admin=False
        )
        
        if test_user:
            print(f"  ✅ Test user created successfully!")
            print(f"  📧 Email: {test_email}")
            print(f"  🔑 Password: {test_password}")
            print(f"  👤 Admin privileges: No")
            return True
        else:
            print(f"  ❌ Failed to create test user")
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating test user: {e}")
        return False

def test_admin_login():
    """Test admin login"""
    print("\n🧪 Testing Admin Login...")
    
    try:
        supabase_manager = SupabaseManager()
        
        # Test admin authentication
        admin_user = supabase_manager.authenticate_user("admin@jobsprint.com", "admin123")
        
        if admin_user:
            print(f"  ✅ Admin login test successful!")
            print(f"  👑 Is Admin: {admin_user.get('is_admin', False)}")
            print(f"  📧 Email: {admin_user.get('email')}")
            print(f"  👤 Name: {admin_user.get('name')}")
            return True
        else:
            print(f"  ❌ Admin login test failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing admin login: {e}")
        return False

def main():
    print("🚀 INITIALIZING JOBSPRINT USERS")
    print("=" * 50)
    
    # Create admin user
    admin_success = create_admin_user()
    
    # Create test user
    test_success = create_test_user()
    
    # Test admin login
    login_success = test_admin_login()
    
    print("\n" + "=" * 50)
    print("📊 INITIALIZATION RESULTS")
    print("=" * 50)
    
    print(f"🔐 Admin User: {'✅ SUCCESS' if admin_success else '❌ FAILED'}")
    print(f"👤 Test User: {'✅ SUCCESS' if test_success else '❌ FAILED'}")
    print(f"🧪 Login Test: {'✅ SUCCESS' if login_success else '❌ FAILED'}")
    
    if admin_success and login_success:
        print(f"\n🎉 ALL USERS INITIALIZED SUCCESSFULLY!")
        print(f"\n🔗 Now you can login:")
        print(f"   Admin: admin@jobsprint.com / admin123")
        print(f"   Test:  test@jobsprint.com / test123")
        print(f"\n🌐 Frontend: http://127.0.0.1:3000")
        print(f"🚂 Backend:  http://127.0.0.1:5000")
    else:
        print(f"\n❌ SOME INITIALIZATION FAILED")
        print(f"Check the errors above and try again")

if __name__ == "__main__":
    main()
