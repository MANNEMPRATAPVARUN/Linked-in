// JobSprint Frontend JavaScript

// Configuration
const CONFIG = {
    API_BASE_URL: 'https://web-production-f50b3.up.railway.app/api', // Your Railway API URL
    LOCAL_API_URL: 'http://localhost:5000/api', // For local development
    DEMO_MODE: false // API is ready - disable demo mode
};

// Get API URL based on environment
function getApiUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return CONFIG.LOCAL_API_URL;
    }
    return CONFIG.API_BASE_URL;
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of page
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Loading...';
    button.disabled = true;
    
    return () => {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Modal Functions
function showLogin() {
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
}

function showAdminLogin() {
    const modal = new bootstrap.Modal(document.getElementById('adminLoginModal'));
    modal.show();
}

function showDemo() {
    showAlert(`
        <strong>🚀 Demo Mode Active!</strong><br>
        • Ultra-recent filtering finds jobs in 5-10 minutes<br>
        • 108 Canada locations optimized for better results<br>
        • Real-time notifications and job management<br>
        • Professional admin panel with user management
    `, 'info');
}

// API Functions
async function apiCall(endpoint, options = {}) {
    const url = `${getApiUrl()}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session management
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Authentication Functions
async function login(email, password) {
    if (CONFIG.DEMO_MODE) {
        // Demo mode - simulate successful login
        showAlert('🎉 Demo login successful! In production, this would authenticate with the Railway API.', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 2000);
        return;
    }
    
    try {
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (response.success) {
            showAlert('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        }
    } catch (error) {
        showAlert(`Login failed: ${error.message}`, 'danger');
    }
}

async function adminLogin(email, password) {
    if (CONFIG.DEMO_MODE) {
        // Demo mode - simulate successful admin login
        showAlert('🔐 Demo admin login successful! In production, this would authenticate with the Railway API.', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html?admin=true';
        }, 2000);
        return;
    }
    
    try {
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (response.success && response.user.is_admin) {
            showAlert('Admin login successful! Redirecting to admin dashboard...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html?admin=true';
            }, 1500);
        } else {
            throw new Error('Admin access required');
        }
    } catch (error) {
        showAlert(`Admin login failed: ${error.message}`, 'danger');
    }
}

// Job Search Functions
async function searchJobs(keywords, location, timeFilter = 'r3600') {
    if (CONFIG.DEMO_MODE) {
        // Return demo data
        return {
            success: true,
            jobs: [
                {
                    title: 'Senior Python Developer',
                    company: 'TechCorp Inc.',
                    location: 'Toronto, ON',
                    job_url: 'https://linkedin.com/jobs/demo1',
                    quality_score: 85,
                    posted_date: new Date(Date.now() - 5 * 60 * 1000).toISOString() // 5 minutes ago
                },
                {
                    title: 'Full Stack Engineer',
                    company: 'StartupXYZ',
                    location: 'Canada Remote',
                    job_url: 'https://linkedin.com/jobs/demo2',
                    quality_score: 78,
                    posted_date: new Date(Date.now() - 8 * 60 * 1000).toISOString() // 8 minutes ago
                },
                {
                    title: 'Software Architect',
                    company: 'MegaCorp Ltd.',
                    location: 'Vancouver, BC',
                    job_url: 'https://linkedin.com/jobs/demo3',
                    quality_score: 92,
                    posted_date: new Date(Date.now() - 10 * 60 * 1000).toISOString() // 10 minutes ago
                }
            ],
            count: 3
        };
    }
    
    try {
        const response = await apiCall('/jobs/search', {
            method: 'POST',
            body: JSON.stringify({
                keywords,
                location,
                time_filter: timeFilter,
                max_results: 25
            })
        });
        
        return response;
    } catch (error) {
        console.error('Job search failed:', error);
        throw error;
    }
}

// Location Functions
async function getCanadaLocations() {
    if (CONFIG.DEMO_MODE) {
        return {
            locations: [
                'Canada Remote',
                'Toronto, ON',
                'Vancouver, BC',
                'Montreal, QC',
                'Calgary, AB',
                'Ottawa, ON',
                'Edmonton, AB',
                'Mississauga, ON',
                'Winnipeg, MB',
                'Quebec City, QC',
                'Hamilton, ON',
                'Brampton, ON',
                'Surrey, BC',
                'Laval, QC',
                'Halifax, NS',
                'London, ON',
                'Markham, ON',
                'Vaughan, ON',
                'Gatineau, QC',
                'Saskatoon, SK'
            ]
        };
    }
    
    try {
        const response = await apiCall('/locations/canada');
        return response;
    } catch (error) {
        console.error('Failed to get Canada locations:', error);
        throw error;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Login form handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = e.target.querySelector('button[type="submit"]');
            
            const stopLoading = showLoading(submitBtn);
            
            try {
                await login(email, password);
            } catch (error) {
                console.error('Login error:', error);
            } finally {
                stopLoading();
            }
        });
    }
    
    // Admin login form handler
    const adminLoginForm = document.getElementById('adminLoginForm');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('adminEmail').value;
            const password = document.getElementById('adminPassword').value;
            const submitBtn = e.target.querySelector('button[type="submit"]');
            
            const stopLoading = showLoading(submitBtn);
            
            try {
                await adminLogin(email, password);
            } catch (error) {
                console.error('Admin login error:', error);
            } finally {
                stopLoading();
            }
        });
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation classes to elements as they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe all cards and feature elements
    document.querySelectorAll('.card, .feature-icon').forEach(el => {
        observer.observe(el);
    });
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showAlert('An unexpected error occurred. Please try again.', 'danger');
});

// Dashboard Functions
function showJobSearch() {
    const searchForm = document.getElementById('jobSearchForm');
    if (searchForm) {
        searchForm.scrollIntoView({ behavior: 'smooth' });
        document.getElementById('keywords').focus();
    }
}

function showPreferences() {
    const modal = new bootstrap.Modal(document.getElementById('preferencesModal'));
    modal.show();
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        showAlert('Logged out successfully!', 'success');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
    }
}

async function loadCanadaLocations() {
    try {
        const response = await getCanadaLocations();
        const locationSelect = document.getElementById('location');

        // Clear existing options except the first one
        while (locationSelect.children.length > 1) {
            locationSelect.removeChild(locationSelect.lastChild);
        }

        // Add Canada locations
        response.locations.forEach(location => {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            locationSelect.appendChild(option);
        });

        showAlert('Canada locations loaded successfully!', 'success');
    } catch (error) {
        showAlert('Failed to load Canada locations', 'danger');
    }
}

function savePreferences() {
    // In demo mode, just show success message
    showAlert('Preferences saved successfully!', 'success');

    const modal = bootstrap.Modal.getInstance(document.getElementById('preferencesModal'));
    modal.hide();
}

function displayJobResults(jobs) {
    const resultsContainer = document.getElementById('jobResults');
    const jobCountBadge = document.getElementById('jobCount');

    jobCountBadge.textContent = `${jobs.length} jobs`;

    if (jobs.length === 0) {
        resultsContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-search fa-3x mb-3"></i>
                <p>No jobs found for your search criteria</p>
                <small>Try adjusting your keywords or location</small>
            </div>
        `;
        return;
    }

    const jobsHtml = jobs.map(job => {
        const timeAgo = getTimeAgo(new Date(job.posted_date));
        const qualityClass = job.quality_score >= 80 ? 'high' : job.quality_score >= 65 ? 'medium' : 'low';

        return `
            <div class="job-list-item position-relative">
                <div class="quality-score ${qualityClass}">
                    ${job.quality_score}%
                </div>
                <h6 class="job-title">${job.title}</h6>
                <p class="job-company mb-1">
                    <i class="fas fa-building me-2"></i>${job.company}
                </p>
                <p class="job-location mb-2">
                    <i class="fas fa-map-marker-alt me-2"></i>${job.location}
                    <span class="badge bg-success ms-2">${timeAgo}</span>
                </p>
                <div class="job-actions">
                    <a href="${job.job_url}" target="_blank" class="btn btn-primary btn-sm">
                        <i class="fas fa-external-link-alt me-1"></i>View Job
                    </a>
                    <button class="btn btn-outline-success btn-sm" onclick="saveJob('${job.id || 'demo'}')">
                        <i class="fas fa-bookmark me-1"></i>Save
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" onclick="hideJob('${job.id || 'demo'}')">
                        <i class="fas fa-eye-slash me-1"></i>Hide
                    </button>
                </div>
            </div>
        `;
    }).join('');

    resultsContainer.innerHTML = jobsHtml;
}

function getTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

function saveJob(jobId) {
    showAlert('Job saved successfully!', 'success');
    updateStats();
}

function hideJob(jobId) {
    showAlert('Job hidden from future results', 'info');
}

function updateStats() {
    // Update dashboard stats (demo values)
    document.getElementById('totalJobs').textContent = Math.floor(Math.random() * 50) + 10;
    document.getElementById('recentJobs').textContent = Math.floor(Math.random() * 10) + 1;
    document.getElementById('notifications').textContent = Math.floor(Math.random() * 20) + 5;
    document.getElementById('savedJobs').textContent = Math.floor(Math.random() * 15) + 2;
}

// Export functions for use in other files
window.JobSprint = {
    login,
    adminLogin,
    searchJobs,
    getCanadaLocations,
    showAlert,
    showLoading,
    apiCall,
    showJobSearch,
    showPreferences,
    logout,
    loadCanadaLocations,
    savePreferences,
    displayJobResults,
    updateStats
};
