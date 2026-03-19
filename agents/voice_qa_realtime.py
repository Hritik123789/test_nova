# -*- coding: utf-8 -*-
"""
Real-Time Voice Q&A System
Enables voice-based interaction with CityPulse data
Uses Nova 2 Lite for Q&A + Amazon Polly Neural TTS for voice
"""

import json
import os
import sys
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import boto3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_json_data, save_json_data, log_cost


class VoiceQASystem:
    """Real-time voice Q&A using Nova 2 Lite + Amazon Polly Neural TTS"""

    def __init__(self):
        print("Initializing Voice Q&A System...\n")
        self.tokens_used = 0
        self.estimated_cost = 0.0

        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.polly = boto3.client(
            service_name='polly',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        print("Connected to Bedrock + Polly\n")

    def load_citypulse_data(self):
        """Load all CityPulse data for context"""
        print("Loading CityPulse data...")
        data = {
            'news': load_json_data('news.json', default=[]),
            'social': load_json_data('social.json', default=[]),
            'permits': load_json_data('permits.json', default=[]),
            'safety_alerts': load_json_data('safety_alerts.json', default={}),
            'investment_insights': load_json_data('investment_insights.json', default={}),
            'community_pulse': load_json_data('community_pulse.json', default={})
        }
        print(f"  Loaded {len(data)} data sources\n")
        return data

    def _build_context(self, data: dict) -> str:
        """Build a concise context string from loaded data"""
        parts = []

        news = data.get('news', [])
        if isinstance(news, list) and news:
            parts.append(f"- {len(news)} recent Mumbai news articles")

        social = data.get('social', [])
        if isinstance(social, list) and social:
            parts.append(f"- {len(social)} social media posts from Mumbai residents")

        permits = data.get('permits', [])
        if isinstance(permits, list) and permits:
            parts.append(f"- {len(permits)} building permits on record")

        safety = data.get('safety_alerts', {})
        alerts = safety.get('alerts', []) if isinstance(safety, dict) else []
        if alerts:
            parts.append(f"- {len(alerts)} active safety alerts")

        pulse = data.get('community_pulse', {})
        topics = pulse.get('insights', {}).get('trending_topics', []) if isinstance(pulse, dict) else []
        if topics:
            topic_names = [t.get('topic', '') for t in topics[:3]]
            parts.append(f"- Trending topics: {', '.join(topic_names)}")

        investment = data.get('investment_insights', {})
        neighborhoods = investment.get('insights', {}).get('trending_neighborhoods', []) if isinstance(investment, dict) else []
        if neighborhoods:
            parts.append(f"- {len(neighborhoods)} investment neighborhoods analyzed")

        return "\n".join(parts) if parts else "- Limited data available"

    def answer_question(self, question: str, context_data: dict) -> str:
        """Answer a question using Nova 2 Lite with CityPulse context"""
        print(f"Processing: '{question}'")

        context = self._build_context(context_data)

        prompt = f"""You are a helpful AI assistant for CityPulse, a civic intelligence platform for Mumbai.

Available data:
{context}

User question: {question}

Answer in 2-3 clear sentences. Be specific and helpful. If data is unavailable, say so briefly."""

        try:
            response = self.bedrock.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 200, "temperature": 0.7}
                })
            )

            body = json.loads(response['body'].read())
            answer = body['output']['message']['content'][0]['text'].strip()

            usage = body.get('usage', {})
            self.tokens_used += usage.get('inputTokens', 0) + usage.get('outputTokens', 0)
            self.estimated_cost += (
                (usage.get('inputTokens', 0) / 1000) * 0.00006 +
                (usage.get('outputTokens', 0) / 1000) * 0.00024
            )

            print(f"Answer generated\n")
            return answer

        except Exception as e:
            print(f"Q&A failed: {e}\n")
            return "Sorry, I couldn't process your question right now."

    def text_to_speech(self, text: str, output_file: str = "voice_response.mp3") -> str:
        """Convert text to speech using Amazon Polly Neural TTS"""
        print(f"Generating voice with Amazon Polly Neural TTS...")

        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Matthew',
                Engine='neural'
            )

            audio_data = response['AudioStream'].read()

            output_path = os.path.join('data', output_file)
            with open(output_path, 'wb') as f:
                f.write(audio_data)

            # Polly Neural: $16 per 1M characters
            self.estimated_cost += (len(text) / 1_000_000) * 16.00

            print(f"Audio saved: {output_path} ({len(audio_data) / 1024:.1f} KB)\n")
            return output_path

        except Exception as e:
            print(f"Polly TTS failed: {e}\n")
            return None

    def process_voice_query(self, question: str) -> dict:
        """Full pipeline: question -> answer -> voice"""
        context_data = self.load_citypulse_data()
        answer = self.answer_question(question, context_data)
        audio_file = self.text_to_speech(answer)

        result = {
            "question": question,
            "answer": answer,
            "audio_file": audio_file,
            "voice_engine": "Amazon Polly Neural TTS",
            "qa_engine": "Amazon Nova 2 Lite",
            "timestamp": datetime.now().isoformat(),
            "cost": self.estimated_cost
        }

        save_json_data('voice_qa_response.json', result)
        log_cost(
            agent_name="voice_qa_realtime",
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model="Nova 2 Lite + Amazon Polly Neural",
            operation="voice_qa"
        )

        return result


def main():
    print("="*70)
    print("  VOICE Q&A SYSTEM")
    print("="*70)
    print()

    questions = [
        "What are the trending topics in Mumbai right now?",
        "Are there any safety alerts I should know about?",
        "Which neighborhoods are good for investment?"
    ]

    try:
        qa = VoiceQASystem()

        for i, question in enumerate(questions, 1):
            print(f"Question {i}: '{question}'")
            print("-" * 70)
            result = qa.process_voice_query(question)

            print(f"Answer: {result['answer']}")
            if result['audio_file']:
                print(f"Audio: {result['audio_file']}")
            print(f"Cost so far: ${qa.estimated_cost:.6f}")
            print()

        print("="*70)
        print("Voice Q&A completed!")
        print(f"Total cost: ${qa.estimated_cost:.6f}")
        print(f"Voice engine: Amazon Polly Neural TTS")
        print(f"Q&A engine: Amazon Nova 2 Lite")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
