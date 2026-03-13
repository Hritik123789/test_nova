# 🏙️ CityPulse - Hyperlocal Community Intelligence Platform

**Amazon Nova Hackathon 2026**

> AI-powered civic transparency for Mumbai's 20 million residents

---

## 🎯 What is CityPulse?

CityPulse monitors your neighborhood's digital footprint—local news, permit filings, community posts, and construction activity—to provide actionable hyperlocal intelligence that affects your daily life.

**Category**: Agentic AI + Multimodal Understanding + UI Automation

---

## ✨ Key Features

### 🏗️ Permit Monitor Agent
- Tracks building permits, liquor licenses, zoning changes
- AI-powered location and action extraction
- Priority-based investigation queue
- RERA compliance checking for real estate

### 📰 News Synthesis Agent
- Aggregates local news from Mumbai sources
- AI categorization (Civic, Traffic, Real Estate)
- Entity recognition (BMC, MHADA, BEST, etc.)
- Relevance scoring for residents

### 🎙️ Voice Briefing Agent
- Daily personalized neighborhood briefings
- "What's happening in my neighborhood today?"
- Accessible for all literacy levels
- Text-to-speech ready scripts

### 🖼️ Visual Intelligence Agent
- Analyzes construction site photos
- Verifies permit documents
- Detects safety concerns
- Identifies project types

### 🤖 Web Scraping Agent
- Automates BMC portal monitoring
- RERA database tracking
- Real-time permit updates
- Government website automation

---

## 🚀 All 4 Amazon Nova Models

### Nova 2 Lite
- News analysis and categorization
- Permit processing and location extraction
- Entity recognition and relevance scoring
- **Cost**: $0.0065 per 10 articles

### Nova 2 Sonic
- Voice briefing generation
- Conversational script creation
- Accessibility features
- **Cost**: $0.0002 per briefing

### Nova 2 Omni (Multimodal)
- Construction site image analysis
- Permit document extraction
- Safety concern detection
- **Cost**: $0.0016 per image

### Nova Act (Agentic)
- Automated web scraping
- BMC portal monitoring
- RERA database tracking
- **Cost**: $4.75 per hour

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CityPulse Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ News Agent   │  │ Permit Agent │  │ Social Agent │      │
│  │ Nova 2 Lite  │  │ Nova Act     │  │ Nova Act     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  Bridge Agent  │                        │
│                    │  Nova 2 Lite   │                        │
│                    └───────┬────────┘                        │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐              │
│         │                  │                  │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │ Voice Agent  │  │ Image Agent  │  │ Alert System │      │
│  │ Nova 2 Sonic │  │ Nova 2 Omni  │  │ Nova 2 Lite  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Tech Stack

### Backend
- **Python 3.9+** - Agent orchestration
- **Amazon Bedrock** - Nova model access
- **boto3** - AWS SDK
- **Flask** - REST API
- **feedparser** - RSS feed collection

### Frontend
- **HTML5/CSS3/JavaScript** - User interface
- **Tailwind CSS** - Styling
- **Responsive Design** - Mobile-first

### AI Models
- **Amazon Nova 2 Lite** - Text analysis
- **Amazon Nova 2 Sonic** - Voice generation
- **Amazon Nova 2 Omni** - Image analysis
- **Amazon Nova Act** - Web automation

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9+
python --version

# AWS CLI configured
aws configure

# Install dependencies
pip install boto3 feedparser flask flask-cors
```

### Run the Demo
```bash
# 1. Collect news
python agents/news-synthesis/news_collector.py

# 2. Analyze with Nova 2 Lite
python agents/news-synthesis/local_news_agent_nova.py

# 3. Process permits with Nova 2 Lite
python agents/bridge_to_permits_nova.py

# 4. Generate voice briefing with Nova 2 Sonic
python agents/voice_briefing_nova.py

# 5. Analyze images with Nova 2 Omni
python agents/image_analysis_nova.py

# 6. Scrape permits with Nova Act
python agents/web_scraper_nova_act.py
```

### Or Run Complete Demo
```bash
python agents/demo_all_nova_models.py
```

---

## 📊 Cost Optimization

### Built-in Cost Controls
- ✅ Default limits (10 articles, 7 investigations, 5 images)
- ✅ User confirmation for expensive operations
- ✅ Real-time cost estimation
- ✅ Automatic cost logging
- ✅ Environment variable configuration

### Operating Costs
- **Per demo**: $0.43
- **Weekly production**: $2.64
- **Annual**: $137

**232 full demos possible with $100 budget!**

---

## 🎯 Real-World Impact

### For Citizens (20M+ Mumbai Residents)
- 🏠 Track construction permits near your home
- 🚦 Get alerts about road closures
- 🏗️ Monitor civic projects in your area
- 🔊 Voice briefings for accessibility

### For Government
- 📊 Citizen engagement analytics
- 🔍 Transparency and accountability
- 📱 Modern communication channel
- 💡 Data-driven policy insights

### For Developers
- 🏢 Real estate market intelligence
- 📈 Development trend analysis
- 🗺️ Location-based insights
- 🔌 API access for integration

---

## 📈 Scalability

### Current: Mumbai
- 170 news articles/day
- 28 relevant civic issues
- 7 permit investigations
- Real-time monitoring

### Future: Pan-India
- Scale to 50+ cities
- Multi-language support
- Regional customization
- National civic dashboard

---

## 🏆 What Makes This Special

### Technical Excellence
- ✅ All 4 Amazon Nova models integrated
- ✅ Multi-agent orchestration
- ✅ Real-world data (170 Mumbai articles)
- ✅ Production-ready architecture
- ✅ Cost-optimized design

### Social Impact
- ✅ Civic transparency for 20M+ residents
- ✅ Accessibility (voice briefings)
- ✅ Government accountability
- ✅ Community empowerment

### Business Viability
- ✅ Low operating costs ($137/year)
- ✅ Multiple revenue streams
- ✅ Proven demand
- ✅ Scalable globally

---

## 📝 Project Structure

```
citypulse/
├── agents/
│   ├── news-synthesis/
│   │   ├── news_collector.py
│   │   ├── local_news_agent_nova.py
│   │   └── collected_news.json
│   ├── permit-monitor/
│   │   ├── permit_collector.py
│   │   └── pending_investigations.json
│   ├── social-listening/
│   │   └── social_collector.py
│   ├── bridge_to_permits_nova.py
│   ├── voice_briefing_nova.py
│   ├── image_analysis_nova.py
│   ├── web_scraper_nova_act.py
│   └── demo_all_nova_models.py
├── frontend/
│   └── CityPlus-prototype/
│       ├── index.html
│       ├── main.html
│       ├── map.html
│       └── styles.css
├── shared/
│   └── schemas/
│       ├── news-article.json
│       ├── permit.json
│       └── briefing.json
└── README.md
```

---

## 🎬 Demo Video

[Link to demo video]

---

## 👥 Team

[Your team information]

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- Amazon Nova team for the incredible AI models
- Mumbai civic authorities for open data
- Local news sources (Mid-Day, HT, TOI, The Hindu)

---

## 🔗 Links

- **GitHub**: [Repository URL]
- **Demo**: [Live demo URL]
- **Video**: [Demo video URL]
- **Devpost**: [Devpost submission URL]

---

**Built with ❤️ for Mumbai's 20 million residents**

**Powered by Amazon Nova** 🚀
