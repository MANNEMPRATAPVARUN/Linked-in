"""
🚀 JobSprint Enhanced - Simple Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

app = FastAPI(
    title="JobSprint Enhanced",
    description="Modern LinkedIn Job Alert System",
    version="2.0.0",
    docs_url="/api/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JobSprint Enhanced",
        "version": "2.0.0"
    }

@app.get("/api/jobs")
async def get_jobs():
    """Get sample jobs for testing"""
    return {
        "jobs": [
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
        ],
        "total": 5
    }

@app.get("/api/search")
async def search_jobs(keywords: str = "", location: str = "", job_type: str = ""):
    """Search jobs with filters"""
    all_jobs = [
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
    
    # Simple filtering
    filtered_jobs = []
    for job in all_jobs:
        if keywords.lower() in job["title"].lower() or keywords.lower() in job["description"].lower() or not keywords:
            if location.lower() in job["location"].lower() or not location:
                if job_type.lower() == job["type"].lower() or not job_type:
                    filtered_jobs.append(job)
    
    return {
        "jobs": filtered_jobs,
        "total": len(filtered_jobs),
        "filters": {
            "keywords": keywords,
            "location": location,
            "job_type": job_type
        }
    }

if __name__ == "__main__":
    print("🚀 Starting JobSprint Enhanced Server...")
    print("📱 Frontend: http://localhost:8000")
    print("🔧 API Docs: http://localhost:8000/api/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
