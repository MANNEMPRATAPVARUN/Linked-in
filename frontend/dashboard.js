// Dashboard-specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Job search form handler
    const jobSearchForm = document.getElementById('jobSearchForm');
    if (jobSearchForm) {
        jobSearchForm.addEventListener('submit', handleJobSearch);
    }
    
    // Load initial stats
    JobSprint.updateStats();
    
    // Auto-refresh stats every 30 seconds
    setInterval(() => {
        JobSprint.updateStats();
    }, 30000);
});

function initializeDashboard() {
    // Set default values
    const keywordsInput = document.getElementById('keywords');
    if (keywordsInput && !keywordsInput.value) {
        keywordsInput.value = 'software engineer, python developer';
    }
    
    const locationSelect = document.getElementById('location');
    if (locationSelect && !locationSelect.value) {
        locationSelect.value = 'Canada Remote';
    }
    
    // Show welcome message
    setTimeout(() => {
        JobSprint.showAlert(`
            <strong>🎉 Welcome to JobSprint Dashboard!</strong><br>
            • Configure your search preferences below<br>
            • Use ultra-recent filtering for first applicant advantage<br>
            • All job searches are optimized for Canadian locations
        `, 'info');
    }, 1000);
}

async function handleJobSearch(e) {
    e.preventDefault();
    
    const keywords = document.getElementById('keywords').value;
    const location = document.getElementById('location').value;
    const timeFilter = document.getElementById('timeFilter').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!keywords || !location) {
        JobSprint.showAlert('Please fill in both keywords and location', 'warning');
        return;
    }
    
    const stopLoading = JobSprint.showLoading(submitBtn);
    
    try {
        JobSprint.showAlert('🔍 Searching for ultra-recent jobs...', 'info');
        
        const response = await JobSprint.searchJobs(keywords, location, timeFilter);
        
        if (response.success) {
            JobSprint.displayJobResults(response.jobs);
            
            const timeFilterText = getTimeFilterText(timeFilter);
            JobSprint.showAlert(`
                ✅ Found ${response.jobs.length} jobs posted in ${timeFilterText}!<br>
                <small>Jobs are sorted by posting time and quality score</small>
            `, 'success');
            
            // Update stats
            JobSprint.updateStats();
            
            // Scroll to results
            setTimeout(() => {
                document.getElementById('jobResults').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 500);
        }
    } catch (error) {
        console.error('Job search error:', error);
        JobSprint.showAlert(`Job search failed: ${error.message}`, 'danger');
    } finally {
        stopLoading();
    }
}

function getTimeFilterText(timeFilter) {
    const filters = {
        'r300': 'the last 5 minutes',
        'r600': 'the last 10 minutes', 
        'r1800': 'the last 30 minutes',
        'r3600': 'the last hour',
        'r86400': 'the last 24 hours'
    };
    return filters[timeFilter] || 'the specified time period';
}

// Auto-complete functionality for keywords
function setupKeywordAutocomplete() {
    const keywordsInput = document.getElementById('keywords');
    if (!keywordsInput) return;
    
    const commonKeywords = [
        'software engineer',
        'python developer',
        'java developer',
        'full stack developer',
        'frontend developer',
        'backend developer',
        'devops engineer',
        'data scientist',
        'machine learning engineer',
        'product manager',
        'ui/ux designer',
        'qa engineer',
        'system administrator',
        'cloud architect',
        'mobile developer',
        'react developer',
        'node.js developer',
        'angular developer',
        'vue.js developer',
        'php developer'
    ];
    
    // Simple autocomplete implementation
    keywordsInput.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        const suggestions = commonKeywords.filter(keyword => 
            keyword.toLowerCase().includes(value) && value.length > 2
        );
        
        // You could implement a dropdown here
        if (suggestions.length > 0) {
            this.setAttribute('title', `Suggestions: ${suggestions.slice(0, 3).join(', ')}`);
        }
    });
}

// Initialize autocomplete
setTimeout(setupKeywordAutocomplete, 1000);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to search
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const searchForm = document.getElementById('jobSearchForm');
        if (searchForm) {
            searchForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Ctrl/Cmd + P to open preferences
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        JobSprint.showPreferences();
    }
});

// Real-time job updates simulation (demo mode)
function startRealTimeUpdates() {
    if (!window.CONFIG || !window.CONFIG.DEMO_MODE) return;
    
    setInterval(() => {
        const jobCount = document.getElementById('jobCount');
        const recentJobs = document.getElementById('recentJobs');
        
        if (jobCount && jobCount.textContent !== '0 jobs') {
            // Simulate new job discovery
            const currentCount = parseInt(recentJobs.textContent) || 0;
            if (Math.random() > 0.7) { // 30% chance of new job
                recentJobs.textContent = currentCount + 1;
                
                // Show notification
                JobSprint.showAlert(`
                    🚨 <strong>New Ultra-Recent Job Found!</strong><br>
                    <small>A job matching your criteria was posted ${Math.floor(Math.random() * 5) + 1} minutes ago</small>
                `, 'success');
            }
        }
    }, 60000); // Check every minute
}

// Start real-time updates
setTimeout(startRealTimeUpdates, 5000);

// Export dashboard functions
window.Dashboard = {
    handleJobSearch,
    getTimeFilterText,
    setupKeywordAutocomplete,
    startRealTimeUpdates
};
