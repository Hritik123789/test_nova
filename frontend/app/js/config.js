// API Configuration
const API_CONFIG = {
    // Automatically detect environment
    // In production, set this to your deployed backend URL
    // In development, it will use localhost
    BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:5000'
        : 'https://your-backend-url.herokuapp.com',  // ⚠️ CHANGE THIS to your deployed backend URL
    
    // Endpoints
    ENDPOINTS: {
        ALERTS: '/api/alerts',
        ALERTS_BY_TYPE: '/api/alerts',
        COMMUNITY: '/api/community',
        SAFETY: '/api/safety',
        INVESTMENT: '/api/investment',
        PERMITS: '/api/permits',
        NEWS: '/api/news',
        SOCIAL: '/api/social',
        BRIEFING: '/api/briefing',
        VOICE_ASK: '/api/voice/ask',
        RUN_AGENTS: '/api/run-agents',
        HEALTH: '/health'
    },
    
    // Request timeout (ms) - increased for slower connections
    TIMEOUT: 60000,  // 60 seconds
    
    // Retry configuration
    RETRY_ATTEMPTS: 2,
    RETRY_DELAY: 1000
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}
