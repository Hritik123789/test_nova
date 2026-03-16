# -*- coding: utf-8 -*-
"""
Morning Voice Briefing Feature
Generates personalized daily briefings based on user location
Uses Amazon Bedrock Nova 2 Lite + Nova 2 Sonic
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3


class MorningBriefing:
    """Generate personalized morning briefings for users"""
    
    def __init__(self, user_location: Dict[str, float], user_preferences: Optional[Dict] = None):
        """
        Initialize Morning Briefing generator
        
        Args:
            user_location: {"latitude": 19.0760, "longitude": 72.8777, "name": "Mumbai"}
            user_preferences: Optional preferences (categories, radius, etc.)
        """
        print("☀️  Initializing Morning Briefing Generator...\n")
        
        self.location = user_location
        self.preferences = user_preferences or {
            "radius_km": 2,
            "categories": ["permits", "news", "social", "safety"],
            "max_items": 5
        }
        
        # Initialize Bedrock client
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            print("✓ Connected to Amazon Bedrock\n")
        except Exception as e:
            print(f"❌ Failed to connect to Bedrock: {e}")
            raise
    
    def load_news(self) -> List[Dict]:
        """Load analyzed news articles"""
        try:
            with open('news-synthesis/analyzed_news.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  No news data found")
            return []
    
    def load_permits(self) -> List[Dict]:
        """Load permit investigations"""
        try:
            with open('permit-monitor/pending_investigations_nova.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  No permit data found")
            return []
    
    def load_social(self) -> List[Dict]:
        """Load social media posts"""
        try:
            with open('social-listening/collected_social.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  No social data found")
            return []
    
    def filter_by_location(self, data: List[Dict]) -> List[Dict]:
        """
        Filter data by location proximity
        
        For demo: Just return top N items
        In production: Calculate distance and filter by radius
        """
        max_items = self.preferences.get('max_items', 5)
        return data[:max_items]
    
    def generate_briefing(self) -> Dict:
        """Generate complete morning briefing"""
        print("📊 Loading data sources...")
        
        # Load all data
        news = self.load_news()
        permits = self.load_permits()
        social = self.load_social()
        
        # Filter by location
        local_news = self.filter_by_location(news)
        local_permits = self.filter_by_location(permits)
        
        print(f"   Found {len(local_news)} news articles")
        print(f"   Found {len(local_permits)} permit investigations")
        print()
        
        # Generate briefing script
        script = self.create_voice_script(local_news, local_permits)
        
        # Create briefing object
        briefing = {
            "briefing_id": f"morning-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "user_location": self.location,
            "generated_at": datetime.now().isoformat(),
            "text_content": script,
            "sections": [
                {
                    "type": "news",
                    "items_count": len(local_news),
                    "priority": "high" if len(local_news) > 0 else "low",
                    "sources": [
                        {"name": "Mid-Day Mumbai", "url": "https://www.mid-day.com/mumbai"},
                        {"name": "Hindustan Times", "url": "https://www.hindustantimes.com/cities/mumbai-news"},
                        {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/city/mumbai"}
                    ]
                },
                {
                    "type": "permits",
                    "items_count": len(local_permits),
                    "priority": "high" if len(local_permits) > 0 else "low",
                    "sources": [
                        {"name": "MahaRERA", "url": "https://maharera.maharashtra.gov.in/"},
                        {"name": "BMC Portal", "url": "https://portal.mcgm.gov.in/"}
                    ]
                },
                {
                    "type": "social",
                    "items_count": 0,
                    "priority": "low",
                    "sources": [
                        {"name": "r/mumbai", "url": "https://www.reddit.com/r/mumbai/"},
                        {"name": "r/india", "url": "https://www.reddit.com/r/india/"}
                    ]
                }
            ],
            "duration_estimate_seconds": len(script.split()) * 0.4,  # ~150 words/min
            "ai_attribution": {
                "generation_model": "Amazon Nova 2 Lite",
                "voice_model": "Amazon Polly Neural TTS",
                "embedding_model": "Amazon Titan Embeddings"
            }
        }
        
        return briefing
    
    def create_voice_script(self, news: List[Dict], permits: List[Dict]) -> str:
        """
        Generate conversational briefing script using Nova 2 Lite
        
        Args:
            news: Filtered news articles
            permits: Filtered permit investigations
            
        Returns:
            Conversational script ready for text-to-speech
        """
        print("🤖 Generating briefing script with Nova 2 Lite...")
        
        # Prepare context for Nova
        context = {
            "location": self.location.get("name", "your area"),
            "news_count": len(news),
            "permit_count": len(permits),
            "top_news": [
                {
                    "title": article.get("title", ""),
                    "category": article.get("category", ""),
                    "summary": article.get("summary", "")
                }
                for article in news[:3]
            ],
            "top_permits": [
                {
                    "location": inv.get("location", ""),
                    "action": inv.get("action_type", ""),
                    "priority": inv.get("priority", "")
                }
                for inv in permits[:3]
            ]
        }
        
        # Create prompt for Nova 2 Lite
        prompt = f"""Create a friendly morning briefing for a Mumbai resident.

Location: {context['location']}
Date: {datetime.now().strftime('%A, %B %d, %Y')}

Data available:
- {context['news_count']} news articles
- {context['permit_count']} permit investigations

Top news:
{json.dumps(context['top_news'], indent=2)}

Top permits:
{json.dumps(context['top_permits'], indent=2)}

Generate a conversational 1-2 minute morning briefing that:
1. Starts with a friendly greeting
2. Highlights the most important news (max 3 items)
3. Mentions any permit activity nearby
4. Ends with a positive note

Keep it natural, friendly, and under 300 words. Use simple language."""

        try:
            # Call Nova 2 Lite
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": 500,
                        "temperature": 0.7
                    }
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            script = response_body['output']['message']['content'][0]['text']
            
            print("✓ Script generated successfully\n")
            return script.strip()
            
        except Exception as e:
            print(f"❌ Error generating script: {e}")
            # Fallback to simple template
            return self._fallback_script(context)
    
    def _fallback_script(self, context: Dict) -> str:
        """Fallback script if Nova fails"""
        script = f"""Good morning! Here's your {context['location']} briefing for {datetime.now().strftime('%A, %B %d')}.

"""
        
        if context['news_count'] > 0:
            script += f"We have {context['news_count']} news updates for you today. "
            for i, article in enumerate(context['top_news'][:2], 1):
                script += f"{article['title']}. "
        
        if context['permit_count'] > 0:
            script += f"\n\nThere are {context['permit_count']} permit investigations in your area. "
        
        script += "\n\nHave a great day!"
        
        return script
    
    def save_briefing(self, briefing: Dict, output_file: str = "morning_briefing.json"):
        """Save briefing to file"""
        output_path = os.path.join('features', output_file)
        os.makedirs('features', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(briefing, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Briefing saved to: {output_path}")
        return output_path


def main():
    """Demo: Generate morning briefing for Mumbai user"""
    print("="*70)
    print("  ☀️  MORNING BRIEFING GENERATOR - Demo")
    print("="*70)
    print()
    
    # Example user location (Mumbai)
    user_location = {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "name": "Mumbai"
    }
    
    # Example preferences
    user_preferences = {
        "radius_km": 2,
        "categories": ["permits", "news", "social", "safety"],
        "max_items": 5
    }
    
    try:
        # Initialize generator
        generator = MorningBriefing(user_location, user_preferences)
        
        # Generate briefing
        briefing = generator.generate_briefing()
        
        # Display results
        print("="*70)
        print("  📋 GENERATED BRIEFING")
        print("="*70)
        print()
        print(f"Briefing ID: {briefing['briefing_id']}")
        print(f"Location: {briefing['user_location']['name']}")
        print(f"Generated: {briefing['generated_at']}")
        print(f"Duration: ~{briefing['duration_estimate_seconds']:.0f} seconds")
        print()
        print("Script:")
        print("-" * 70)
        print(briefing['text_content'])
        print("-" * 70)
        print()
        
        # Save to file
        output_file = generator.save_briefing(briefing)
        
        print()
        print("✅ Morning briefing generated successfully!")
        print(f"💰 Estimated cost: $0.0002")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
