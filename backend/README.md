# CityPulse Backend API

Simple Flask API to serve agent data to the frontend.

## Features

- RESTful API endpoints for all agent data
- CORS enabled for frontend integration
- Health check endpoint
- Voice Q&A endpoint
- Agent execution trigger

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Running Locally

```bash
python api.py
```

API will be available at `http://localhost:5000`

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Data Endpoints
- `GET /api/alerts` - All alerts (smart + safety)
- `GET /api/alerts/<type>` - Filtered alerts (safety, development, community, business)
- `GET /api/community` - Community pulse data
- `GET /api/safety` - Safety alerts
- `GET /api/investment` - Investment insights
- `GET /api/permits` - Permits data
- `GET /api/news` - News data
- `GET /api/social` - Social media data

### Interactive Endpoints
- `POST /api/voice/ask` - Voice Q&A
  ```json
  {
    "question": "What are the trending topics?"
  }
  ```

- `POST /api/run-agents` - Trigger agent execution

## Deployment

### Option 1: Render.com (Recommended)
1. Create account on render.com
2. New Web Service
3. Connect GitHub repo
4. Build command: `pip install -r backend/requirements.txt`
5. Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.api:app`

### Option 2: Railway.app
1. Create account on railway.app
2. New Project from GitHub
3. Add environment variables if needed
4. Deploy automatically

### Option 3: Heroku
```bash
# In backend folder
echo "web: gunicorn api:app" > Procfile
git push heroku main
```

## Environment Variables

None required for basic operation. Optional:
- `PORT` - Server port (default: 5000)
- `DEBUG` - Debug mode (default: True)

## Testing

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test alerts endpoint
curl http://localhost:5000/api/alerts

# Test voice Q&A
curl -X POST http://localhost:5000/api/voice/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the trending topics?"}'
```

## Integration with Frontend

Update `frontend/demo/app.js` to use this API:

```javascript
const API_URL = 'http://localhost:5000';  // or your deployed URL

async function loadAlerts() {
    const response = await fetch(`${API_URL}/api/alerts`);
    const data = await response.json();
    // render alerts
}
```

## Production Considerations

1. **Security**: Add API key authentication
2. **Rate Limiting**: Implement rate limiting
3. **Caching**: Cache agent data responses
4. **Logging**: Add proper logging
5. **Error Handling**: Improve error responses
