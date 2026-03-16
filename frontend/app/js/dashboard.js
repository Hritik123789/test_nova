// Dashboard Page JavaScript

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUserDashboard();
    loadRecentActivity();
    setupEventListeners();
});

// Load user dashboard
async function loadUserDashboard() {
    const dashboardContainer = document.getElementById('userDashboard');
    if (!dashboardContainer) return;

    // Get user info from auth
    const userEmail = localStorage.getItem('userEmail');
    const userName = localStorage.getItem('userName') || 'User';

    // Load user activity stats
    const stats = {
        topicsViewed: parseInt(localStorage.getItem('topicsViewed') || '0'),
        alertsChecked: parseInt(localStorage.getItem('alertsChecked') || '0'),
        permitsViewed: parseInt(localStorage.getItem('permitsViewed') || '0'),
        voiceQueries: parseInt(localStorage.getItem('voiceQueries') || '0')
    };

    // Calculate total activity
    const totalActivity = stats.topicsViewed + stats.alertsChecked + stats.permitsViewed + stats.voiceQueries;

    dashboardContainer.innerHTML = `
        <div class="user-dashboard-card">
            <div class="dashboard-header">
                <div>
                    <h3><i class="fas fa-user-circle"></i> Welcome back${userName !== 'User' ? ', ' + userName : ''}!</h3>
                    ${userEmail ? `<p style="color: var(--gray); font-size: 0.875rem; margin-top: 0.5rem;">${userEmail}</p>` : ''}
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2.5rem; font-weight: 800; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">${totalActivity}</div>
                    <div style="color: var(--gray); font-size: 0.875rem; font-weight: 600;">Total Actions</div>
                </div>
            </div>
            <div class="dashboard-stats">
                <div class="dashboard-stat">
                    <div class="stat-icon" style="background: #6366f120; color: #6366f1;">
                        <i class="fas fa-comments"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value">${stats.topicsViewed}</div>
                        <div class="stat-label">Topics Viewed</div>
                    </div>
                </div>
                <div class="dashboard-stat">
                    <div class="stat-icon" style="background: #f5930020; color: #f59300;">
                        <i class="fas fa-bell"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value">${stats.alertsChecked}</div>
                        <div class="stat-label">Alerts Checked</div>
                    </div>
                </div>
                <div class="dashboard-stat">
                    <div class="stat-icon" style="background: #10b98120; color: #10b981;">
                        <i class="fas fa-building"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value">${stats.permitsViewed}</div>
                        <div class="stat-label">Permits Viewed</div>
                    </div>
                </div>
                <div class="dashboard-stat">
                    <div class="stat-icon" style="background: #8b5cf620; color: #8b5cf6;">
                        <i class="fas fa-microphone"></i>
                    </div>
                    <div class="stat-info">
                        <div class="stat-value">${stats.voiceQueries}</div>
                        <div class="stat-label">Voice Queries</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Load recent activity
async function loadRecentActivity() {
    const activityList = document.getElementById('activityList');
    if (!activityList) return;

    // Get recent activity from localStorage
    const recentActivity = JSON.parse(localStorage.getItem('recentActivity') || '[]');

    if (recentActivity.length === 0) {
        activityList.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--gray);">
                <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>No recent activity yet. Start exploring CityPulse!</p>
            </div>
        `;
        return;
    }

    activityList.innerHTML = recentActivity.slice(0, 10).map(activity => `
        <div class="activity-item">
            <div class="activity-icon" style="background: ${activity.color}20; color: ${activity.color};">
                <i class="${activity.icon}"></i>
            </div>
            <div class="activity-details">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-time">${formatTime(activity.timestamp)}</div>
            </div>
        </div>
    `).join('');
}

// Setup event listeners
function setupEventListeners() {
    // Notification panel
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationPanel = document.getElementById('notificationPanel');
    const closeNotifications = document.getElementById('closeNotifications');
    
    if (notificationBtn && notificationPanel) {
        notificationBtn.addEventListener('click', () => {
            notificationPanel.classList.add('active');
            loadNotifications();
        });
    }
    
    if (closeNotifications && notificationPanel) {
        closeNotifications.addEventListener('click', () => {
            notificationPanel.classList.remove('active');
        });
    }
}

// Load notifications
async function loadNotifications() {
    const notificationList = document.getElementById('notificationList');
    if (!notificationList) return;

    try {
        const data = await api.getAlerts();
        const alerts = data.alerts || [];
        const recentAlerts = alerts.slice(0, 5);

        notificationList.innerHTML = recentAlerts.map((alert, index) => `
            <div class="notification-item" onclick="handleNotificationClick(${index})">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="width: 40px; height: 40px; border-radius: 10px; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        <i class="fas fa-${getSourceIcon(alert.source)}"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${alert.title}</div>
                        <div style="color: var(--gray); font-size: 0.875rem; margin-bottom: 0.5rem;">${alert.message.substring(0, 80)}...</div>
                        <div style="color: var(--gray); font-size: 0.75rem;">${formatTime(alert.timestamp)}</div>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Handle notification click
function handleNotificationClick(index) {
    const notificationPanel = document.getElementById('notificationPanel');
    if (notificationPanel) {
        notificationPanel.classList.remove('active');
    }
    window.location.href = 'alerts.html';
}

// Utility functions
function getSourceIcon(source) {
    const icons = {
        'news': 'newspaper',
        'social': 'comments',
        'permit': 'file-alt',
        'image_analysis': 'camera',
        'community': 'users'
    };
    return icons[source] || 'info-circle';
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

// Track activity helper (called from other pages)
function trackActivity(type, title, icon, color) {
    const activity = {
        type,
        title,
        icon,
        color,
        timestamp: new Date().toISOString()
    };

    const recentActivity = JSON.parse(localStorage.getItem('recentActivity') || '[]');
    recentActivity.unshift(activity);
    
    // Keep only last 50 activities
    if (recentActivity.length > 50) {
        recentActivity.pop();
    }

    localStorage.setItem('recentActivity', JSON.stringify(recentActivity));
}
