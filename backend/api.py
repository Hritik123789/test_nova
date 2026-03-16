"""
CityPulse Flask API
Simple backend to serve agent data to frontend
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
import sys

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'agents', 'data')

def load_json_file(filename):
    """Load JSON file from data directory"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

@app.route('/')
def home():
    """API home"""
    return jsonify({
        'name': 'CityPulse API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'alerts': '/api/alerts',
            'community': '/api/community',
            'safety': '/api/safety',
            'investment': '/api/investment',
            'voice': '/api/voice/ask',
            'health': '/health'
        }
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})

@app.route('/api/alerts')
def get_alerts():
    """Get all alerts (smart + safety)"""
    smart_alerts = load_json_file('smart_alerts.json')
    safety_alerts = load_json_file('safety_alerts.json')
    
    all_alerts = []
    
    if smart_alerts and 'alerts' in smart_alerts:
        all_alerts.extend(smart_alerts['alerts'])
    
    if safety_alerts and 'alerts' in safety_alerts:
        all_alerts.extend(safety_alerts['alerts'])
    
    # Sort by priority score
    all_alerts.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    return jsonify({
        'success': True,
        'count': len(all_alerts),
        'alerts': all_alerts
    })

@app.route('/api/alerts/<alert_type>')
def get_alerts_by_type(alert_type):
    """Get alerts filtered by type"""
    smart_alerts = load_json_file('smart_alerts.json')
    
    if not smart_alerts or 'alerts' not in smart_alerts:
        return jsonify({'success': False, 'alerts': []})
    
    if alert_type == 'all':
        filtered = smart_alerts['alerts']
    else:
        filtered = [a for a in smart_alerts['alerts'] if a.get('type') == alert_type]
    
    return jsonify({
        'success': True,
        'count': len(filtered),
        'alerts': filtered
    })

@app.route('/api/community')
def get_community():
    """Get community pulse data"""
    data = load_json_file('community_pulse.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/safety')
def get_safety():
    """Get safety alerts"""
    data = load_json_file('safety_alerts.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/investment')
def get_investment():
    """Get investment insights"""
    data = load_json_file('investment_insights.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/permits')
def get_permits():
    """Get permits data"""
    data = load_json_file('permits.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/news')
def get_news():
    """Get news data"""
    data = load_json_file('news.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/social')
def get_social():
    """Get social media data"""
    data = load_json_file('social.json')
    
    if not data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/voice/ask', methods=['POST'])
def voice_ask():
    """Voice Q&A endpoint"""
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'success': False, 'message': 'No question provided'})
    
    # Simple response logic (in production, call voice_qa_realtime.py)
    responses = {
        'trending': 'Based on current data, the top trending topics in Mumbai are Metro Development, LPG Shortage, and Road Infrastructure.',
        'safety': 'There are currently 2 high-priority safety alerts in your area.',
        'investment': 'The best neighborhoods for investment are Andheri West, Bandra, and Thane.',
        'default': 'I can help you with information about Mumbai. Try asking about trending topics, safety alerts, or investment neighborhoods.'
    }
    
    answer = responses['default']
    if 'trending' in question.lower() or 'topic' in question.lower():
        answer = responses['trending']
    elif 'safety' in question.lower() or 'alert' in question.lower():
        answer = responses['safety']
    elif 'investment' in question.lower() or 'neighborhood' in question.lower():
        answer = responses['investment']
    
    return jsonify({
        'success': True,
        'question': question,
        'answer': answer,
        'audio_available': False  # Set to True when Polly is integrated
    })

@app.route('/api/run-agents', methods=['POST'])
def run_agents():
    """Trigger agent execution"""
    import subprocess
    
    try:
        # Run agents in background
        result = subprocess.run(
            ['python', 'agents/run_all_agents.py', '--parallel'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return jsonify({
            'success': True,
            'message': 'Agents executed successfully',
            'output': result.stdout
        })
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'Agent execution timed out'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
