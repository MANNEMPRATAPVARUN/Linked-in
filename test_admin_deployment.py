#!/usr/bin/env python3
"""
🧪 Test Admin Page Deployment
Quick test to verify admin.html is deployed to Vercel
"""

import requests
import time

def test_admin_page():
    print("🧪 Testing Admin Page Deployment...")
    
    urls_to_test = [
        "https://jobsprint-frontend.vercel.app/",
        "https://jobsprint-frontend.vercel.app/admin.html",
        "https://jobsprint-frontend.vercel.app/dashboard.html"
    ]
    
    for url in urls_to_test:
        try:
            print(f"\n🔍 Testing: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS: Status {response.status_code}")
                if "admin" in url.lower():
                    if "Admin Panel" in response.text:
                        print(f"  ✅ Admin content found!")
                    else:
                        print(f"  ⚠️ Admin content not found in response")
            else:
                print(f"  ❌ FAILED: Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"If admin.html shows 404, wait 1-2 minutes for Vercel deployment")
    print(f"Then test: https://jobsprint-frontend.vercel.app/admin.html")

if __name__ == "__main__":
    test_admin_page()
