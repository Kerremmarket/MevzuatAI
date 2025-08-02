"""
Cloud Embeddings Setup - AWS S3 Focus
Move embeddings to cloud storage for production deployment
"""

import os
import boto3
import requests
import json
import numpy as np
from typing import Optional

class CloudEmbeddingsLoader:
    """Load embeddings from cloud storage instead of local files"""
    
    def __init__(self, provider='aws'):
        self.provider = provider
        
    def upload_embeddings_to_aws_s3(self, bucket_name, local_embeddings_dir):
        """Upload embeddings to AWS S3"""
        s3 = boto3.client('s3')
        
        files_to_upload = [
            'legal_embeddings_20250730_005323.npy',
            'legal_chunks_20250730_005323.json',
            'legal_rag_data_20250730_005323.pkl'
        ]
        
        for file_name in files_to_upload:
            local_path = os.path.join(local_embeddings_dir, file_name)
            if os.path.exists(local_path):
                s3.upload_file(local_path, bucket_name, f'embeddings/{file_name}')
                print(f"✅ Uploaded {file_name} to S3")
    
    def download_from_s3(self, bucket_name, file_name, local_path):
        """Download embeddings from S3"""
        s3 = boto3.client('s3')
        s3.download_file(bucket_name, f'embeddings/{file_name}', local_path)
        
    def upload_to_google_cloud(self, bucket_name, local_embeddings_dir):
        """Upload embeddings to Google Cloud Storage"""
        client = gcs.Client()
        bucket = client.bucket(bucket_name)
        
        files_to_upload = [
            'legal_embeddings_20250730_005323.npy',
            'legal_chunks_20250730_005323.json',
            'legal_rag_data_20250730_005323.pkl'
        ]
        
        for file_name in files_to_upload:
            local_path = os.path.join(local_embeddings_dir, file_name)
            if os.path.exists(local_path):
                blob = bucket.blob(f'embeddings/{file_name}')
                blob.upload_from_filename(local_path)
                print(f"✅ Uploaded {file_name} to Google Cloud")
                
    def download_from_url(self, url, local_path):
        """Download embeddings from any URL"""
        response = requests.get(url, stream=True)
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

def setup_s3_bucket():
    """Create S3 bucket and upload embeddings"""
    
    # Step 1: Create bucket
    bucket_name = 'mevzuat-ai-embeddings'  # Must be globally unique
    
    s3 = boto3.client('s3')
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Created bucket: {bucket_name}")
    except Exception as e:
        print(f"Bucket might already exist: {e}")
    
    # Step 2: Upload embeddings
    embeddings_dir = 'rag_system/embeddings_output'
    
    essential_files = [
        'legal_embeddings_20250730_005323.npy',
        'legal_chunks_20250730_005323.json',
        'embedding_stats_20250730_005323.json'
    ]
    
    for file_name in essential_files:
        local_path = os.path.join(embeddings_dir, file_name)
        if os.path.exists(local_path):
            try:
                s3.upload_file(local_path, bucket_name, f'embeddings/{file_name}')
                print(f"✅ Uploaded {file_name} ({os.path.getsize(local_path)/1024/1024:.1f} MB)")
            except Exception as e:
                print(f"❌ Failed to upload {file_name}: {e}")
        else:
            print(f"⚠️ File not found: {local_path}")

if __name__ == "__main__":
    print("🚀 Setting up cloud embeddings storage...")
    print("\n1. First install AWS CLI and configure credentials")
    print("2. Then run this script to upload embeddings")
    print("3. Update RAG system to load from S3")
    
    # Uncomment when ready:
    # setup_s3_bucket()