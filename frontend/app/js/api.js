// API Client for CityPulse Backend

class APIClient {
    constructor(config) {
        this.baseURL = config.BASE_URL;
        this.endpoints = config.ENDPOINTS;
        this.timeout = config.TIMEOUT;
        this.retryAttempts = config.RETRY_ATTEMPTS;
        this.retryDelay = config.RETRY_DELAY;
    }

    async request(endpoint, options = {}, retryCount = 0) {
        const url = `${this.baseURL}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            
            // Retry logic for network errors
            if (retryCount < this.retryAttempts && (error.name === 'AbortError' || error.message.includes('fetch'))) {
                console.log(`Retrying request (${retryCount + 1}/${this.retryAttempts})...`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                return this.request(endpoint, options, retryCount + 1);
            }
            
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Get all alerts
    async getAlerts() {
        return this.request(this.endpoints.ALERTS);
    }

    // Get alerts by type
    async getAlertsByType(type) {
        return this.request(`${this.endpoints.ALERTS_BY_TYPE}/${type}`);
    }

    // Get community data
    async getCommunity() {
        return this.request(this.endpoints.COMMUNITY);
    }

    // Get safety alerts
    async getSafety() {
        return this.request(this.endpoints.SAFETY);
    }

    // Get investment insights
    async getInvestment() {
        return this.request(this.endpoints.INVESTMENT);
    }

    // Get permits
    async getPermits() {
        return this.request(this.endpoints.PERMITS);
    }

    // Get news
    async getNews() {
        return this.request(this.endpoints.NEWS);
    }

    // Get social data
    async getSocial() {
        return this.request(this.endpoints.SOCIAL);
    }

    // Get briefing
    async getBriefing() {
        return this.request(this.endpoints.BRIEFING);
    }

    // Voice Q&A
    async askVoice(question) {
        return this.request(this.endpoints.VOICE_ASK, {
            method: 'POST',
            body: JSON.stringify({ question })
        });
    }

    // Run agents
    async runAgents() {
        return this.request(this.endpoints.RUN_AGENTS, {
            method: 'POST'
        });
    }

    // Health check
    async healthCheck() {
        return this.request(this.endpoints.HEALTH);
    }
}

// Create global API client instance
const api = new APIClient(API_CONFIG);
