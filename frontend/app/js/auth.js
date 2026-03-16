// Google Authentication for CityPulse

// Initialize Google Sign-In
function initGoogleAuth() {
    // Check if user is already logged in
    const user = getLoggedInUser();
    if (user) {
        updateUIForLoggedInUser(user);
    }
}

// Handle Google Sign-In response
function handleCredentialResponse(response) {
    // Decode JWT token to get user info
    const userInfo = parseJwt(response.credential);
    
    // Store user info in localStorage
    const user = {
        id: userInfo.sub,
        name: userInfo.name,
        email: userInfo.email,
        picture: userInfo.picture,
        loginTime: new Date().toISOString()
    };
    
    localStorage.setItem('citypulse_user', JSON.stringify(user));
    
    // Update UI
    updateUIForLoggedInUser(user);
    
    // Show success message
    showNotification('Successfully logged in!', 'success');
}

// Parse JWT token
function parseJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    
    return JSON.parse(jsonPayload);
}

// Get logged in user from localStorage
function getLoggedInUser() {
    const userStr = localStorage.getItem('citypulse_user');
    if (!userStr) return null;
    
    try {
        return JSON.parse(userStr);
    } catch (e) {
        return null;
    }
}

// Update UI for logged in user
function updateUIForLoggedInUser(user) {
    const loginBtn = document.getElementById('loginBtn');
    const userProfile = document.getElementById('userProfile');
    
    if (loginBtn) {
        loginBtn.style.display = 'none';
    }
    
    if (userProfile) {
        userProfile.style.display = 'flex';
        userProfile.innerHTML = `
            <img src="${user.picture}" alt="${user.name}" 
                 style="width: 36px; height: 36px; border-radius: 50%; border: 2px solid var(--primary);">
            <div style="margin-left: 0.75rem;">
                <div style="font-weight: 600; font-size: 0.875rem;">${user.name}</div>
                <div style="font-size: 0.75rem; color: var(--gray);">${user.email}</div>
            </div>
            <button onclick="logout()" style="margin-left: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; cursor: pointer; font-size: 0.875rem;">
                Logout
            </button>
        `;
    }
}

// Logout function
function logout() {
    localStorage.removeItem('citypulse_user');
    
    // Reset UI
    const loginBtn = document.getElementById('loginBtn');
    const userProfile = document.getElementById('userProfile');
    
    if (loginBtn) {
        loginBtn.style.display = 'block';
    }
    
    if (userProfile) {
        userProfile.style.display = 'none';
        userProfile.innerHTML = '';
    }
    
    // Show message
    showNotification('Successfully logged out!', 'info');
    
    // Reload page
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', initGoogleAuth);
