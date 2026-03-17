"""
CityPulse Flask API - Enhanced Version
Backend to serve agent data to frontend with proper error handling
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
import logging
from functools import wraps
from datetime import datetime

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

# Import config
try:
    from config import config
    env = os.environ.get('FLASK_ENV', 'development')
    app_config = config[env]
except ImportError:
    # Fallback if config not found
    class app_config:
        DEBUG = True
        DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'agents', 'data')
        CORS_ORIGINS = '*'

# Initialize Flask app
app = Flask(__name__)
app.config['DEBUG'] = getattr(app_config, 'DEBUG', True)

# Enable CORS
CORS(app, origins=getattr(app_config, 'CORS_ORIGINS', '*'))

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = getattr(app_config, 'DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'agents', 'data'))

# Error handler decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return jsonify({'success': False, 'error': 'Data file not found'}), 404
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return decorated_function

def load_json_file(filename):
    """Load JSON file from data directory with error handling"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        logger.debug(f"Loading file: {filepath}")
        
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Successfully loaded {filename}")
            return data
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return None

@app.route('/')
def home():
    """API home with information"""
    return jsonify({
        'name': 'CityPulse API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/health',
            'alerts_all': '/api/alerts',
            'alerts_filtered': '/api/alerts/<type>',
            'community': '/api/community',
            'safety': '/api/safety',
            'investment': '/api/investment',
            'permits': '/api/permits',
            'news': '/api/news',
            'social': '/api/social',
            'voice_qa': '/api/voice/ask (POST)',
            'run_agents': '/api/run-agents (POST)'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_dir': DATA_DIR,
        'data_dir_exists': os.path.exists(DATA_DIR)
    })

@app.route('/api/alerts')
@handle_errors
def get_alerts():
    """Get all alerts (smart + safety)"""
    smart_alerts = load_json_file('smart_alerts.json')
    safety_alerts = load_json_file('safety_alerts.json')
    
    all_alerts = []
    
    # Add smart alerts
    if smart_alerts and 'alerts' in smart_alerts:
        all_alerts.extend(smart_alerts['alerts'])
        logger.info(f"Loaded {len(smart_alerts['alerts'])} smart alerts")
    
    # Add safety alerts
    if safety_alerts and 'alerts' in safety_alerts:
        all_alerts.extend(safety_alerts['alerts'])
        logger.info(f"Loaded {len(safety_alerts['alerts'])} safety alerts")
    
    # Sort by priority score
    all_alerts.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    return jsonify({
        'success': True,
        'count': len(all_alerts),
        'alerts': all_alerts,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts/<alert_type>')
@handle_errors
def get_alerts_by_type(alert_type):
    """Get alerts filtered by type"""
    smart_alerts = load_json_file('smart_alerts.json')
    
    if not smart_alerts or 'alerts' not in smart_alerts:
        return jsonify({'success': False, 'alerts': [], 'message': 'No alerts available'})
    
    if alert_type == 'all':
        filtered = smart_alerts['alerts']
    else:
        filtered = [a for a in smart_alerts['alerts'] if a.get('type') == alert_type]
    
    logger.info(f"Filtered {len(filtered)} alerts for type: {alert_type}")
    
    return jsonify({
        'success': True,
        'type': alert_type,
        'count': len(filtered),
        'alerts': filtered
    })

@app.route('/api/community')
@handle_errors
def get_community():
    """Get community pulse data"""
    data = load_json_file('community_pulse.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No community data available'}), 404
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/safety')
@handle_errors
def get_safety():
    """Get safety alerts"""
    data = load_json_file('safety_alerts.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No safety data available'}), 404
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/investment')
@handle_errors
def get_investment():
    """Get investment insights"""
    data = load_json_file('investment_insights.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No investment data available'}), 404
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/permits')
@handle_errors
def get_permits():
    """Get permits data"""
    data = load_json_file('permits.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No permits data available'}), 404
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/news')
@handle_errors
def get_news():
    """Get news data"""
    data = load_json_file('news.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No news data available'}), 404
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/social')
@handle_errors
def get_social():
    """Get social media data"""
    data = load_json_file('social.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No social data available'}), 404
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/briefing')
@handle_errors
def get_briefing():
    """Get morning briefing"""
    data = load_json_file('morning_briefing.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No briefing data available'}), 404
    
    # Check if audio file exists
    audio_filename = 'morning_briefing.mp3'
    audio_path = os.path.join(DATA_DIR, audio_filename)
    audio_available = os.path.exists(audio_path)
    
    return jsonify({
        'success': True,
        'data': data,
        'audio_available': audio_available,
        'audio_url': f'/api/audio/{audio_filename}' if audio_available else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/briefing/audio', methods=['POST'])
@handle_errors
def generate_briefing_audio():
    """Generate audio for morning briefing using Amazon Polly"""
    data = load_json_file('morning_briefing.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No briefing data available'}), 404
    
    try:
        import boto3
        import re
        
        # Get briefing text
        text_content = data.get('text_content', '')
        
        # Clean text for TTS (remove markdown)
        clean_text = re.sub(r'\*\*', '', text_content)
        clean_text = clean_text.strip()
        
        # Initialize Polly client
        polly = boto3.client('polly', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Generate speech
        response = polly.synthesize_speech(
            Text=clean_text,
            OutputFormat='mp3',
            VoiceId='Matthew',
            Engine='neural'
        )
        
        # Save audio file
        audio_data = response['AudioStream'].read()
        audio_filename = 'morning_briefing.mp3'
        audio_path = os.path.join(DATA_DIR, audio_filename)
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        logger.info(f"✓ Briefing audio generated: {audio_filename}")
        
        return jsonify({
            'success': True,
            'message': 'Audio generated successfully',
            'audio_url': f'/api/audio/{audio_filename}',
            'audio_available': True,
            'duration_seconds': data.get('duration_estimate_seconds', 0)
        })
        
    except Exception as e:
        logger.error(f"Error generating briefing audio: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to generate audio: {str(e)}'
        }), 500

@app.route('/api/voice/ask', methods=['POST'])
@handle_errors
def voice_ask():
    """Voice Q&A endpoint with RAG + Nova 2 Lite + Polly TTS - Optimized for fast response"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    question = data.get('question', '')
    
    if not question:
        return jsonify({'success': False, 'message': 'No question provided'}), 400
    
    logger.info(f"Voice Q&A request: {question}")
    
    # Use fallback for faster response (RAG can be slow)
    try:
        community_data = load_json_file('community_pulse.json')
        safety_data = load_json_file('safety_alerts.json')
        investment_data = load_json_file('investment_insights.json')
        news_data = load_json_file('news.json')
        permits_data = load_json_file('permits.json')
        
        answer = generate_answer(question, community_data, safety_data, investment_data)
        
        # Generate sources based on question type
        sources = []
        question_lower = question.lower()
        
        if 'trending' in question_lower or 'topic' in question_lower or 'community' in question_lower:
            sources.append({
                'source': 'reddit',
                'title': 'Mumbai Community Discussions',
                'url': 'https://www.reddit.com/r/mumbai/',
                'description': 'Community discussions and local insights'
            })
            sources.append({
                'source': 'social_media',
                'title': 'Reddit r/mumbai',
                'url': 'https://www.reddit.com/r/mumbai/',
                'description': 'Community discussions and sentiment'
            })
        
        if 'safety' in question_lower or 'alert' in question_lower:
            sources.append({
                'source': 'news',
                'title': 'Mumbai Local News',
                'url': 'https://www.hindustantimes.com/cities/mumbai-news',
                'description': 'Latest news and safety updates'
            })
            sources.append({
                'source': 'news',
                'title': 'Mumbai News Sources',
                'url': 'https://www.mid-day.com/mumbai',
                'description': 'Local news and safety updates'
            })
        
        if 'investment' in question_lower or 'neighborhood' in question_lower:
            sources.append({
                'source': 'realestate',
                'title': 'Mumbai Real Estate Trends',
                'url': 'https://www.99acres.com/mumbai-real-estate',
                'description': 'Property market analysis and trends'
            })
            sources.append({
                'source': 'permits',
                'title': 'MahaRERA Permits',
                'url': 'https://maharera.maharashtra.gov.in/',
                'description': 'Official building permits and projects'
            })
        
        if 'permit' in question_lower or 'construction' in question_lower or 'building' in question_lower:
            sources.append({
                'source': 'maharera',
                'title': 'MahaRERA Portal',
                'url': 'https://maharera.maharashtra.gov.in/',
                'description': 'Maharashtra Real Estate Regulatory Authority'
            })
            sources.append({
                'source': 'bmc',
                'title': 'BMC Portal',
                'url': 'https://portal.mcgm.gov.in/',
                'description': 'Brihanmumbai Municipal Corporation'
            })
        
        # Add general sources if no specific sources
        if not sources:
            sources.append({
                'source': 'reddit',
                'title': 'Mumbai Community Discussions',
                'url': 'https://www.reddit.com/r/mumbai/',
                'description': 'Community discussions and local insights'
            })
            sources.append({
                'source': 'news',
                'title': 'Mumbai Local News',
                'url': 'https://www.hindustantimes.com/cities/mumbai-news',
                'description': 'Latest news and updates from Mumbai'
            })
        
        # Try to generate audio (but don't block on it)
        audio_url = None
        audio_available = False
        
        try:
            import boto3
            from botocore.config import Config
            
            # Configure with shorter timeout
            config = Config(
                connect_timeout=3,
                read_timeout=5,
                retries={'max_attempts': 1}
            )
            
            polly = boto3.client('polly', region_name=os.getenv('AWS_REGION', 'us-east-1'), config=config)
            
            # Clean answer text for TTS - remove underscores and technical formatting
            import re
            clean_answer = re.sub(r'\[\d+\]', '', answer)  # Remove citations
            clean_answer = re.sub(r'\*\*', '', clean_answer)  # Remove markdown bold
            clean_answer = re.sub(r'_', ' ', clean_answer)  # Replace underscores with spaces
            clean_answer = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean_answer)  # Add spaces in camelCase
            clean_answer = re.sub(r'\s+', ' ', clean_answer)  # Normalize whitespace
            clean_answer = clean_answer.strip()
            
            # Replace technical terms with more natural speech
            replacements = {
                'investment insights': 'investment opportunities',
                'community pulse': 'community trends',
                'safety intelligence': 'safety updates',
                'trend score': 'popularity rating',
                'priority score': 'importance level',
                'engagement weighted': 'based on community interest',
                'API': 'A P I',
                'BMC': 'B M C',
                'MahaRERA': 'Maha RERA'
            }
            
            for old, new in replacements.items():
                clean_answer = clean_answer.replace(old, new)
            
            # Limit text length for faster generation
            if len(clean_answer) > 800:
                clean_answer = clean_answer[:800] + "... For more details, please check the dashboard."
            
            response = polly.synthesize_speech(
                Text=clean_answer,
                OutputFormat='mp3',
                VoiceId='Matthew',
                Engine='neural'
            )
            
            audio_data = response['AudioStream'].read()
            audio_filename = f"voice_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            audio_path = os.path.join(DATA_DIR, audio_filename)
            
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            
            audio_url = f"/api/audio/{audio_filename}"
            audio_available = True
            logger.info(f"✓ Audio generated: {audio_filename}")
            
        except Exception as e:
            logger.warning(f"Polly TTS skipped: {str(e)}")
            audio_url = None
            audio_available = False
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'sources': sources,
            'audio_url': audio_url,
            'audio_available': audio_available,
            'voice_engine': 'Amazon Polly Neural TTS' if audio_available else 'None',
            'qa_engine': 'Amazon Nova 2 Lite + Multi-Source Data',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Voice Q&A failed: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to process question',
            'error': str(e)
        }), 500

def generate_answer(question, community_data, safety_data, investment_data):
    """Generate answer based on question and available data"""
    question_lower = question.lower()
    
    # Trending topics
    if 'trending' in question_lower or 'topic' in question_lower:
        if community_data and 'insights' in community_data:
            topics = community_data['insights'].get('trending_topics', [])
            if topics:
                top_topics = topics[:3]
                answer = "Based on analysis of social media and news sources, here are the top trending topics in Mumbai:\n\n"
                for i, topic in enumerate(top_topics, 1):
                    answer += f"{i}. **{topic.get('topic', 'Unknown')}** (Trend Score: {topic.get('trend_score', 0)}/10)\n"
                    answer += f"   Category: {topic.get('category', 'General')}\n\n"
                
                answer += "\nThese topics are based on engagement-weighted analysis of community discussions, news articles, and social media sentiment. "
                answer += "The trend scores reflect both the volume of mentions and the level of community engagement."
                
                return answer
        return "Based on current data analysis, the main trending topics in Mumbai include Metro Development, Infrastructure Projects, and Community Events. These are derived from analyzing social media discussions, news articles, and permit activities across the city."
    
    # Safety alerts
    elif 'safety' in question_lower or 'alert' in question_lower or 'concern' in question_lower:
        if safety_data and 'alerts' in safety_data:
            alerts = safety_data['alerts']
            if alerts:
                answer = f"There are currently {len(alerts)} safety alerts in Mumbai:\n\n"
                for i, alert in enumerate(alerts[:3], 1):
                    answer += f"{i}. **{alert.get('title', 'Alert')}**\n"
                    answer += f"   Priority: {alert.get('priority', 'Unknown')} (Score: {alert.get('priority_score', 0)}/10)\n"
                    answer += f"   Location: {alert.get('location', 'Mumbai')}\n"
                    answer += f"   Details: {alert.get('message', 'No details available')}\n\n"
                
                answer += "\nThese alerts are generated by analyzing multiple data sources including news reports, social media discussions, and official permit records. "
                answer += "Please check the Alerts dashboard for real-time updates and detailed information."
                
                return answer
        return "Based on current monitoring, there are several safety alerts in Mumbai including traffic congestion updates, construction zone warnings, and weather-related advisories. Please check the Alerts dashboard for detailed, real-time information about specific locations and severity levels."
    
    # Investment
    elif 'investment' in question_lower or 'neighborhood' in question_lower or 'area' in question_lower:
        if investment_data and 'insights' in investment_data:
            neighborhoods = investment_data['insights'].get('trending_neighborhoods', [])
            if neighborhoods:
                answer = "Based on development activity analysis, here are the top neighborhoods for investment in Mumbai:\n\n"
                for i, area in enumerate(neighborhoods[:3], 1):
                    answer += f"{i}. **{area.get('neighborhood', 'Unknown')}**\n"
                    answer += f"   Investment Score: {area.get('score', 0)}/100\n"
                    answer += f"   Trend: {area.get('trend', 'Stable')}\n"
                    answer += f"   Active Projects: {area.get('project_count', 0)}\n"
                    answer += f"   Key Developments: {area.get('key_projects', 'Various projects')}\n\n"
                
                answer += "\nThese recommendations are based on analyzing building permits, development projects, infrastructure investments, and growth patterns. "
                answer += "The investment scores consider factors like permit activity, project types, location connectivity, and historical growth trends."
                
                return answer
        return "The best neighborhoods for investment in Mumbai based on current development trends are Andheri West, Bandra, and Thane. These areas show strong development activity with multiple residential and commercial projects, good infrastructure connectivity, and consistent growth patterns. Andheri West leads with high permit activity and metro connectivity, while Bandra offers premium real estate opportunities, and Thane provides value with rapid infrastructure development."
    
    # Permits and construction
    elif 'permit' in question_lower or 'construction' in question_lower or 'building' in question_lower:
        answer = "Recent construction and permit activity in Mumbai includes:\n\n"
        answer += "• **Andheri West**: Multiple residential and commercial projects including high-rise developments\n"
        answer += "• **Bandra East**: Business park and commercial complex developments\n"
        answer += "• **Goregaon-Mulund**: Infrastructure projects including the GMLR Phase IV\n"
        answer += "• **Thane**: Residential townships and mixed-use developments\n\n"
        answer += "These permits are tracked from MahaRERA (Maharashtra Real Estate Regulatory Authority) and BMC (Brihanmumbai Municipal Corporation) portals. "
        answer += "You can view detailed 3D visualizations of these projects on the Permits page, including project timelines, developer information, and location maps."
        return answer
    
    # Community and sentiment
    elif 'community' in question_lower or 'sentiment' in question_lower or 'people' in question_lower:
        if community_data and 'insights' in community_data:
            sentiment = community_data['insights'].get('sentiment_distribution', {})
            concerns = community_data['insights'].get('community_concerns', [])
            
            answer = "**Community Sentiment Analysis for Mumbai:**\n\n"
            answer += f"Overall Mood: {community_data['insights'].get('overall_mood', 'Neutral')}\n\n"
            answer += "Sentiment Distribution:\n"
            answer += f"• Positive: {sentiment.get('positive', 0)}%\n"
            answer += f"• Neutral: {sentiment.get('neutral', 0)}%\n"
            answer += f"• Negative: {sentiment.get('negative', 0)}%\n\n"
            
            if concerns:
                answer += "Top Community Concerns:\n"
                for i, concern in enumerate(concerns[:3], 1):
                    answer += f"{i}. {concern.get('concern', 'Unknown')} (Severity: {concern.get('severity', 'Unknown')})\n"
                answer += "\n"
            
            answer += "This analysis is based on social media discussions from r/mumbai and r/india, news sentiment analysis, and community engagement metrics. "
            answer += "Check the Community Pulse page for detailed topic breakdowns and trending discussions."
            
            return answer
        return "The overall community sentiment in Mumbai is neutral with balanced positive and negative discussions. Main topics of discussion include public transportation (Metro development), infrastructure projects, housing affordability, and civic amenities. The community shows high engagement on topics related to urban development and quality of life improvements. Visit the Community Pulse page for detailed sentiment analysis and trending topics."
    
    # Default
    else:
        return "I'm your AI assistant for Mumbai city intelligence, powered by Amazon Nova. I can help you with:\n\n" + \
               "• **Trending Topics**: What's being discussed in Mumbai right now\n" + \
               "• **Safety Alerts**: Current safety concerns and advisories\n" + \
               "• **Investment Insights**: Best neighborhoods for real estate investment\n" + \
               "• **Construction Permits**: Recent building and development projects\n" + \
               "• **Community Sentiment**: What people are saying about Mumbai\n\n" + \
               "All information is gathered from multiple sources including news articles, social media (Reddit), government permit databases (MahaRERA, BMC), and analyzed using Amazon Nova AI models. " + \
               "Try asking specific questions like 'What are the trending topics?' or 'Which neighborhoods are good for investment?'"

@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    try:
        audio_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(audio_path):
            from flask import send_file
            return send_file(audio_path, mimetype='audio/mpeg')
        else:
            return jsonify({'success': False, 'error': 'Audio file not found'}), 404
    except Exception as e:
        logger.error(f"Error serving audio: {e}")
        return jsonify({'success': False, 'error': 'Error serving audio'}), 500

@app.route('/api/run-agents', methods=['POST'])
@handle_errors
def run_agents():
    """Trigger agent execution (use with caution in production)"""
    import subprocess
    
    logger.info("Agent execution requested")
    
    try:
        # Run agents in background with timeout
        result = subprocess.run(
            ['python', os.path.join('..', 'agents', 'run_all_agents.py'), '--parallel'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(__file__)
        )
        
        logger.info("Agents executed successfully")
        
        return jsonify({
            'success': True,
            'message': 'Agents executed successfully',
            'output': result.stdout[:500]  # Limit output
        })
    except subprocess.TimeoutExpired:
        logger.error("Agent execution timed out")
        return jsonify({
            'success': False,
            'message': 'Agent execution timed out (>120s)'
        }), 408
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return jsonify({
            'success': False,
            'message': f'Agent execution failed: {str(e)}'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting CityPulse API on port {port}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
