# 🏛️ Legal RAG System - Turkish Legal Documents

A comprehensive Retrieval-Augmented Generation (RAG) system for Turkish legal documents, featuring semantic search, law type classification, and intelligent chunking.

## 📋 Overview

This RAG system processes and provides intelligent search capabilities for Turkish legal documents including:
- **İklim Kanunu** (Climate Law)
- **Siber Güvenlik Kanunu** (Cyber Security Law)  
- **Ticaret Kanunu** (Trade Law)
- **Ceza Kanunu** (Criminal Law)
- And many more...

### 🎯 Key Features

- **🔍 Semantic Search**: Find relevant content using natural language queries
- **📊 Law Type Classification**: Automatic categorization into 16+ law types
- **🧩 Intelligent Chunking**: Article-level and section-level text segments
- **🌐 Multilingual Support**: Optimized for Turkish legal terminology
- **📈 Performance Analytics**: Search logging and performance tracking
- **🔌 Multiple Embedding Options**: SentenceTransformers, OpenAI, TF-IDF

## 🗂️ Dataset Structure

### Enhanced Metadata Dataset
- **1,570 laws** with rich metadata
- **16 law categories** automatically classified
- **Full text** with structured information
- **Section extraction** and article counting

### Chunked RAG Dataset  
- **1,854 optimized chunks** for retrieval
- **Article-level granularity** where possible
- **Contextual metadata** preserved in each chunk
- **Perfect for** vector embeddings and semantic search

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install core dependencies
pip install pandas numpy sqlite3

# For best performance (recommended)
pip install sentence-transformers torch transformers

# Alternative: TF-IDF (lightweight)
pip install scikit-learn

# Optional: OpenAI embeddings
pip install openai

# Complete requirements
pip install -r requirements_rag.txt
```

### 2. Create Enhanced Dataset

```bash
# Process original legal documents
python create_enhanced_dataset.py
```

This creates:
- `mevzuat_enhanced_dataset.csv` - Laws with metadata
- `mevzuat_chunked_for_rag.csv` - Chunks for RAG

### 3. Build Vector Database

```bash
# Build the complete RAG system
python build_vector_database.py
```

This will:
- ✅ Create SQLite database
- 📡 Load multilingual embedding model  
- 🔄 Generate embeddings for all chunks
- 💾 Save model configuration

### 4. Query the System

```bash
# Interactive mode
python query_legal_rag.py

# Single search
python query_legal_rag.py --search "iklim değişikliği"

# Show statistics
python query_legal_rag.py --stats
```

## 💻 Usage Examples

### Interactive Query Interface

```python
from build_vector_database import LegalRAGDatabase

# Initialize system
rag = LegalRAGDatabase("mevzat_rag.db")

# Semantic search
results = rag.search("karbon emisyonu azaltımı", top_k=5)

for result in results:
    print(f"Law: {result['law_name']}")
    print(f"Type: {result['law_type']}")
    print(f"Score: {result['similarity_score']:.3f}")
    print(f"Text: {result['text'][:200]}...")
    print("-" * 50)
```

### Filtered Search

```python
# Search only in environmental laws
results = rag.search(
    query="sera gazı", 
    top_k=3,
    law_type_filter="Çevre ve İklim"
)

# Search only in articles (not sections)
results = rag.search(
    query="ceza hükümleri",
    chunk_type_filter="article"
)
```

### Get Law Information

```python
# Get detailed law metadata
law_info = rag.get_law_metadata("İKLİM KANUNU")
print(f"Articles: {law_info['article_count']}")
print(f"Word count: {law_info['word_count']:,}")
print(f"Sections: {law_info['sections']}")
```

## 🔧 Configuration Options

### Embedding Models

#### 1. SentenceTransformers (Recommended)
```python
rag.load_embedding_model(
    "sentence_transformer", 
    "paraphrase-multilingual-MiniLM-L12-v2"
)
```

#### 2. OpenAI Embeddings
```python
import openai
openai.api_key = "your-api-key"

rag.load_embedding_model("openai", "text-embedding-ada-002")
```

#### 3. TF-IDF (Lightweight)
```python
rag.load_embedding_model("tfidf")
```

### Database Schema

```sql
-- Chunks table
CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,
    law_name TEXT,
    law_type TEXT,
    chunk_type TEXT,  -- 'article' or 'section'
    chunk_index INTEGER,
    text TEXT,
    char_count INTEGER,
    word_count INTEGER,
    embedding BLOB,    -- Pickled numpy array
    created_at TIMESTAMP
);

-- Laws metadata table
CREATE TABLE laws_metadata (
    law_id TEXT PRIMARY KEY,
    law_name TEXT,
    law_type TEXT,
    full_text TEXT,
    sections TEXT,     -- JSON array
    article_count INTEGER,
    character_count INTEGER,
    word_count INTEGER,
    processing_date TEXT
);
```

## 🎯 Law Type Categories

The system automatically classifies laws into these categories:

1. **Çevre ve İklim** - Environment & Climate
2. **Teknoloji ve Siber Güvenlik** - Technology & Cyber Security  
3. **Ticaret Kanunu** - Trade Law
4. **İş ve Sosyal Güvenlik** - Labor & Social Security
5. **Ceza Kanunu** - Criminal Law
6. **Medeni Kanun** - Civil Law
7. **İdare Kanunu** - Administrative Law
8. **Vergi Kanunu** - Tax Law
9. **Sağlık** - Health
10. **Eğitim** - Education
11. **Ulaştırma** - Transportation
12. **Tarım** - Agriculture
13. **Enerji** - Energy
14. **Bankacılık ve Finans** - Banking & Finance
15. **İnsan Hakları** - Human Rights
16. **Anayasa** - Constitutional Law

## 📊 Performance & Statistics

### Search Performance
- **Semantic Search**: ~0.1-0.5 seconds per query
- **Text Search**: ~0.05-0.1 seconds per query
- **Database Size**: ~50MB (with embeddings)

### Dataset Statistics
```
Total Laws: 1,570
Total Chunks: 1,854
Average Chunks per Law: 1.2
Top Law Types:
  - Ticaret Kanunu: 681 chunks
  - İş ve Sosyal Güvenlik: 390 chunks
  - İdare Kanunu: 116 chunks
```

## 🔍 Interactive Commands

The query interface supports these commands:

```bash
search <query>          # Text-based search
vsearch <query>         # Vector/semantic search  
types                   # List available law types
laws [type]            # List laws (optionally by type)
info <law_name>        # Get detailed law information
browse <law_type>      # Browse chunks by law type
stats                  # Show database statistics
help                   # Show help
exit                   # Exit program
```

## 🛠️ Advanced Usage

### Batch Processing

```python
# Process multiple queries
queries = [
    "iklim değişikliği",
    "siber saldırı", 
    "çevre koruma",
    "veri güvenliği"
]

for query in queries:
    results = rag.search(query, top_k=3)
    print(f"\n=== {query} ===")
    for r in results:
        print(f"{r['law_name']}: {r['similarity_score']:.3f}")
```

### Custom Chunking

```python
# Modify chunking parameters
chunks = chunk_law_text(
    text=law_text,
    law_name="Custom Law", 
    law_type="Custom Type",
    chunk_size=2000  # Larger chunks
)
```

### Export Results

```python
import pandas as pd

# Search and export to CSV
results = rag.search("karbon ticareti", top_k=20)
df = pd.DataFrame(results)
df.to_csv("search_results.csv", index=False)
```

## 🔮 Future Enhancements

- **🤖 Integration with LLMs** (GPT, Claude, Llama)
- **🌐 Web Interface** (Streamlit/FastAPI)
- **📱 Mobile App** support
- **🔄 Real-time Updates** as new laws are published
- **🌍 Multi-language** support (English summaries)
- **📈 Advanced Analytics** and search insights

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. **Data Quality**: Better text preprocessing
2. **Embedding Models**: Test domain-specific models
3. **Chunking Strategy**: Smarter document segmentation  
4. **Performance**: Optimize search speed
5. **Features**: Additional metadata extraction

## 📄 License

This project is for educational and research purposes. Legal document usage should comply with Turkish legal framework and copyright requirements.

## 🆘 Troubleshooting

### Common Issues

**Database not found:**
```bash
python build_vector_database.py
```

**Import errors:**
```bash
pip install -r requirements_rag.txt
```

**Slow embedding generation:**
- Use smaller embedding model
- Reduce batch size
- Consider TF-IDF for faster setup

**Memory issues:**
- Process data in smaller batches
- Use TF-IDF instead of neural embeddings
- Increase swap space

### Performance Tips

1. **SSD Storage**: Store database on SSD for faster access
2. **RAM**: 8GB+ recommended for large embedding models
3. **Batch Size**: Adjust based on available memory
4. **Indexing**: Database automatically creates search indexes

## 📞 Support

For questions and support:
- Check the troubleshooting section
- Review example usage in `query_legal_rag.py`
- Test with simple queries first

---

🏛️ **Built for Turkish Legal Research & Analysis**