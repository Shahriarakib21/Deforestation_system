// Global variables
let trendsChart, riskChart;
let realTimeInterval;

// Main Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded, initializing...');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Set up real-time updates
    setInterval(updateDashboard, 30000); // Update every 30 seconds
});

async function initializeDashboard() {
    try {
        console.log('Loading dashboard data...');
        
        // Load all dashboard data
        await Promise.all([
            loadSystemStatus(),
            loadDeforestationStatistics(),
            loadRecentActivity()
        ]);
        
        console.log('Dashboard initialized successfully');
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

async function loadSystemStatus() {
    try {
        const response = await fetch('/api/system-status');
        if (!response.ok) throw new Error('Failed to load system status');
        
        const status = await response.json();
        updateSystemStatus(status);
        
    } catch (error) {
        console.error('Error loading system status:', error);
        updateSystemStatus({
            system_status: 'error',
            last_update: 'Error loading status',
            model_status: 'unknown',
            upload_folder_status: 'unknown',
            google_drive_status: 'unknown'
        });
    }
}

async function loadDeforestationStatistics() {
    try {
        const response = await fetch('/api/deforestation-statistics');
        if (!response.ok) throw new Error('Failed to load deforestation statistics');
        
        const stats = await response.json();
        displayDeforestationStatistics(stats);
        
    } catch (error) {
        console.error('Error loading deforestation statistics:', error);
        document.getElementById('deforestationData').innerHTML = 
            '<div class="error">Failed to load deforestation statistics</div>';
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch('/api/recent-activity');
        if (!response.ok) throw new Error('Failed to load recent activity');
        
        const activity = await response.json();
        displayRecentActivity(activity);
        
    } catch (error) {
        console.error('Error loading recent activity:', error);
        document.getElementById('recentActivity').innerHTML = 
            '<div class="error">Failed to load recent activity</div>';
    }
}

function updateSystemStatus(status) {
    // Update last update time
    const lastUpdateElement = document.getElementById('lastUpdate');
    if (lastUpdateElement) {
        if (status.last_update) {
            const date = new Date(status.last_update);
            lastUpdateElement.textContent = date.toLocaleString();
        } else {
            lastUpdateElement.textContent = 'Unknown';
        }
    }
    
    // Update model status
    const modelStatusElement = document.getElementById('modelStatus');
    if (modelStatusElement) {
        switch (status.model_status) {
            case 'ready':
                modelStatusElement.innerHTML = '<span class="status-indicator active"></span>Ready';
                break;
            case 'training':
                modelStatusElement.innerHTML = '<span class="status-indicator warning"></span>Training';
                break;
            default:
                modelStatusElement.innerHTML = '<span class="status-indicator inactive"></span>Unknown';
        }
    }
}

function displayDeforestationStatistics(stats) {
    const container = document.getElementById('deforestationData');
    if (!container) return;
    
    const totalSizeMB = stats.total_size_mb.toFixed(2);
    const lastUpload = stats.last_upload ? new Date(stats.last_upload).toLocaleDateString() : 'No uploads yet';
    
    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-images"></i>
                </div>
                <div class="stat-content">
                    <h3>${stats.total_images}</h3>
                    <p>Total Images</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-tree"></i>
                </div>
                <div class="stat-content">
                    <h3>${stats.forest_count}</h3>
                    <p>Forest Images</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-cut"></i>
                </div>
                <div class="stat-content">
                    <h3>${stats.deforested_count}</h3>
                    <p>Deforested Images</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-satellite"></i>
                </div>
                <div class="stat-content">
                    <h3>${stats.satellite_images}</h3>
                    <p>Satellite Images</p>
                </div>
            </div>
        </div>
        
        <div class="stats-details">
            <div class="detail-item">
                <strong>Total Data Size:</strong> ${totalSizeMB} MB
            </div>
            <div class="detail-item">
                <strong>Last Upload:</strong> ${lastUpload}
            </div>
            <div class="detail-item">
                <strong>Mixed Category:</strong> ${stats.mixed_count} images
            </div>
        </div>
        
        ${stats.upload_trend.length > 0 ? `
        <div class="upload-trend">
            <h4>Upload Trend (Last 7 Days)</h4>
            <div class="trend-chart">
                ${stats.upload_trend.map(day => `
                    <div class="trend-bar" style="height: ${Math.max(day.count * 20, 10)}px" title="${day.date}: ${day.count} uploads">
                        <span class="trend-label">${day.count}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}

function displayRecentActivity(activity) {
    const container = document.getElementById('recentActivity');
    if (!container) return;
    
    if (!activity.activities || activity.activities.length === 0) {
        container.innerHTML = '<div class="info">No recent activity found.</div>';
        return;
    }
    
    const activitiesHtml = activity.activities.map(item => {
        const date = new Date(item.timestamp).toLocaleDateString();
        const time = new Date(item.timestamp).toLocaleTimeString();
        const colorClass = item.color || 'info';
        
        return `
            <div class="activity-item ${colorClass}">
                <div class="activity-icon">
                    <i class="${item.icon}"></i>
                </div>
                <div class="activity-content">
                    <h4>${item.title}</h4>
                    <p>${item.description}</p>
                    <span class="activity-time">${date} at ${time}</span>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <div class="activity-header">
            <h3>Recent Activity (${activity.total_activities} total)</h3>
        </div>
        <div class="activity-list">
            ${activitiesHtml}
        </div>
    `;
}

function updateDashboard() {
    console.log('Updating dashboard...');
    loadSystemStatus();
}

function showError(message) {
    console.error('Dashboard Error:', message);
    // You can add a toast notification here if needed
}

// Utility function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Export functions for global access
window.dashboard = {
    refresh: initializeDashboard,
    update: updateDashboard
};

// Initialize Chart.js charts
function initializeCharts() {
    // Trends Chart
    const trendsCtx = document.getElementById('trendsChart');
    if (trendsCtx) {
        trendsChart = new Chart(trendsCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Daily Detections',
                    data: [12, 15, 8, 20, 18, 25, 22],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    // Risk Chart
    const riskCtx = document.getElementById('riskChart');
    if (riskCtx) {
        riskChart = new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: ['High Risk', 'Medium Risk', 'Low Risk'],
                datasets: [{
                    data: [45, 35, 20],
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#10b981'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Load initial data from the backend
async function loadInitialData() {
    try {
        const response = await fetch('/api/deforestation-data');
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error loading initial data:', error);
        showNotification('Error loading data', 'error');
    }
}

// Start real-time updates
function startRealTimeUpdates() {
    realTimeInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/real-time-update');
            const data = await response.json();
            updateRealTimeData(data);
        } catch (error) {
            console.error('Error updating real-time data:', error);
        }
    }, 5000); // Update every 5 seconds
}

// Update dashboard with new data
function updateDashboard(data) {
    // Update hero stats
    document.getElementById('detection-count').textContent = data.detection_count;
    document.getElementById('area-affected').textContent = data.total_area_affected;
    document.getElementById('risk-level').textContent = data.risk_level;
    
    // Update last updated time
    document.getElementById('last-updated').textContent = `Last updated: ${formatTime(data.last_updated)}`;
    
    // Update detection list
    updateDetectionList(data.coordinates);
    
    // Update charts
    updateCharts(data.statistics);
}

// Update real-time data
function updateRealTimeData(data) {
    // Update detection count
    const detectionCountElement = document.getElementById('detection-count');
    if (detectionCountElement) {
        detectionCountElement.textContent = data.updated_stats.detection_count;
    }
    
    // Update last updated time
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        lastUpdatedElement.textContent = `Last updated: ${formatTime(data.updated_stats.last_updated)}`;
    }
    
    // Add new detection to the list
    if (data.new_detection) {
        addNewDetection(data.new_detection);
    }
    
    // Show notification for new detection
    if (data.new_detection && data.new_detection.severity === 'High') {
        showNotification('New high-severity deforestation detected!', 'warning');
    }
}

// Update detection list
function updateDetectionList(detections) {
    const detectionList = document.getElementById('detection-list');
    if (!detectionList) return;
    
    detectionList.innerHTML = '';
    
    // Show last 5 detections
    const recentDetections = detections.slice(-5).reverse();
    
    recentDetections.forEach(detection => {
        const detectionItem = createDetectionItem(detection);
        detectionList.appendChild(detectionItem);
    });
}

// Create detection item element
function createDetectionItem(detection) {
    const item = document.createElement('div');
    item.className = 'detection-item';
    
    const severityClass = detection.severity.toLowerCase();
    const severityColor = {
        'high': '#ef4444',
        'medium': '#f59e0b',
        'low': '#10b981'
    };
    
    item.innerHTML = `
        <div class="detection-header">
            <span class="detection-severity ${severityClass}" style="background-color: ${severityColor[severityClass]}">
                ${detection.severity}
            </span>
            <span class="detection-time">${formatTime(detection.timestamp)}</span>
        </div>
        <div class="detection-details">
            <p>Location: ${detection.lat.toFixed(4)}, ${detection.lng.toFixed(4)}</p>
            <p>Confidence: ${(detection.confidence * 100).toFixed(1)}%</p>
        </div>
    `;
    
    return item;
}

// Add new detection to the list
function addNewDetection(detection) {
    const detectionList = document.getElementById('detection-list');
    if (!detectionList) return;
    
    const detectionItem = createDetectionItem(detection);
    
    // Add with animation
    detectionItem.style.opacity = '0';
    detectionItem.style.transform = 'translateX(-20px)';
    detectionList.insertBefore(detectionItem, detectionList.firstChild);
    
    // Animate in
    setTimeout(() => {
        detectionItem.style.transition = 'all 0.3s ease';
        detectionItem.style.opacity = '1';
        detectionItem.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove old items if more than 5
    while (detectionList.children.length > 5) {
        detectionList.removeChild(detectionList.lastChild);
    }
}

// Update charts with new data
function updateCharts(statistics) {
    if (trendsChart && statistics.daily_detections) {
        trendsChart.data.datasets[0].data = statistics.daily_detections;
        trendsChart.update('none');
    }
    
    if (riskChart) {
        // Simulate risk distribution changes
        const newData = [
            Math.floor(Math.random() * 30) + 30, // High risk: 30-60
            Math.floor(Math.random() * 30) + 25, // Medium risk: 25-55
            Math.floor(Math.random() * 20) + 15  // Low risk: 15-35
        ];
        
        riskChart.data.datasets[0].data = newData;
        riskChart.update('none');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Time filter buttons
    const timeFilters = document.querySelectorAll('.time-filters .btn');
    timeFilters.forEach(btn => {
        btn.addEventListener('click', function() {
            timeFilters.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateChartPeriod(this.dataset.period);
        });
    });
    
    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            const targetId = this.getAttribute('href').substring(1);
            scrollToSection(targetId);
        });
    });
    
    // Map toggle button
    const mapToggleBtn = document.querySelector('.btn-secondary');
    if (mapToggleBtn) {
        mapToggleBtn.addEventListener('click', toggleMapView);
    }
}

// Update chart period
function updateChartPeriod(period) {
    if (!trendsChart) return;
    
    const labels = {
        'daily': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'weekly': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'monthly': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    };
    
    const data = {
        'daily': [12, 15, 8, 20, 18, 25, 22],
        'weekly': [85, 92, 78, 105],
        'monthly': [320, 450, 380, 520, 480, 600]
    };
    
    trendsChart.data.labels = labels[period];
    trendsChart.data.datasets[0].data = data[period];
    trendsChart.update();
}

// Scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Toggle map view
function toggleMapView() {
    const mapPlaceholder = document.getElementById('map-placeholder');
    if (mapPlaceholder) {
        const currentView = mapPlaceholder.dataset.view || 'satellite';
        const newView = currentView === 'satellite' ? 'terrain' : 'satellite';
        
        mapPlaceholder.dataset.view = newView;
        
        if (newView === 'terrain') {
            mapPlaceholder.style.background = 'linear-gradient(135deg, #8B4513, #A0522D)';
            mapPlaceholder.querySelector('h4').textContent = 'Terrain View';
        } else {
            mapPlaceholder.style.background = 'linear-gradient(135deg, #1e293b, #334155)';
            mapPlaceholder.querySelector('h4').textContent = 'Satellite View';
        }
        
        showNotification(`Switched to ${newView} view`, 'info');
    }
}

// Format time for display
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 400px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Get notification color
function getNotificationColor(type) {
    const colors = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6'
    };
    return colors[type] || '#3b82f6';
}

// Add CSS for detection items and notifications
const additionalStyles = `
    .detection-item {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .detection-item:hover {
        border-color: rgba(16, 185, 129, 0.3);
        transform: translateX(5px);
    }
    
    .detection-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .detection-severity {
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .detection-time {
        color: #94a3b8;
        font-size: 0.75rem;
    }
    
    .detection-details p {
        color: #cbd5e1;
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }
    
    .notification-close:hover {
        opacity: 0.8;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (realTimeInterval) {
        clearInterval(realTimeInterval);
    }
});

// Data Management Functions
function exportData(format) {
    showNotification(`Exporting data in ${format.toUpperCase()} format...`, 'info');
    
    // Simulate export process
    setTimeout(() => {
        const data = {
            format: format,
            timestamp: new Date().toISOString(),
            records: 2847,
            data: deforestation_data
        };
        
        // Create download link
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `deforestation-data-${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification(`Data exported successfully in ${format.toUpperCase()} format!`, 'success');
        
        // Update last export time
        document.querySelector('.summary-value:nth-child(2)').textContent = 'Just now';
    }, 2000);
}

function importData() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a file first', 'error');
        return;
    }
    
    showNotification('Importing data...', 'info');
    
    // Simulate import process
    setTimeout(() => {
        // Update last import time
        document.querySelector('.summary-value:nth-child(3)').textContent = 'Just now';
        
        // Update total records (simulate)
        const currentRecords = parseInt(document.querySelector('.summary-value:nth-child(1)').textContent.replace(',', ''));
        const newRecords = Math.floor(Math.random() * 100) + 50;
        document.querySelector('.summary-value:nth-child(1)').textContent = (currentRecords + newRecords).toLocaleString();
        
        showNotification(`Data imported successfully! Added ${newRecords} new records.`, 'success');
        
        // Reset file input
        fileInput.value = '';
        document.getElementById('fileInfo').textContent = 'No file selected';
        document.getElementById('importBtn').disabled = true;
    }, 3000);
}

// File input change handler
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('importFile');
    const fileInfo = document.getElementById('fileInfo');
    const importBtn = document.getElementById('importBtn');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                importBtn.disabled = false;
            } else {
                fileInfo.textContent = 'No file selected';
                importBtn.disabled = true;
            }
        });
    }
});

// Logout function
function logout() {
    showNotification('Logging out...', 'info');
    
    setTimeout(() => {
        // Redirect to login page
        window.location.href = '/login';
    }, 1000);
}
