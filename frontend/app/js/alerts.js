// Alerts Page JavaScript

let allAlerts = [];
let currentFilter = 'all';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAlerts();
    setupEventListeners();
    initInteractiveMap();
});

// Location coordinates mapping for Mumbai areas
const locationCoords = {
    'Andheri West': [19.1136, 72.8697],
    'Bandra': [19.0596, 72.8295],
    'Thane': [19.2183, 72.9781],
    'Kandivali': [19.2043, 72.8543],
    'Goregaon-Mulund': [19.1646, 72.9106],
    'Sion': [19.0433, 72.8636],
    'Nagpur': [21.1458, 79.0882],
    'Mumbai': [19.076, 72.8777]
};

// Load alerts from API
async function loadAlerts() {
    try {
        const data = await api.getAlerts();
        allAlerts = data.alerts || [];
        
        updateStats(allAlerts);
        displayAlerts(allAlerts);
    } catch (error) {
        console.error('Error loading alerts:', error);
        document.getElementById('alertsGrid').innerHTML = 
            '<p style="text-align: center; color: var(--gray); padding: 3rem;">Unable to load alerts. Please try again later.</p>';
    }
}

// Update statistics
function updateStats(alerts) {
    const highPriority = alerts.filter(a => a.priority === 'high').length;
    const mediumPriority = alerts.filter(a => a.priority === 'medium').length;
    const lowPriority = alerts.filter(a => a.priority === 'low').length;
    
    animateCounter('highPriorityCount', highPriority);
    animateCounter('mediumPriorityCount', mediumPriority);
    animateCounter('lowPriorityCount', lowPriority);
    animateCounter('totalAlertsCount', alerts.length);
}

// Display alerts
function displayAlerts(alerts) {
    const alertsGrid = document.getElementById('alertsGrid');
    if (!alertsGrid) return;

    if (alerts.length === 0) {
        alertsGrid.innerHTML = '<p style="text-align: center; color: var(--gray); padding: 3rem;">No alerts found.</p>';
        return;
    }

    alertsGrid.innerHTML = alerts.map((alert, index) => `
        <div class="alert-card priority-${alert.priority}" data-alert-index="${index}" style="cursor: pointer;">
            <div class="alert-card-header">
                <div>
                    <div class="alert-card-title">${alert.title}</div>
                </div>
                <div class="alert-card-priority">${alert.priority_score}/10</div>
            </div>
            <div class="alert-card-message">${alert.message}</div>
            <div class="alert-card-details" id="alertDetails${index}" style="display: none; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
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
                    ${alert.metadata ? `
                    <div>
                        <div style="color: var(--gray); font-size: 0.875rem;">Additional Info</div>
                        <div style="font-weight: 600;">${alert.metadata.project_name || alert.metadata.title || 'N/A'}</div>
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
            <div class="alert-card-footer">
                <div class="alert-card-source">
                    <i class="fas fa-${getSourceIcon(alert.source)}"></i>
                    <span>${alert.source}</span>
                    ${alert.location ? `<span>• ${alert.location}</span>` : ''}
                </div>
                <div class="alert-card-time">${formatTime(alert.timestamp)}</div>
            </div>
        </div>
    `).join('');
    
    // Add event delegation for alert clicks
    alertsGrid.addEventListener('click', handleAlertClick);
}

// Handle alert card clicks with event delegation
function handleAlertClick(event) {
    // Find the alert card element (could be clicked on child element)
    const alertCard = event.target.closest('.alert-card');
    if (!alertCard) return;
    
    // Don't toggle if clicking on a link
    if (event.target.tagName === 'A' || event.target.closest('a')) return;
    
    // Get the alert index from data attribute
    const index = alertCard.dataset.alertIndex;
    if (index !== undefined) {
        toggleAlertDetails(index);
    }
}

// Toggle alert details
function toggleAlertDetails(index) {
    const details = document.getElementById(`alertDetails${index}`);
    if (details) {
        if (details.style.display === 'none') {
            details.style.display = 'block';
            
            // Track activity when alert is opened
            if (typeof trackActivity === 'function' && allAlerts[index]) {
                trackActivity(
                    'alertsChecked',
                    `Checked alert: ${allAlerts[index].title}`,
                    'fas fa-bell',
                    '#f59300'
                );
            }
        } else {
            details.style.display = 'none';
        }
    }
}

// Filter alerts
function filterAlerts(type) {
    currentFilter = type;
    
    if (type === 'all') {
        displayAlerts(allAlerts);
    } else {
        const filtered = allAlerts.filter(alert => alert.type === type);
        displayAlerts(filtered);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.dataset.filter;
            filterAlerts(filter);
        });
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

// Initialize interactive map with Leaflet.js
function initInteractiveMap() {
    const mapContainer = document.getElementById('alertsMap');
    if (!mapContainer) {
        console.error('Map container not found');
        return;
    }

    console.log('Initializing Leaflet map...');

    // Initialize Leaflet map centered on Mumbai
    const map = L.map('alertsMap').setView([19.076, 72.8777], 11);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        minZoom: 10
    }).addTo(map);

    console.log('Map tiles added');

    // Wait for alerts to load, then add markers
    const checkAlertsInterval = setInterval(() => {
        if (allAlerts && allAlerts.length > 0) {
            console.log('Alerts loaded, adding markers:', allAlerts.length);
            clearInterval(checkAlertsInterval);
            addMarkersToMap(map);
        }
    }, 100);
}

// Add markers to map for each alert
function addMarkersToMap(map) {
    // Group alerts by location for clustering
    const alertsByLocation = {};
    
    allAlerts.forEach(alert => {
        const location = alert.location || 'Mumbai';
        if (!alertsByLocation[location]) {
            alertsByLocation[location] = [];
        }
        alertsByLocation[location].push(alert);
    });

    console.log('Grouped alerts by location:', Object.keys(alertsByLocation));

    // Add markers for each location
    Object.keys(alertsByLocation).forEach(location => {
        try {
            const alerts = alertsByLocation[location];
            
            // Try to get coordinates from alert data first, then fall back to locationCoords
            let coords = locationCoords['Mumbai']; // default
            
            // Check if any alert has geo coordinates
            const alertWithGeo = alerts.find(alert => alert.geo && alert.geo.lat && alert.geo.lon);
            if (alertWithGeo) {
                coords = [alertWithGeo.geo.lat, alertWithGeo.geo.lon];
            } else if (locationCoords[location]) {
                coords = locationCoords[location];
            }
            
            console.log(`Creating marker for ${location} at`, coords);
            
            // Determine marker color based on highest priority in this location
            const highestPriority = alerts.reduce((max, alert) => {
                return alert.priority_score > max ? alert.priority_score : max;
            }, 0);
            
            const markerColor = highestPriority >= 8 ? '#ef4444' : 
                               highestPriority >= 5 ? '#f59e0b' : '#10b981';
            
            // Create custom icon with better clickability
            const customIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div class="marker-circle" style="background-color: ${markerColor}; 
                                  width: 40px; height: 40px; border-radius: 50%; 
                                  border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                                  display: flex; align-items: center; justify-content: center;
                                  color: white; font-weight: bold; font-size: 16px;
                                  cursor: pointer;">
                        ${alerts.length}
                       </div>`,
                iconSize: [40, 40],
                iconAnchor: [20, 20],
                popupAnchor: [0, -20]
            });
            
            // Create marker
            const marker = L.marker(coords, { 
                icon: customIcon,
                title: `${location} - ${alerts.length} alert${alerts.length > 1 ? 's' : ''}` 
            }).addTo(map);
            
            console.log(`Marker created for ${location}`);
            
            // Build popup HTML
            let popupHTML = `
                <div style="max-width: 300px; max-height: 400px; overflow-y: auto; padding: 4px;">
                    <h3 style="margin: 0 0 8px 0; color: #1e293b; font-size: 16px; font-weight: 700;">${location}</h3>
                    <div style="color: #64748b; font-size: 13px; margin-bottom: 12px; font-weight: 500;">${alerts.length} alert${alerts.length > 1 ? 's' : ''}</div>
                    <div class="popup-alerts-list">`;
            
            alerts.forEach((alert, index) => {
                // Defensive checks for all properties
                const priorityColor = alert.priority === 'high' ? '#ef4444' : 
                                     alert.priority === 'medium' ? '#f59e0b' : '#10b981';
                
                const alertIndex = allAlerts.indexOf(alert);
                const alertTitle = (alert.title || alert.metadata?.title || 'Alert').toString();
                const alertMessage = (alert.message || alert.description || alert.metadata?.description || 'No details available').toString();
                const alertPriority = alert.priority_score || 0;
                
                // Safely truncate message
                const truncatedMessage = alertMessage.length > 100 ? alertMessage.substring(0, 100) + '...' : alertMessage;
                
                popupHTML += `
                    <div class="popup-alert-item" data-alert-index="${alertIndex}" 
                         style="border-left: 3px solid ${priorityColor}; 
                                padding: 8px 0 8px 12px; 
                                margin-bottom: ${index < alerts.length - 1 ? '12px' : '0'}; 
                                cursor: pointer;
                                transition: all 0.2s;">
                        <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px; font-size: 14px;">${alertTitle}</div>
                        <div style="color: #64748b; font-size: 13px; margin-bottom: 6px; line-height: 1.4;">${truncatedMessage}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                            <span style="font-weight: 600; color: ${priorityColor}; font-size: 12px;">Priority: ${alertPriority}/10</span>
                            <span style="color: #6366f1; font-size: 12px; font-weight: 500;">Click to view →</span>
                        </div>
                    </div>`;
            });
            
            popupHTML += `</div></div>`;
            
            // Create and bind popup
            marker.bindPopup(popupHTML, {
                maxWidth: 320,
                minWidth: 280,
                className: 'custom-popup',
                closeButton: true,
                autoClose: true,
                closeOnClick: false
            });
            
            console.log(`Popup bound for ${location}`);
            
            // Handle popup open event to attach click listeners
            marker.on('popupopen', function(e) {
                console.log('Popup opened for', location);
                // Small delay to ensure DOM is ready
                setTimeout(() => {
                    const popup = e.popup;
                    const popupElement = popup.getElement();
                    
                    if (popupElement) {
                        const alertItems = popupElement.querySelectorAll('.popup-alert-item');
                        console.log('Found alert items in popup:', alertItems.length);
                        
                        alertItems.forEach(item => {
                            item.addEventListener('click', function(event) {
                                event.stopPropagation();
                                const alertIndex = parseInt(this.getAttribute('data-alert-index'));
                                
                                console.log('Clicked alert index:', alertIndex);
                                
                                // Close popup
                                map.closePopup();
                                
                                // Scroll to alert
                                scrollToAlert(alertIndex);
                            });
                            
                            // Add hover effect
                            item.addEventListener('mouseenter', function() {
                                this.style.background = 'rgba(99, 102, 241, 0.05)';
                                this.style.borderRadius = '8px';
                                this.style.marginLeft = '-4px';
                                this.style.paddingLeft = '16px';
                            });
                            
                            item.addEventListener('mouseleave', function() {
                                this.style.background = '';
                                this.style.borderRadius = '';
                                this.style.marginLeft = '';
                                this.style.paddingLeft = '12px';
                            });
                        });
                    }
                }, 50);
            });
            
            // Disable double-click zoom on marker
            marker.on('dblclick', function(e) {
                L.DomEvent.stopPropagation(e);
            });
            
        } catch (error) {
            console.error(`Error creating marker for ${location}:`, error);
        }
    });
    
    console.log('All markers added to map');
}

// Old SVG map function (kept as fallback/reference)
/*
function initMap() {
    const mapContainer = document.getElementById('alertsMap');
    if (!mapContainer) return;

    // Create SVG map of Mumbai
    const locations = [
        { name: 'Andheri West', x: 200, y: 150, alerts: 2 },
        { name: 'Bandra', x: 250, y: 200, alerts: 1 },
        { name: 'Thane', x: 400, y: 100, alerts: 3 },
        { name: 'Kandivali', x: 150, y: 100, alerts: 1 },
        { name: 'Goregaon-Mulund', x: 350, y: 150, alerts: 1 },
        { name: 'Sion', x: 300, y: 250, alerts: 1 },
        { name: 'Nagpur', x: 500, y: 200, alerts: 2 }
    ];

    const svg = `
        <svg width="100%" height="100%" viewBox="0 0 700 500" style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%);">
            <!-- Mumbai outline (simplified) -->
            <path d="M 150 100 L 200 80 L 300 100 L 400 80 L 500 120 L 550 200 L 500 300 L 400 350 L 300 320 L 200 300 L 150 250 Z" 
                  fill="rgba(99, 102, 241, 0.1)" 
                  stroke="rgba(99, 102, 241, 0.3)" 
                  stroke-width="2"/>
            
            <!-- Location markers -->
            ${locations.map(loc => `
                <g class="location-marker" style="cursor: pointer;" onmouseover="this.querySelector('circle').setAttribute('r', '${15 + loc.alerts * 3}')" onmouseout="this.querySelector('circle').setAttribute('r', '${10 + loc.alerts * 2}')">
                    <circle cx="${loc.x}" cy="${loc.y}" r="${10 + loc.alerts * 2}" 
                            fill="${loc.alerts > 2 ? '#ef4444' : loc.alerts > 1 ? '#f59e0b' : '#10b981'}" 
                            opacity="0.6">
                        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="${loc.x}" cy="${loc.y}" r="${5 + loc.alerts}" 
                            fill="${loc.alerts > 2 ? '#ef4444' : loc.alerts > 1 ? '#f59e0b' : '#10b981'}"/>
                    <text x="${loc.x}" y="${loc.y - 20}" 
                          text-anchor="middle" 
                          fill="white" 
                          font-size="12" 
                          font-weight="600">
                        ${loc.name}
                    </text>
                    <text x="${loc.x}" y="${loc.y + 25}" 
                          text-anchor="middle" 
                          fill="white" 
                          font-size="10" 
                          opacity="0.8">
                        ${loc.alerts} alert${loc.alerts > 1 ? 's' : ''}
                    </text>
                </g>
            `).join('')}
            
            <!-- Legend -->
            <g transform="translate(20, 420)">
                <rect x="0" y="0" width="200" height="70" fill="rgba(15, 23, 42, 0.9)" rx="10"/>
                <text x="10" y="20" fill="white" font-size="12" font-weight="600">Alert Severity</text>
                <circle cx="20" cy="35" r="6" fill="#ef4444"/>
                <text x="35" y="40" fill="white" font-size="11">High (3+)</text>
                <circle cx="20" cy="55" r="6" fill="#f59e0b"/>
                <text x="35" y="60" fill="white" font-size="11">Medium (2)</text>
                <circle cx="120" cy="55" r="6" fill="#10b981"/>
                <text x="135" y="60" fill="white" font-size="11">Low (1)</text>
            </g>
        </svg>
    `;

    mapContainer.innerHTML = svg;
}
*/

// Scroll to specific alert in the list
function scrollToAlert(alertIndex) {
    // Close the map popup
    const alertsGrid = document.getElementById('alertsGrid');
    if (!alertsGrid) return;
    
    // Find the alert card
    const alertCard = alertsGrid.querySelector(`[data-alert-index="${alertIndex}"]`);
    if (alertCard) {
        // Scroll to the alert
        alertCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Highlight the alert briefly
        alertCard.style.transform = 'translateX(10px)';
        alertCard.style.borderColor = 'var(--primary)';
        
        // Open details automatically
        setTimeout(() => {
            toggleAlertDetails(alertIndex);
        }, 500);
        
        // Reset highlight after animation
        setTimeout(() => {
            alertCard.style.transform = '';
        }, 2000);
    }
}
