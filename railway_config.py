#!/usr/bin/env python3
"""
Railway Configuration - Hardcoded API Keys
This ensures the app works on Railway even if environment variables fail
"""

import os

# Hardcoded API keys for Railway deployment
RAILWAY_API_KEYS = {
    'GEMINI_API_KEY': 'AIzaSyDjhJnJdnbhVH0njqro60JMBhTZ-DhcJfY',
    'PERPLEXITY_API_KEY': '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'
}

def get_api_key(key_name):
    """
    Get API key with fallback to hardcoded values
    """
    # First try environment variable
    env_value = os.getenv(key_name)
    if env_value:
        return env_value
    
    # Fallback to hardcoded value
    if key_name in RAILWAY_API_KEYS:
        return RAILWAY_API_KEYS[key_name]
    
    return None

def setup_environment():
    """
    Set up environment variables for Railway
    """
    print("🔧 Setting up Railway environment...")
    
    for key, value in RAILWAY_API_KEYS.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"✅ Set {key} from hardcoded value")
        else:
            print(f"✅ {key} already set from environment")

if __name__ == "__main__":
    setup_environment()
    print("\n🎉 Environment setup complete!")
