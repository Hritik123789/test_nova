// Permits Page - 3D Visualization

let scene, camera, renderer, buildings = [];
let selectedBuilding = null;
let isRotating = true;
let permitsData = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    init3DScene();
    loadPermits();
    setupEventListeners();
});

// Initialize 3D scene
function init3DScene() {
    const canvas = document.getElementById('permitsCanvas');
    if (!canvas) return;

    const container = canvas.parentElement;
    
    // Scene setup
    scene = new THREE.Scene();
    scene.background = null;
    scene.fog = new THREE.Fog(0x0f172a, 10, 50);

    // Camera setup
    camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(15, 15, 15);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    scene.add(directionalLight);

    const pointLight = new THREE.PointLight(0x6366f1, 1, 50);
    pointLight.position.set(0, 10, 0);
    scene.add(pointLight);

    // Ground grid
    const gridHelper = new THREE.GridHelper(30, 30, 0x6366f1, 0x1e293b);
    scene.add(gridHelper);

    // Mouse interaction
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    canvas.addEventListener('click', (event) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(buildings);

        if (intersects.length > 0) {
            selectBuilding(intersects[0].object);
        }
    });

    // Handle resize
    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });

    // Animation loop
    animate();
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);

    if (isRotating) {
        buildings.forEach((building, index) => {
            building.rotation.y += 0.002 * (index % 2 === 0 ? 1 : -1);
        });
    }

    // Pulse selected building
    if (selectedBuilding) {
        const scale = 1 + Math.sin(Date.now() * 0.003) * 0.05;
        selectedBuilding.scale.set(1, scale, 1);
    }

    renderer.render(scene, camera);
}

// Load permits and create 3D buildings
async function loadPermits() {
    try {
        const data = await api.getPermits();
        permitsData = data.data || [];

        // Create 3D buildings
        createBuildings(permitsData);

        // Load permits list
        loadPermitsList(permitsData);
    } catch (error) {
        console.error('Error loading permits:', error);
        // Create sample buildings
        createSampleBuildings();
    }
}

// Create 3D buildings from permits data
function createBuildings(permits) {
    const positions = [
        { x: -8, z: -8 },
        { x: 8, z: -8 },
        { x: -8, z: 8 },
        { x: 8, z: 8 }
    ];

    permits.forEach((permit, index) => {
        if (index >= positions.length) return;

        const pos = positions[index];
        const height = 3 + Math.random() * 5;
        const width = 2 + Math.random() * 1;

        // Building geometry
        const geometry = new THREE.BoxGeometry(width, height, width);
        
        // Building material with gradient
        const material = new THREE.MeshPhongMaterial({
            color: getColorForPermitType(permit.event_type),
            emissive: 0x6366f1,
            emissiveIntensity: 0.2,
            shininess: 100
        });

        const building = new THREE.Mesh(geometry, material);
        building.position.set(pos.x, height / 2, pos.z);
        building.userData = permit;

        // Add edges
        const edges = new THREE.EdgesGeometry(geometry);
        const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x8b5cf6 });
        const edgeLines = new THREE.LineSegments(edges, edgeMaterial);
        building.add(edgeLines);

        scene.add(building);
        buildings.push(building);
    });
}

// Create sample buildings if API fails
function createSampleBuildings() {
    const samplePermits = [
        { project_name: 'Andheri Heights', location: 'Andheri West', event_type: 'real_estate_project' },
        { project_name: 'Bandra Business Park', location: 'Bandra East', event_type: 'real_estate_project' },
        { project_name: 'GMLR Phase IV', location: 'Goregaon-Mulund', event_type: 'construction_approval' },
        { project_name: 'Sion ROB', location: 'Sion', event_type: 'construction_approval' }
    ];
    createBuildings(samplePermits);
    loadPermitsList(samplePermits);
}

// Select building
function selectBuilding(building) {
    // Reset previous selection
    if (selectedBuilding) {
        selectedBuilding.scale.set(1, 1, 1);
        selectedBuilding.material.emissiveIntensity = 0.2;
    }

    selectedBuilding = building;
    selectedBuilding.material.emissiveIntensity = 0.5;

    // Show details panel
    showPermitDetails(building.userData);
}

// Show permit details
function showPermitDetails(permit) {
    const panel = document.getElementById('permitDetailsPanel');
    const title = document.getElementById('permitDetailsTitle');
    const grid = document.getElementById('permitDetailsGrid');

    if (!panel || !title || !grid) return;

    // Track activity
    if (typeof trackActivity === 'function') {
        trackActivity(
            'permitsViewed',
            `Viewed permit: ${permit.metadata?.project_name || permit.description || 'Permit'}`,
            'fas fa-building',
            '#10b981'
        );
    }

    title.textContent = permit.metadata?.project_name || permit.description || 'Permit Details';

    grid.innerHTML = `
        <div class="permit-detail-item">
            <div class="permit-detail-label">Location</div>
            <div class="permit-detail-value">${permit.location || 'N/A'}</div>
        </div>
        <div class="permit-detail-item">
            <div class="permit-detail-label">Type</div>
            <div class="permit-detail-value">${formatEventType(permit.event_type)}</div>
        </div>
        <div class="permit-detail-item">
            <div class="permit-detail-label">Promoter</div>
            <div class="permit-detail-value">${permit.metadata?.promoter || 'N/A'}</div>
        </div>
        <div class="permit-detail-item">
            <div class="permit-detail-label">Date</div>
            <div class="permit-detail-value">${formatDate(permit.timestamp)}</div>
        </div>
        ${permit.metadata?.registration_number ? `
        <div class="permit-detail-item">
            <div class="permit-detail-label">Registration</div>
            <div class="permit-detail-value">${permit.metadata.registration_number}</div>
        </div>
        ` : ''}
        ${permit.metadata?.status ? `
        <div class="permit-detail-item">
            <div class="permit-detail-label">Status</div>
            <div class="permit-detail-value">${permit.metadata.status}</div>
        </div>
        ` : ''}
        <div class="permit-detail-item" style="grid-column: 1 / -1;">
            <div class="permit-detail-label">View Source</div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
                ${permit.source === 'MahaRERA' || permit.metadata?.project_name ? `
                <a href="https://maharera.maharashtra.gov.in/projects-search-result" target="_blank" 
                   style="display: inline-flex; align-items: center; gap: 0.5rem; background: var(--primary); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.875rem;">
                    <i class="fas fa-building"></i> MahaRERA Portal
                </a>
                ` : ''}
                ${permit.source === 'BMC_NovaAct' || permit.source === 'BMC' || permit.event_type === 'construction_approval' ? `
                <a href="https://portal.mcgm.gov.in/irj/portal/anonymous?guest_user=english" target="_blank" 
                   style="display: inline-flex; align-items: center; gap: 0.5rem; background: var(--success); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.875rem;">
                    <i class="fas fa-landmark"></i> BMC Portal
                </a>
                ` : ''}
                ${permit.metadata?.registration_number ? `
                <a href="https://maharera.maharashtra.gov.in/projects-search-result?searchText=${encodeURIComponent(permit.metadata.registration_number)}" target="_blank" 
                   style="display: inline-flex; align-items: center; gap: 0.5rem; background: var(--warning); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-size: 0.875rem;">
                    <i class="fas fa-search"></i> Search Registration
                </a>
                ` : ''}
            </div>
        </div>
    `;

    panel.classList.add('active');
}

// Load permits list
function loadPermitsList(permits) {
    const permitsList = document.getElementById('permitsList');
    if (!permitsList) return;

    permitsList.innerHTML = permits.map((permit, index) => `
        <div class="permit-card" onclick="selectBuildingByIndex(${index})">
            <div class="permit-card-header">
                <div class="permit-card-title">
                    ${permit.metadata?.project_name || permit.description || 'Permit'}
                </div>
                <div class="permit-card-badge">
                    ${formatEventType(permit.event_type)}
                </div>
            </div>
            <div class="permit-card-info">
                <div>
                    <i class="fas fa-map-marker-alt"></i>
                    ${permit.location}
                </div>
                <div>
                    <i class="fas fa-calendar"></i>
                    ${formatDate(permit.timestamp)}
                </div>
                ${permit.metadata?.promoter ? `
                <div>
                    <i class="fas fa-user"></i>
                    ${permit.metadata.promoter}
                </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Select building by index
function selectBuildingByIndex(index) {
    if (buildings[index]) {
        selectBuilding(buildings[index]);
        // Scroll to 3D view
        document.querySelector('.permits-3d-container').scrollIntoView({ behavior: 'smooth' });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Reset view button
    const resetViewBtn = document.getElementById('resetViewBtn');
    if (resetViewBtn) {
        resetViewBtn.addEventListener('click', () => {
            camera.position.set(15, 15, 15);
            camera.lookAt(0, 0, 0);
        });
    }

    // Toggle rotation button
    const toggleRotationBtn = document.getElementById('toggleRotationBtn');
    if (toggleRotationBtn) {
        toggleRotationBtn.addEventListener('click', () => {
            isRotating = !isRotating;
            toggleRotationBtn.innerHTML = isRotating 
                ? '<i class="fas fa-pause"></i> Pause'
                : '<i class="fas fa-play"></i> Play';
        });
    }

    // Close permit details
    const closePermitDetails = document.getElementById('closePermitDetails');
    const permitDetailsPanel = document.getElementById('permitDetailsPanel');
    if (closePermitDetails && permitDetailsPanel) {
        closePermitDetails.addEventListener('click', () => {
            permitDetailsPanel.classList.remove('active');
            if (selectedBuilding) {
                selectedBuilding.scale.set(1, 1, 1);
                selectedBuilding.material.emissiveIntensity = 0.2;
                selectedBuilding = null;
            }
        });
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
function getColorForPermitType(type) {
    const colors = {
        'real_estate_project': 0x6366f1,
        'construction_approval': 0x10b981,
        'commercial': 0xf59e0b
    };
    return colors[type] || 0x8b5cf6;
}

function formatEventType(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
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

function getSourceIcon(source) {
    const icons = {
        'news': 'newspaper',
        'social': 'comments',
        'permit': 'file-alt',
        'image_analysis': 'camera'
    };
    return icons[source] || 'info-circle';
}
