#!/usr/bin/env python3
"""
Environment variable helper for Railway deployment
Handles both .env files (local) and environment variables (Railway)
"""

import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file if it exists (local development)"""
    try:
        # Try to load .env file (for local development)
        load_dotenv()
        print("✅ Loaded .env file for local development")
    except Exception as e:
        print(f"ℹ️  No .env file found (Railway deployment): {e}")

def get_required_env_vars():
    """Get all required environment variables with helpful error messages"""
    required_vars = {
        'GEMINI_API_KEY': 'Your Gemini API key from Google AI Studio',
        'PERPLEXITY_API_KEY': 'Your Perplexity API key from Perplexity AI',
        'GOOGLE_CLIENT_ID': 'Google OAuth2 Client ID for Calendar integration',
        'GOOGLE_CLIENT_SECRET': 'Google OAuth2 Client Secret for Calendar integration'
    }
    
    missing_vars = []
    env_status = {}
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            env_status[var] = "✅ Set"
        else:
            env_status[var] = "❌ Missing"
            missing_vars.append((var, description))
    
    return env_status, missing_vars

def check_environment():
    """Check environment variables and provide helpful messages"""
    print("🔍 Checking environment variables...")
    
    # Load environment
    load_environment()
    
    # Check required variables
    env_status, missing_vars = get_required_env_vars()
    
    print("\n📋 Environment Variables Status:")
    for var, status in env_status.items():
        print(f"  {var}: {status}")
    
    if missing_vars:
        print(f"\n❌ Missing {len(missing_vars)} required environment variables:")
        for var, description in missing_vars:
            print(f"  • {var}: {description}")
        
        print("\n🚀 To fix this:")
        print("1. For Railway deployment:")
        print("   - Go to Railway Dashboard → Your Project → Variables")
        print("   - Add each missing variable with its value")
        print("2. For local development:")
        print("   - Create a .env file in the project root")
        print("   - Add each variable: VARIABLE_NAME=your_value")
        
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

if __name__ == "__main__":
    check_environment()
