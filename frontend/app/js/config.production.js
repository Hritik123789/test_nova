// Production API Configuration
// Copy this to config.js and update with your backend URL

const API_CONFIG = {
    // PRODUCTION: Set this to your deployed backend URL
    BASE_URL: 'https://your-backend-url.herokuapp.com',  // ⚠️ CHANGE THIS!
    
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
    
    // Request timeout (ms)
    TIMEOUT: 60000,  // 60 seconds
    
    // Retry configuration
    RETRY_ATTEMPTS: 2,
    RETRY_DELAY: 1000
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}
