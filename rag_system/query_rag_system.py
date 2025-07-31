#!/usr/bin/env python3
"""
Legal RAG Query System
Interactive query interface for searching Turkish legal documents
"""

import numpy as np
import pandas as pd
import json
import pickle
import openai
import os
from typing import List, Dict, Tuple
import glob
from sklearn.metrics.pairwise import cosine_similarity

class LegalRAGQuerySystem:
    def __init__(self):
        """Initialize the query system with latest embeddings"""
        self.chunks = None
        self.embeddings = None
        self.chunk_metadata = None
        self.load_latest_embeddings()
        
    def load_latest_embeddings(self):
        """Load the most recent embedding files"""
        print("🔄 Loading embeddings...")
        
        # Find the latest embedding files
        embedding_files = glob.glob("embeddings_output/legal_embeddings_*.npy")
        chunk_files = glob.glob("embeddings_output/legal_chunks_*.json")
        
        if not embedding_files or not chunk_files:
            raise FileNotFoundError("No embedding files found. Please run create_embeddings.py first.")
        
        # Get the latest files (sorted by timestamp in filename)
        latest_embedding_file = sorted(embedding_files)[-1]
        latest_chunk_file = sorted(chunk_files)[-1]
        
        print(f"📂 Loading embeddings from: {latest_embedding_file}")
        print(f"📂 Loading chunks from: {latest_chunk_file}")
        
        # Load embeddings
        self.embeddings = np.load(latest_embedding_file)
        
        # Load chunks
        with open(latest_chunk_file, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        print(f"✅ Loaded {len(self.chunks)} chunks with {self.embeddings.shape[1]}-dimensional embeddings")
        
    def get_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for user query"""
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"❌ Error generating query embedding: {e}")
            return None
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant legal chunks"""
        print(f"🔍 Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.get_query_embedding(query)
        if query_embedding is None:
            return []
        
        # Calculate similarities
        query_embedding = query_embedding.reshape(1, -1)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            chunk = self.chunks[idx]
            similarity = similarities[idx]
            
            result = {
                'rank': i + 1,
                'similarity': float(similarity),
                'law_name': chunk.get('law_name', 'Unknown'),
                'law_type': chunk.get('law_type', 'Unknown'),
                'chunk_text': chunk.get('text', ''),
                'full_metadata': chunk
            }
            results.append(result)
        
        return results
    
    def display_results(self, results: List[Dict]):
        """Display search results in a nice format"""
        if not results:
            print("❌ No results found.")
            return
        
        print(f"\n📋 Found {len(results)} relevant results:\n")
        
        for result in results:
            print(f"🏛️ **{result['rank']}. {result['law_name']}**")
            print(f"📂 Type: {result['law_type']}")
            print(f"🎯 Similarity: {result['similarity']:.3f}")
            
            # Show preview of text (first 200 characters for better readability with 10 results)
            text_preview = result['chunk_text'][:200]
            if len(result['chunk_text']) > 200:
                text_preview += "..."
            
            print(f"📝 Content: {text_preview}")
            print("-" * 80)
    
    def interactive_search(self):
        """Interactive search loop"""
        print("🏛️ Legal RAG Search System")
        print("=" * 50)
        print("Enter your legal questions in Turkish or English")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                query = input("🔍 Your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                results = self.search(query, top_k=10)
                self.display_results(results)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    try:
        # Initialize system
        rag_system = LegalRAGQuerySystem()
        
        # Start interactive search
        rag_system.interactive_search()
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        print("\nMake sure you have:")
        print("1. Generated embeddings (run create_embeddings.py)")
        print("2. Set OPENAI_API_KEY environment variable")

if __name__ == "__main__":
    main() 