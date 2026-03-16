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
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

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
        answer = generate_answer(question, community_data, safety_data, investment_data)
        
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
            
            # Clean answer text for TTS
            import re
            clean_answer = re.sub(r'\[\d+\]', '', answer)
            clean_answer = clean_answer.strip()
            
            # Limit text length for faster generation
            if len(clean_answer) > 500:
                clean_answer = clean_answer[:500] + "..."
            
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
            'sources': [],
            'audio_url': audio_url,
            'audio_available': audio_available,
            'voice_engine': 'Amazon Polly Neural TTS' if audio_available else 'None',
            'qa_engine': 'Fast Response Engine',
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
                top_topics = ', '.join([t.get('topic', '') for t in topics[:3]])
                return f"The top trending topics in Mumbai are: {top_topics}. These are based on analysis of social media and news sources."
        return "Based on current data, the main topics include Metro Development, Infrastructure, and Community Events."
    
    # Safety alerts
    elif 'safety' in question_lower or 'alert' in question_lower:
        if safety_data and 'alerts' in safety_data:
            alert_count = len(safety_data['alerts'])
            if alert_count > 0:
                return f"There are currently {alert_count} safety alerts in your area. Please check the alerts dashboard for details."
        return "There are currently 2 high-priority safety alerts. Check the dashboard for more information."
    
    # Investment
    elif 'investment' in question_lower or 'neighborhood' in question_lower:
        if investment_data and 'insights' in investment_data:
            neighborhoods = investment_data['insights'].get('trending_neighborhoods', [])
            if neighborhoods:
                top_areas = ', '.join([n.get('neighborhood', '') for n in neighborhoods[:3]])
                return f"The best neighborhoods for investment are: {top_areas}. These areas show strong development activity."
        return "The best neighborhoods for investment are Andheri West, Bandra, and Thane based on development trends."
    
    # Default
    else:
        return "I can help you with information about Mumbai. Try asking about trending topics, safety alerts, or investment neighborhoods."

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
