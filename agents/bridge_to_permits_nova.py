# -*- coding: utf-8 -*-
"""
Bridge to Permits - Nova Version
Uses Amazon Bedrock Nova 2 Lite for location/action extraction
CREDIT-SAFE with cost tracking
"""

import json
import os
import sys

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3
from typing import List, Dict, Optional
from datetime import datetime


class NovaBridge:
    """Bridge using Amazon Bedrock Nova 2 Lite"""
    
    def __init__(self, max_investigations: int = 7, demo_mode: bool = True):
        """Initialize with Nova 2 Lite"""
        print("🌉 Initializing Nova Bridge (Amazon Bedrock Nova 2 Lite)...\n")
        
        self.max_investigations = max_investigations
        self.demo_mode = demo_mode
        self.tokens_used = 0
        self.estimated_cost = 0.0
        
        # Initialize Bedrock client
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            print("✓ Connected to Amazon Bedrock\n")
        except Exception as e:
            print(f"❌ Failed to connect to Bedrock: {str(e)}")
            raise
        
        # Cost tracking (March 2026 pricing)
        self.cost_per_1k_input_tokens = 0.0003  # Nova 2 Lite
        self.cost_per_1k_output_tokens = 0.0025
    
    def load_analyzed_news(self, filename: str = "news-synthesis/analyzed_news.json") -> List[Dict]:
        """Load analyzed news"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            print(f"📰 Loaded {len(articles)} analyzed articles\n")
            return articles
        except FileNotFoundError:
            print(f"❌ {filename} not found!")
            return []
    
    def filter_permit_required(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles requiring permit checks"""
        permit_articles = [a for a in articles if a.get('permit_check_required', False)]
        limited = permit_articles[:self.max_investigations]
        print(f"🔍 Found {len(permit_articles)} articles, processing {len(limited)}\n")
        return limited
    
    def call_nova(self, prompt: str) -> str:
        """Call Amazon Bedrock Nova 2 Lite"""
        try:
            request_body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"max_new_tokens": 200, "temperature": 0.3}
            }
            
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-lite-v1:0",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['output']['message']['content'][0]['text']
            
            # Track usage
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            
            self.tokens_used += (input_tokens + output_tokens)
            cost = ((input_tokens / 1000) * self.cost_per_1k_input_tokens +
                   (output_tokens / 1000) * self.cost_per_1k_output_tokens)
            self.estimated_cost += cost
            
            if self.demo_mode:
                print(f"  💰 Tokens: {input_tokens + output_tokens}, Cost: ${cost:.6f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Nova API error: {str(e)}")
            return ""
    
    def extract_location_and_action(self, title: str, summary: str) -> Dict:
        """Extract location and action using Nova"""
        prompt = f"""Extract location and action type from this Mumbai news:

Title: {title}
Summary: {summary}

Return in this format:
LOCATION: [specific area like Bandra, Thane, or "Mumbai (General)"]
ACTION: [one of: Redevelopment, New Construction, Infrastructure Project, Road Work, Metro Project, Demolition, Other]"""

        result = self.call_nova(prompt)
        
        # Parse response
        location = "Mumbai (General)"
        action = "Infrastructure Project"
        
        try:
            if 'LOCATION:' in result:
                location = result.split('LOCATION:')[1].split('\n')[0].strip()
            if 'ACTION:' in result:
                action = result.split('ACTION:')[1].split('\n')[0].strip()
        except:
            pass
        
        return {'location': location, 'action': action}
    
    def enrich_articles(self, articles: List[Dict]) -> List[Dict]:
        """Enrich articles with location and action"""
        enriched = []
        
        print("🔍 Extracting locations and actions with Nova 2 Lite...\n")
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            summary = article.get('summary', '')
            
            print(f"Processing {i}/{len(articles)}: {title[:60]}...")
            
            extracted = self.extract_location_and_action(title, summary)
            
            enriched_article = article.copy()
            enriched_article['location'] = extracted['location']
            enriched_article['action'] = extracted['action']
            enriched_article['priority'] = self.calculate_priority(article)
            
            enriched.append(enriched_article)
            
            print(f"  → Location: {extracted['location']}, Action: {extracted['action']}")
        
        print(f"\n💰 Total cost: ${self.estimated_cost:.4f}\n")
        return enriched
    
    def calculate_priority(self, article: Dict) -> str:
        """Calculate priority"""
        relevance = article.get('relevance_score', 5)
        category = article.get('category', '')
        
        if relevance >= 8 and category == 'Real Estate':
            return "HIGH"
        elif relevance >= 7:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_investigations(self, enriched: List[Dict]) -> List[Dict]:
        """Generate investigation tasks"""
        investigations = []
        
        for article in enriched:
            investigation = {
                'investigation_id': f"INV-{article['article_number']:03d}",
                'source': 'Nova News Agent',
                'title': article['title'],
                'location': article['location'],
                'action': article['action'],
                'priority': article['priority'],
                'category': article.get('category', 'Unknown'),
                'relevance_score': article.get('relevance_score', 0),
                'news_url': article.get('url', ''),
                'created_at': datetime.now().isoformat(),
                'status': 'Pending Investigation',
                'analyzed_by': 'Amazon Nova 2 Lite'
            }
            investigations.append(investigation)
        
        return investigations
    
    def save_investigations(self, investigations: List[Dict], 
                          filename: str = "permit-monitor/pending_investigations_nova.json"):
        """Save investigations"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(investigations, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(investigations)} investigations to {filename}")
        print(f"💰 Session cost: ${self.estimated_cost:.4f}")
        
        # Log cost
        self.log_cost(len(investigations))
    
    def log_cost(self, num_investigations: int):
        """Log cost for tracking"""
        # Add parent directory to path for utils import
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import log_cost
        log_cost(
            agent_name='bridge_processing',
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model='Amazon Nova 2 Lite',
            operation='bridge_processing',
            investigations=num_investigations
        )


def main():
    """Main execution"""
    print("="*80)
    print("🌉 Bridge to Permits - Powered by Amazon Nova 2 Lite")
    print("="*80)
    print()
    
    # Get configuration
    max_investigations = int(os.getenv('MAX_INVESTIGATIONS', '7'))
    demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
    
    # Initialize bridge
    bridge = NovaBridge(max_investigations=max_investigations, demo_mode=demo_mode)
    
    # Load analyzed news
    articles = bridge.load_analyzed_news()
    if not articles:
        return
    
    # Filter for permit-required
    permit_articles = bridge.filter_permit_required(articles)
    if not permit_articles:
        print("⚠️  No articles require permit checks")
        return
    
    # Enrich with Nova
    enriched = bridge.enrich_articles(permit_articles)
    
    # Generate investigations
    investigations = bridge.generate_investigations(enriched)
    
    # Save results
    bridge.save_investigations(investigations)
    
    print("\n✅ Bridge complete!")


if __name__ == "__main__":
    main()
