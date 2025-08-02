"""
RAG System Integration
Loads embeddings and performs semantic search to find top 10 relevant laws
"""

import numpy as np
import json
import glob
from openai import OpenAI
from typing import List, Dict, Optional
import logging
from config.config import Config

# Import sklearn with fallback
try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ scikit-learn not available: {e}")
    SKLEARN_AVAILABLE = False
    # Simple cosine similarity fallback
    def cosine_similarity(a, b):
        """Simple cosine similarity fallback"""
        import numpy as np
        return np.dot(a, b.T) / (np.linalg.norm(a) * np.linalg.norm(b, axis=1))

class RAGSystem:
    def __init__(self, api_key: str = None):
        """Initialize RAG System"""
        self.api_key = api_key or Config.AGENT3_API_KEY or Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        
        self.chunks = None
        self.embeddings = None
        self.logger = logging.getLogger(__name__)
        
        # Load embeddings and chunks
        self.load_embeddings()
    
    def load_embeddings(self):
        """Load embeddings from local files or cloud storage"""
        try:
            # Try cloud storage first (for production)
            if Config.IS_PRODUCTION and self._try_load_from_cloud():
                return
            
            # Fall back to local files (for development)
            if self._try_load_from_local():
                return
                
            # If both fail, use demo mode
            self.logger.warning("🚧 No embeddings found - running in demo mode")
            self.chunks = []
            self.embeddings = None
            
        except Exception as e:
            self.logger.warning(f"🚧 Error loading embeddings: {str(e)} - using demo mode")
            self.chunks = []
            self.embeddings = None
    
    def _try_load_from_cloud(self):
        """Try to load embeddings from S3"""
        try:
            import boto3
            import tempfile
            
            bucket_name = os.getenv('S3_EMBEDDINGS_BUCKET', 'mevzuat-ai-embeddings')
            
            s3 = boto3.client('s3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Download to temp files
            with tempfile.TemporaryDirectory() as temp_dir:
                embeddings_file = os.path.join(temp_dir, 'embeddings.npy')
                chunks_file = os.path.join(temp_dir, 'chunks.json')
                
                # Download embeddings
                s3.download_file(bucket_name, 'embeddings/legal_embeddings_20250730_005323.npy', embeddings_file)
                s3.download_file(bucket_name, 'embeddings/legal_chunks_20250730_005323.json', chunks_file)
                
                # Load into memory
                self.embeddings = np.load(embeddings_file)
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
                
                self.logger.info(f"✅ Loaded {len(self.chunks)} chunks from S3")
                return True
                
        except Exception as e:
            self.logger.info(f"Could not load from cloud: {str(e)}")
            return False
    
    def _try_load_from_local(self):
        """Try to load embeddings from local files"""
        try:
            embeddings_dir = Config.RAG_EMBEDDINGS_DIR
            
            search_paths = [
                f"{embeddings_dir}/legal_embeddings_*.npy",
                "../rag_system/embeddings_output/legal_embeddings_*.npy",
                "rag_system/embeddings_output/legal_embeddings_*.npy"
            ]
            
            embedding_files = []
            chunk_files = []
            
            for path in search_paths:
                embedding_files.extend(glob.glob(path))
                chunk_path = path.replace("legal_embeddings_", "legal_chunks_").replace(".npy", ".json")
                chunk_files.extend(glob.glob(chunk_path))
            
            if not embedding_files or not chunk_files:
                return False
            
            # Get the latest files
            latest_embedding_file = sorted(embedding_files)[-1]
            latest_chunk_file = sorted(chunk_files)[-1]
            
            # Load embeddings
            self.embeddings = np.load(latest_embedding_file)
            
            # Load chunks
            with open(latest_chunk_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            
            self.logger.info(f"✅ Loaded {len(self.chunks)} chunks from local files")
            return True
            
        except Exception as e:
            self.logger.info(f"Could not load from local: {str(e)}")
            return False
    
    def get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Generate embedding for the search query"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            self.logger.error(f"Error generating query embedding: {str(e)}")
            return None
    
    def search_laws(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search for relevant laws using semantic similarity
        
        Args:
            query (str): Search query (optimized by Agent 1)
            top_k (int): Number of laws to return
            
        Returns:
            List[Dict]: List of relevant law information
        """
        try:
            # Check if RAG system is available
            if self.embeddings is None or not self.chunks:
                self.logger.warning("🚧 RAG system not available, returning empty results")
                return []
            
            self.logger.info(f"Searching for: '{query}'")
            
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
            seen_laws = set()  # To avoid duplicate laws
            
            for idx in top_indices:
                chunk = self.chunks[idx]
                law_name = chunk.get('law_name', 'Unknown')
                
                # Skip if we already have this law (to get diverse laws)
                if law_name in seen_laws:
                    continue
                seen_laws.add(law_name)
                
                similarity = similarities[idx]
                
                result = {
                    'rank': len(results) + 1,
                    'law_name': law_name,
                    'law_type': chunk.get('law_type', 'Unknown'),
                    'similarity': float(similarity),
                    'law_number': chunk.get('law_number', ''),
                    'acceptance_date': chunk.get('acceptance_date', ''),
                    'gazette_date': chunk.get('gazette_date', ''),
                    'detail_url': chunk.get('detail_url', ''),
                    'relevant_text': chunk.get('text', '')[:300] + "..."  # Preview
                }
                results.append(result)
                
                # Stop when we have enough unique laws
                if len(results) >= top_k:
                    break
            
            self.logger.info(f"Found {len(results)} relevant laws")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in law search: {str(e)}")
            return []
    
    def get_law_names(self, query: str, top_k: int = 10) -> List[str]:
        """
        Get just the law names for matching with the Excel dataset
        
        Args:
            query (str): Search query
            top_k (int): Number of law names to return
            
        Returns:
            List[str]: List of law names
        """
        results = self.search_laws(query, top_k)
        return [result['law_name'] for result in results]
    
    def test_rag_system(self):
        """Test the RAG system with sample queries"""
        test_queries = [
            "çevre koruma",
            "işçi hakları", 
            "vergi ödemeleri",
            "trafik cezası"
        ]
        
        print("🧪 Testing RAG System")
        print("=" * 50)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            results = self.search_laws(query, top_k=5)
            
            print("   Top Laws Found:")
            for result in results:
                print(f"   - {result['law_name']} (similarity: {result['similarity']:.3f})")

if __name__ == "__main__":
    # Test the RAG system
    rag = RAGSystem()
    rag.test_rag_system()