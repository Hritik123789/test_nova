# CityPulse Deployment Guide

Complete guide to deploy your full-stack CityPulse application.

## Architecture

```
Frontend (Vercel/Netlify)
    ↓
Backend API (Render/Railway)
    ↓
Python Agents (Generate Data)
    ↓
JSON Files (agents/data/)
```

## Quick Deployment (15 minutes)

### Step 1: Deploy Backend API (5 min)

**Option A: Render.com (Recommended - Free tier)**

1. Go to https://render.com
2. Sign up / Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repo: `https://github.com/Hritik123789/Amazon_nova.git`
5. Configure:
   - **Name**: `citypulse-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`
6. Click "Create Web Service"
7. Wait 2-3 minutes for deployment
8. Copy your API URL (e.g., `https://citypulse-api.onrender.com`)

**Option B: Railway.app (Alternative)**

1. Go to https://railway.app
2. Sign up / Login
3. "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Add service → Select `backend` folder
6. Railway auto-detects Python and deploys
7. Copy your API URL

### Step 2: Deploy Frontend (5 min)

**Option A: Vercel (Recommended - Free tier)**

1. Go to https://vercel.com
2. Sign up / Login
3. "Add New" → "Project"
4. Import your GitHub repo
5. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend/demo`
   - **Build Command**: (leave empty)
   - **Output Directory**: `.`
6. Add Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: Your backend URL from Step 1
7. Click "Deploy"
8. Wait 1-2 minutes
9. Your site is live!

**Option B: Netlify (Alternative)**

1. Go to https://netlify.com
2. "Add new site" → "Import an existing project"
3. Connect GitHub
4. Configure:
   - **Base directory**: `frontend/demo`
   - **Build command**: (leave empty)
   - **Publish directory**: `.`
5. Deploy

### Step 3: Update Frontend with API URL (2 min)

Edit `frontend/demo/app.js`:

```javascript
// Line 1-2, replace with:
const API_URL = 'https://your-api-url.onrender.com';  // Your backend URL from Step 1
```

Commit and push:
```bash
git add frontend/demo/app.js
git commit -m "feat: Connect frontend to deployed API"
git push origin main
```

Vercel/Netlify will auto-redeploy.

### Step 4: Test Deployment (3 min)

1. Visit your frontend URL
2. Check if alerts load
3. Try voice Q&A
4. Check browser console for errors

## Alternative: Simple Static Deployment

If you just want to demo without backend:

### GitHub Pages (Easiest)

1. Go to your repo settings
2. Pages → Source → `main` branch → `/frontend/demo` folder
3. Save
4. Visit `https://hritik123789.github.io/Amazon_nova/`

**Note**: This uses sample data only, no live API.

## Running Locally for Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python api.py
# API at http://localhost:5000
```

### Frontend
```bash
cd frontend/demo
python -m http.server 8000
# Frontend at http://localhost:8000
```

### Generate Fresh Data
```bash
cd agents
python run_all_agents.py --parallel
# Updates all JSON files in agents/data/
```

## Environment Variables

### Backend (Optional)
- `PORT` - Server port (auto-set by hosting platform)
- `DEBUG` - Debug mode (set to `False` in production)

### Frontend
- `VITE_API_URL` - Backend API URL

## Troubleshooting

### Backend Issues

**"Module not found"**
- Check `requirements.txt` includes all dependencies
- Rebuild on hosting platform

**"CORS error"**
- Backend has `flask-cors` enabled
- Check API URL is correct in frontend

**"502 Bad Gateway"**
- Backend is starting (wait 1-2 min)
- Check logs on hosting platform

### Frontend Issues

**"Failed to fetch"**
- Check API URL in `app.js`
- Check backend is running
- Check CORS is enabled

**"Blank page"**
- Check browser console for errors
- Verify all files deployed correctly

## Cost Estimate

### Free Tier (Recommended for Hackathon)
- **Render.com**: Free (750 hours/month)
- **Vercel**: Free (unlimited)
- **Total**: $0/month

### Paid Tier (Production)
- **Render.com**: $7/month (always-on)
- **Vercel**: Free
- **Total**: $7/month

## Post-Deployment Checklist

- [ ] Backend API is accessible
- [ ] Frontend loads without errors
- [ ] Alerts display correctly
- [ ] Voice Q&A works
- [ ] All sections load data
- [ ] Mobile responsive
- [ ] Share demo URL with judges!

## Demo URLs

After deployment, you'll have:
- **Frontend**: `https://citypulse-demo.vercel.app`
- **Backend API**: `https://citypulse-api.onrender.com`
- **GitHub**: `https://github.com/Hritik123789/Amazon_nova`

## For Hackathon Judges

Provide these links:
1. **Live Demo**: [Your Vercel URL]
2. **API Docs**: [Your Render URL]
3. **GitHub**: https://github.com/Hritik123789/Amazon_nova
4. **Video Demo**: [If you make one]

## Next Steps

1. Deploy backend to Render (5 min)
2. Deploy frontend to Vercel (5 min)
3. Update API URL in frontend (2 min)
4. Test everything (3 min)
5. Share with judges! 🎉

Total time: ~15 minutes

## Need Help?

Common issues and solutions are in the Troubleshooting section above.

Good luck with your hackathon! 🚀
