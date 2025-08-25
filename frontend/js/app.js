/**
 * Ì∫Ä JobSprint Enhanced - Frontend JavaScript
 */

const API_BASE_URL = 'http://localhost:8000';
const DEMO_MODE = true;

let currentUser = null;
let currentJobs = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log('Ì∫Ä JobSprint Enhanced initialized');
    setupEventListeners();
    checkBackendHealth();
});

function setupEventListeners() {
    const quickSearchForm = document.getElementById('quickSearchForm');
    if (quickSearchForm) {
        quickSearchForm.addEventListener('submit', handleQuickSearch);
    }
    
    const advancedSearchForm = document.getElementById('advancedSearchForm');
    if (advancedSearchForm) {
        advancedSearchForm.addEventListener('submit', handleAdvancedSearch);
    }
}

async function handleQuickSearch(event) {
    event.preventDefault();
    
    const searchParams = {
        keywords: document.getElementById('keywords').value,
        location: document.getElementById('location').value,
        time_filter: document.getElementById('timeFilter').value,
        max_results: 25
    };
    
    await performJobSearch(searchParams);
}

async function performJobSearch(params) {
    showSearchLoading(true);
    
    try {
        let jobs = await simulateJobSearch(params);
        currentJobs = jobs;
        displaySearchResults(jobs, params);
        updateDashboardStats();
    } catch (error) {
        console.error('Search failed:', error);
        showAlert('Search failed. Please try again.', 'danger');
    } finally {
        showSearchLoading(false);
    }
}

async function simulateJobSearch(params) {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return [
        {
            id: 1,
            title: `Senior ${params.keywords}`,
            company: 'TechCorp Inc.',
            location: params.location,
            job_url: 'https://linkedin.com/jobs/view/demo-1',
            posted_date: new Date().toISOString(),
            category: 'Software Development',
            description: 'Exciting opportunity for an experienced developer...',
            salary_min: 80000,
            salary_max: 120000
        },
        {
            id: 2,
            title: `${params.keywords} Specialist`,
            company: 'Innovation Labs',
            location: params.location,
            job_url: 'https://linkedin.com/jobs/view/demo-2',
            posted_date: new Date().toISOString(),
            category: 'Technology',
            description: 'Join our dynamic team...',
            salary_min: 70000,
            salary_max: 100000
        }
    ];
}

function displaySearchResults(jobs, searchParams) {
    const jobsList = document.getElementById('jobsList');
    
    if (!jobs || jobs.length === 0) {
        jobsList.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <p class="text-muted">No jobs found. Try different criteria.</p>
            </div>
        `;
        return;
    }
    
    const jobsHTML = jobs.map(job => createJobCard(job)).join('');
    jobsList.innerHTML = jobsHTML;
    
    document.getElementById('newJobsCount').textContent = jobs.length;
}

function createJobCard(job) {
    const postedDate = new Date(job.posted_date).toLocaleDateString();
    const salaryRange = job.salary_min && job.salary_max 
        ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`
        : 'Salary not specified';
    
    return `
        <div class="card job-card mb-3">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h5 class="card-title">
                            <a href="${job.job_url}" target="_blank" class="text-decoration-none">
                                ${job.title}
                            </a>
                        </h5>
                        <h6 class="card-subtitle mb-2 text-muted">
                            <i class="fas fa-building me-1"></i>${job.company}
                        </h6>
                        <p class="card-text">
                            <i class="fas fa-map-marker-alt me-1"></i>${job.location}
                            <span class="ms-3">
                                <i class="fas fa-calendar me-1"></i>Posted ${postedDate}
                            </span>
                        </p>
                        <p class="card-text">${job.description.substring(0, 150)}...</p>
                        <p class="card-text">
                            <small class="text-muted">
                                <i class="fas fa-dollar-sign me-1"></i>${salaryRange}
                            </small>
                        </p>
                    </div>
                    <div class="col-md-4 text-end">
                        <span class="badge bg-primary status-badge mb-2">${job.category}</span>
                        <div class="btn-group-vertical w-100">
                            <button class="btn btn-outline-primary btn-sm" onclick="saveJob(${job.id})">
                                <i class="fas fa-bookmark me-1"></i>Save Job
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="applyToJob('${job.job_url}')">
                                <i class="fas fa-external-link-alt me-1"></i>Apply Now
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showSearchLoading(show) {
    const searchBtn = document.querySelector('#quickSearchForm button[type="submit"]');
    if (show) {
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Searching...';
        searchBtn.disabled = true;
    } else {
        searchBtn.innerHTML = '<i class="fas fa-search me-1"></i>Search';
        searchBtn.disabled = false;
    }
}

function showAlert(message, type = 'info') {
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const mainContent = document.querySelector('.col-md-9');
    if (mainContent) {
        mainContent.insertAdjacentHTML('afterbegin', alertHTML);
    }
}

function showSection(sectionName) {
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.style.display = 'none';
    });
    
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

function showLogin() {
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

function saveJob(jobId) {
    showAlert('Job saved successfully!', 'success');
}

function applyToJob(jobUrl) {
    window.open(jobUrl, '_blank');
}

function refreshJobs() {
    const searchParams = {
        keywords: 'software engineer',
        location: 'Canada',
        time_filter: 'r86400',
        max_results: 25
    };
    performJobSearch(searchParams);
}

function updateDashboardStats() {
    document.getElementById('savedJobsCount').textContent = Math.floor(Math.random() * 20) + 5;
    document.getElementById('applicationsCount').textContent = Math.floor(Math.random() * 10) + 2;
    document.getElementById('successRate').textContent = Math.floor(Math.random() * 30) + 15 + '%';
}

async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const health = await response.json();
            console.log('‚úÖ Backend health:', health);
        }
    } catch (error) {
        console.log('‚ö†Ô∏è Backend not available, running in demo mode');
    }
}

// Global functions
window.showSection = showSection;
window.showLogin = showLogin;
window.saveJob = saveJob;
window.applyToJob = applyToJob;
window.refreshJobs = refreshJobs;
