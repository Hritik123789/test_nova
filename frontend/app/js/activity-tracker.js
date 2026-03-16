// Activity Tracker - Shared across all pages

// Track activity and update dashboard stats
function trackActivity(type, title, icon, color) {
    // Update stat counter
    const statKey = type; // e.g., 'topicsViewed', 'alertsChecked', 'permitsViewed', 'voiceQueries'
    const current = parseInt(localStorage.getItem(statKey) || '0');
    localStorage.setItem(statKey, (current + 1).toString());

    // Add to recent activity
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

// Increment stat without adding to activity feed
function incrementStat(statName) {
    const current = parseInt(localStorage.getItem(statName) || '0');
    localStorage.setItem(statName, (current + 1).toString());
}
