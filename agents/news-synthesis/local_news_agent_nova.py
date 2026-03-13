# -*- coding: utf-8 -*-
"""
Local News Agent using Amazon Bedrock Nova 2 Lite
CREDIT-SAFE VERSION with built-in cost tracking and limits
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
from typing import List, Dict, Optional


class NovaNewsAgent:
    """Mumbai news analyst using Amazon Bedrock Nova 2 Lite"""
    
    def __init__(self, max_articles: int = 10, demo_mode: bool = True):
        """
        Initialize with Nova 2 Lite
        
        Args:
            max_articles: Maximum articles to process (default: 10 for cost control)
            demo_mode: Enable cost tracking and warnings
        """
        print("🤖 Initializing Nova News Agent (Amazon Bedrock Nova 2 Lite)...\n")
        
        self.max_articles = max_articles
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
            print("💡 Make sure AWS credentials are configured")
            raise
        
        # Cost tracking (March 2026 pricing)
        self.cost_per_1k_input_tokens = 0.0003  # Nova 2 Lite: $0.30 per 1M input tokens
        self.cost_per_1k_output_tokens = 0.0025  # Nova 2 Lite: $2.50 per 1M output tokens
        
        if self.demo_mode:
            print(f"💰 DEMO MODE: Processing max {max_articles} articles")
            print(f"💰 Estimated cost: ~${self.estimate_total_cost(max_articles):.4f}\n")
    
    def estimate_total_cost(self, num_articles: int) -> float:
        """Estimate total cost for processing articles"""
        # Average tokens per article
        input_tokens_per_article = 500  # title + summary
        output_tokens_per_article = 200  # analysis
        
        total_input = (input_tokens_per_article * num_articles) / 1000
        total_output = (output_tokens_per_article * num_articles) / 1000
        
        cost = (total_input * self.cost_per_1k_input_tokens + 
                total_output * self.cost_per_1k_output_tokens)
        
        return cost
    
    def load_collected_news(self, filename: str = "collected_news.json") -> List[Dict]:
        """Load news from NewsCollector output"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            total = len(articles)
            limited = min(total, self.max_articles)
            
            print(f"📰 Loaded {total} articles from {filename}")
            
            if total > self.max_articles:
                print(f"⚠️  COST CONTROL: Processing only {limited} articles")
                print(f"💡 Set MAX_ARTICLES env var to process more\n")
            else:
                print()
            
            return articles[:limited]
            
        except FileNotFoundError:
            print(f"❌ {filename} not found. Run news_collector.py first!")
            return []
    
    def call_nova(self, prompt: str) -> str:
        """Call Amazon Bedrock Nova 2 Lite"""
        try:
            # Prepare request
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 300,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            # Call Nova 2 Lite
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-lite-v1:0",
                body=json.dumps(request_body)
            )
            
            # Parse response
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
    
    def analyze_article(self, article: Dict, article_num: int) -> Optional[Dict]:
        """Analyze a single article using Nova 2 Lite"""
        
        prompt = f"""Analyze this Mumbai news article:

Title: {article['title']}
Summary: {article.get('summary', 'N/A')}

Tasks:
1. Does it mention 'Andheri', 'BMC' (Brihanmumbai Municipal Corporation), or other Mumbai civic bodies? Answer: yes or no
2. List which entities are mentioned (e.g., BMC, Andheri, MHADA, BEST, etc.)
3. If yes, categorize as: Civic, Traffic, or Real Estate
4. Does it mention new buildings, construction, or redevelopment? Answer: yes or no
5. Rate relevance to local Mumbai residents (1-10)

Respond in this exact format:
MENTIONS: yes/no
ENTITIES: comma-separated list (e.g., BMC, Andheri) or "none"
CATEGORY: Civic/Traffic/Real Estate (only if mentions is yes)
PERMIT_CHECK: yes/no
RELEVANCE: number 1-10
"""
        
        try:
            result = self.call_nova(prompt)
            
            if not result:
                return None
            
            # Parse response
            mentions = 'yes' in result.split('MENTIONS:')[1].split('\n')[0].lower()
            
            if not mentions:
                return None
            
            # Extract entities
            try:
                entities_line = result.split('ENTITIES:')[1].split('\n')[0].strip()
                if entities_line.lower() != 'none':
                    mentions_list = [e.strip() for e in entities_line.split(',')]
                else:
                    mentions_list = []
            except:
                mentions_list = []
            
            # Extract category
            try:
                category_line = result.split('CATEGORY:')[1].split('\n')[0].strip()
                if 'Civic' in category_line:
                    category = 'Civic'
                elif 'Traffic' in category_line:
                    category = 'Traffic'
                elif 'Real Estate' in category_line:
                    category = 'Real Estate'
                else:
                    category = 'Civic'
            except:
                category = 'Civic'
            
            # Extract permit check
            try:
                permit_check = 'yes' in result.split('PERMIT_CHECK:')[1].split('\n')[0].lower()
            except:
                permit_check = False
            
            # Extract relevance
            try:
                relevance_line = result.split('RELEVANCE:')[1].split('\n')[0].strip()
                relevance = int(''.join(filter(str.isdigit, relevance_line)))
                if relevance < 1 or relevance > 10:
                    relevance = 5
            except:
                relevance = 5
            
            return {
                'article_number': article_num,
                'title': article['title'],
                'category': category,
                'mentions': mentions_list,
                'permit_check_required': permit_check,
                'relevance_score': relevance,
                'url': article.get('url', ''),
                'summary': article.get('summary', ''),
                'analyzed_by': 'Amazon Nova 2 Lite'
            }
            
        except Exception as e:
            print(f"⚠️  Error analyzing article {article_num}: {str(e)}")
            return None
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles using Nova 2 Lite"""
        
        if not articles:
            print("⚠️  No articles to process")
            return []
        
        # Cost warning
        if self.demo_mode:
            estimated = self.estimate_total_cost(len(articles))
            print(f"💰 Estimated cost for {len(articles)} articles: ${estimated:.4f}")
            
            if estimated > 0.05:  # More than 5 cents
                confirm = input("⚠️  Continue? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("❌ Cancelled by user")
                    return []
        
        print(f"\n🔍 Analyzing {len(articles)} articles with Amazon Nova 2 Lite...\n")
        
        analyzed = []
        for i, article in enumerate(articles, 1):
            print(f"Processing {i}/{len(articles)}: {article['title'][:60]}...")
            
            result = self.analyze_article(article, i)
            if result:
                analyzed.append(result)
                print(f"  ✓ Relevant! Category: {result['category']}, Mentions: {', '.join(result['mentions'])}")
            else:
                print(f"  - Not relevant")
        
        print(f"\n✓ Analysis complete! Found {len(analyzed)} relevant articles")
        print(f"💰 Total tokens used: {self.tokens_used}")
        print(f"💰 Total cost: ${self.estimated_cost:.4f}\n")
        
        # Log cost
        if self.demo_mode:
            self.log_cost(len(articles), len(analyzed))
        
        return analyzed
    
    def log_cost(self, total_articles: int, relevant_articles: int):
        """Log cost to file for tracking"""
        # Add parent directory to path for utils import
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import log_cost
        log_cost(
            agent_name='news_analysis',
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model='Amazon Nova 2 Lite',
            operation='news_analysis',
            total_articles=total_articles,
            relevant_articles=relevant_articles
        )
    
    def save_results(self, analyzed: List[Dict], filename: str = "analyzed_news_nova.json"):
        """Save analyzed articles"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analyzed, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(analyzed)} analyzed articles to {filename}")


def main():
    """Main execution"""
    print("="*80)
    print("Mumbai Local News Agent - Powered by Amazon Nova 2 Lite")
    print("="*80)
    print()
    
    # Get configuration from environment
    max_articles = int(os.getenv('MAX_ARTICLES', '10'))
    demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
    
    # Initialize agent
    agent = NovaNewsAgent(max_articles=max_articles, demo_mode=demo_mode)
    
    # Load collected news
    articles = agent.load_collected_news()
    
    if not articles:
        return
    
    # Process articles
    analyzed = agent.process_articles(articles)
    
    # Save results
    if analyzed:
        agent.save_results(analyzed)
        
        # Show summary
        print("\n" + "="*80)
        print("📊 Analysis Summary:")
        print("="*80)
        print(f"Total articles analyzed: {len(analyzed)}")
        
        # Category breakdown
        categories = {}
        permit_required = 0
        for article in analyzed:
            cat = article.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            if article.get('permit_check_required'):
                permit_required += 1
        
        print(f"\nCategories:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}")
        
        print(f"\nArticles requiring permit check: {permit_required}")
        
        print(f"\n💰 Session Cost: ${agent.estimated_cost:.4f}")
        print(f"💰 Remaining budget (est.): ${100 - agent.estimated_cost:.2f}")
    else:
        print("\n⚠️  No articles matched the criteria")


if __name__ == "__main__":
    main()
