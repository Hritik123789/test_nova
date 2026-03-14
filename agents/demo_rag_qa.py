# -*- coding: utf-8 -*-
"""
Quick RAG Q&A Demo
Interactive demo for testing the RAG system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rag_qa_system import CityPulseRAG


def main():
    """Interactive Q&A demo"""
    print("="*80)
    print("🔍 CityPulse RAG Q&A - Interactive Demo")
    print("="*80)
    print()
    
    # Initialize
    rag = CityPulseRAG(demo_mode=True)
    
    # Load data
    rag.load_all_data()
    
    # Create embeddings
    print("💡 Creating embeddings (one-time cost: ~$3-5)...")
    print("   This indexes all your neighborhood data for search\n")
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    rag.create_embeddings()
    
    # Interactive Q&A
    print("\n" + "="*80)
    print("💬 Ask questions about your neighborhood!")
    print("="*80)
    print("Examples:")
    print("  - What's happening in Andheri?")
    print("  - Are there safety concerns?")
    print("  - What new businesses are opening?")
    print("  - Tell me about recent permits")
    print()
    print("Type 'quit' to exit\n")
    
    qa_results = []
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        print()
        result = rag.answer_question(question)
        print(f"💬 {result['answer']}\n")
        print(f"📚 Based on {len(result['sources'])} sources\n")
        
        qa_results.append(result)
    
    # Save results
    if qa_results:
        rag.save_qa_results(qa_results)
        print(f"\n✅ Answered {len(qa_results)} questions")
        print(f"💰 Total cost: ${rag.estimated_cost:.4f}")


if __name__ == "__main__":
    main()
