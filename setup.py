"""
Setup script for Legal AI System
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("\n🔧 Environment Setup")
    print("=" * 30)
    
    api_key = input("Enter your OpenAI API Key: ").strip()
    
    if not api_key:
        print("❌ OpenAI API Key is required")
        return False
    
    # Set environment variable for current session
    os.environ['OPENAI_API_KEY'] = api_key
    
    print("✅ Environment configured for this session")
    print("\n💡 To make this permanent, add this to your system environment:")
    print(f"   OPENAI_API_KEY={api_key}")
    
    return True

def check_data_files():
    """Check if required data files exist"""
    print("\n📁 Checking data files...")
    
    dataset_path = "data/mevzuat_combined_final.xlsx"
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        print("Please copy your dataset to the data/ folder")
        return False
    
    print("✅ Dataset found")
    
    # Check for RAG embeddings
    embeddings_dir = "rag_system/embeddings_output"
    if not os.path.exists(embeddings_dir):
        print(f"⚠️ RAG embeddings not found: {embeddings_dir}")
        print("You may need to copy embeddings from your existing system")
        return False
    
    print("✅ RAG embeddings found")
    return True

def main():
    """Main setup function"""
    print("🏛️ Legal AI System Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Setup environment
    if not setup_environment():
        return
    
    # Check data files
    data_ok = check_data_files()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Run: python main.py (for command line interface)")
    print("2. Run: python frontend/app.py (for web interface)")
    print("3. Open: http://localhost:5000 (for web interface)")
    
    if not data_ok:
        print("\n⚠️ Note: Some data files are missing. Please:")
        print("- Copy your dataset to data/mevzuat_combined_final.xlsx")
        print("- Copy RAG embeddings to rag_system/embeddings_output/")

if __name__ == "__main__":
    main()