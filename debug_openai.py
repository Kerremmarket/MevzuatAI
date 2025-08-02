"""
Debug OpenAI client initialization
"""

import os
import sys

print("🔍 Debugging OpenAI Client...")
print(f"Python version: {sys.version}")

# Check environment variables
print("\n📋 Environment Variables:")
openai_key = os.getenv('OPENAI_API_KEY') 
openai_large = os.getenv('OPENAI_API_KEY_LARGE')
openai_nano = os.getenv('OPENAI_API_KEY_NANO')

print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
print(f"OPENAI_API_KEY_LARGE: {'✅ Set' if openai_large else '❌ Not set'}")
print(f"OPENAI_API_KEY_NANO: {'✅ Set' if openai_nano else '❌ Not set'}")

# Check for proxy-related env vars
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
print(f"\n🌐 Proxy Environment Variables:")
for var in proxy_vars:
    value = os.getenv(var)
    if value:
        print(f"{var}: {value}")
    else:
        print(f"{var}: Not set")

# Try importing OpenAI
print(f"\n📦 Testing OpenAI Import...")
try:
    from openai import OpenAI
    print("✅ OpenAI import successful")
    
    # Test client creation with minimal config
    print(f"\n🧪 Testing OpenAI Client Creation...")
    
    # Use the first available key
    api_key = openai_large or openai_nano or openai_key or "dummy-key-for-test"
    
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
        
        # Test a simple call (will fail with dummy key but should not crash on init)
        try:
            response = client.models.list()
            print("✅ OpenAI API call successful")
        except Exception as e:
            print(f"⚠️ API call failed (expected if using dummy key): {e}")
            
    except Exception as e:
        print(f"❌ OpenAI client creation failed: {e}")
        print(f"Error type: {type(e)}")
        
        # Try with explicit parameters
        print(f"\n🔧 Trying with explicit parameters...")
        try:
            client = OpenAI(
                api_key=api_key,
                timeout=30.0,
                max_retries=2
            )
            print("✅ OpenAI client with explicit params successful")
        except Exception as e2:
            print(f"❌ Still failed: {e2}")
        
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")

print(f"\n✅ Debug complete!")