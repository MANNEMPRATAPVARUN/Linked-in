#!/usr/bin/env python3
"""
Simple API Server for JobSprint Enhanced
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

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

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "JobSprint Enhanced API"}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/jobs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"jobs": SAMPLE_JOBS, "total": len(SAMPLE_JOBS)}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/search':
            keywords = query_params.get('keywords', [''])[0].lower()
            location = query_params.get('location', [''])[0].lower()
            job_type = query_params.get('job_type', [''])[0].lower()
            
            filtered_jobs = []
            for job in SAMPLE_JOBS:
                if (not keywords or keywords in job["title"].lower() or keywords in job["description"].lower()) and \
                   (not location or location in job["location"].lower()) and \
                   (not job_type or job_type == job["type"].lower()):
                    filtered_jobs.append(job)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "jobs": filtered_jobs,
                "total": len(filtered_jobs),
                "filters": {"keywords": keywords, "location": location, "job_type": job_type}
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    server = HTTPServer(('localhost', 5000), APIHandler)
    print("🚀 API Server running on http://localhost:5000")
    print("🔧 Health check: http://localhost:5000/health")
    print("📊 Jobs API: http://localhost:5000/api/jobs")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
