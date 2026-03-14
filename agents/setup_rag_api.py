# -*- coding: utf-8 -*-
"""
Setup script for RAG API
Run this ONCE to create embeddings cache
Then rag_api.py will be fast (~1-2 seconds per query)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rag_api import CityPulseRAG, save_embeddings

def main():
    print("="*80)
    print("🔧 Setting up RAG API")
    print("="*80)
    print()
    print("This will create embeddings cache for fast API responses")
    print("Cost: ~$3-5 (one-time)")
    print()
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    # Initialize and create embeddings
    rag = CityPulseRAG(demo_mode=True)
    rag.load_all_data()
    rag.create_embeddings()
    
    # Save to cache
    save_embeddings(rag)
    
    print()
    print("="*80)
    print("✅ Setup Complete!")
    print("="*80)
    print()
    print("Now you can use the API:")
    print('  python agents/rag_api.py "What is happening in Andheri?"')
    print()
    print("Responses will be fast (~1-2 seconds)")

if __name__ == "__main__":
    main()
