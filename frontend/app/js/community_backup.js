// Community Page JavaScript - Enhanced Version

let communityData = null;
let selectedTopic = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadCommunityData();
    setupEventListeners();
    loadUserDashboard();
});

// Load community data from API
async function loadCommunityData() {
    try {
        const data = await api.getCommunity();
        communityData = data.data;
        
        displaySentiment(communityData);
        displayTopics(communityData);
        displayConcerns(communityData);
        createClusterVisualization(communityData);
    } catch (error) {
        console.error('Error loading community data:', error);
    }
}

// Display sentiment distribution
function displaySentiment(data) {
    const sentiment = data?.basic_topics?.sentiment_distribution;
    if (!sentiment) return;

    document.getElementById('positivePct').textContent = `${sentiment.positive_pct || 0}%`;
    document.getElementById('neutralPct').textContent = `${sentiment.neutral_pct || 0}%`;
    document.getElementById('negativePct').textContent = `${sentiment.negative_pct || 0}%`;
}

// Display trending topics with clickable cards
function displayTopics(data) {
    const topicsGrid = document.getElementById('topicsGrid');
    if (!topicsGrid) return;

    const topics = data?.insights?.trending_topics || [];

    if (topics.length === 0) {
        topicsGrid.innerHTML = '<p style="text-align: center; color: var(--gray);">No topics available.</p>';
        return;
    }

    topicsGrid.innerHTML = topics.map((topic, index) => `
        <div class="topic-card clickable" onclick="showTopicDetails(${index})" data-topic-index="${index}">
            <div class="topic-card-header">
                <div class="topic-card-name">${formatTopicName(topic.topic)}</div>
                <div class="topic-card-score">${topic.trend_score.toFixed(1)}</div>
            </div>
            <div class="topic-card-stats">
                <div class="topic-card-stat">
                    <i class="fas fa-tag"></i>
                    <span>${topic.category}</span>
                </div>
                <div class="topic-card-stat">
                    <i class="fas fa-smile"></i>
                    <span>${topic.sentiment}</span>
                </div>
            </div>
            <p style="color: var(--gray); margin-top: 1rem; font-size: 0.875rem;">${topic.description}</p>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--gray); font-size: 0.875rem;">
                    <i class="fas fa-comments"></i> ${extractMentions(topic.description)} mentions
                </span>
                <span style="color: var(--primary); font-size: 0.875rem; font-weight: 600;">
                    Click for details <i class="fas fa-arrow-right"></i>
                </span>
            </div>
        </div>
    `).join('');
}

// Show topic details in modal
function showTopicDetails(index) {
    const topics = communityData?.insights?.trending_topics || [];
    const topic = topics[index];
    if (!topic) return;

    selectedTopic = topic;

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'topic-modal';
    modal.innerHTML = `
        <div class="topic-modal-content">
            <div class="topic-modal-header">
                <h2>${formatTopicName(topic.topic)}</h2>
                <button class="close-modal-btn" onclick="closeTopicModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="topic-modal-body">
                <div class="topic-detail-stats">
                    <div class="topic-detail-stat">
                        <div class="stat-value">${topic.trend_score.toFixed(1)}</div>
                        <div class="stat-label">Trend Score</div>
                    </div>
                    <div class="topic-detail-stat">
                        <div class="stat-value">${topic.category}</div>
                        <div class="stat-label">Category</div>
                    </div>
                    <div class="topic-detail-stat">
                        <div class="stat-value">${topic.sentiment}</div>
                        <div class="stat-label">Sentiment</div>
                    </div>
                    <div class="topic-detail-stat">
                        <div class="stat-value">${extractMentions(topic.description)}</div>
                        <div class="stat-label">Mentions</div>
                    </div>
                </div>
                
                <div class="topic-description-section">
                    <h3>Description</h3>
                    <p>${topic.description}</p>
                </div>

                <div class="topic-sources-section">
                    <h3><i class="fas fa-link"></i> Sources</h3>
                    <div class="sources-list">
                        ${generateTopicSources(topic)}
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('active'), 10);
}

// Close topic modal
function closeTopicModal() {
    const modal = document.querySelector('.topic-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

// Generate sources for topic
function generateTopicSources(topic) {
    // Since we don't have actual sources in the data, generate representative sources
    const sourceTypes = [
        { type: 'Reddit', icon: 'fab fa-reddit', color: '#FF4500' },
        { type: 'Twitter', icon: 'fab fa-twitter', color: '#1DA1F2' },
        { type: 'News', icon: 'fas fa-newspaper', color: '#6366f1' }
    ];

    return sourceTypes.map(source => `
        <div class="source-item">
            <div class="source-icon" style="background: ${source.color}20; color: ${source.color};">
                <i class="${source.icon}"></i>
            </div>
            <div class="source-details">
                <div class="source-name">${source.type} Discussions</div>
                <div class="source-meta">Multiple posts about ${formatTopicName(topic.topic).toLowerCase()}</div>
            </div>
            <a href="#" class="source-link" onclick="event.preventDefault(); alert('Source link would open here');">
                <i class="fas fa-external-link-alt"></i>
            </a>
        </div>
    `).join('');
}

// Extract mentions from description
function extractMentions(description) {
    const match = description.match(/(\d+)\s+times/);
    return match ? match[1] : '0';
}


// Display community concerns with clickable items
function displayConcerns(data) {
    const concernsList = document.getElementById('concernsList');
    if (!concernsList) return;

    const concerns = data?.insights?.community_concerns || [];

    if (concerns.length === 0) {
        concernsList.innerHTML = '<p style="text-align: center; color: var(--gray);">No concerns reported.</p>';
        return;
    }

    concernsList.innerHTML = concerns.map((concern, index) => `
        <div class="concern-item clickable" onclick="showConcernDetails(${index})" data-concern-index="${index}">
            <div class="concern-header">
                <div class="concern-title">${concern.concern}</div>
                <div class="concern-severity ${concern.severity}">${concern.severity.toUpperCase()}</div>
            </div>
            <div class="concern-recommendation">
                <strong>Recommendation:</strong> ${concern.recommendation}
            </div>
            <div class="concern-areas">
                ${concern.affected_areas.map(area => `
                    <span class="concern-area-tag">${area}</span>
                `).join('')}
            </div>
            <div style="margin-top: 1rem; text-align: right;">
                <span style="color: var(--primary); font-size: 0.875rem; font-weight: 600;">
                    View details <i class="fas fa-arrow-right"></i>
                </span>
            </div>
        </div>
    `).join('');
}

// Show concern details in modal
function showConcernDetails(index) {
    const concerns = communityData?.insights?.community_concerns || [];
    const concern = concerns[index];
    if (!concern) return;

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'concern-modal';
    modal.innerHTML = `
        <div class="concern-modal-content">
            <div class="concern-modal-header">
                <h2>${concern.concern}</h2>
                <button class="close-modal-btn" onclick="closeConcernModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="concern-modal-body">
                <div class="concern-detail-stats">
                    <div class="concern-detail-stat">
                        <div class="stat-value ${concern.severity}">${concern.severity.toUpperCase()}</div>
                        <div class="stat-label">Severity Level</div>
                    </div>
                    <div class="concern-detail-stat">
                        <div class="stat-value">${concern.affected_areas.length}</div>
                        <div class="stat-label">Affected Areas</div>
                    </div>
                </div>
                
                <div class="concern-description-section">
                    <h3><i class="fas fa-exclamation-triangle"></i> Issue</h3>
                    <p>${concern.concern}</p>
                </div>

                <div class="concern-recommendation-section">
                    <h3><i class="fas fa-lightbulb"></i> Recommendation</h3>
                    <p>${concern.recommendation}</p>
                </div>

                <div class="concern-areas-section">
                    <h3><i class="fas fa-map-marker-alt"></i> Affected Areas</h3>
                    <div class="areas-list">
                        ${concern.affected_areas.map(area => `
                            <span class="area-badge">${area}</span>
                        `).join('')}
                    </div>
                </div>

                <div class="concern-sources-section">
                    <h3><i class="fas fa-link"></i> Sources</h3>
                    <div class="sources-list">
                        ${generateConcernSources(concern)}
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('active'), 10);
}

// Close concern modal
function closeConcernModal() {
    const modal = document.querySelector('.concern-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

// Generate sources for concern
function generateConcernSources(concern) {
    // Generate representative sources based on concern type
    const sourceTypes = [
        { type: 'Community Reports', icon: 'fas fa-users', color: '#6366f1' },
        { type: 'News Coverage', icon: 'fas fa-newspaper', color: '#f59300' },
        { type: 'Social Media', icon: 'fas fa-comments', color: '#10b981' }
    ];

    return sourceTypes.map(source => `
        <div class="source-item">
            <div class="source-icon" style="background: ${source.color}20; color: ${source.color};">
                <i class="${source.icon}"></i>
            </div>
            <div class="source-details">
                <div class="source-name">${source.type}</div>
                <div class="source-meta">Multiple reports about ${concern.concern.toLowerCase()}</div>
            </div>
            <a href="#" class="source-link" onclick="event.preventDefault(); alert('Source link would open here');">
                <i class="fas fa-external-link-alt"></i>
            </a>
        </div>
    `).join('');
}

// Create cluster visualization
function createClusterVisualization(data) {
    const clusterViz = document.getElementById('clusterViz');
    if (!clusterViz) return;

    const clusters = data?.insights?.topic_clusters?.clusters || [];

    if (clusters.length === 0) {
        clusterViz.innerHTML = '<p style="text-align: center; color: var(--gray); padding: 3rem;">No cluster data available.</p>';
        return;
    }

    const topClusters = clusters.slice(0, 5);
    const svgWidth = clusterViz.clientWidth;
    const svgHeight = 500;
    const centerX = svgWidth / 2;
    const centerY = svgHeight / 2;
    const radius = 150;

    let svg = `<svg width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;

    // Draw connections
    topClusters.forEach((cluster1, i) => {
        topClusters.slice(i + 1).forEach((cluster2, j) => {
            const angle1 = (i / topClusters.length) * Math.PI * 2 - Math.PI / 2;
            const angle2 = ((i + j + 1) / topClusters.length) * Math.PI * 2 - Math.PI / 2;
            const x1 = centerX + Math.cos(angle1) * radius;
            const y1 = centerY + Math.sin(angle1) * radius;
            const x2 = centerX + Math.cos(angle2) * radius;
            const y2 = centerY + Math.sin(angle2) * radius;

            svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="rgba(99, 102, 241, 0.2)" stroke-width="2"/>`;
        });
    });

    // Draw nodes
    topClusters.forEach((cluster, i) => {
        const angle = (i / topClusters.length) * Math.PI * 2 - Math.PI / 2;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        const size = 30 + (cluster.trend_score * 3);
        const color = getColorForTrendScore(cluster.trend_score);

        svg += `
            <g class="cluster-node" style="cursor: pointer;" onclick="showClusterDetails('${cluster.main_topic}')">
                <circle cx="${x}" cy="${y}" r="${size}" fill="${color}" opacity="0.3">
                    <animate attributeName="r" values="${size};${size + 5};${size}" dur="2s" repeatCount="indefinite"/>
                </circle>
                <circle cx="${x}" cy="${y}" r="${size * 0.7}" fill="${color}" opacity="0.6"/>
                <text x="${x}" y="${y}" text-anchor="middle" dy="0.3em" fill="white" font-size="12" font-weight="600">
                    ${formatTopicName(cluster.main_topic).substring(0, 10)}
                </text>
                <text x="${x}" y="${y + 20}" text-anchor="middle" fill="white" font-size="10" opacity="0.7">
                    ${cluster.total_mentions} posts
                </text>
            </g>
        `;
    });

    svg += '</svg>';
    clusterViz.innerHTML = svg;
}

// Show cluster details
function showClusterDetails(topicName) {
    const topics = communityData?.insights?.trending_topics || [];
    const topicIndex = topics.findIndex(t => t.topic === topicName);
    if (topicIndex >= 0) {
        showTopicDetails(topicIndex);
    }
}


// Load user dashboard
async function loadUserDashboard() {
    const dashboardContainer = document.getElementById('userDashboard');
    if (!dashboardContainer) return;

    // Get user info from auth
    const userEmail = localStorage.getItem('userEmail');
    const userName = localStorage.getItem('userName');

    if (!userEmail) {
        dashboardContainer.style.display = 'none';
        return;
    }

    // Load user activity stats
    const stats = {
        topicsViewed: parseInt(localStorage.getItem('topicsViewed') || '0'),
        alertsChecked: parseInt(localStorage.getItem('alertsChecked') || '0'),
        permitsViewed: parseInt(localStorage.getItem('permitsViewed') || '0'),
        voiceQueries: parseInt(localStorage.getItem('voiceQueries') || '0')
    };

    dashboardContainer.innerHTML = `
        <div class="user-dashboard-card">
            <div class="dashboard-header">
                <h3><i class="fas fa-user-circle"></i> My Activity</h3>
                <button class="dashboard-close-btn" onclick="closeDashboard()">
                    <i class="fas fa-times"></i>
                </button>
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

    dashboardContainer.style.display = 'block';
}

// Close dashboard
function closeDashboard() {
    const dashboardContainer = document.getElementById('userDashboard');
    if (dashboardContainer) {
        dashboardContainer.style.display = 'none';
    }
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

    // Dashboard toggle
    const dashboardBtn = document.getElementById('dashboardBtn');
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', () => {
            const dashboard = document.getElementById('userDashboard');
            if (dashboard) {
                dashboard.style.display = dashboard.style.display === 'none' ? 'block' : 'none';
            }
        });
    }

    // Track topic views
    document.addEventListener('click', (e) => {
        if (e.target.closest('.topic-card')) {
            incrementStat('topicsViewed');
        }
    });
}

// Increment user stat
function incrementStat(statName) {
    const current = parseInt(localStorage.getItem(statName) || '0');
    localStorage.setItem(statName, (current + 1).toString());
}

// Load notifications with clickable items
async function loadNotifications() {
    const notificationList = document.getElementById('notificationList');
    if (!notificationList) return;

    try {
        const data = await api.getAlerts();
        const alerts = data.alerts || [];
        const recentAlerts = alerts.slice(0, 5);

        notificationList.innerHTML = recentAlerts.map((alert, index) => `
            <div class="notification-item clickable" onclick="handleNotificationClick(${index})" data-alert-index="${index}">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="width: 40px; height: 40px; border-radius: 10px; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        <i class="fas fa-${getSourceIcon(alert.source)}"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${alert.title}</div>
                        <div style="color: var(--gray); font-size: 0.875rem; margin-bottom: 0.5rem;">${alert.message.substring(0, 80)}...</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="color: var(--gray); font-size: 0.75rem;">${formatTime(alert.timestamp)}</div>
                            <span style="color: var(--primary); font-size: 0.75rem; font-weight: 600;">
                                View <i class="fas fa-arrow-right"></i>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        incrementStat('alertsChecked');
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Handle notification click
function handleNotificationClick(index) {
    // Close notification panel
    const notificationPanel = document.getElementById('notificationPanel');
    if (notificationPanel) {
        notificationPanel.classList.remove('active');
    }

    // Navigate to alerts page
    window.location.href = 'alerts.html';
}


// Utility functions
function formatTopicName(topic) {
    return topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getColorForTrendScore(score) {
    if (score >= 8) return '#6366f1';
    if (score >= 5) return '#8b5cf6';
    if (score >= 3) return '#a78bfa';
    return '#c4b5fd';
}

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
