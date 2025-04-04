// SocialInsight main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
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