#!/usr/bin/env python3
"""
Test environment variables on Railway
"""

import os

def test_env():
    print("🔍 Testing Environment Variables on Railway")
    print("=" * 50)
    
    # Test all possible ways to get environment variables
    gemini_key = os.getenv('GEMINI_API_KEY')
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    
    print(f"GEMINI_API_KEY: {gemini_key}")
    print(f"PERPLEXITY_API_KEY: {perplexity_key}")
    
    # Test if they exist at all
    print(f"\nAll environment variables containing 'GEMINI':")
    for key, value in os.environ.items():
        if 'GEMINI' in key.upper():
            print(f"  {key} = {value}")
    
    print(f"\nAll environment variables containing 'PERPLEXITY':")
    for key, value in os.environ.items():
        if 'PERPLEXITY' in key.upper():
            print(f"  {key} = {value}")
    
    # Test direct access
    print(f"\nDirect access test:")
    print(f"os.environ.get('GEMINI_API_KEY'): {os.environ.get('GEMINI_API_KEY')}")
    print(f"os.environ.get('PERPLEXITY_API_KEY'): {os.environ.get('PERPLEXITY_API_KEY')}")
    
    if gemini_key and perplexity_key:
        print("\n✅ Environment variables are accessible!")
        return True
    else:
        print("\n❌ Environment variables are NOT accessible!")
        return False

if __name__ == "__main__":
    test_env()
