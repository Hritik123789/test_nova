// Main JavaScript for Homepage

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initHeroAnimation();
    loadStats();
    loadRecentAlerts();
    setupEventListeners();
});

// Hero 3D Animation with Three.js
function initHeroAnimation() {
    const canvas = document.getElementById('heroCanvas');
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Create particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1000;
    const posArray = new Float32Array(particlesCount * 3);
    
    for (let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 10;
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.02,
        color: 0x6366f1,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });
    
    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);
    
    camera.position.z = 3;
    
    // Mouse movement
    let mouseX = 0;
    let mouseY = 0;
    
    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    });
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        particlesMesh.rotation.y += 0.001;
        particlesMesh.rotation.x += 0.0005;
        
        // Follow mouse
        camera.position.x += (mouseX * 0.5 - camera.position.x) * 0.05;
        camera.position.y += (mouseY * 0.5 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);
        
        renderer.render(scene, camera);
    }
    
    animate();
    
    // Handle resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Load stats with animation
async function loadStats() {
    try {
        const [alertsData, permitsData, communityData] = await Promise.all([
            api.getAlerts().catch(() => ({ count: 13 })),
            api.getPermits().catch(() => ({ data: new Array(4) })),
            api.getCommunity().catch(() => ({ data: { basic_topics: { top_social_topics: new Array(10) } } }))
        ]);

        animateCounter('alertCount', alertsData.count || 13);
        animateCounter('permitCount', permitsData.data?.length || 4);
        animateCounter('topicCount', communityData.data?.basic_topics?.top_social_topics?.length || 10);
    } catch (error) {
        console.error('Error loading stats:', error);
        // Fallback to default values
        animateCounter('alertCount', 13);
        animateCounter('permitCount', 4);
        animateCounter('topicCount', 10);
    }
}

// Animate counter
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

// Load recent alerts
async function loadRecentAlerts() {
    const alertsPreview = document.getElementById('alertsPreview');
    if (!alertsPreview) return;

    try {
        const data = await api.getAlerts();
        const alerts = data.alerts || [];
        const recentAlerts = alerts.slice(0, 5);

        alertsPreview.innerHTML = recentAlerts.map((alert, index) => `
            <div class="alert-item priority-${alert.priority}" data-alert-index="${index}" style="cursor: pointer;">
                <div class="alert-header">
                    <div>
                        <div class="alert-title">${alert.title}</div>
                        <div class="alert-message">${alert.message}</div>
                    </div>
                    <div class="alert-priority">${alert.priority_score}/10</div>
                </div>
                <div class="alert-details" id="homeAlertDetails${index}" style="display: none; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                        <div>
                            <div style="color: var(--gray); font-size: 0.875rem;">Priority Reason</div>
                            <div style="font-weight: 600;">${alert.priority_reason || 'N/A'}</div>
                        </div>
                        ${alert.engagement ? `
                        <div>
                            <div style="color: var(--gray); font-size: 0.875rem;">Engagement</div>
                            <div style="font-weight: 600;">${alert.engagement.upvotes} upvotes, ${alert.engagement.comments} comments</div>
                        </div>
                        ` : ''}
                    </div>
                    ${alert.url ? `
                    <a href="${alert.url}" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; background: var(--primary); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.875rem;">
                        <i class="fas fa-external-link-alt"></i> View Source
                    </a>
                    ` : alert.metadata && alert.metadata.url ? `
                    <a href="${alert.metadata.url}" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; background: var(--primary); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.875rem;">
                        <i class="fas fa-search"></i> Search on MahaRERA
                    </a>
                    ` : alert.type === 'development' || alert.type === 'new_business' ? `
                    <a href="https://maharera.maharashtra.gov.in/projects-search-result" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; background: var(--success); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.875rem;">
                        <i class="fas fa-building"></i> View on MahaRERA
                    </a>
                    ` : `
                    <div style="color: var(--gray); font-size: 0.875rem; font-style: italic;">
                        <i class="fas fa-database"></i> Internal data source
                    </div>
                    `}
                </div>
                <div class="alert-footer">
                    <div class="alert-source">
                        <i class="fas fa-${getSourceIcon(alert.source)}"></i>
                        <span>${alert.source}</span>
                    </div>
                    <div class="alert-time">${formatTime(alert.timestamp)}</div>
                </div>
            </div>
        `).join('');
        
        // Add event delegation for alert clicks
        alertsPreview.addEventListener('click', handleHomeAlertClick);
    } catch (error) {
        console.error('Error loading alerts:', error);
        alertsPreview.innerHTML = '<p style="text-align: center; color: var(--gray);">Unable to load alerts. Please try again later.</p>';
    }
}

// Handle home alert card clicks with event delegation
function handleHomeAlertClick(event) {
    // Find the alert item element (could be clicked on child element)
    const alertItem = event.target.closest('.alert-item');
    if (!alertItem) return;
    
    // Don't toggle if clicking on a link
    if (event.target.tagName === 'A' || event.target.closest('a')) return;
    
    // Get the alert index from data attribute
    const index = alertItem.dataset.alertIndex;
    if (index !== undefined) {
        toggleHomeAlertDetails(index);
    }
}

// Toggle home alert details
function toggleHomeAlertDetails(index) {
    const details = document.getElementById(`homeAlertDetails${index}`);
    if (details) {
        if (details.style.display === 'none') {
            details.style.display = 'block';
        } else {
            details.style.display = 'none';
        }
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
            <div class="notification-item clickable" data-alert-index="${index}">
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

        // Add click event listeners to notification items
        document.querySelectorAll('.notification-item[data-alert-index]').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(item.getAttribute('data-alert-index'));
                handleNotificationClick(index);
            });
        });
    } catch (error) {
        console.error('Error loading notifications:', error);
        notificationList.innerHTML = '<p style="text-align: center; color: var(--gray); padding: 2rem;">Unable to load notifications.</p>';
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
