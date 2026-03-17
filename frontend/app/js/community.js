// Community Page JavaScript - Fixed Version

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
            <div class="topic-header">
                <div class="topic-title">${formatTopicName(topic.topic)}</div>
                <div class="topic-score">${topic.trend_score}/10</div>
            </div>
            <div class="topic-category">${topic.category}</div>
            <div class="topic-engagement">
                <div class="engagement-item">
                    <i class="fas fa-comments"></i>
                    <span>${topic.engagement_metrics?.total_posts || 0} posts</span>
                </div>
                <div class="engagement-item">
                    <i class="fas fa-heart"></i>
                    <span>${topic.engagement_metrics?.total_engagement || 0} interactions</span>
                </div>
            </div>
            <div style="margin-top: 1rem; text-align: right;">
                <span style="color: var(--primary); font-size: 0.875rem; font-weight: 600;">
                    View details <i class="fas fa-arrow-right"></i>
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
                        <div class="stat-value">${topic.trend_score}/10</div>
                        <div class="stat-label">Trend Score</div>
                    </div>
                    <div class="topic-detail-stat">
                        <div class="stat-value">${topic.engagement_metrics?.total_posts || 0}</div>
                        <div class="stat-label">Total Posts</div>
                    </div>
                    <div class="topic-detail-stat">
                        <div class="stat-value">${topic.engagement_metrics?.total_engagement || 0}</div>
                        <div class="stat-label">Engagement</div>
                    </div>
                </div>
                
                <div class="topic-category-section">
                    <h3><i class="fas fa-tag"></i> Category</h3>
                    <span class="category-badge">${topic.category}</span>
                </div>

                <div class="topic-keywords-section">
                    <h3><i class="fas fa-key"></i> Related Keywords</h3>
                    <div class="keywords-list">
                        ${(topic.related_keywords || []).map(keyword => `
                            <span class="keyword-tag">${keyword}</span>
                        `).join('')}
                    </div>
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
    selectedTopic = topic;
    
    // Track activity
    if (typeof trackActivity === 'function') {
        trackActivity(
            'topicViews',
            `Viewed topic: ${formatTopicName(topic.topic)}`,
            'fas fa-eye',
            '#8b5cf6'
        );
    }
}

// Generate sources for topic - FIXED VERSION
function generateTopicSources(topic) {
    // Get sources from the topic data if available
    const sources = topic.sources || [];
    
    if (sources.length === 0) {
        // Fallback with actual working links
        return `
            <div class="source-item">
                <div class="source-icon" style="background: #FF450020; color: #FF4500;">
                    <i class="fab fa-reddit"></i>
                </div>
                <div class="source-details">
                    <div class="source-name">Mumbai Community Discussions</div>
                    <div class="source-meta">Multiple posts about ${formatTopicName(topic.topic).toLowerCase()}</div>
                </div>
                <a href="https://www.reddit.com/r/mumbai/" target="_blank" rel="noopener noreferrer" class="source-link">
                    <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
            <div class="source-item">
                <div class="source-icon" style="background: #6366f120; color: #6366f1;">
                    <i class="fas fa-newspaper"></i>
                </div>
                <div class="source-details">
                    <div class="source-name">Mumbai Local News</div>
                    <div class="source-meta">News coverage about ${formatTopicName(topic.topic).toLowerCase()}</div>
                </div>
                <a href="https://www.hindustantimes.com/cities/mumbai-news" target="_blank" rel="noopener noreferrer" class="source-link">
                    <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        `;
    }
    
    // If we have actual sources, display them
    const iconMap = {
        'social': { icon: 'fab fa-reddit', color: '#FF4500' },
        'news': { icon: 'fas fa-newspaper', color: '#6366f1' },
        'twitter': { icon: 'fab fa-twitter', color: '#1DA1F2' }
    };
    
    return sources.map(source => {
        const iconData = iconMap[source.type] || iconMap['news'];
        
        return `
            <div class="source-item">
                <div class="source-icon" style="background: ${iconData.color}20; color: ${iconData.color};">
                    <i class="${iconData.icon}"></i>
                </div>
                <div class="source-details">
                    <div class="source-name">${source.title.substring(0, 60)}${source.title.length > 60 ? '...' : ''}</div>
                    <div class="source-meta">${source.type === 'social' ? 'Social Media' : 'News Article'}</div>
                </div>
                <a href="${source.url}" target="_blank" rel="noopener noreferrer" class="source-link">
                    <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        `;
    }).join('');
}

// Close topic modal
function closeTopicModal() {
    const modal = document.querySelector('.topic-modal');
    if (modal) {
        modal.remove();
    }
    selectedTopic = null;
}

// Display community concerns
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
    
    // Track activity
    if (typeof trackActivity === 'function') {
        trackActivity(
            'concernViews',
            `Viewed concern: ${concern.concern}`,
            'fas fa-exclamation-triangle',
            '#ef4444'
        );
    }
}

// Generate sources for concern - FIXED VERSION
function generateConcernSources(concern) {
    return `
        <div class="source-item">
            <div class="source-icon" style="background: #6366f120; color: #6366f1;">
                <i class="fas fa-newspaper"></i>
            </div>
            <div class="source-details">
                <div class="source-name">Mumbai Local News</div>
                <div class="source-meta">Multiple reports about ${concern.concern.toLowerCase()}</div>
            </div>
            <a href="https://www.hindustantimes.com/cities/mumbai-news" target="_blank" rel="noopener noreferrer" class="source-link">
                <i class="fas fa-external-link-alt"></i>
            </a>
        </div>
        <div class="source-item">
            <div class="source-icon" style="background: #FF450020; color: #FF4500;">
                <i class="fab fa-reddit"></i>
            </div>
            <div class="source-details">
                <div class="source-name">Community Reports</div>
                <div class="source-meta">Citizen discussions about ${concern.concern.toLowerCase()}</div>
            </div>
            <a href="https://www.reddit.com/r/mumbai/" target="_blank" rel="noopener noreferrer" class="source-link">
                <i class="fas fa-external-link-alt"></i>
            </a>
        </div>
    `;
}

// Close concern modal
function closeConcernModal() {
    const modal = document.querySelector('.concern-modal');
    if (modal) {
        modal.remove();
    }
}

// Format topic name for display
function formatTopicName(topic) {
    if (!topic) return 'Unknown Topic';
    
    // Convert to title case and handle special cases
    return topic
        .split(/[\s_-]+/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ')
        .replace(/\bMumbai\b/g, 'Mumbai')
        .replace(/\bBmc\b/g, 'BMC')
        .replace(/\bApi\b/g, 'API');
}

// Create cluster visualization
function createClusterVisualization(data) {
    const canvas = document.getElementById('clusterCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;

    const topics = data?.insights?.trending_topics || [];
    if (topics.length === 0) return;

    // Create clusters based on categories
    const clusters = {};
    topics.forEach(topic => {
        const category = topic.category || 'General';
        if (!clusters[category]) {
            clusters[category] = [];
        }
        clusters[category].push(topic);
    });

    const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444'];
    let colorIndex = 0;

    Object.keys(clusters).forEach(category => {
        const color = colors[colorIndex % colors.length];
        const clusterTopics = clusters[category];
        
        // Position clusters in a circle
        const centerX = canvas.width / 2 + Math.cos(colorIndex * 2 * Math.PI / Object.keys(clusters).length) * 100;
        const centerY = canvas.height / 2 + Math.sin(colorIndex * 2 * Math.PI / Object.keys(clusters).length) * 100;

        clusterTopics.forEach((topic, index) => {
            const angle = (index / clusterTopics.length) * 2 * Math.PI;
            const radius = 30 + topic.trend_score * 3;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;

            // Draw topic circle
            ctx.beginPath();
            ctx.arc(x, y, 5 + topic.trend_score, 0, 2 * Math.PI);
            ctx.fillStyle = color + '80';
            ctx.fill();
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.stroke();

            // Draw connection to center
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.strokeStyle = color + '40';
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        // Draw category label
        ctx.fillStyle = color;
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(category, centerX, centerY - 20);

        colorIndex++;
    });
}

// Setup event listeners
function setupEventListeners() {
    // Close modals when clicking outside
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('topic-modal') || e.target.classList.contains('concern-modal')) {
            e.target.remove();
        }
    });

    // Handle window resize for canvas
    window.addEventListener('resize', () => {
        if (communityData) {
            createClusterVisualization(communityData);
        }
    });

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
            <div class="notification-item clickable" onclick="handleNotificationClick(${index})" data-alert-index="${index}">
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
    // Navigate to alerts page or show alert details
    window.location.href = 'alerts.html';
}

// Load user dashboard data
async function loadUserDashboard() {
    // This would typically load user-specific data
    // For now, we'll use placeholder data
}

// Utility functions
function getSourceIcon(source) {
    const icons = {
        'news': 'newspaper',
        'social': 'comments',
        'permit': 'file-alt',
        'image_analysis': 'camera'
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