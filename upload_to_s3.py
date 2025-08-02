"""
Simple script to upload embeddings to S3
Run this ONCE from your local machine
"""

import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def upload_embeddings():
    # Load credentials from .env file
    load_dotenv()
    
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('S3_EMBEDDINGS_BUCKET', 'mevzuat-ai-embeddings-kerem')
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='us-east-1'
    )
    
    # Files to upload (adjust paths if needed)
    files_to_upload = [
        {
            'local_path': 'rag_system/embeddings_output/legal_embeddings_20250730_005323.npy',
            's3_key': 'embeddings/legal_embeddings_20250730_005323.npy'
        },
        {
            'local_path': 'rag_system/embeddings_output/legal_chunks_20250730_005323.json',
            's3_key': 'embeddings/legal_chunks_20250730_005323.json'
        },
        {
            'local_path': 'rag_system/embeddings_output/embedding_stats_20250730_005323.json',
            's3_key': 'embeddings/embedding_stats_20250730_005323.json'
        }
    ]
    
    print("🚀 Starting upload to S3...")
    
    for file_info in files_to_upload:
        local_path = file_info['local_path']
        s3_key = file_info['s3_key']
        
        if not os.path.exists(local_path):
            print(f"❌ File not found: {local_path}")
            continue
            
        try:
            # Get file size for progress
            file_size = os.path.getsize(local_path)
            print(f"📤 Uploading {os.path.basename(local_path)} ({file_size / 1024 / 1024:.1f} MB)...")
            
            # Upload file
            s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
            print(f"✅ Successfully uploaded {os.path.basename(local_path)}")
            
        except ClientError as e:
            print(f"❌ Error uploading {local_path}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error uploading {local_path}: {e}")
    
    print("\n🎉 Upload complete! Your embeddings are now in S3.")
    print(f"Bucket: {BUCKET_NAME}")
    print("Next step: Add AWS credentials to Railway environment variables.")

if __name__ == "__main__":
    print("Before running this script:")
    print("1. Replace AWS_ACCESS_KEY_ID with your actual access key")
    print("2. Replace AWS_SECRET_ACCESS_KEY with your actual secret key") 
    print("3. Replace BUCKET_NAME with your actual bucket name")
    print("4. Make sure you're in the project root directory")
    print("\nReady? Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    upload_embeddings()