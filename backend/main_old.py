"""
íº€ JobSprint Enhanced - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JobSprint Enhanced",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "JobSprint Enhanced API",
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
