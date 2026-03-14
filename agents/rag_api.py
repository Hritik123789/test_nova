# -*- coding: utf-8 -*-
"""
Fast API wrapper for RAG Q&A
Loads pre-built embeddings for instant responses
Your friend can call this from Laravel/Next.js
"""

import sys
import json
import os
import pickle
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rag_qa_system import CityPulseRAG

# Cache file paths
CACHE_DIR = os.path.join(os.path.dirname(__file__), '.rag_cache')
EMBEDDINGS_FILE = os.path.join(CACHE_DIR, 'embeddings.pkl')
DOCUMENTS_FILE = os.path.join(CACHE_DIR, 'documents.pkl')

def save_embeddings(rag: CityPulseRAG):
    """Save embeddings and documents to cache"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(rag.embeddings, f)
    
    with open(DOCUMENTS_FILE, 'wb') as f:
        pickle.dump(rag.documents, f)
    
    print(f"✓ Cached embeddings to {CACHE_DIR}", file=sys.stderr)

def load_embeddings(rag: CityPulseRAG) -> bool:
    """Load embeddings and documents from cache"""
    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(DOCUMENTS_FILE):
        return False
    
    try:
        with open(EMBEDDINGS_FILE, 'rb') as f:
            rag.embeddings = pickle.load(f)
        
        with open(DOCUMENTS_FILE, 'rb') as f:
            rag.documents = pickle.load(f)
        
        # Recreate FAISS index
        try:
            import faiss
            dimension = rag.embeddings.shape[1]
            rag.index = faiss.IndexFlatL2(dimension)
            rag.index.add(rag.embeddings)
            return True
        except ImportError:
            return False
            
    except Exception as e:
        print(f"⚠️  Cache load failed: {e}", file=sys.stderr)
        return False

def answer_question(question: str) -> dict:
    """
    Answer a single question using cached embeddings
    Usage: python agents/rag_api.py "What's happening in Andheri?"
    """
    # Initialize RAG
    rag = CityPulseRAG(demo_mode=False)
    
    # Try to load from cache
    if load_embeddings(rag):
        print("✓ Loaded embeddings from cache", file=sys.stderr)
    else:
        print("⚠️  No cache found, creating embeddings...", file=sys.stderr)
        rag.load_all_data()
        rag.create_embeddings()
        save_embeddings(rag)
    
    # Answer question
    result = rag.answer_question(question)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No question provided"}))
        sys.exit(1)
    
    question = sys.argv[1]
    result = answer_question(question)
    
    # Output JSON for Laravel to parse
    print(json.dumps(result, ensure_ascii=False))
