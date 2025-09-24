#!/usr/bin/env python3
"""
Railway Environment Setup - Final Solution
This script will help you set up environment variables correctly
"""

import os
from dotenv import load_dotenv

def main():
    print("🚀 Railway Environment Setup - Final Solution")
    print("=" * 50)
    
    # Load local .env file
    try:
        load_dotenv()
        print("✅ Loaded local .env file")
    except:
        print("ℹ️  No local .env file found")
    
    # Check what we have
    gemini_key = os.getenv('GEMINI_API_KEY')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    print("\n📋 Current Environment Variables:")
    print(f"GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Missing'}")
    print(f"PERPLEXITY_API_KEY: {'✅ Set' if perplexity_key else '❌ Missing'}")
    print(f"GOOGLE_CLIENT_ID: {'✅ Set' if google_client_id else '❌ Missing'}")
    print(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if google_client_secret else '❌ Missing'}")
    
    if gemini_key and perplexity_key:
        print("\n🎉 You have the main API keys!")
        print("\n📋 Copy these to Railway Dashboard:")
        print("=" * 50)
        print(f"GEMINI_API_KEY = {gemini_key}")
        print(f"PERPLEXITY_API_KEY = {perplexity_key}")
        if google_client_id:
            print(f"GOOGLE_CLIENT_ID = {google_client_id}")
        if google_client_secret:
            print(f"GOOGLE_CLIENT_SECRET = {google_client_secret}")
        print("=" * 50)
        
        print("\n🚀 Steps to fix Railway:")
        print("1. Go to: https://railway.app")
        print("2. Click your Genie Backend project")
        print("3. Click 'Variables' tab")
        print("4. Add each variable above")
        print("5. Railway will auto-redeploy")
        
    else:
        print("\n❌ Missing API keys!")
        print("\n🔑 Get your API keys:")
        print("1. Gemini: https://aistudio.google.com/")
        print("2. Perplexity: https://www.perplexity.ai/settings/api")
        print("3. Add them to .env file, then run this script again")

if __name__ == "__main__":
    main()
