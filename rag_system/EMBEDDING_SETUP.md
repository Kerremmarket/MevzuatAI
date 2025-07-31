# 🚀 Legal Document Embedding Setup Guide

## 📋 Overview
This guide will help you create OpenAI embeddings for your 1,708 Turkish legal documents for use in a RAG (Retrieval-Augmented Generation) system.

## 🛠️ Prerequisites

### 1. OpenAI API Key
You'll need an OpenAI API key with credits to generate embeddings.

- Sign up at: https://platform.openai.com/
- Go to: https://platform.openai.com/api-keys
- Create a new API key
- **Cost estimate**: ~$15-30 for the full dataset (using text-embedding-3-small)

### 2. Python Dependencies
Install required packages:

```bash
pip install -r requirements_embeddings.txt
```

Or individually:
```bash
pip install pandas numpy openpyxl openai tiktoken tqdm python-dotenv
```

## 🔧 Setup Steps

### Step 1: Set Your API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

**Option B: Create .env file**
```bash
# Create a .env file in your project directory
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Step 2: Test Your Setup
```bash
python test_embeddings.py
```

This will:
- ✅ Test OpenAI connection
- 🧪 Process 3 sample documents
- 💰 Estimate costs for full dataset
- 📊 Show chunking results

### Step 3: Run Full Embedding Generation
```bash
python create_embeddings.py
```

## 📊 What the Script Does

### 🔄 Processing Pipeline
1. **Load Dataset**: Reads your Excel file with 1,708 legal documents
2. **Intelligent Chunking**: Splits documents by articles (MADDE) while respecting token limits
3. **Token Management**: Ensures chunks stay under 7,000 tokens
4. **Embedding Generation**: Creates vector embeddings using OpenAI API
5. **Progress Tracking**: Shows real-time progress with tqdm
6. **Auto-Save**: Saves intermediate results every 50 documents
7. **Multiple Formats**: Outputs JSON, NumPy, and Pickle formats

### 📁 Output Files
The script creates an `embeddings_output/` directory with:

- **`legal_chunks_TIMESTAMP.json`** - Chunk metadata (without embeddings)
- **`legal_embeddings_TIMESTAMP.npy`** - Embeddings as NumPy array
- **`legal_rag_data_TIMESTAMP.pkl`** - Complete data (chunks + embeddings)
- **`embedding_stats_TIMESTAMP.json`** - Statistics and summary

## 🧩 Smart Chunking Features

### Article-Level Chunking
- Automatically detects Turkish legal articles ("MADDE 1", "MADDE 2", etc.)
- Groups related articles into coherent chunks
- Preserves legal context and structure

### Fallback Chunking
- For documents without clear articles, uses sentence-based chunking
- Respects token limits while maintaining readability

### Rich Metadata
Each chunk includes:
```json
{
  "chunk_id": "7552_0",
  "text": "İKLİM KANUNU MADDE 1...",
  "tokens": 2847,
  "law_type": "Kanun",
  "law_name": "İKLİM KANUNU",
  "law_number": "7552",
  "acceptance_date": "02.07.2025",
  "gazette_date": "09.07.2025",
  "gazette_number": "32951",
  "detail_url": "https://mevzuat.gov.tr/...",
  "chunk_index": 0,
  "total_law_length": 45750
}
```

## 💰 Cost Estimation

### Current Dataset (1,708 documents)
- **Total characters**: ~87 million
- **Estimated tokens**: ~21.7 million
- **Estimated cost**: $15-30 USD (using text-embedding-3-small)

### Model Options
- **text-embedding-3-small** (1536 dimensions): $0.00002/1K tokens ✅ Recommended
- **text-embedding-3-large** (3072 dimensions): $0.00013/1K tokens (6.5x more expensive)

## 🔧 Troubleshooting

### Common Issues

**❌ "No module named 'openai'"**
```bash
pip install openai>=1.0.0
```

**❌ "Invalid API key"**
- Check your API key is correct
- Ensure you have credits in your OpenAI account
- Verify the key has embedding permissions

**❌ "Rate limit exceeded"**
- The script has built-in rate limiting
- If persistent, reduce batch size or add longer delays

**❌ "Token limit exceeded"**
- The script automatically chunks text
- If issues persist, reduce `max_chunk_tokens` in the script

### Rate Limiting
The script includes:
- ✅ Exponential backoff on rate limits
- ✅ 0.1-second delay between requests
- ✅ Automatic retry logic
- ✅ Intermediate saves to prevent data loss

## 📈 Performance Optimization

### Batch Processing
- Process documents in smaller batches
- Use intermediate saves to resume if interrupted
- Monitor OpenAI usage dashboard

### Memory Management
- Large datasets may require chunking into smaller batches
- Consider processing by law type if memory is limited

## 🎯 Next Steps After Embedding Generation

Once embeddings are created, you can:

1. **Build Vector Database**: Use FAISS, Pinecone, or Weaviate
2. **Create RAG System**: Implement semantic search + LLM generation
3. **Add Filtering**: Use law_type metadata for targeted search
4. **Implement Hybrid Search**: Combine semantic + keyword search

## 📞 Support

If you encounter issues:

1. Run `python test_embeddings.py` to isolate the problem
2. Check OpenAI API status: https://status.openai.com/
3. Review error messages for specific troubleshooting
4. Monitor your OpenAI usage dashboard for rate limits

---

## 🚀 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements_embeddings.txt

# 2. Set API key
export OPENAI_API_KEY="your-key-here"

# 3. Test setup
python test_embeddings.py

# 4. Generate embeddings
python create_embeddings.py
```

**Estimated time**: 2-4 hours for full dataset
**Estimated cost**: $15-30 USD 