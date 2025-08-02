# 🚀 Cloud Embeddings Setup Guide

## Quick Overview
Your embeddings (110MB+) are too large for GitHub, so we'll store them on AWS S3 and load them in production.

## Step 1: Set Up AWS Account (5 minutes)

1. **Go to [AWS Console](https://aws.amazon.com)**
2. **Create account** (if you don't have one)
3. **Go to IAM → Users → Create User**
4. **Give permissions:** `AmazonS3FullAccess`
5. **Create Access Key** and save:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

## Step 2: Upload Your Embeddings (5 minutes)

```bash
# Install AWS CLI
pip install boto3

# Configure credentials (temporary - we'll use env vars in production)
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1

# Run the upload script
cd the_project
python cloud_embeddings_setup.py
```

**Or manually upload via AWS Console:**
1. Create S3 bucket: `mevzuat-ai-embeddings-YOUR_NAME` (must be globally unique)
2. Upload these files to `/embeddings/` folder:
   - `legal_embeddings_20250730_005323.npy`
   - `legal_chunks_20250730_005323.json`
   - `embedding_stats_20250730_005323.json`

## Step 3: Configure Railway Environment Variables

**Add these to your Railway project:**

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_EMBEDDINGS_BUCKET=mevzuat-ai-embeddings-YOUR_NAME

# OpenAI Keys (if you haven't already)
OPENAI_API_KEY_LARGE=your_gpt4o_key_here
OPENAI_API_KEY_NANO=your_gpt4o_mini_key_here
```

## Step 4: Deploy and Test

```bash
# Commit and push the cloud storage code
git add .
git commit -m "Add cloud storage support for embeddings"
git push origin main

# Wait for Railway to deploy (2-3 minutes)
# Test your app - it should now load embeddings from S3!
```

## What Happens Now:

✅ **Production:** Loads embeddings from S3  
✅ **Development:** Uses local files  
✅ **Fallback:** Demo mode if both fail  
✅ **No more size limits!** 

## Alternative: Free Options

**If you don't want AWS:**
- **Railway Volumes:** Mount persistent storage (included in Railway)
- **GitHub LFS:** Git Large File Storage (100MB limit still applies)
- **Google Drive/Dropbox:** Public download links

## Cost Estimate:
- **AWS S3:** ~$0.025/month for 110MB storage
- **Data transfer:** ~$0.01 per deployment
- **Total:** Less than $1/month

---

**Need help?** The system will work in demo mode until you set this up!