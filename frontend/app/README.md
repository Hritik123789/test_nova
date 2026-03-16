# CityPulse Frontend Application

Modern, responsive web application for CityPulse - AI-powered civic intelligence platform.

## Features

### 1. Homepage (index.html)
- 3D particle animation hero section
- Real-time statistics (alerts, permits, topics)
- Quick action cards
- Recent alerts preview
- Responsive navigation

### 2. Permits Page (permits.html)
- Interactive 3D visualization of construction permits
- Click buildings to view details
- Rotation controls (play/pause, reset view)
- Detailed permit information panel
- List view of all permits

### 3. Alerts Page (alerts.html)
- Real-time safety and community alerts
- Filter by type (safety, community, development, business)
- Priority-based color coding
- Statistics dashboard
- Responsive grid layout

### 4. Community Page (community.html)
- Sentiment distribution visualization
- Topic clusters network (SVG)
- Trending topics cards
- Community concerns with severity levels
- Affected areas tags

### 5. Voice AI Page (voice.html)
- Natural language Q&A interface
- Animated particle background
- Suggestion chips for common questions
- Audio playback support (Polly TTS)
- Real-time data integration

## Technology Stack

- **Frontend**: Pure HTML5, CSS3, JavaScript (ES6+)
- **3D Graphics**: Three.js (r128)
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Inter (Google Fonts)
- **Backend API**: Flask REST API
- **AI Models**: Amazon Nova 2 Lite, Titan Embeddings, Polly TTS

## File Structure

```
frontend/app/
├── index.html          # Homepage
├── permits.html        # 3D Permits visualization
├── alerts.html         # Alerts dashboard
├── community.html      # Community pulse
├── voice.html          # Voice AI interface
├── css/
│   └── main.css        # Main stylesheet
└── js/
    ├── config.js       # API configuration
    ├── api.js          # API client
    ├── main.js         # Homepage logic
    ├── permits.js      # 3D permits visualization
    ├── alerts.js       # Alerts page logic
    ├── community.js    # Community page logic
    └── voice.js        # Voice AI logic
```

## Setup Instructions

### 1. Configure Backend URL

Edit `js/config.js` and update the `BASE_URL`:

```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000',  // Change to your deployed backend URL
    // ...
};
```

### 2. Start Backend Server

Make sure your Flask backend is running:

```bash
cd backend
python api_v2.py
```

### 3. Serve Frontend

You can use any static file server. Options:

**Python:**
```bash
cd frontend/app
python -m http.server 8000
```

**Node.js (http-server):**
```bash
cd frontend/app
npx http-server -p 8000
```

**VS Code Live Server:**
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

### 4. Open in Browser

Navigate to `http://localhost:8000`

## API Integration

The frontend connects to the Flask backend API for:

- `/api/alerts` - Get all alerts
- `/api/alerts/<type>` - Get filtered alerts
- `/api/community` - Get community pulse data
- `/api/permits` - Get permits data
- `/api/voice/ask` - Voice Q&A
- `/health` - Health check

## Features by Page

### Homepage
- Animated 3D particle background
- Live statistics counters
- Quick navigation cards
- Recent alerts preview
- Notification panel

### Permits
- 3D buildings representing permits
- Interactive selection (click to view details)
- Auto-rotation with pause/play controls
- Color-coded by permit type
- Detailed information panel
- List view with all permits

### Alerts
- Priority-based filtering
- Color-coded alerts (high/medium/low)
- Statistics dashboard
- Real-time updates
- Source attribution

### Community
- Sentiment distribution (positive/neutral/negative)
- Topic clusters network visualization
- Trending topics with scores
- Community concerns with severity
- Affected areas mapping

### Voice AI
- Natural language input
- Suggestion chips for common queries
- Animated particle background
- Audio playback support
- Real-time AI responses

## Responsive Design

All pages are fully responsive:
- Desktop: Full layout with all features
- Tablet: Adjusted grid layouts
- Mobile: Single-column layout, simplified navigation

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Minimal dependencies (Three.js only)
- Optimized animations (60 FPS)
- Lazy loading for images
- Efficient API calls
- Local fallbacks for offline mode

## Customization

### Colors

Edit CSS variables in `css/main.css`:

```css
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    /* ... */
}
```

### API Endpoints

Edit `js/config.js` to change API endpoints or add new ones.

### 3D Visualization

Modify `js/permits.js` to customize:
- Building colors
- Animation speed
- Camera position
- Lighting

## Deployment

### Static Hosting (Recommended)

Deploy to:
- **Netlify**: Drag & drop `frontend/app` folder
- **Vercel**: Connect GitHub repo
- **GitHub Pages**: Push to `gh-pages` branch
- **AWS S3**: Upload to S3 bucket with static hosting

### Configuration for Production

1. Update `js/config.js` with production backend URL
2. Enable CORS on backend for your domain
3. Use HTTPS for both frontend and backend
4. Set up CDN for static assets (optional)

## Troubleshooting

### API Connection Issues

- Check backend is running
- Verify `BASE_URL` in `config.js`
- Check browser console for CORS errors
- Ensure backend CORS is configured

### 3D Visualization Not Working

- Check Three.js is loaded (CDN)
- Verify WebGL support in browser
- Check console for errors

### Animations Laggy

- Reduce particle count in animation code
- Disable animations on mobile
- Check GPU acceleration is enabled

## Future Enhancements

- [ ] Speech-to-text input (Amazon Transcribe)
- [ ] Real-time notifications (WebSockets)
- [ ] User authentication
- [ ] Saved preferences
- [ ] Dark/light theme toggle
- [ ] Multi-language support
- [ ] Progressive Web App (PWA)
- [ ] Offline mode with service workers

## License

Built for Amazon Nova Hackathon 2026

## Support

For issues or questions, check the main project README or contact the development team.
