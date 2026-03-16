# 🌆 CityPulse - Hyperlocal Community Intelligence Platform

> **Amazon Nova Hackathon 2026** | Agentic AI + Multimodal Understanding + UI Automation

[![Built with Amazon Nova](https://img.shields.io/badge/Built%20with-Amazon%20Nova-FF9900?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/bedrock/nova/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**CityPulse** is an AI-powered hyperlocal intelligence platform that monitors your neighborhood's digital footprint and provides actionable insights that actually affect your daily life. Built entirely with Amazon Nova AI models, it combines agentic AI, multimodal understanding, and UI automation to deliver proactive community intelligence.

[🎥 Demo Video](#) | [📖 Documentation](docs/) | [🚀 Live Demo](#)

---

## 🎯 The Unique Angle

Unlike traditional chatbots or document processors, CityPulse is a **proactive intelligence gathering system** that:

- 🤖 **Monitors** your neighborhood 24/7 using autonomous AI agents
- 🧠 **Analyzes** multi-modal data (text, images, permits, social media)
- 📊 **Synthesizes** insights from disparate sources
- 🔔 **Alerts** you to relevant changes in real-time
- 🎙️ **Briefs** you daily via voice with personalized updates

### Why This Is Different

✅ **Truly Novel Use Case** - Not another chatbot or RAG system  
✅ **Multi-Agent Orchestration** - 5 specialized AI agents working in parallel  
✅ **All Nova Capabilities** - Leverages every Amazon Nova model  
✅ **Real-World Impact** - Actionable intelligence for daily life  
✅ **Proactive, Not Reactive** - Agents work autonomously, not on-demand

---

## 🏗️ Architecture

### Multi-Agent System

```
CityPulse Multi-Agent System
├── 🏢 Permit Monitor Agent (Nova Act)
│   └── Scrapes city building permits, liquor licenses, zoning changes
│
├── 👥 Social Listening Agent (Nova Act)
│   └── Monitors community Facebook groups, local subreddits, NextDoor
│
├── 📰 News Synthesis Agent (Nova 2 Lite)
│   └── Aggregates local news, identifies trends, extracts insights
│
├── 📸 Visual Intelligence Agent (Nova 2 Omni)
│   └── Analyzes photos: construction sites, events, safety issues
│
└── 🎙️ Voice Briefing Agent (Nova 2 Lite + Polly)
    └── Daily personalized neighborhood briefing with audio
```

### Technology Stack

**AI & ML:**
- 🧠 **Amazon Nova 2 Lite** - Real-time reasoning and text generation
- 🎨 **Amazon Nova 2 Omni** - Multimodal understanding (text + images)
- 🤖 **Amazon Nova Act** - UI automation and web scraping
- 🎙️ **Amazon Polly Neural TTS** - Natural voice synthesis
- 🔍 **Amazon Titan Embeddings** - Vector search for RAG
- 📊 **FAISS** - Fast similarity search

**Backend:**
- 🐍 Python 3.11
- 🌐 Flask 3.0 (REST API)
- 🔄 Gunicorn (Production server)
- 📦 Boto3 (AWS SDK)

**Frontend:**
- 💻 Vanilla JavaScript (No framework overhead)
- 🎨 Modern CSS with gradients and animations
- 📱 Fully responsive design
- 🗺️ Leaflet.js (Interactive maps)
- 🎮 Three.js (3D permit visualization)

**Infrastructure:**
- ☁️ AWS Bedrock (Nova models)
- 🚀 Heroku (Backend deployment)
- ⚡ Vercel (Frontend deployment)

---

## ✨ Features

### 🏠 For Residents

#### 📊 User Dashboard
- Track your engagement across all features
- View recent activity history
- Personalized stats and insights
- **Tech:** LocalStorage API, Real-time updates

#### 🏗️ 3D Permits Visualization
- Interactive 3D view of construction permits
- Click buildings to see permit details
- Filter by type, status, and location
- **Tech:** Three.js, WebGL, Nova Act for data collection

#### 🔔 Smart Alerts
- Real-time safety notifications
- New business openings nearby
- Road closures and construction updates
- Community events and meetings
- **Tech:** Nova 2 Lite for alert generation, Leaflet maps

#### 👥 Community Pulse
- Trending topics in your neighborhood
- Sentiment analysis of community discussions
- Key concerns and celebrations
- Interactive topic exploration
- **Tech:** Nova 2 Lite for NLP, Social media aggregation

#### 💰 Investment Insights
- Trending neighborhoods for investment
- Development activity heatmaps
- Property value indicators
- Commercial vs residential trends
- **Tech:** Nova 2 Lite for analysis, Data visualization

#### ☀️ Morning Briefing
- Personalized daily audio briefing
- News, permits, and community updates
- Listen on-the-go
- **Tech:** Nova 2 Lite + Amazon Polly Neural TTS

#### 🎙️ Voice AI Assistant
- Ask questions in natural language
- Voice input with browser speech recognition
- Audio responses with Polly TTS
- RAG-powered answers from local data
- **Tech:** Nova 2 Lite, Polly, FAISS, Titan Embeddings

---

## 🎨 Where Each Technology Is Used

### Amazon Nova 2 Lite
**Location:** Backend agents + Voice AI  
**Purpose:** Text generation, reasoning, analysis
- `agents/features/community_pulse_nova.py` - Community sentiment analysis
- `agents/features/safety_intelligence_nova.py` - Safety alert generation
- `agents/features/investment_insights_nova.py` - Investment analysis
- `agents/voice_qa_realtime.py` - Voice Q&A responses
- `agents/voice_briefing_nova.py` - Morning briefing generation

### Amazon Nova 2 Omni (Multimodal)
**Location:** Image analysis agents  
**Purpose:** Analyze photos from permits, social media, news
- `agents/image_analysis_nova.py` - Construction site analysis
- `agents/features/community_pulse_nova.py` - Social media image analysis
- Visual intelligence for safety concerns

### Amazon Nova Act
**Location:** Web scraping agents  
**Purpose:** Automated data collection from websites
- `agents/permit-monitor/permit_monitor_real.py` - BMC permit scraping
- `agents/social-listening/social_listener_nova.py` - Social media monitoring
- `agents/nova_act_permit_checker.py` - Automated permit checking

### Amazon Polly Neural TTS
**Location:** Voice features  
**Purpose:** Natural voice synthesis
- `backend/api_v2.py` - `/api/voice/ask` endpoint
- `agents/voice_briefing_nova.py` - Morning briefing audio
- `agents/speech_to_speech_simple.py` - Voice responses

### Amazon Titan Embeddings
**Location:** RAG system  
**Purpose:** Vector embeddings for semantic search
- `agents/rag_qa_system.py` - Document embeddings
- `agents/rag_api.py` - Fast RAG API

### FAISS (Facebook AI Similarity Search)
**Location:** RAG system  
**Purpose:** Fast vector similarity search
- `agents/rag_qa_system.py` - Semantic search over local data

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- AWS credentials configured
- Node.js (optional, for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hritik123789/amazon_nova_2.git
   cd amazon_nova_2
   ```

2. **Set up backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Run agents to generate data**
   ```bash
   cd agents
   python run_all_agents.py --parallel
   ```

4. **Start backend server**
   ```bash
   cd backend
   python api_v2.py
   ```

5. **Open frontend**
   ```bash
   cd frontend/app
   # Open index.html in browser
   # Or use: python -m http.server 8000
   ```

### Configuration

**Backend Environment Variables** (`.env`):
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
CORS_ORIGINS=*
```

**Frontend Configuration** (`frontend/app/js/config.js`):
```javascript
BASE_URL: 'http://localhost:5000'  // Change for production
```

---

## 📁 Project Structure

```
citypulse/
├── agents/                      # AI Agents
│   ├── features/               # Feature-specific agents
│   │   ├── community_pulse_nova.py
│   │   ├── safety_intelligence_nova.py
│   │   └── investment_insights_nova.py
│   ├── permit-monitor/         # Permit scraping
│   ├── social-listening/       # Social media monitoring
│   ├── rag_qa_system.py       # RAG Q&A system
│   ├── voice_qa_realtime.py   # Voice AI
│   └── run_all_agents.py      # Orchestrator
│
├── backend/                    # Flask API
│   ├── api_v2.py              # Main API
│   ├── config.py              # Configuration
│   └── requirements.txt       # Dependencies
│
├── frontend/app/              # Web Application
│   ├── index.html            # Home page
│   ├── dashboard.html        # User dashboard
│   ├── permits.html          # 3D permits view
│   ├── alerts.html           # Smart alerts
│   ├── community.html        # Community pulse
│   ├── briefing.html         # Morning briefing
│   ├── voice.html            # Voice AI
│   ├── css/main.css          # Styles
│   └── js/                   # JavaScript
│       ├── config.js         # API config
│       ├── api.js            # API client
│       ├── permits.js        # 3D visualization
│       ├── alerts.js         # Alerts + maps
│       ├── community.js      # Community features
│       ├── voice.js          # Voice AI
│       └── dashboard.js      # Dashboard
│
└── docs/                      # Documentation
```

---

## 🎯 Key Innovations

### 1. Multi-Agent Orchestration
- **5 specialized agents** working in parallel
- **Autonomous operation** - agents run on schedule
- **Data synthesis** - combining insights from multiple sources
- **Conflict resolution** - handling contradictory information

### 2. Multimodal Intelligence
- **Text analysis** - News, social media, permits
- **Image analysis** - Construction sites, events, safety
- **Voice interaction** - Natural language Q&A
- **Spatial data** - Maps, locations, proximity

### 3. Proactive Intelligence
- **Not reactive** - Agents work 24/7, not on-demand
- **Predictive** - Identifies trends before they're obvious
- **Personalized** - Tailored to your neighborhood
- **Actionable** - Insights you can act on

### 4. Real-World Impact
- **Safety** - Early warning of hazards
- **Investment** - Identify opportunities
- **Community** - Stay connected
- **Convenience** - Know what's happening

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/alerts` | GET | All alerts |
| `/api/community` | GET | Community pulse data |
| `/api/safety` | GET | Safety alerts |
| `/api/investment` | GET | Investment insights |
| `/api/permits` | GET | Building permits |
| `/api/briefing` | GET | Morning briefing |
| `/api/voice/ask` | POST | Voice Q&A |
| `/api/audio/<file>` | GET | Audio files |

---

## 🎬 Demo

### Screenshots

**Home Page**
![Home](docs/screenshots/home.png)

**3D Permits Visualization**
![Permits](docs/screenshots/permits.png)

**Smart Alerts with Map**
![Alerts](docs/screenshots/alerts.png)

**Community Pulse**
![Community](docs/screenshots/community.png)

**Voice AI Assistant**
![Voice](docs/screenshots/voice.png)

---

## 🏆 Amazon Nova Hackathon Submission

### Category
**Agentic AI + Multimodal Understanding + UI Automation**

### What Makes This Unique

1. **Comprehensive Nova Usage**
   - ✅ Nova 2 Lite for reasoning
   - ✅ Nova 2 Omni for multimodal
   - ✅ Nova Act for automation
   - ✅ Polly for voice
   - ✅ Titan for embeddings

2. **Novel Use Case**
   - Not a chatbot
   - Not document processing
   - Truly proactive intelligence

3. **Real-World Application**
   - Solves actual problems
   - Provides daily value
   - Scalable to any city

4. **Technical Excellence**
   - Multi-agent orchestration
   - Production-ready code
   - Comprehensive documentation
   - Deployed and accessible

---

## 🛠️ Development

### Running Agents

```bash
# Run all agents in parallel
python agents/run_all_agents.py --parallel

# Run specific agent
python agents/features/community_pulse_nova.py

# Build RAG cache
python agents/rag_api.py "test question"
```

### Testing

```bash
# Test backend endpoints
cd backend
python test_api.py

# Test specific endpoint
curl http://localhost:5000/api/alerts
```

### Deployment

See [DEPLOYMENT_GUIDE_FINAL.md](DEPLOYMENT_GUIDE_FINAL.md) for detailed instructions.

**Quick Deploy:**
```bash
# Backend (Heroku)
heroku create citypulse-backend
git subtree push --prefix backend heroku main

# Frontend (Vercel)
vercel --prod
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 👥 Team

Built with ❤️ for the Amazon Nova Hackathon 2026

---

## 🙏 Acknowledgments

- Amazon Web Services for Amazon Nova AI models
- Amazon Bedrock team for the amazing platform
- Open source community for tools and libraries

---

## 📧 Contact

For questions or feedback:
- GitHub Issues: [Create an issue](https://github.com/Hritik123789/amazon_nova_2/issues)
- Email: [your-email@example.com]

---

**⭐ If you find this project interesting, please star the repository!**

