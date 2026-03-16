// Morning Briefing Page JavaScript

let briefingData = null;
let audioElement = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadBriefing();
    setupEventListeners();
});

// Load morning briefing
async function loadBriefing() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/api/briefing`);
        const data = await response.json();
        
        if (data.success) {
            briefingData = data.data;
            displayBriefing(briefingData);
        } else {
            showError('Unable to load briefing');
        }
    } catch (error) {
        console.error('Error loading briefing:', error);
        showError('Failed to connect to server');
    }
}

// Display briefing
function displayBriefing(briefing) {
    // Update title and subtitle
    const title = document.getElementById('briefingTitle');
    const subtitle = document.getElementById('briefingSubtitle');
    
    if (title) {
        const date = new Date(briefing.generated_at);
        title.textContent = `Good Morning, Mumbai! - ${date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}`;
    }
    
    if (subtitle) {
        subtitle.textContent = `Generated at ${new Date(briefing.generated_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
    }
    
    // Update stats
    const newsSection = briefing.sections.find(s => s.type === 'news');
    const permitSection = briefing.sections.find(s => s.type === 'permits');
    
    animateCounter('newsCount', newsSection ? newsSection.items_count : 0);
    animateCounter('permitCount', permitSection ? permitSection.items_count : 0);
    
    const durationEl = document.getElementById('durationEstimate');
    if (durationEl) {
        durationEl.textContent = `${Math.round(briefing.duration_estimate_seconds)}s`;
    }
    
    // Update content
    const content = document.getElementById('briefingContent');
    if (content) {
        // Format the text content with proper paragraphs
        const formattedText = briefing.text_content
            .replace(/\*\*/g, '')  // Remove markdown bold
            .split('\n\n')  // Split by double newlines
            .filter(p => p.trim())  // Remove empty paragraphs
            .map(p => `<p>${p.trim()}</p>`)  // Wrap in paragraph tags
            .join('');
        
        content.innerHTML = formattedText;
        
        // Add sources section if available
        if (briefing.sections && briefing.sections.length > 0) {
            const sourcesHtml = createSourcesSection(briefing.sections);
            content.innerHTML += sourcesHtml;
        }
    }
    
    // Enable play button if audio is available
    const playBtn = document.getElementById('playBriefingBtn');
    if (playBtn) {
        playBtn.disabled = false;
    }
}

// Show error message
function showError(message) {
    const content = document.getElementById('briefingContent');
    if (content) {
        content.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--gray);">
                <i class="fas fa-exclamation-circle" style="font-size: 3rem; margin-bottom: 1rem; color: var(--danger);"></i>
                <p>${message}</p>
                <button onclick="loadBriefing()" style="margin-top: 1rem; padding: 0.75rem 1.5rem; background: var(--primary); border: none; border-radius: 8px; color: white; cursor: pointer;">
                    Try Again
                </button>
            </div>
        `;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Play briefing button
    const playBtn = document.getElementById('playBriefingBtn');
    if (playBtn) {
        playBtn.addEventListener('click', playBriefing);
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBriefingBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            loadBriefing().then(() => {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
            });
        });
    }
    
    // Share button
    const shareBtn = document.getElementById('shareBriefingBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', shareBriefing);
    }
    
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

// Play briefing audio
async function playBriefing() {
    const playBtn = document.getElementById('playBriefingBtn');
    
    if (!briefingData) {
        alert('No briefing data available');
        return;
    }
    
    // If audio is already playing, pause it
    if (audioElement && !audioElement.paused) {
        audioElement.pause();
        playBtn.innerHTML = '<i class="fas fa-play"></i> Play Audio Briefing';
        return;
    }
    
    // Try to get audio from server
    try {
        playBtn.disabled = true;
        playBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading Audio...';
        
        // Check if audio file exists
        const audioUrl = `${API_CONFIG.BASE_URL}/api/audio/morning_briefing.mp3`;
        
        audioElement = new Audio(audioUrl);
        
        audioElement.onloadeddata = () => {
            playBtn.disabled = false;
            playBtn.innerHTML = '<i class="fas fa-pause"></i> Pause Audio';
            audioElement.play();
        };
        
        audioElement.onended = () => {
            playBtn.innerHTML = '<i class="fas fa-play"></i> Play Audio Briefing';
        };
        
        audioElement.onerror = () => {
            playBtn.disabled = false;
            playBtn.innerHTML = '<i class="fas fa-play"></i> Play Audio Briefing';
            alert('Audio not available. The briefing text is displayed above.');
        };
        
    } catch (error) {
        console.error('Error playing audio:', error);
        playBtn.disabled = false;
        playBtn.innerHTML = '<i class="fas fa-play"></i> Play Audio Briefing';
        alert('Unable to play audio. Please check your connection.');
    }
}

// Share briefing
function shareBriefing() {
    if (!briefingData) return;
    
    const shareText = `Check out my morning briefing from CityPulse!\n\n${briefingData.text_content.substring(0, 200)}...`;
    
    if (navigator.share) {
        navigator.share({
            title: 'CityPulse Morning Briefing',
            text: shareText,
            url: window.location.href
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Briefing copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
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

        notificationList.innerHTML = recentAlerts.map(alert => `
            <div class="notification-item">
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

// Utility functions
function createSourcesSection(sections) {
    const newsSection = sections.find(s => s.type === 'news');
    const permitSection = sections.find(s => s.type === 'permits');
    
    let sourcesHtml = '<div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">';
    sourcesHtml += '<h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; color: var(--primary);">📚 Data Sources</h3>';
    sourcesHtml += '<div style="display: grid; gap: 1rem;">';
    
    if (newsSection && newsSection.items_count > 0) {
        sourcesHtml += `
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; border-left: 3px solid #6366f1;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <i class="fas fa-newspaper" style="color: #6366f1;"></i>
                    <span style="font-weight: 600;">News Articles</span>
                </div>
                <div style="color: var(--gray); font-size: 0.875rem;">
                    ${newsSection.items_count} articles from Mumbai news sources
                </div>
                <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <a href="https://www.mid-day.com/mumbai" target="_blank" style="font-size: 0.75rem; color: #6366f1; text-decoration: none;">Mid-Day</a>
                    <span style="color: var(--gray);">•</span>
                    <a href="https://www.hindustantimes.com/cities/mumbai-news" target="_blank" style="font-size: 0.75rem; color: #6366f1; text-decoration: none;">Hindustan Times</a>
                    <span style="color: var(--gray);">•</span>
                    <a href="https://timesofindia.indiatimes.com/city/mumbai" target="_blank" style="font-size: 0.75rem; color: #6366f1; text-decoration: none;">Times of India</a>
                </div>
            </div>
        `;
    }
    
    if (permitSection && permitSection.items_count > 0) {
        sourcesHtml += `
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; border-left: 3px solid #10b981;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <i class="fas fa-building" style="color: #10b981;"></i>
                    <span style="font-weight: 600;">Permit Data</span>
                </div>
                <div style="color: var(--gray); font-size: 0.875rem;">
                    ${permitSection.items_count} permit activities tracked
                </div>
                <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <a href="https://maharera.maharashtra.gov.in/" target="_blank" style="font-size: 0.75rem; color: #10b981; text-decoration: none;">MahaRERA</a>
                    <span style="color: var(--gray);">•</span>
                    <a href="https://portal.mcgm.gov.in/" target="_blank" style="font-size: 0.75rem; color: #10b981; text-decoration: none;">BMC Portal</a>
                </div>
            </div>
        `;
    }
    
    // Add social media source
    sourcesHtml += `
        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; border-left: 3px solid #f59e0b;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <i class="fas fa-comments" style="color: #f59e0b;"></i>
                <span style="font-weight: 600;">Community Insights</span>
            </div>
            <div style="color: var(--gray); font-size: 0.875rem;">
                Social media sentiment and community discussions
            </div>
            <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <a href="https://www.reddit.com/r/mumbai/" target="_blank" style="font-size: 0.75rem; color: #f59e0b; text-decoration: none;">r/mumbai</a>
                <span style="color: var(--gray);">•</span>
                <a href="https://www.reddit.com/r/india/" target="_blank" style="font-size: 0.75rem; color: #f59e0b; text-decoration: none;">r/india</a>
            </div>
        </div>
    `;
    
    // Add AI attribution
    sourcesHtml += `
        <div style="background: rgba(99,102,241,0.1); padding: 1rem; border-radius: 10px; border: 1px solid rgba(99,102,241,0.3); margin-top: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <i class="fas fa-robot" style="color: #6366f1;"></i>
                <span style="font-weight: 600; color: #6366f1;">AI-Powered Analysis</span>
            </div>
            <div style="color: var(--gray); font-size: 0.875rem; line-height: 1.6;">
                This briefing was generated using <strong>Amazon Nova 2 Lite</strong> for natural language generation 
                and <strong>Amazon Polly Neural TTS</strong> for voice synthesis. 
                All data is analyzed and summarized by AI to provide you with the most relevant information.
            </div>
        </div>
    `;
    
    sourcesHtml += '</div></div>';
    
    return sourcesHtml;
}

function animateCounter(elementId, target) {
    const element = document.getElementById(elementId);
    if (!element) return;

    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 30);
}

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
