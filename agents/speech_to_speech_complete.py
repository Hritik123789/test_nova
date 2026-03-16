# -*- coding: utf-8 -*-
"""
Complete Speech-to-Speech Agent for CityPulse
Audio Input → Transcription → AI Response → Audio Output
Uses: Amazon Transcribe + Nova 2 Lite + Amazon Polly Neural TTS

Note: Requires S3 bucket for Transcribe. Set environment variable:
export S3_BUCKET=your-bucket-name
"""

import json
import os
import sys
import time
from datetime import datetime
import tempfile
import urllib.request

import boto3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_json_data, save_json_data, log_cost


class CompleteSpeechAgent:
    """Complete speech-to-speech pipeline for CityPulse"""

    def __init__(self):
        print("="*70)
        print("  COMPLETE SPEECH-TO-SPEECH AGENT - CityPulse")
        print("="*70)
        print("\nInitializing services...")
        
        self.tokens_used = 0
        self.estimated_cost = 0.0
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize AWS clients
        self.transcribe = boto3.client('transcribe', region_name=self.region)
        self.s3 = boto3.client('s3', region_name=self.region)
        self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
        self.polly = boto3.client('polly', region_name=self.region)
        
        # S3 bucket for transcription (Transcribe requires S3)
        self.bucket_name = os.getenv('S3_BUCKET', 'citypulse-audio-temp')
        
        # Verify S3 bucket exists
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            print(f"✓ S3 Bucket: {self.bucket_name}")
        except:
            print(f"⚠️  S3 Bucket '{self.bucket_name}' not found!")
            print(f"   Create it with: aws s3 mb s3://{self.bucket_name}")
            print(f"   Or set S3_BUCKET environment variable")
        
        print("✓ Amazon Transcribe")
        print("✓ Amazon Bedrock (Nova 2 Lite)")
        print("✓ Amazon Polly (Neural TTS)")
        print()

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using Amazon Transcribe
        Supports: MP3, MP4, WAV, FLAC, OGG, AMR, WebM
        """
        print(f"Step 1: Transcribing audio file...")
        print(f"  File: {audio_file_path}")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Upload to S3 (required for Transcribe)
        file_name = os.path.basename(audio_file_path)
        timestamp = int(time.time())
        s3_key = f"transcribe-input/{timestamp}_{file_name}"
        
        try:
            print(f"  Uploading to S3...")
            self.s3.upload_file(audio_file_path, self.bucket_name, s3_key)
            s3_uri = f"s3://{self.bucket_name}/{s3_key}"
            print(f"  ✓ Uploaded: {s3_uri}")
        except Exception as e:
            print(f"  ❌ S3 upload failed: {e}")
            print(f"  Note: Make sure bucket '{self.bucket_name}' exists")
            raise
        
        # Start transcription job
        job_name = f"citypulse-{timestamp}"
        
        try:
            print(f"  Starting transcription job: {job_name}")
            
            # Detect file format
            file_ext = file_name.split('.')[-1].lower()
            if file_ext == 'mp3':
                media_format = 'mp3'
            elif file_ext == 'mp4':
                media_format = 'mp4'
            elif file_ext == 'wav':
                media_format = 'wav'
            elif file_ext == 'flac':
                media_format = 'flac'
            elif file_ext == 'ogg':
                media_format = 'ogg'
            elif file_ext == 'webm':
                media_format = 'webm'
            else:
                media_format = 'mp3'  # default
            
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': s3_uri},
                MediaFormat=media_format,
                LanguageCode='en-US'
            )
            
            # Wait for completion
            print(f"  Waiting for transcription...")
            max_wait = 60  # 60 seconds timeout
            wait_time = 0
            
            while wait_time < max_wait:
                status = self.transcribe.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status == 'COMPLETED':
                    transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    
                    # Download transcript
                    with urllib.request.urlopen(transcript_uri) as response:
                        transcript_data = json.loads(response.read())
                    
                    transcript_text = transcript_data['results']['transcripts'][0]['transcript']
                    
                    # Estimate cost (Amazon Transcribe: $0.024 per minute)
                    # Assuming average 1 minute audio
                    transcribe_cost = 0.024
                    self.estimated_cost += transcribe_cost
                    
                    print(f"  ✓ Transcription complete")
                    print(f"  Text: \"{transcript_text}\"")
                    print(f"  Cost: ${transcribe_cost:.4f}")
                    print()
                    
                    # Cleanup
                    try:
                        self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                        self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
                    except:
                        pass  # Ignore cleanup errors
                    
                    return transcript_text
                    
                elif job_status == 'FAILED':
                    failure_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown')
                    raise Exception(f"Transcription job failed: {failure_reason}")
                
                time.sleep(2)
                wait_time += 2
            
            raise Exception("Transcription timeout")
                
        except Exception as e:
            print(f"  ❌ Transcription failed: {e}")
            # Cleanup on error
            try:
                self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            except:
                pass
            raise

    def get_ai_response(self, question: str) -> str:
        """Get AI response using Nova 2 Lite with CityPulse context"""
        print(f"Step 2: Getting AI response...")
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
        print(f"Step 3: Converting to speech...")
        
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

    def process_audio_to_audio(self, input_audio_path: str) -> dict:
        """
        Complete pipeline: Audio Input → Text → AI Response → Audio Output
        """
        print("\n" + "="*70)
        print("  PROCESSING AUDIO-TO-AUDIO")
        print("="*70 + "\n")
        
        start_time = time.time()
        
        try:
            # Step 1: Transcribe audio to text
            question = self.transcribe_audio(input_audio_path)
            
            # Step 2: Get AI response
            answer = self.get_ai_response(question)
            
            # Step 3: Convert answer to speech
            output_audio = self.text_to_speech(answer)
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Save result
            result = {
                "input_audio": input_audio_path,
                "transcribed_question": question,
                "ai_answer": answer,
                "output_audio": output_audio,
                "processing_time_seconds": round(total_time, 2),
                "total_cost": round(self.estimated_cost, 6),
                "timestamp": datetime.now().isoformat(),
                "services_used": {
                    "transcription": "Amazon Transcribe",
                    "ai_model": "Amazon Nova 2 Lite",
                    "text_to_speech": "Amazon Polly Neural TTS"
                }
            }
            
            save_json_data('complete_speech_result.json', result)
            
            # Log cost
            log_cost(
                agent_name="complete_speech",
                tokens_used=self.tokens_used,
                estimated_cost=self.estimated_cost,
                model="Transcribe + Nova 2 Lite + Polly Neural",
                operation="audio_to_audio"
            )
            
            print("="*70)
            print("  ✅ AUDIO-TO-AUDIO COMPLETE")
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
    """Test the complete speech agent"""
    
    # Check if test audio file exists
    test_audio = "test_audio.mp3"
    
    if not os.path.exists(test_audio):
        print("\n⚠️  No test audio file found!")
        print(f"Creating test audio file...")
        
        # Create test audio using Polly
        try:
            polly = boto3.client('polly', region_name='us-east-1')
            response = polly.synthesize_speech(
                Text="What are the trending topics in Mumbai right now?",
                OutputFormat='mp3',
                VoiceId='Joanna',
                Engine='neural'
            )
            
            with open(test_audio, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            print(f"✓ Test audio created: {test_audio}")
        except Exception as e:
            print(f"❌ Failed to create test audio: {e}")
            return
    
    try:
        agent = CompleteSpeechAgent()
        result = agent.process_audio_to_audio(test_audio)
        
        if result:
            print("✅ Test completed successfully!")
            print(f"📁 Result saved to: data/complete_speech_result.json")
            print(f"🎧 Output audio: {result['output_audio']}")
            print("\nYou can play the output audio file to hear the AI response!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
