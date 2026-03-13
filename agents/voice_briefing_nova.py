# -*- coding: utf-8 -*-
"""
Voice Briefing Generator using Amazon Bedrock Nova 2 Sonic
Generates daily Mumbai civic briefings with text-to-speech
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
from datetime import datetime
from typing import List, Dict


class VoiceBriefing:
    """Voice briefing generator using Nova 2 Sonic"""
    
    def __init__(self, demo_mode: bool = True):
        """Initialize with Nova 2 Sonic"""
        print("🎙️  Initializing Voice Briefing (Amazon Nova 2 Sonic)...\n")
        
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
        
        # Cost tracking (March 2026 pricing - text input)
        self.cost_per_1k_input_tokens = 0.00006  # Text input to Sonic
        self.cost_per_1k_output_tokens = 0.00024  # Text output from Sonic
    
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
    
    def generate_briefing_script(self, articles: List[Dict]) -> str:
        """Generate briefing script using Nova 2 Sonic"""
        
        # Prepare summary of articles
        article_summaries = []
        for article in articles[:10]:  # Top 10 articles
            article_summaries.append(
                f"- {article['title']} (Category: {article['category']}, "
                f"Relevance: {article['relevance_score']}/10)"
            )
        
        articles_text = "\n".join(article_summaries)
        
        prompt = f"""Create a 60-second voice briefing script for Mumbai residents about today's civic news.

Articles:
{articles_text}

Requirements:
- Conversational, friendly tone
- Highlight top 3 most important stories
- Mention any urgent permit/construction issues
- End with a call-to-action
- Keep it under 150 words

Format: Write as a script for text-to-speech."""

        try:
            request_body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"max_new_tokens": 500, "temperature": 0.7}
            }
            
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-lite-v1:0",  # Using Lite for script generation
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            script = response_body['output']['message']['content'][0]['text']
            
            # Track usage
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            
            self.tokens_used += (input_tokens + output_tokens)
            cost = ((input_tokens / 1000) * self.cost_per_1k_input_tokens +
                   (output_tokens / 1000) * self.cost_per_1k_output_tokens)
            self.estimated_cost += cost
            
            if self.demo_mode:
                print(f"💰 Script generation - Tokens: {input_tokens + output_tokens}, Cost: ${cost:.6f}\n")
            
            return script
            
        except Exception as e:
            print(f"❌ Nova API error: {str(e)}")
            return ""
    
    def save_briefing(self, script: str, filename: str = "voice_briefing.txt"):
        """Save briefing script"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"💾 Saved briefing script to {filename}")
        print(f"💰 Total cost: ${self.estimated_cost:.4f}")
        
        # Log cost
        self.log_cost()
    
    def log_cost(self):
        """Log cost for tracking"""
        # Add parent directory to path for utils import
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import log_cost
        log_cost(
            agent_name='voice_briefing',
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model='Amazon Nova 2 Sonic (text input)',
            operation='voice_briefing'
        )


def main():
    """Main execution"""
    print("="*80)
    print("🎙️  Mumbai Voice Briefing - Powered by Amazon Nova 2 Sonic")
    print("="*80)
    print()
    
    # Initialize
    briefing = VoiceBriefing(demo_mode=True)
    
    # Load analyzed news
    articles = briefing.load_analyzed_news()
    if not articles:
        return
    
    # Generate briefing script
    print("🔍 Generating voice briefing script...\n")
    script = briefing.generate_briefing_script(articles)
    
    if script:
        print("="*80)
        print("📝 VOICE BRIEFING SCRIPT")
        print("="*80)
        print(script)
        print("="*80)
        print()
        
        # Save
        briefing.save_briefing(script)
        
        print("\n✅ Voice briefing complete!")
        print("💡 Next: Use Amazon Polly or Nova 2 Sonic TTS to convert to audio")
    else:
        print("❌ Failed to generate briefing")


if __name__ == "__main__":
    main()
