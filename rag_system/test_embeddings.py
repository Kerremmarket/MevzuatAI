import pandas as pd
import openai
import os
from create_embeddings import LegalDocumentEmbedder

def test_openai_connection():
    """Test basic OpenAI connection"""
    print("🔧 Testing OpenAI connection...")
    
    try:
        # Test with a simple embedding
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input="Bu bir test metnidir."
        )
        
        embedding = response.data[0].embedding
        print(f"✅ OpenAI connection successful!")
        print(f"📏 Embedding dimensions: {len(embedding)}")
        print(f"🔢 First 5 values: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {str(e)}")
        return False

def test_with_sample_data():
    """Test embedding generation with a few sample documents"""
    print("\n🧪 Testing with sample legal documents...")
    
    # Load dataset
    excel_file = "mevzuat_combined_20250729_181132.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return False
    
    # Read only first 3 documents for testing
    df = pd.read_excel(excel_file, nrows=3)
    print(f"📖 Loaded {len(df)} sample documents for testing")
    
    try:
        # Initialize embedder
        embedder = LegalDocumentEmbedder(model="text-embedding-3-small")
        
        # Process first document
        row = df.iloc[0]
        
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
        
        print(f"\n📄 Testing document: {row['mevAdi'][:50]}...")
        print(f"📊 Original text length: {len(str(row['full_text']))} characters")
        print(f"📊 Token count: {embedder.count_tokens(str(row['full_text']))} tokens")
        
        # Test chunking
        chunks = embedder.chunk_text(row['full_text'], law_info)
        print(f"✂️ Created {len(chunks)} chunks")
        
        # Test embedding for first chunk
        if chunks:
            first_chunk = chunks[0]
            print(f"📝 First chunk preview: {first_chunk['text'][:100]}...")
            print(f"🔢 First chunk tokens: {first_chunk['tokens']}")
            
            # Get embedding
            embedding = embedder.get_embedding(first_chunk['text'])
            print(f"✅ Successfully created embedding for first chunk!")
            print(f"📏 Embedding dimensions: {len(embedding)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def estimate_costs():
    """Estimate embedding generation costs"""
    print("\n💰 Cost Estimation for Full Dataset...")
    
    excel_file = "mevzuat_combined_20250729_181132.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return
    
    # Load dataset info
    df = pd.read_excel(excel_file)
    
    # Estimate tokens (rough calculation)
    total_chars = df['text_length'].sum()
    estimated_tokens = total_chars // 4  # Rough estimation: 4 chars = 1 token
    
    # OpenAI pricing (as of 2024)
    # text-embedding-3-small: $0.00002 per 1K tokens
    cost_per_1k_tokens = 0.00002
    estimated_cost = (estimated_tokens / 1000) * cost_per_1k_tokens
    
    print(f"📊 Dataset Statistics:")
    print(f"  - Total documents: {len(df)}")
    print(f"  - Total characters: {total_chars:,}")
    print(f"  - Estimated tokens: {estimated_tokens:,}")
    print(f"  - Estimated cost: ${estimated_cost:.2f}")
    
    print(f"\n💡 Tips to reduce costs:")
    print(f"  - Use text-embedding-3-small (cheaper than large)")
    print(f"  - Consider processing in batches")
    print(f"  - Remove unnecessary text/metadata")

def main():
    print("🧪 OpenAI Embedding Test Suite")
    print("=" * 40)
    
    # Check API key
    if "OPENAI_API_KEY" not in os.environ:
        print("❌ OpenAI API key not found!")
        print("Please set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  or create a .env file with OPENAI_API_KEY=your-key-here")
        return
    
    print(f"✅ API key found: {os.environ['OPENAI_API_KEY'][:10]}...")
    
    # Run tests
    if test_openai_connection():
        if test_with_sample_data():
            estimate_costs()
            print(f"\n🎉 All tests passed! Ready to run full embedding generation.")
            print(f"💡 To start: python create_embeddings.py")
        else:
            print(f"\n❌ Sample data test failed. Check your data format.")
    else:
        print(f"\n❌ Connection test failed. Check your API key and internet connection.")

if __name__ == "__main__":
    main() 