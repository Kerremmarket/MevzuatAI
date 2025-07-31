import pandas as pd
import numpy as np
import sqlite3
import json
import os
from typing import List, Dict, Tuple, Optional
import pickle
from datetime import datetime

# Multiple embedding options
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class LegalRAGDatabase:
    def __init__(self, db_path="legal_rag.db"):
        """Initialize the Legal RAG Database"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.embedding_model = None
        self.embedding_type = None
        self.setup_database()
        
    def setup_database(self):
        """Setup SQLite database with proper schema"""
        cursor = self.conn.cursor()
        
        # Create chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT UNIQUE,
                law_name TEXT,
                law_type TEXT,
                chunk_type TEXT,
                chunk_index INTEGER,
                text TEXT,
                char_count INTEGER,
                word_count INTEGER,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create laws metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laws_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                law_id TEXT UNIQUE,
                law_name TEXT,
                law_type TEXT,
                full_text TEXT,
                sections TEXT,
                article_count INTEGER,
                character_count INTEGER,
                word_count INTEGER,
                processing_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create search logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                top_k INTEGER,
                search_method TEXT,
                law_type_filter TEXT,
                results_count INTEGER,
                search_time REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for faster search
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_law_type ON chunks(law_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_chunk_type ON chunks(chunk_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_laws_law_type ON laws_metadata(law_type)")
        
        self.conn.commit()
        print("✅ Database schema created successfully")
        
    def load_embedding_model(self, model_type="sentence_transformer", model_name=None):
        """Load embedding model based on type"""
        
        if model_type == "sentence_transformer" and SENTENCE_TRANSFORMERS_AVAILABLE:
            if model_name is None:
                # Use multilingual model for Turkish legal text
                model_name = "paraphrase-multilingual-MiniLM-L12-v2"
            self.embedding_model = SentenceTransformer(model_name)
            self.embedding_type = f"sentence_transformer_{model_name}"
            print(f"✅ Loaded SentenceTransformer: {model_name}")
            
        elif model_type == "openai" and OPENAI_AVAILABLE:
            if model_name is None:
                model_name = "text-embedding-ada-002"
            self.embedding_model = model_name  # Store model name for OpenAI
            self.embedding_type = f"openai_{model_name}"
            print(f"✅ Configured OpenAI embeddings: {model_name}")
            
        elif model_type == "tfidf" and SKLEARN_AVAILABLE:
            self.embedding_model = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words=None,  # Keep for Turkish
                lowercase=True
            )
            self.embedding_type = "tfidf"
            print("✅ Configured TF-IDF vectorizer")
            
        else:
            raise ValueError(f"Embedding type '{model_type}' not available or dependencies missing")
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        
        if self.embedding_type.startswith("sentence_transformer"):
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            return embeddings
            
        elif self.embedding_type.startswith("openai"):
            embeddings = []
            for text in texts:
                response = openai.Embedding.create(
                    input=text,
                    model=self.embedding_model
                )
                embeddings.append(response['data'][0]['embedding'])
            return np.array(embeddings)
            
        elif self.embedding_type == "tfidf":
            if not hasattr(self.embedding_model, 'vocabulary_'):
                # First time - fit the vectorizer
                self.embedding_model.fit(texts)
            embeddings = self.embedding_model.transform(texts).toarray()
            return embeddings
            
        else:
            raise ValueError(f"Unknown embedding type: {self.embedding_type}")
    
    def load_data(self, chunks_file: str, metadata_file: str):
        """Load data from CSV files into database"""
        
        # Load chunks
        print("📊 Loading chunks data...")
        chunks_df = pd.read_csv(chunks_file)
        print(f"Loaded {len(chunks_df)} chunks")
        
        # Load metadata
        print("📊 Loading metadata...")
        metadata_df = pd.read_csv(metadata_file)
        print(f"Loaded {len(metadata_df)} laws metadata")
        
        # Insert metadata
        cursor = self.conn.cursor()
        for _, row in metadata_df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO laws_metadata 
                (law_id, law_name, law_type, full_text, sections, article_count, 
                 character_count, word_count, processing_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['law_id'], row['law_name'], row['law_type'], row['full_text'],
                row['sections'], row['article_count'], row['character_count'],
                row['word_count'], row['processing_date']
            ))
        
        # Insert chunks (without embeddings first)
        for _, row in chunks_df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO chunks 
                (chunk_id, law_name, law_type, chunk_type, chunk_index, 
                 text, char_count, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['chunk_id'], row['law_name'], row['law_type'], row['chunk_type'],
                row['chunk_index'], row['text'], row['char_count'], row['word_count']
            ))
        
        self.conn.commit()
        print("✅ Data loaded into database")
        
        return len(chunks_df), len(metadata_df)
    
    def generate_embeddings(self, batch_size=50):
        """Generate embeddings for all chunks in database"""
        
        if self.embedding_model is None:
            raise ValueError("No embedding model loaded. Call load_embedding_model() first.")
        
        cursor = self.conn.cursor()
        
        # Get all chunks without embeddings
        cursor.execute("SELECT id, text FROM chunks WHERE embedding IS NULL")
        chunks = cursor.fetchall()
        
        print(f"🔄 Generating embeddings for {len(chunks)} chunks...")
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            batch_ids = [chunk[0] for chunk in batch]
            batch_texts = [chunk[1] for chunk in batch]
            
            # Generate embeddings
            embeddings = self.get_embeddings(batch_texts)
            
            # Store embeddings in database
            for chunk_id, embedding in zip(batch_ids, embeddings):
                embedding_blob = pickle.dumps(embedding)
                cursor.execute(
                    "UPDATE chunks SET embedding = ? WHERE id = ?",
                    (embedding_blob, chunk_id)
                )
            
            self.conn.commit()
            print(f"✅ Processed batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
        
        print("🎉 All embeddings generated successfully!")
    
    def search(self, query: str, top_k: int = 5, law_type_filter: str = None, 
               chunk_type_filter: str = None) -> List[Dict]:
        """Search for relevant chunks using semantic similarity"""
        
        start_time = datetime.now()
        
        # Generate query embedding
        query_embedding = self.get_embeddings([query])[0]
        
        # Build SQL query with filters
        sql_conditions = ["embedding IS NOT NULL"]
        params = []
        
        if law_type_filter:
            sql_conditions.append("law_type = ?")
            params.append(law_type_filter)
            
        if chunk_type_filter:
            sql_conditions.append("chunk_type = ?")
            params.append(chunk_type_filter)
        
        sql_query = f"""
            SELECT chunk_id, law_name, law_type, chunk_type, chunk_index, 
                   text, char_count, word_count, embedding
            FROM chunks 
            WHERE {' AND '.join(sql_conditions)}
        """
        
        cursor = self.conn.cursor()
        cursor.execute(sql_query, params)
        results = cursor.fetchall()
        
        # Calculate similarities
        similarities = []
        for result in results:
            embedding = pickle.loads(result[8])  # embedding is the 9th column (index 8)
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            similarities.append((similarity, result))
        
        # Sort by similarity and take top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_results = similarities[:top_k]
        
        # Format results
        formatted_results = []
        for similarity, result in top_results:
            formatted_results.append({
                'chunk_id': result[0],
                'law_name': result[1],
                'law_type': result[2],
                'chunk_type': result[3],
                'chunk_index': result[4],
                'text': result[5],
                'char_count': result[6],
                'word_count': result[7],
                'similarity_score': similarity
            })
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        # Log search
        cursor.execute("""
            INSERT INTO search_logs (query, top_k, search_method, law_type_filter, 
                                   results_count, search_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (query, top_k, self.embedding_type, law_type_filter, len(formatted_results), search_time))
        self.conn.commit()
        
        return formatted_results
    
    def get_law_metadata(self, law_name: str) -> Dict:
        """Get metadata for a specific law"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT law_id, law_name, law_type, sections, article_count, 
                   character_count, word_count, processing_date
            FROM laws_metadata 
            WHERE law_name = ?
        """, (law_name,))
        
        result = cursor.fetchone()
        if result:
            return {
                'law_id': result[0],
                'law_name': result[1],
                'law_type': result[2],
                'sections': json.loads(result[3]) if result[3] else [],
                'article_count': result[4],
                'character_count': result[5],
                'word_count': result[6],
                'processing_date': result[7]
            }
        return None
    
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
        cursor.execute("SELECT law_type, COUNT(*) FROM chunks GROUP BY law_type")
        stats['chunks_by_law_type'] = dict(cursor.fetchall())
        
        # Search statistics
        cursor.execute("SELECT COUNT(*) FROM search_logs")
        stats['total_searches'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(search_time) FROM search_logs")
        avg_time = cursor.fetchone()[0]
        stats['avg_search_time'] = round(avg_time, 4) if avg_time else 0
        
        return stats
    
    def save_model_info(self, model_info_file="model_info.json"):
        """Save model information for later loading"""
        info = {
            'embedding_type': self.embedding_type,
            'model_name': getattr(self.embedding_model, 'model_name', str(self.embedding_model)),
            'created_at': datetime.now().isoformat(),
            'database_path': self.db_path
        }
        
        with open(model_info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Model info saved to {model_info_file}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Example usage and setup function
def setup_legal_rag_system():
    """Complete setup for legal RAG system"""
    
    print("🚀 Setting up Legal RAG System...")
    
    # Initialize database
    rag_db = LegalRAGDatabase("mevzat_rag.db")
    
    # Load embedding model (choose best available)
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        print("📡 Loading multilingual embedding model...")
        rag_db.load_embedding_model("sentence_transformer", "paraphrase-multilingual-MiniLM-L12-v2")
    elif SKLEARN_AVAILABLE:
        print("📡 Loading TF-IDF model...")
        rag_db.load_embedding_model("tfidf")
    else:
        raise Exception("No embedding library available. Install sentence-transformers or scikit-learn")
    
    # Load data
    chunks_file = "mevzuat_chunked_for_rag.csv"
    metadata_file = "mevzuat_enhanced_dataset.csv"
    
    if os.path.exists(chunks_file) and os.path.exists(metadata_file):
        rag_db.load_data(chunks_file, metadata_file)
        rag_db.generate_embeddings()
        rag_db.save_model_info()
    else:
        print("❌ Data files not found. Please run create_enhanced_dataset.py first")
        return None
    
    print("🎉 Legal RAG System setup complete!")
    return rag_db

if __name__ == "__main__":
    # Setup the system
    rag_system = setup_legal_rag_system()
    
    if rag_system:
        # Show statistics
        stats = rag_system.get_statistics()
        print("\n📊 Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Example searches
        print("\n🔍 Example Searches:")
        
        queries = [
            "iklim değişikliği ile mücadele",
            "siber güvenlik",
            "karbon emisyonu",
            "ceza hükümleri"
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            results = rag_system.search(query, top_k=3)
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['law_name']} ({result['law_type']}) - Score: {result['similarity_score']:.3f}")
        
        rag_system.close()