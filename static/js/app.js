/**
 * CryoLink - Cold-Chain Logistics Control Tower
 * Main Application JavaScript with Mobile Support
 */

// Sidebar Toggle
document.addEventListener('DOMContentLoaded', function() {
    const desktopSidebarToggle = document.getElementById('desktopSidebarToggle');
    
    // Restore collapsed state from localStorage
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        document.body.classList.add('sidebar-collapsed');
    }
    
    if (desktopSidebarToggle) {
        desktopSidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            
            // Persist state
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed);
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
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Auto-hide sidebar early upon scrolling down (well before Tenant Management)
    let isUserManuallyToggled = false;
    if (desktopSidebarToggle) {
        desktopSidebarToggle.addEventListener('click', function() {
            isUserManuallyToggled = true;
        });
    }
    
    window.addEventListener('scroll', function() {
        if (isUserManuallyToggled) return;
        
        // Hide sidebar early at 80px scroll offset
        if (window.scrollY > 80) {
            if (!document.body.classList.contains('sidebar-collapsed')) {
                document.body.classList.add('sidebar-collapsed');
            }
        } else {
            if (document.body.classList.contains('sidebar-collapsed')) {
                document.body.classList.remove('sidebar-collapsed');
            }
        }
    }, { passive: true });

    // IntersectionObserver ScrollSpy for Single-Page Continuous Scroll Navigation
    const sections = document.querySelectorAll('section[id^="sec-"]');
    if (sections.length > 0) {
        const navLinks = document.querySelectorAll('#sidebarNav .nav-link[data-section]');
        
        // Smooth scroll on sidebar link click
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('data-section');
                const targetEl = document.getElementById(targetId);
                if (targetEl) {
                    e.preventDefault();
                    targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    // Update active class
                    navLinks.forEach(nl => nl.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Update URL hash without scroll jump
                    history.pushState(null, null, '#' + targetId);
                }
            });
        });

        // IntersectionObserver for scroll tracking
        const observerOptions = {
            root: null,
            rootMargin: '-20% 0px -60% 0px',
            threshold: 0
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    navLinks.forEach(link => {
                        if (link.getAttribute('data-section') === id) {
                            link.classList.add('active');
                        } else {
                            link.classList.remove('active');
                        }
                    });
                }
            });
        }, observerOptions);

        sections.forEach(section => observer.observe(section));
    }
});

// Toggle Sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
    }
}

// Close sidebar when clicking overlay
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar && overlay) {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
    }
}

// Real-time temperature update simulation
function updateTemperature(shipmentId) {
    fetch(`/api/shipments/${shipmentId}/temperature`)
        .then(response => response.json())
        .then(data => {
            if (data.readings && data.readings.length > 0) {
                const latestTemp = data.readings[0].temperature;
                const tempElement = document.getElementById(`temp-${shipmentId}`);
                if (tempElement) {
                    tempElement.textContent = `${latestTemp.toFixed(1)}°C`;
                    
                    // Update status badge
                    const isWithinRange = latestTemp >= data.temp_min && latestTemp <= data.temp_max;
                    tempElement.className = isWithinRange ? 'text-success' : 'text-danger';
                }
            }
        })
        .catch(error => console.error('Error fetching temperature:', error));
}

// Risk meter update
function updateRiskMeter(elementId, riskScore) {
    const meter = document.getElementById(elementId);
    if (meter) {
        const percentage = Math.min(100, Math.max(0, riskScore));
        meter.style.left = `${percentage}%`;
        
        // Update color based on risk level
        meter.className = 'risk-indicator';
        if (percentage <= 30) {
            meter.style.background = '#00C853';
        } else if (percentage <= 60) {
            meter.style.background = '#FFB300';
        } else {
            meter.style.background = '#D32F2F';
        }
    }
}

// Format date relative to now
function timeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
}

// Confirm action dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show toast notification
        showToast('Copied to clipboard!');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(toast);
        bsAlert.close();
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999;';
    document.body.appendChild(container);
    return container;
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length - 1; j++) { // Skip last column (actions)
            row.push('"' + cols[j].innerText.replace(/"/g, '""') + '"');
        }
        
        csv.push(row.join(','));
    }
    
    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Print current page
function printPage() {
    window.print();
}

// Refresh page
function refreshPage() {
    location.reload();
}

// Navigate to URL
function navigateTo(url) {
    window.location.href = url;
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('[required]');
    let isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Clear form validation
function clearValidation(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const inputs = form.querySelectorAll('.is-invalid');
        inputs.forEach(function(input) {
            input.classList.remove('is-invalid');
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('CryoLink Liquid Glass UI initialized');
});

// Throttled Liquid Glass Spotlight Mouse Tracking via requestAnimationFrame
let isSpotlightTicking = false;
document.addEventListener('mousemove', function(e) {
    if (!isSpotlightTicking) {
        window.requestAnimationFrame(() => {
            const cards = document.querySelectorAll('.glass-card, .liquid-glass-card, .stats-card');
            cards.forEach(card => {
                const rect = card.getBoundingClientRect();
                if (e.clientX >= rect.left - 50 && e.clientX <= rect.right + 50 &&
                    e.clientY >= rect.top - 50 && e.clientY <= rect.bottom + 50) {
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    card.style.setProperty('--mouse-x', `${x}px`);
                    card.style.setProperty('--mouse-y', `${y}px`);
                }
            });
            isSpotlightTicking = false;
        });
        isSpotlightTicking = true;
    }
}, { passive: true });

