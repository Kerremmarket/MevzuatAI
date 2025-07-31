#!/usr/bin/env python3
"""
Test the Legal RAG system with sample queries
"""

from query_rag_system import LegalRAGQuerySystem

def test_sample_queries():
    """Test with some sample legal queries"""
    
    # Initialize the system
    print("🔄 Initializing Legal RAG System...")
    rag_system = LegalRAGQuerySystem()
    
    # Sample queries to test
    test_queries = [
        "çevre koruma",
        "işçi hakları",
        "vergi ödemeleri", 
        "cyber security",
        "iklim değişikliği",
        "ticaret kanunu",
        "What are the regulations about environmental protection?",
        "İş sözleşmesi feshi"
    ]
    
    print("\n🧪 Testing sample queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{'='*60}")
        print(f"🔍 TEST {i}: {query}")
        print(f"{'='*60}")
        
        results = rag_system.search(query, top_k=2)
        rag_system.display_results(results)
        
        print("\n")

if __name__ == "__main__":
    test_sample_queries() 