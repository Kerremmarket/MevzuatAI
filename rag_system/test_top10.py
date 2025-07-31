#!/usr/bin/env python3
"""
Test the Legal RAG system with top 10 results
"""

from query_rag_system import LegalRAGQuerySystem

def test_top10_results():
    """Test showing top 10 results for a query"""
    
    print("🔄 Initializing Legal RAG System...")
    rag_system = LegalRAGQuerySystem()
    
    # Test query
    query = "çevre koruma"
    print(f"\n🔍 Testing query: '{query}' - Top 10 Results\n")
    print("=" * 80)
    
    results = rag_system.search(query, top_k=10)
    rag_system.display_results(results)

if __name__ == "__main__":
    test_top10_results() 