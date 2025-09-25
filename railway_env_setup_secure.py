#!/usr/bin/env python3
"""
Secure Railway Environment Setup Helper
This script helps you set up environment variables in Railway without exposing API keys
"""

import os
from dotenv import load_dotenv

def main():
    print("🔐 Railway Environment Variables Setup")
    print("=" * 50)
    
    # Load local .env file if it exists
    try:
        load_dotenv()
        print("✅ Loaded local .env file")
    except:
        print("ℹ️  No local .env file found")
    
    # Check what variables are available locally
    required_vars = {
        'GEMINI_API_KEY': 'Your Gemini API key for AI processing',
        'PERPLEXITY_API_KEY': 'Your Perplexity API key for web search',
        'GOOGLE_CLIENT_ID': 'Google OAuth client ID for calendar integration',
        'GOOGLE_CLIENT_SECRET': 'Google OAuth client secret for calendar integration'
    }
    
    print("\n📋 Required Environment Variables for Railway:")
    print("-" * 50)
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Show only first 8 characters for security
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var_name}: {masked_value}")
        else:
            print(f"❌ {var_name}: NOT SET")
    
    print("\n🚀 How to set these in Railway:")
    print("-" * 50)
    print("1. Go to your Railway project dashboard")
    print("2. Click on the 'Variables' tab")
    print("3. Add each variable with its value:")
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            print(f"   • {var_name} = [your {var_name.lower().replace('_', ' ')}]")
        else:
            print(f"   • {var_name} = [you need to get this value]")
    
    print("\n🔒 Security Notes:")
    print("-" * 50)
    print("• Never commit API keys to git")
    print("• Use Railway's Variables tab for secure storage")
    print("• Each variable is encrypted in Railway")
    print("• Keys are only accessible to your deployed app")
    
    print("\n✨ After setting variables in Railway:")
    print("-" * 50)
    print("• Your app will automatically restart")
    print("• Environment variables will be available")
    print("• No hardcoded keys in your code")

if __name__ == "__main__":
    main()
