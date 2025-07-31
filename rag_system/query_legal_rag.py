#!/usr/bin/env python3
"""
Legal RAG Query Interface
Simple command-line interface for querying the Legal RAG system
"""

import sqlite3
import pickle
import json
from datetime import datetime
from typing import List, Dict
import argparse

# Try to import the RAG class
try:
    from build_vector_database import LegalRAGDatabase
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False

class LegalRAGQuery:
    def __init__(self, db_path="mevzat_rag.db"):
        """Initialize query interface"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.check_database()
        
    def check_database(self):
        """Check if database exists and has data"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM chunks")
            chunk_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
            embedded_count = cursor.fetchone()[0]
            
            if chunk_count == 0:
                raise Exception("No chunks found in database. Please build the database first.")
            
            if embedded_count == 0:
                raise Exception("No embeddings found. Please generate embeddings first.")
                
            print(f"✅ Database ready: {chunk_count} chunks, {embedded_count} with embeddings")
            
        except sqlite3.OperationalError:
            raise Exception("Database not found or corrupted. Please build the database first.")
    
    def search_simple(self, query: str, top_k: int = 5) -> List[Dict]:
        """Simple text-based search using SQL LIKE"""
        cursor = self.conn.cursor()
        
        # Simple text search in chunks
        cursor.execute("""
            SELECT chunk_id, law_name, law_type, chunk_type, chunk_index, 
                   text, char_count, word_count
            FROM chunks 
            WHERE text LIKE ? 
            ORDER BY 
                CASE 
                    WHEN text LIKE ? THEN 1
                    WHEN text LIKE ? THEN 2
                    ELSE 3
                END
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"% {query} %", top_k))
        
        results = cursor.fetchall()
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                'chunk_id': result[0],
                'law_name': result[1],
                'law_type': result[2],
                'chunk_type': result[3],
                'chunk_index': result[4],
                'text': result[5][:500] + "..." if len(result[5]) > 500 else result[5],
                'char_count': result[6],
                'word_count': result[7],
                'search_type': 'text_similarity'
            })
        
        return formatted_results
    
    def get_law_types(self) -> List[str]:
        """Get available law types"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT law_type FROM chunks ORDER BY law_type")
        return [row[0] for row in cursor.fetchall()]
    
    def get_law_names(self, law_type: str = None) -> List[str]:
        """Get available law names, optionally filtered by type"""
        cursor = self.conn.cursor()
        
        if law_type:
            cursor.execute("SELECT DISTINCT law_name FROM chunks WHERE law_type = ? ORDER BY law_name", (law_type,))
        else:
            cursor.execute("SELECT DISTINCT law_name FROM chunks ORDER BY law_name")
            
        return [row[0] for row in cursor.fetchall()]
    
    def get_law_info(self, law_name: str) -> Dict:
        """Get detailed information about a specific law"""
        cursor = self.conn.cursor()
        
        # Get metadata
        cursor.execute("""
            SELECT law_id, law_name, law_type, sections, article_count, 
                   character_count, word_count, processing_date
            FROM laws_metadata 
            WHERE law_name = ?
        """, (law_name,))
        
        metadata = cursor.fetchone()
        
        # Get chunks count
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE law_name = ?", (law_name,))
        chunk_count = cursor.fetchone()[0]
        
        if metadata:
            return {
                'law_id': metadata[0],
                'law_name': metadata[1],
                'law_type': metadata[2],
                'sections': json.loads(metadata[3]) if metadata[3] else [],
                'article_count': metadata[4],
                'character_count': metadata[5],
                'word_count': metadata[6],
                'processing_date': metadata[7],
                'chunk_count': chunk_count
            }
        
        return None
    
    def search_by_law_type(self, law_type: str, limit: int = 10) -> List[Dict]:
        """Get chunks from a specific law type"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT chunk_id, law_name, law_type, chunk_type, chunk_index, 
                   text, char_count, word_count
            FROM chunks 
            WHERE law_type = ?
            ORDER BY law_name, chunk_index
            LIMIT ?
        """, (law_type, limit))
        
        results = cursor.fetchall()
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                'chunk_id': result[0],
                'law_name': result[1],
                'law_type': result[2],
                'chunk_type': result[3],
                'chunk_index': result[4],
                'text': result[5][:300] + "..." if len(result[5]) > 300 else result[5],
                'char_count': result[6],
                'word_count': result[7]
            })
        
        return formatted_results
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM chunks")
        stats['total_chunks'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM laws_metadata")
        stats['total_laws'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
        stats['chunks_with_embeddings'] = cursor.fetchone()[0]
        
        # Law type distribution
        cursor.execute("SELECT law_type, COUNT(*) FROM chunks GROUP BY law_type ORDER BY COUNT(*) DESC")
        stats['chunks_by_law_type'] = dict(cursor.fetchall())
        
        # Recent searches
        cursor.execute("SELECT COUNT(*) FROM search_logs")
        stats['total_searches'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT query, timestamp FROM search_logs 
            ORDER BY timestamp DESC LIMIT 5
        """)
        stats['recent_searches'] = cursor.fetchall()
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def interactive_mode():
    """Interactive command-line interface"""
    print("🏛️  Legal RAG Query Interface")
    print("=" * 50)
    
    try:
        query_system = LegalRAGQuery()
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Load vector database if available
    vector_db = None
    if VECTOR_DB_AVAILABLE:
        try:
            vector_db = LegalRAGDatabase("mevzat_rag.db")
            # Try to load embedding model info
            try:
                with open("model_info.json", 'r', encoding='utf-8') as f:
                    model_info = json.load(f)
                    print(f"📡 Vector search available with {model_info['embedding_type']}")
            except:
                print("📡 Vector search may be available (model info not found)")
        except:
            print("⚠️  Vector search not available, using text search only")
    
    while True:
        print("\n" + "="*50)
        print("Commands:")
        print("1. search <query>        - Search for content")
        print("2. vsearch <query>       - Vector search (if available)")
        print("3. types                 - List law types")
        print("4. laws [type]           - List laws (optionally by type)")
        print("5. info <law_name>       - Get law information")
        print("6. browse <law_type>     - Browse chunks by law type")
        print("7. stats                 - Show statistics")
        print("8. help                  - Show this help")
        print("9. exit                  - Exit program")
        
        command = input("\n🔍 Enter command: ").strip()
        
        if command.lower() in ['exit', 'quit', 'q']:
            break
        elif command.lower() in ['help', 'h']:
            continue
        elif command.startswith('search '):
            query = command[7:].strip()
            if query:
                print(f"\n📋 Text search results for: '{query}'")
                results = query_system.search_simple(query, top_k=5)
                
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result['law_name']} ({result['law_type']})")
                        print(f"   Text: {result['text']}")
                        print(f"   Chunk: {result['chunk_type']} #{result['chunk_index']}")
                else:
                    print("No results found.")
            else:
                print("Please provide a search query.")
                
        elif command.startswith('vsearch ') and vector_db:
            query = command[8:].strip()
            if query:
                print(f"\n🧠 Vector search results for: '{query}'")
                try:
                    results = vector_db.search(query, top_k=5)
                    
                    if results:
                        for i, result in enumerate(results, 1):
                            print(f"\n{i}. {result['law_name']} ({result['law_type']})")
                            print(f"   Similarity: {result['similarity_score']:.3f}")
                            print(f"   Text: {result['text'][:300]}...")
                            print(f"   Chunk: {result['chunk_type']} #{result['chunk_index']}")
                    else:
                        print("No results found.")
                except Exception as e:
                    print(f"Error in vector search: {e}")
            else:
                print("Please provide a search query.")
                
        elif command == 'types':
            law_types = query_system.get_law_types()
            print(f"\n📊 Available law types ({len(law_types)}):")
            for i, law_type in enumerate(law_types, 1):
                print(f"  {i}. {law_type}")
                
        elif command.startswith('laws'):
            parts = command.split(' ', 1)
            law_type = parts[1].strip() if len(parts) > 1 else None
            
            laws = query_system.get_law_names(law_type)
            type_text = f" of type '{law_type}'" if law_type else ""
            print(f"\n📜 Available laws{type_text} ({len(laws)}):")
            
            for i, law_name in enumerate(laws[:20], 1):  # Limit to first 20
                print(f"  {i}. {law_name}")
            
            if len(laws) > 20:
                print(f"  ... and {len(laws) - 20} more")
                
        elif command.startswith('info '):
            law_name = command[5:].strip()
            if law_name:
                info = query_system.get_law_info(law_name)
                if info:
                    print(f"\n📋 Law Information:")
                    print(f"  Name: {info['law_name']}")
                    print(f"  Type: {info['law_type']}")
                    print(f"  Articles: {info['article_count']}")
                    print(f"  Characters: {info['character_count']:,}")
                    print(f"  Words: {info['word_count']:,}")
                    print(f"  Chunks: {info['chunk_count']}")
                    if info['sections']:
                        print(f"  Sections: {', '.join(info['sections'][:5])}")
                else:
                    print("Law not found.")
            else:
                print("Please provide a law name.")
                
        elif command.startswith('browse '):
            law_type = command[7:].strip()
            if law_type:
                print(f"\n📖 Browsing '{law_type}' chunks:")
                results = query_system.search_by_law_type(law_type, limit=10)
                
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result['law_name']}")
                        print(f"   Text: {result['text']}")
                        print(f"   Chunk: {result['chunk_type']} #{result['chunk_index']}")
                else:
                    print("No chunks found for this law type.")
            else:
                print("Please provide a law type.")
                
        elif command == 'stats':
            stats = query_system.get_statistics()
            print(f"\n📊 Database Statistics:")
            print(f"  Total laws: {stats['total_laws']:,}")
            print(f"  Total chunks: {stats['total_chunks']:,}")
            print(f"  Chunks with embeddings: {stats['chunks_with_embeddings']:,}")
            print(f"  Total searches: {stats['total_searches']:,}")
            
            print(f"\n📈 Top Law Types by Chunk Count:")
            for law_type, count in list(stats['chunks_by_law_type'].items())[:5]:
                print(f"  {law_type}: {count:,} chunks")
                
            if stats['recent_searches']:
                print(f"\n🔍 Recent Searches:")
                for query, timestamp in stats['recent_searches']:
                    print(f"  '{query}' at {timestamp}")
        else:
            print("Unknown command. Type 'help' for available commands.")
    
    query_system.close()
    if vector_db:
        vector_db.close()
    print("\n👋 Goodbye!")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description="Legal RAG Query Interface")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Start interactive mode")
    parser.add_argument("--search", "-s", type=str, 
                       help="Perform a single search and exit")
    parser.add_argument("--stats", action="store_true",
                       help="Show statistics and exit")
    parser.add_argument("--top-k", type=int, default=5,
                       help="Number of results to return (default: 5)")
    
    args = parser.parse_args()
    
    if args.stats:
        try:
            query_system = LegalRAGQuery()
            stats = query_system.get_statistics()
            
            print("📊 Legal RAG Database Statistics")
            print("=" * 40)
            print(f"Total laws: {stats['total_laws']:,}")
            print(f"Total chunks: {stats['total_chunks']:,}")
            print(f"Chunks with embeddings: {stats['chunks_with_embeddings']:,}")
            print(f"Total searches performed: {stats['total_searches']:,}")
            
            print("\nLaw types distribution:")
            for law_type, count in stats['chunks_by_law_type'].items():
                print(f"  {law_type}: {count:,}")
                
            query_system.close()
        except Exception as e:
            print(f"Error: {e}")
            
    elif args.search:
        try:
            query_system = LegalRAGQuery()
            print(f"🔍 Searching for: '{args.search}'")
            
            results = query_system.search_simple(args.search, top_k=args.top_k)
            
            if results:
                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['law_name']} ({result['law_type']})")
                    print(f"   {result['text']}")
            else:
                print("No results found.")
                
            query_system.close()
        except Exception as e:
            print(f"Error: {e}")
            
    else:
        # Default to interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()