import pandas as pd
import numpy as np
import openai
import os
import time
import json
import pickle
from typing import List, Dict, Tuple
from datetime import datetime
import tiktoken
from tqdm import tqdm

class LegalDocumentEmbedder:
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize the embedder with OpenAI API
        
        Args:
            api_key: OpenAI API key (if None, will look for OPENAI_API_KEY env var)
            model: Embedding model to use
        """
        if api_key:
            openai.api_key = api_key
        elif "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
        else:
            raise ValueError("Please provide OpenAI API key or set OPENAI_API_KEY environment variable")
        
        self.model = model
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        
        # Model limits
        self.max_tokens = 8192 if "text-embedding-3" in model else 8191
        self.max_chunk_tokens = 7000  # Leave buffer for safety
        
        print(f"🤖 Using model: {model}")
        print(f"📏 Max tokens per chunk: {self.max_chunk_tokens}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(str(text)))
    
    def chunk_text(self, text: str, law_info: Dict) -> List[Dict]:
        """
        Intelligently chunk legal text while preserving context
        """
        text = str(text)
        chunks = []
        
        # First, try to split by articles (MADDE)
        article_pattern = r'\bMADDE\s+\d+'
        import re
        
        # Split by articles
        article_splits = re.split(article_pattern, text)
        current_article_match = re.finditer(article_pattern, text)
        article_numbers = [match.group() for match in current_article_match]
        
        # If we have articles, process them
        if len(article_splits) > 1:
            current_chunk = article_splits[0]  # Introduction/preamble
            current_chunk_tokens = self.count_tokens(current_chunk)
            
            for i, (article_num, article_text) in enumerate(zip(article_numbers, article_splits[1:])):
                article_content = f"{article_num} {article_text}"
                article_tokens = self.count_tokens(article_content)
                
                # If adding this article would exceed limit, save current chunk
                if current_chunk_tokens + article_tokens > self.max_chunk_tokens and current_chunk.strip():
                    chunks.append(self._create_chunk(current_chunk, law_info, len(chunks)))
                    current_chunk = article_content
                    current_chunk_tokens = article_tokens
                else:
                    current_chunk += " " + article_content
                    current_chunk_tokens += article_tokens
            
            # Add final chunk
            if current_chunk.strip():
                chunks.append(self._create_chunk(current_chunk, law_info, len(chunks)))
        
        else:
            # No articles found, split by sentences/paragraphs
            chunks = self._chunk_by_sentences(text, law_info)
        
        return chunks
    
    def _chunk_by_sentences(self, text: str, law_info: Dict) -> List[Dict]:
        """Fallback chunking by sentences"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + ". " + sentence if current_chunk else sentence
            
            if self.count_tokens(test_chunk) > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, law_info, len(chunks)))
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, law_info, len(chunks)))
        
        return chunks
    
    def _create_chunk(self, text: str, law_info: Dict, chunk_idx: int) -> Dict:
        """Create a chunk with metadata"""
        return {
            'chunk_id': f"{law_info['mevzuatNo']}_{chunk_idx}",
            'text': text.strip(),
            'tokens': self.count_tokens(text),
            'law_type': law_info['law_type'],
            'law_name': law_info['mevAdi'],
            'law_number': law_info['mevzuatNo'],
            'acceptance_date': law_info['kabulTarih'],
            'gazette_date': law_info['resmiGazeteTarihi'],
            'gazette_number': law_info['resmiGazeteSayisi'],
            'detail_url': law_info['detail_url'],
            'chunk_index': chunk_idx,
            'total_law_length': law_info['text_length']
        }
    
    def get_embedding(self, text: str, retries: int = 3) -> List[float]:
        """Get embedding with retry logic"""
        for attempt in range(retries):
            try:
                response = openai.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            
            except openai.RateLimitError:
                wait_time = (2 ** attempt) * 5  # Exponential backoff
                print(f"⏳ Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            
            except Exception as e:
                print(f"❌ Error getting embedding (attempt {attempt + 1}): {str(e)}")
                if attempt == retries - 1:
                    raise e
                time.sleep(2)
        
        raise Exception("Failed to get embedding after all retries")
    
    def process_dataset(self, excel_file: str, output_dir: str = "embeddings_output"):
        """Process the entire legal dataset"""
        print(f"📖 Loading dataset from {excel_file}...")
        df = pd.read_excel(excel_file)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"📊 Dataset info:")
        print(f"  - Total laws: {len(df)}")
        print(f"  - Law types: {df['law_type'].value_counts().to_dict()}")
        
        all_chunks = []
        all_embeddings = []
        
        # Process each law
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing laws"):
            try:
                law_info = {
                    'law_type': row['law_type'],
                    'mevzuatNo': row['mevzuatNo'],
                    'mevAdi': row['mevAdi'],
                    'kabulTarih': row['kabulTarih'],
                    'resmiGazeteTarihi': row['resmiGazeteTarihi'],
                    'resmiGazeteSayisi': row['resmiGazeteSayisi'],
                    'text_length': row['text_length'],
                    'detail_url': row['detail_url']
                }
                
                # Chunk the text
                chunks = self.chunk_text(row['full_text'], law_info)
                
                print(f"\n📄 Processing: {row['mevAdi'][:50]}...")
                print(f"   Created {len(chunks)} chunks")
                
                # Get embeddings for each chunk
                for chunk in tqdm(chunks, desc="  Creating embeddings", leave=False):
                    embedding = self.get_embedding(chunk['text'])
                    chunk['embedding'] = embedding
                    
                    all_chunks.append(chunk)
                    all_embeddings.append(embedding)
                    
                    # Small delay to respect rate limits
                    time.sleep(0.1)
                
                # Save intermediate results every 50 laws
                if (idx + 1) % 50 == 0:
                    self._save_intermediate_results(all_chunks, all_embeddings, output_dir, idx + 1)
            
            except Exception as e:
                print(f"❌ Error processing law {row['mevzuatNo']}: {str(e)}")
                continue
        
        # Save final results
        self._save_final_results(all_chunks, all_embeddings, output_dir)
        
        return all_chunks, all_embeddings
    
    def _save_intermediate_results(self, chunks, embeddings, output_dir, processed_count):
        """Save intermediate results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save chunks
        chunks_file = f"{output_dir}/chunks_intermediate_{processed_count}_{timestamp}.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            # Remove embeddings for JSON serialization
            chunks_no_embed = [{k: v for k, v in chunk.items() if k != 'embedding'} for chunk in chunks]
            json.dump(chunks_no_embed, f, ensure_ascii=False, indent=2)
        
        # Save embeddings
        embeddings_file = f"{output_dir}/embeddings_intermediate_{processed_count}_{timestamp}.npy"
        np.save(embeddings_file, np.array(embeddings))
        
        print(f"💾 Saved intermediate results: {processed_count} laws processed")
    
    def _save_final_results(self, chunks, embeddings, output_dir):
        """Save final results in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n💾 Saving final results...")
        print(f"📊 Total chunks created: {len(chunks)}")
        print(f"📏 Embedding dimensions: {len(embeddings[0]) if embeddings else 0}")
        
        # 1. Save chunks metadata (without embeddings) as JSON
        chunks_file = f"{output_dir}/legal_chunks_{timestamp}.json"
        chunks_no_embed = [{k: v for k, v in chunk.items() if k != 'embedding'} for chunk in chunks]
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_no_embed, f, ensure_ascii=False, indent=2)
        
        # 2. Save embeddings as numpy array
        embeddings_file = f"{output_dir}/legal_embeddings_{timestamp}.npy"
        np.save(embeddings_file, np.array(embeddings))
        
        # 3. Save complete data (chunks + embeddings) as pickle
        complete_file = f"{output_dir}/legal_rag_data_{timestamp}.pkl"
        with open(complete_file, 'wb') as f:
            pickle.dump({'chunks': chunks, 'embeddings': embeddings}, f)
        
        # 4. Save summary statistics
        stats_file = f"{output_dir}/embedding_stats_{timestamp}.json"
        stats = {
            'total_chunks': len(chunks),
            'total_laws': len(set(chunk['law_number'] for chunk in chunks)),
            'embedding_model': self.model,
            'embedding_dimensions': len(embeddings[0]) if embeddings else 0,
            'avg_tokens_per_chunk': np.mean([chunk['tokens'] for chunk in chunks]),
            'law_type_distribution': {},
            'timestamp': timestamp
        }
        
        # Calculate law type distribution
        law_types = {}
        for chunk in chunks:
            law_type = chunk['law_type']
            law_types[law_type] = law_types.get(law_type, 0) + 1
        stats['law_type_distribution'] = law_types
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Results saved to {output_dir}/")
        print(f"  📄 Chunks: {chunks_file}")
        print(f"  🔢 Embeddings: {embeddings_file}")
        print(f"  💾 Complete data: {complete_file}")
        print(f"  📊 Statistics: {stats_file}")

def main():
    print("🚀 Legal Document Embedding Generator")
    print("=" * 50)
    
    # Configuration
    excel_file = "mevzuat_combined_20250729_181132.xlsx"  # Your Excel file
    
    # Check if file exists
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        print("Please ensure the file exists in the current directory.")
        return
    
    # Initialize embedder
    try:
        embedder = LegalDocumentEmbedder(model="text-embedding-3-small")  # Cost-effective choice
        
        # Process dataset
        chunks, embeddings = embedder.process_dataset(excel_file)
        
        print(f"\n🎉 Embedding creation completed!")
        print(f"📊 Final statistics:")
        print(f"  - Total chunks: {len(chunks)}")
        print(f"  - Total laws processed: {len(set(chunk['law_number'] for chunk in chunks))}")
        print(f"  - Average tokens per chunk: {np.mean([chunk['tokens'] for chunk in chunks]):.1f}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Install required packages: pip install openai tiktoken tqdm")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main() 