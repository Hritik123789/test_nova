# -*- coding: utf-8 -*-
"""
RAG-based Q&A System for CityPulse
Uses FAISS for vector search and Nova 2 Lite for generation
Indexes all collected neighborhood data for natural language queries
"""

import json
import os
import sys
import boto3
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.utils import log_cost


class CityPulseRAG:
    """RAG system for neighborhood intelligence Q&A"""
    
    def __init__(self, demo_mode: bool = True):
        """Initialize RAG system with Bedrock"""
        print("🔍 Initializing CityPulse RAG Q&A System...\n")
        
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
        
        # Cost tracking
        self.embedding_cost_per_1k_tokens = 0.0001  # Titan Embeddings
        self.lite_cost_per_1k_input = 0.0003  # Nova 2 Lite
        self.lite_cost_per_1k_output = 0.0025
        
        # Data storage
        self.documents = []
        self.embeddings = []
        self.index = None
    
    def load_all_data(self):
        """Load all data from agents/data/ directory"""
        print("📂 Loading all neighborhood data...\n")
        
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Load each data source
        data_files = {
            'news': 'news.json',
            'permits': 'permits.json',
            'bmc_permits': 'bmc_permits.json',
            'social': 'social.json',
            'smart_alerts': 'smart_alerts.json',
            'safety_alerts': 'safety_alerts.json',
            'investment_insights': 'investment_insights.json',
            'community_pulse': 'community_pulse.json'
        }
        
        for source_type, filename in data_files.items():
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._process_data_source(source_type, data)
        
        print(f"✓ Loaded {len(self.documents)} documents\n")
    
    def _process_data_source(self, source_type: str, data):
        """Process and chunk data from a source"""
        if source_type == 'news':
            for article in data:
                doc = {
                    'source': 'news',
                    'content': f"News: {article.get('title', '')}. {article.get('summary', '')}",
                    'metadata': article
                }
                self.documents.append(doc)
        
        elif source_type in ['permits', 'bmc_permits']:
            items = data if isinstance(data, list) else data.get('permits', [])
            for permit in items:
                # Extract fields from nested metadata if present
                metadata_obj = permit.get('metadata', {})
                project_name = metadata_obj.get('project_name', permit.get('project_name', ''))
                promoter = metadata_obj.get('promoter', permit.get('promoter', ''))
                district = metadata_obj.get('district', permit.get('district', ''))
                location = permit.get('location', district)
                permit_type = permit.get('permit_type', permit.get('event_type', ''))
                status = permit.get('status', 'Registered')
                description = permit.get('description', '')
                
                # Build comprehensive content string
                content_parts = []
                if project_name:
                    content_parts.append(f"Project: {project_name}")
                if promoter:
                    content_parts.append(f"Developer: {promoter}")
                if location:
                    content_parts.append(f"Location: {location}")
                if permit_type:
                    content_parts.append(f"Type: {permit_type}")
                if status:
                    content_parts.append(f"Status: {status}")
                if description:
                    content_parts.append(f"Details: {description}")
                
                content = "Permit - " + ". ".join(content_parts) if content_parts else f"Permit at {location}"
                
                doc = {
                    'source': 'permits',
                    'content': content,
                    'metadata': permit
                }
                self.documents.append(doc)
        
        elif source_type == 'social':
            # Handle both list and dict formats
            posts = data if isinstance(data, list) else data.get('posts', [])
            for post in posts:
                if isinstance(post, dict):
                    doc = {
                        'source': 'social',
                        'content': f"Social post from {post.get('subreddit', '')}: {post.get('title', '')}. {post.get('selftext', '')}. Sentiment: {post.get('sentiment', '')}",
                        'metadata': post
                    }
                    self.documents.append(doc)
        
        elif source_type == 'smart_alerts':
            # Handle both list and dict formats
            alerts = data if isinstance(data, list) else data.get('alerts', [])
            for alert in alerts:
                if isinstance(alert, dict):
                    doc = {
                        'source': 'alerts',
                        'content': f"Alert: {alert.get('title', '')}. {alert.get('description', '')}. Priority: {alert.get('priority', '')}",
                        'metadata': alert
                    }
                    self.documents.append(doc)
        
        elif source_type == 'safety_alerts':
            # Handle both list and dict formats
            alerts = data if isinstance(data, list) else data.get('alerts', [])
            for alert in alerts:
                if isinstance(alert, dict):
                    doc = {
                        'source': 'safety',
                        'content': f"Safety alert: {alert.get('title', '')}. {alert.get('description', '')}. Severity: {alert.get('severity', '')}",
                        'metadata': alert
                    }
                    self.documents.append(doc)
        
        elif source_type == 'investment_insights':
            # Handle both list and dict formats
            insights = data if isinstance(data, list) else data.get('insights', [])
            for insight in insights:
                if isinstance(insight, dict):
                    doc = {
                        'source': 'investment',
                        'content': f"Investment insight for {insight.get('neighborhood', '')}: {insight.get('summary', '')}. Score: {insight.get('score', '')}",
                        'metadata': insight
                    }
                    self.documents.append(doc)
        
        elif source_type == 'community_pulse':
            # Handle both list and dict formats
            topics = data if isinstance(data, list) else data.get('topics', [])
            for topic in topics:
                if isinstance(topic, dict):
                    doc = {
                        'source': 'community',
                        'content': f"Community topic: {topic.get('topic', '')}. {topic.get('summary', '')}",
                        'metadata': topic
                    }
                    self.documents.append(doc)
    
    def create_embeddings(self):
        """Create embeddings for all documents using Bedrock Titan"""
        print("🔢 Creating embeddings with Titan Embeddings...\n")
        
        try:
            import faiss
        except ImportError:
            print("❌ FAISS not installed. Install with: pip install faiss-cpu")
            return
        
        embeddings_list = []
        
        for i, doc in enumerate(self.documents):
            if i % 10 == 0:
                print(f"  Processing {i}/{len(self.documents)}...")
            
            # Get embedding from Bedrock Titan
            embedding = self._get_embedding(doc['content'])
            if embedding is not None:
                embeddings_list.append(embedding)
            else:
                # Fallback: zero vector
                embeddings_list.append(np.zeros(1024))
        
        # Convert to numpy array
        self.embeddings = np.array(embeddings_list).astype('float32')
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)
        
        print(f"\n✓ Created FAISS index with {len(self.documents)} vectors\n")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding from Bedrock Titan Embeddings"""
        try:
            request_body = json.dumps({"inputText": text[:8000]})  # Limit text length
            
            response = self.bedrock.invoke_model(
                modelId="amazon.titan-embed-text-v2:0",
                body=request_body
            )
            
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')
            
            # Track cost
            tokens = len(text.split())  # Rough estimate
            cost = (tokens / 1000) * self.embedding_cost_per_1k_tokens
            self.estimated_cost += cost
            
            return np.array(embedding)
            
        except Exception as e:
            if self.demo_mode:
                print(f"⚠️  Embedding error: {str(e)}")
            return None
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        if self.index is None:
            print("❌ Index not created. Run create_embeddings() first.")
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return []
        
        # Search FAISS index
        query_vector = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_vector, top_k)
        
        # Return relevant documents
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        
        return results
    
    def answer_question(self, question: str) -> Dict:
        """Answer a question using RAG"""
        print(f"❓ Question: {question}\n")
        
        # Search for relevant context
        relevant_docs = self.search(question, top_k=5)
        
        if not relevant_docs:
            return {
                'question': question,
                'answer': "I couldn't find relevant information to answer that question.",
                'sources': []
            }
        
        # Build context from relevant documents
        context_parts = []
        sources = []
        
        for i, doc in enumerate(relevant_docs, 1):
            context_parts.append(f"[{i}] {doc['content']}")
            
            # Extract URL and title from metadata
            metadata = doc['metadata']
            source_url = metadata.get('url', '')
            source_title = metadata.get('title', '') or metadata.get('project_name', '') or 'Source'
            source_type = doc['source']
            
            sources.append({
                'source': source_type,
                'title': source_title,
                'url': source_url,
                'metadata': metadata
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer with Nova 2 Lite
        prompt = f"""You are a helpful assistant for CityPulse, a neighborhood intelligence platform for Mumbai.

Answer the following question based ONLY on the provided context. Be informative and include ALL relevant details from the context.

Context:
{context}

Question: {question}

Instructions:
- Provide a comprehensive answer covering ALL relevant information from the context
- When multiple items are mentioned (permits, alerts, topics), list ALL of them with their details
- Cite sources using [1], [2], etc. when referencing specific information
- Be specific with project names, locations, promoters, and other details
- Use plain text only - NO markdown, NO bold, NO bullet points, NO special formatting
- Write in natural, conversational sentences
- If asked about permits, mention ALL permits with their project names, locations, and promoters
- Keep the response clear and well-organized in paragraph form

Answer:"""

        try:
            request_body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"max_new_tokens": 600, "temperature": 0.3}
            }
            
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-lite-v1:0",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            answer = response_body['output']['message']['content'][0]['text']
            
            # Track usage
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            
            self.tokens_used += (input_tokens + output_tokens)
            cost = ((input_tokens / 1000) * self.lite_cost_per_1k_input +
                   (output_tokens / 1000) * self.lite_cost_per_1k_output)
            self.estimated_cost += cost
            
            if self.demo_mode:
                print(f"💰 Tokens: {input_tokens + output_tokens}, Cost: ${cost:.6f}\n")
            
            return {
                'question': question,
                'answer': answer,
                'sources': sources,
                'cost': cost
            }
            
        except Exception as e:
            print(f"❌ Error generating answer: {str(e)}")
            return {
                'question': question,
                'answer': f"Error: {str(e)}",
                'sources': sources
            }
    
    def save_qa_results(self, qa_results: List[Dict], filename: str = "data/rag_qa_results.json"):
        """Save Q&A results"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(qa_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved Q&A results to {filepath}")
        print(f"💰 Total cost: ${self.estimated_cost:.4f}\n")
        
        # Log cost
        log_cost(
            agent_name='rag_qa_system',
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model='Nova 2 Lite + Titan Embeddings',
            operation='rag_qa',
            num_questions=len(qa_results),
            num_documents=len(self.documents)
        )


def main():
    """Main execution - Demo Q&A"""
    print("="*80)
    print("🔍 CityPulse RAG Q&A System - Powered by Amazon Bedrock")
    print("="*80)
    print()
    
    # Initialize RAG system
    rag = CityPulseRAG(demo_mode=True)
    
    # Load all data
    rag.load_all_data()
    
    # Create embeddings
    print("💡 This will create embeddings for all documents (~$3-5)")
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    rag.create_embeddings()
    
    # Demo questions
    demo_questions = [
        "What construction projects are happening in Andheri?",
        "Are there any safety concerns in Mumbai?",
        "What new restaurants or businesses are opening?",
        "What are people discussing on social media about Mumbai?",
        "What investment opportunities are there in different neighborhoods?",
        "Tell me about recent permits filed in Mumbai",
        "What are the trending topics in the community?",
        "Are there any road closures or traffic issues?"
    ]
    
    print("\n" + "="*80)
    print("📝 Demo Questions")
    print("="*80)
    for i, q in enumerate(demo_questions, 1):
        print(f"{i}. {q}")
    print()
    
    # Ask questions
    qa_results = []
    
    for question in demo_questions[:5]:  # Limit to 5 for cost control
        print("="*80)
        result = rag.answer_question(question)
        qa_results.append(result)
        
        print(f"💬 Answer: {result['answer']}\n")
        print(f"📚 Sources: {len(result['sources'])} documents\n")
    
    # Save results
    rag.save_qa_results(qa_results)
    
    print("="*80)
    print("✅ RAG Q&A Demo Complete!")
    print("="*80)
    print()
    print(f"💰 Total Cost: ${rag.estimated_cost:.4f}")
    print(f"📊 Documents Indexed: {len(rag.documents)}")
    print(f"❓ Questions Answered: {len(qa_results)}")


if __name__ == "__main__":
    main()
