#!/usr/bin/env python3
"""
Railway Configuration - Environment Variable Helper
This helps ensure environment variables are properly loaded on Railway
"""

import os

def check_required_env_vars():
    """
    Check if all required environment variables are set
    """
    required_vars = [
        'GEMINI_API_KEY',
        'PERPLEXITY_API_KEY',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def setup_environment():
    """
    Set up environment variables for Railway
    Only sets variables if they're not already set (from Railway dashboard)
    """
    print("🔧 Checking Railway environment variables...")
    
    missing_vars = check_required_env_vars()
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please set these in your Railway dashboard:")
        print("   1. Go to your Railway project")
        print("   2. Click on 'Variables' tab")
        print("   3. Add the missing variables")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

if __name__ == "__main__":
    success = setup_environment()
    if success:
        print("\n🎉 Environment setup complete!")
    else:
        print("\n⚠️  Please configure environment variables in Railway dashboard")
