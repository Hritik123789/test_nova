# -*- coding: utf-8 -*-
"""
Simplified Speech-to-Speech Agent for CityPulse
Uses: Amazon Polly for TTS + Nova 2 Lite for AI
Note: This version skips transcription and works with text input only
For full speech-to-speech, use speech_to_speech_nova.py
"""

import json
import os
import sys
import time
from datetime import datetime

import boto3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_json_data, save_json_data, log_cost


class SimpleSpeechAgent:
    """Simplified speech agent - text input to audio output"""

    def __init__(self):
        print("="*70)
        print("  SIMPLE SPEECH AGENT - CityPulse")
        print("="*70)
        print("\nInitializing services...")
        
        self.tokens_used = 0
        self.estimated_cost = 0.0
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize AWS clients
        self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
        self.polly = boto3.client('polly', region_name=self.region)
        
        print("✓ Amazon Bedrock (Nova 2 Lite)")
        print("✓ Amazon Polly (Neural TTS)")
        print()

    def get_ai_response(self, question: str) -> str:
        """Get AI response using Nova 2 Lite with CityPulse context"""
        print(f"Step 1: Getting AI response...")
        print(f"  Question: \"{question}\"")
        
        # Load CityPulse data for context
        context_data = {
            'news': load_json_data('news.json', default=[]),
            'social': load_json_data('social.json', default=[]),
            'permits': load_json_data('permits.json', default=[]),
            'smart_alerts': load_json_data('smart_alerts.json', default={}),
            'safety_alerts': load_json_data('safety_alerts.json', default={}),
            'investment_insights': load_json_data('investment_insights.json', default={}),
            'community_pulse': load_json_data('community_pulse.json', default={})
        }
        
        # Build context summary
        context_parts = []
        if context_data.get('news'):
            context_parts.append(f"{len(context_data['news'])} news articles")
        if context_data.get('permits'):
            context_parts.append(f"{len(context_data['permits'])} building permits")
        if context_data.get('smart_alerts', {}).get('alerts'):
            context_parts.append(f"{len(context_data['smart_alerts']['alerts'])} active alerts")
        
        context_summary = ", ".join(context_parts) if context_parts else "limited data"
        
        prompt = f"""You are CityPulse AI, a helpful assistant for Mumbai civic information.

Available data: {context_summary}

User question: {question}

Provide a clear, concise answer in 2-3 sentences. Be conversational and helpful."""

        try:
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 200, "temperature": 0.7}
                })
            )

            body = json.loads(response['body'].read())
            answer = body['output']['message']['content'][0]['text'].strip()

            # Track usage
            usage = body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            self.tokens_used += input_tokens + output_tokens
            
            # Nova 2 Lite pricing
            nova_cost = (input_tokens / 1000) * 0.00006 + (output_tokens / 1000) * 0.00024
            self.estimated_cost += nova_cost

            print(f"  ✓ Response generated")
            print(f"  Answer: \"{answer}\"")
            print(f"  Tokens: {input_tokens + output_tokens}, Cost: ${nova_cost:.6f}")
            print()
            
            return answer

        except Exception as e:
            print(f"  ❌ AI response failed: {e}")
            return "Sorry, I couldn't process your question right now."

    def text_to_speech(self, text: str, output_file: str = None) -> str:
        """Convert text to speech using Amazon Polly Neural TTS"""
        print(f"Step 2: Converting to speech...")
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"speech_response_{timestamp}.mp3"
        
        output_path = os.path.join('data', output_file)

        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Matthew',  # Professional male voice
                Engine='neural'  # High-quality neural TTS
            )

            audio_data = response['AudioStream'].read()

            with open(output_path, 'wb') as f:
                f.write(audio_data)

            # Polly Neural: $16 per 1M characters
            polly_cost = (len(text) / 1_000_000) * 16.00
            self.estimated_cost += polly_cost

            print(f"  ✓ Audio generated")
            print(f"  File: {output_path} ({len(audio_data) / 1024:.1f} KB)")
            print(f"  Cost: ${polly_cost:.6f}")
            print()
            
            return output_path

        except Exception as e:
            print(f"  ❌ Text-to-speech failed: {e}")
            return None

    def process_text_to_speech(self, question: str) -> dict:
        """
        Process text question to speech answer
        """
        print("\n" + "="*70)
        print("  PROCESSING TEXT-TO-SPEECH")
        print("="*70 + "\n")
        
        start_time = time.time()
        
        try:
            # Step 1: Get AI response
            answer = self.get_ai_response(question)
            
            # Step 2: Convert answer to speech
            output_audio = self.text_to_speech(answer)
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Save result
            result = {
                "question": question,
                "ai_answer": answer,
                "output_audio": output_audio,
                "processing_time_seconds": round(total_time, 2),
                "total_cost": round(self.estimated_cost, 6),
                "timestamp": datetime.now().isoformat(),
                "services_used": {
                    "ai_model": "Amazon Nova 2 Lite",
                    "text_to_speech": "Amazon Polly Neural TTS"
                }
            }
            
            save_json_data('simple_speech_result.json', result)
            
            # Log cost
            log_cost(
                agent_name="simple_speech",
                tokens_used=self.tokens_used,
                estimated_cost=self.estimated_cost,
                model="Nova 2 Lite + Polly Neural",
                operation="text_to_speech"
            )
            
            print("="*70)
            print("  ✅ TEXT-TO-SPEECH COMPLETE")
            print("="*70)
            print(f"\n📊 Summary:")
            print(f"  Question: \"{question}\"")
            print(f"  Answer: \"{answer}\"")
            print(f"  Output Audio: {output_audio}")
            print(f"  Processing Time: {total_time:.2f}s")
            print(f"  Total Cost: ${self.estimated_cost:.6f}")
            print()
            
            return result
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Test the simple speech agent"""
    
    test_question = "What are the trending topics in Mumbai right now?"
    
    print(f"\nTest question: \"{test_question}\"\n")
    
    try:
        agent = SimpleSpeechAgent()
        result = agent.process_text_to_speech(test_question)
        
        if result:
            print("✅ Test completed successfully!")
            print(f"📁 Result saved to: data/simple_speech_result.json")
            print(f"🎧 Output audio: {result['output_audio']}")
            print("\nYou can play the audio file to hear the response!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
