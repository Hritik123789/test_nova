# -*- coding: utf-8 -*-
"""
Image Analysis using Amazon Bedrock Nova 2 Omni
Analyzes construction site images, permit documents, etc.
"""

import json
import os
import sys
import boto3
import base64
from datetime import datetime
from typing import Dict

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class ImageAnalyzer:
    """Image analyzer using Nova 2 Omni (Multimodal)"""
    
    def __init__(self, demo_mode: bool = True):
        """Initialize with Nova 2 Omni"""
        print("🖼️  Initializing Image Analyzer (Amazon Nova 2 Omni)...\n")
        
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
        self.cost_per_1k_input_tokens = 0.0006  # Nova 2 Omni
        self.cost_per_1k_output_tokens = 0.0048
    
    def load_image(self, image_path: str) -> str:
        """Load and encode image to base64"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"❌ Failed to load image: {str(e)}")
            return ""
    
    def analyze_construction_site(self, image_path: str) -> Dict:
        """Analyze construction site image"""
        
        print(f"🔍 Analyzing image: {image_path}...\n")
        
        # Load image
        image_base64 = self.load_image(image_path)
        if not image_base64:
            return {}
        
        # Detect image format from file extension
        image_format = "jpeg" if image_path.lower().endswith(('.jpg', '.jpeg')) else "png"
        
        prompt = """Analyze this construction site image for Mumbai civic monitoring:

1. What type of construction is visible? (Building, Road, Infrastructure, etc.)
2. Is there visible signage showing permits or project details?
3. Are there any safety concerns visible?
4. Estimate the project scale (Small, Medium, Large)
5. Any visible violations or issues?

Provide a structured analysis."""

        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": {
                                    "format": image_format,
                                    "source": {
                                        "bytes": image_base64
                                    }
                                }
                            },
                            {"text": prompt}
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 400,
                    "temperature": 0.5
                }
            }
            
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-pro-v1:0",  # Nova 2 Omni
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            analysis = response_body['output']['message']['content'][0]['text']
            
            # Track usage
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            
            self.tokens_used += (input_tokens + output_tokens)
            cost = ((input_tokens / 1000) * self.cost_per_1k_input_tokens +
                   (output_tokens / 1000) * self.cost_per_1k_output_tokens)
            self.estimated_cost += cost
            
            if self.demo_mode:
                print(f"💰 Tokens: {input_tokens + output_tokens}, Cost: ${cost:.6f}\n")
            
            return {
                'image_path': image_path,
                'analysis': analysis,
                'analyzed_at': datetime.now().isoformat(),
                'analyzed_by': 'Amazon Nova 2 Omni',
                'tokens_used': input_tokens + output_tokens,
                'cost': cost
            }
            
        except Exception as e:
            print(f"❌ Nova API error: {str(e)}")
            return {}
    
    def analyze_permit_document(self, image_path: str) -> Dict:
        """Analyze permit document image"""
        
        print(f"📄 Analyzing permit document: {image_path}...\n")
        
        # Load image
        image_base64 = self.load_image(image_path)
        if not image_base64:
            return {}
        
        # Detect image format from file extension
        image_format = "jpeg" if image_path.lower().endswith(('.jpg', '.jpeg')) else "png"
        
        prompt = """Extract information from this permit document:

1. Permit number (if visible)
2. Project name/location
3. Permit type (Construction, Demolition, etc.)
4. Issue date and expiry date
5. Issuing authority
6. Any special conditions or notes

Extract all visible text and structure it."""

        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": {
                                    "format": image_format,
                                    "source": {
                                        "bytes": image_base64
                                    }
                                }
                            },
                            {"text": prompt}
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 400,
                    "temperature": 0.3
                }
            }
            
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-pro-v1:0",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            analysis = response_body['output']['message']['content'][0]['text']
            
            # Track usage
            usage = response_body.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            
            self.tokens_used += (input_tokens + output_tokens)
            cost = ((input_tokens / 1000) * self.cost_per_1k_input_tokens +
                   (output_tokens / 1000) * self.cost_per_1k_output_tokens)
            self.estimated_cost += cost
            
            if self.demo_mode:
                print(f"💰 Tokens: {input_tokens + output_tokens}, Cost: ${cost:.6f}\n")
            
            return {
                'image_path': image_path,
                'analysis': analysis,
                'analyzed_at': datetime.now().isoformat(),
                'analyzed_by': 'Amazon Nova 2 Omni',
                'tokens_used': input_tokens + output_tokens,
                'cost': cost
            }
            
        except Exception as e:
            print(f"❌ Nova API error: {str(e)}")
            return {}
    
    def save_analysis(self, results: list, filename: str = "image_analysis_results.json"):
        """Save analysis results"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved analysis to {filename}")
        print(f"💰 Total cost: ${self.estimated_cost:.4f}")
        
        # Log cost
        self.log_cost(len(results))
    
    def log_cost(self, num_images: int):
        """Log cost for tracking"""
        # Add parent directory to path for utils import
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import log_cost
        log_cost(
            agent_name='image_analysis',
            tokens_used=self.tokens_used,
            estimated_cost=self.estimated_cost,
            model='Amazon Nova 2 Omni',
            operation='image_analysis',
            images_analyzed=num_images
        )


def main():
    """Main execution - DEMO MODE"""
    print("="*80)
    print("🖼️  Image Analysis - Powered by Amazon Nova 2 Omni")
    print("="*80)
    print()
    
    # Initialize
    analyzer = ImageAnalyzer(demo_mode=True)
    
    # Demo: Analyze sample images
    print("💡 DEMO MODE: This script analyzes construction site and permit images")
    print("💡 Place images in 'sample_images/' folder to test\n")
    
    # Check for sample images
    sample_dir = "sample_images"
    if not os.path.exists(sample_dir):
        print(f"⚠️  '{sample_dir}/' folder not found")
        print(f"💡 Create it and add images to analyze")
        print(f"💡 Supported: .jpg, .jpeg, .png\n")
        
        # Create sample directory
        os.makedirs(sample_dir, exist_ok=True)
        print(f"✓ Created '{sample_dir}/' folder")
        print(f"💡 Add images and run again\n")
        return
    
    # Find images
    image_files = [f for f in os.listdir(sample_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print(f"⚠️  No images found in '{sample_dir}/'")
        print(f"💡 Add .jpg or .png images and run again\n")
        return
    
    print(f"📸 Found {len(image_files)} images to analyze\n")
    
    results = []
    for image_file in image_files[:5]:  # Limit to 5 images for cost control
        image_path = os.path.join(sample_dir, image_file)
        
        # Analyze based on filename hint
        if 'permit' in image_file.lower() or 'document' in image_file.lower():
            result = analyzer.analyze_permit_document(image_path)
        else:
            result = analyzer.analyze_construction_site(image_path)
        
        if result:
            results.append(result)
            print("="*80)
            print(f"📊 Analysis for {image_file}:")
            print("="*80)
            print(result['analysis'])
            print("="*80)
            print()
    
    # Save results
    if results:
        analyzer.save_analysis(results)
        print("\n✅ Image analysis complete!")
    else:
        print("❌ No images analyzed")


if __name__ == "__main__":
    main()
