// ProfileScope Web Interface JavaScript

// Utility functions
const formatDateTime = (isoString) => {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
};

const formatDuration = (seconds) => {
    if (!seconds) return '-';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    const parts = [];
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (remainingSeconds > 0 || parts.length === 0) parts.push(`${remainingSeconds}s`);
    
    return parts.join(' ');
};

// Chart utility functions
function createRadarChart(ctx, data) {
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    min: 0,
                    max: 1,
                    ticks: {
                        stepSize: 0.2
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function createBarChart(ctx, data) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Task management
class TaskManager {
    constructor(taskId) {
        this.taskId = taskId;
        this.pollInterval = 2000; // Poll every 2 seconds
        this.polling = false;
        
        // UI Elements
        this.container = document.getElementById('taskContainer');
        this.progressBar = document.getElementById('taskProgress');
        this.statusBadge = document.getElementById('taskStatus');
        this.messageEl = document.getElementById('taskMessage');
        this.errorEl = document.getElementById('taskError');
        this.cancelBtn = document.getElementById('cancelTask');
        
        // Bind event listeners
        if (this.cancelBtn) {
            this.cancelBtn.addEventListener('click', () => this.cancelTask());
        }
    }
    
    startPolling() {
        if (!this.polling) {
            this.polling = true;
            this.poll();
        }
    }
    
    stopPolling() {
        this.polling = false;
    }
    
    async poll() {
        while (this.polling) {
            try {
                const response = await fetch(`/api/tasks/${this.taskId}/status`);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || 'Failed to fetch task status');
                }
                
                this.updateUI(data);
                
                if (['completed', 'failed', 'cancelled'].includes(data.status)) {
                    this.stopPolling();
                    if (data.status === 'completed') {
                        window.location.href = `/result/${this.taskId}`;
                    }
                } else {
                    await new Promise(resolve => setTimeout(resolve, this.pollInterval));
                }
            } catch (error) {
                console.error('Error polling task status:', error);
                this.showError(error.message);
                this.stopPolling();
            }
        }
    }
    
    updateUI(data) {
        // Update progress bar
        if (this.progressBar) {
            this.progressBar.style.width = `${data.progress}%`;
            this.progressBar.setAttribute('aria-valuenow', data.progress);
            this.progressBar.textContent = `${data.progress}%`;
        }
        
        // Update status badge
        if (this.statusBadge) {
            this.statusBadge.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            this.statusBadge.className = `badge ${this.getStatusBadgeClass(data.status)}`;
        }
        
        // Update message
        if (this.messageEl) {
            this.messageEl.textContent = data.message || 'Processing...';
        }
        
        // Update error message if any
        if (this.errorEl) {
            if (data.error) {
                this.errorEl.textContent = data.error;
                this.errorEl.style.display = 'block';
            } else {
                this.errorEl.style.display = 'none';
            }
        }
    }
    
    getStatusBadgeClass(status) {
        const statusClasses = {
            'pending': 'bg-secondary',
            'processing': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        };
        return statusClasses[status] || 'bg-secondary';
    }
    
    showError(message) {
        if (this.errorEl) {
            this.errorEl.textContent = message;
            this.errorEl.style.display = 'block';
        }
    }
    
    async cancelTask() {
        try {
            const response = await fetch(`/api/tasks/${this.taskId}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to cancel task');
            }
            
            this.stopPolling();
            window.location.reload();
        } catch (error) {
            console.error('Error cancelling task:', error);
            this.showError(error.message);
        }
    }
}

// Form validation and submission
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

    // Task polling initialization
    const taskElement = document.querySelector('[data-task-id]');
    if (taskElement) {
        const taskId = taskElement.dataset.taskId;
        const taskStatus = taskElement.dataset.taskStatus;
        
        if (['pending', 'processing'].includes(taskStatus)) {
            const poller = new TaskPoller(taskId);
            poller.start();
        }
    }

    // Form submission handling
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = analysisForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Starting Analysis...';
            
            try {
                const formData = new FormData(analysisForm);
                const response = await fetch(analysisForm.action, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (data.task_id) {
                    window.location.href = `/tasks/${data.task_id}`;
                } else {
                    throw new Error(data.error || 'Failed to start analysis');
                }
            } catch (error) {
                alert(error.message);
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Start Analysis';
            }
        });
    }

    // Filter form auto-submit
    const filterForm = document.querySelector('form[data-auto-submit]');
    if (filterForm) {
        const formControls = filterForm.querySelectorAll('select, input');
        formControls.forEach(control => {
            control.addEventListener('change', () => filterForm.submit());
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add event listener for platform selection
    const platformSelect = document.getElementById('platform');
    if (platformSelect) {
        platformSelect.addEventListener('change', function() {
            const platform = this.value;
            const profileInput = document.getElementById('profile_id');
            
            if (platform === 'twitter') {
                profileInput.placeholder = 'Enter Twitter/X username (without @)';
            } else if (platform === 'facebook') {
                profileInput.placeholder = 'Enter Facebook profile ID or username';
            }
        });
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Initialize task manager if on task page
    const taskElement = document.getElementById('taskContainer');
    if (taskElement) {
        const taskId = taskElement.dataset.taskId;
        const taskManager = new TaskManager(taskId);

        // Start polling if task is not complete
        const status = taskElement.dataset.status;
        if (['pending', 'processing'].includes(status)) {
            taskManager.startPolling();
        }

        // Setup cancel button
        const cancelBtn = document.getElementById('cancelTask');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => taskManager.cancelTask());
        }
    }
});

// Function to toggle sections
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const content = section.querySelector('.section-content');
    const icon = section.querySelector('.toggle-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.classList.remove('bi-chevron-down');
        icon.classList.add('bi-chevron-up');
    } else {
        content.style.display = 'none';
        icon.classList.remove('bi-chevron-up');
        icon.classList.add('bi-chevron-down');
    }
}

// AJAX function to refresh task status
function refreshTaskStatus(taskId) {
    fetch(`/api/tasks/${taskId}`)
        .then(response => response.json())
        .then(data => {
            // Update progress bar
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${data.progress}%`;
                progressBar.setAttribute('aria-valuenow', data.progress);
                progressBar.textContent = `${data.progress}%`;
            }
            
            // Update status message
            const statusMessage = document.getElementById('status-message');
            if (statusMessage) {
                statusMessage.textContent = data.message;
            }
            
            // If completed or failed, update the UI accordingly
            if (data.status === 'completed') {
                window.location.href = `/results/${taskId}`;
            } else if (data.status === 'failed') {
                document.getElementById('loading-spinner').style.display = 'none';
                document.getElementById('error-message').textContent = data.error;
                document.getElementById('error-container').style.display = 'block';
            } else {
                // Continue polling if still in progress
                setTimeout(() => refreshTaskStatus(taskId), 2000);
            }
        })
        .catch(error => {
            console.error('Error refreshing task status:', error);
        });
}