#!/usr/bin/env python3
"""
🚀 JobSprint Enhanced - Simple Flask Server
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Sample job data
SAMPLE_JOBS = [
    {
        "id": 1,
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "location": "Toronto, ON",
        "type": "Remote",
        "posted": "2 hours ago",
        "description": "Looking for an experienced Python developer with 5+ years of experience in Django and FastAPI."
    },
    {
        "id": 2,
        "title": "DevOps Engineer",
        "company": "Cloud Solutions Inc",
        "location": "Vancouver, BC",
        "type": "Hybrid",
        "posted": "4 hours ago",
        "description": "Join our DevOps team to manage cloud infrastructure using AWS, Docker, and Kubernetes."
    },
    {
        "id": 3,
        "title": "Full Stack Developer",
        "company": "StartupXYZ",
        "location": "Montreal, QC",
        "type": "On-site",
        "posted": "1 day ago",
        "description": "Build amazing web applications with React and Node.js in a fast-paced startup environment."
    },
    {
        "id": 4,
        "title": "Data Scientist",
        "company": "AI Innovations",
        "location": "Toronto, ON",
        "type": "Remote",
        "posted": "6 hours ago",
        "description": "Apply machine learning and statistical analysis to solve complex business problems."
    },
    {
        "id": 5,
        "title": "Cybersecurity Analyst",
        "company": "SecureNet Corp",
        "location": "Ottawa, ON",
        "type": "Hybrid",
        "posted": "8 hours ago",
        "description": "Monitor and protect our systems from security threats using SIEM tools and threat intelligence."
    }
]

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('frontend', path)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "JobSprint Enhanced",
        "version": "2.0.0"
    })

@app.route('/api/jobs')
def get_jobs():
    return jsonify({
        "jobs": SAMPLE_JOBS,
        "total": len(SAMPLE_JOBS)
    })

@app.route('/api/search')
def search_jobs():
    keywords = request.args.get('keywords', '').lower()
    location = request.args.get('location', '').lower()
    job_type = request.args.get('job_type', '').lower()
    
    filtered_jobs = []
    for job in SAMPLE_JOBS:
        if (not keywords or keywords in job["title"].lower() or keywords in job["description"].lower()) and \
           (not location or location in job["location"].lower()) and \
           (not job_type or job_type == job["type"].lower()):
            filtered_jobs.append(job)
    
    return jsonify({
        "jobs": filtered_jobs,
        "total": len(filtered_jobs),
        "filters": {
            "keywords": keywords,
            "location": location,
            "job_type": job_type
        }
    })

if __name__ == '__main__':
    print("🚀 Starting JobSprint Enhanced Server...")
    print("📱 Frontend: http://localhost:5000")
    print("🔧 API Health: http://localhost:5000/health")
    print("📊 API Jobs: http://localhost:5000/api/jobs")
    app.run(host='0.0.0.0', port=5000, debug=True)
