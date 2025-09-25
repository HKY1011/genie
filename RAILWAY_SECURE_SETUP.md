# 🔐 Secure Railway Environment Setup Guide

## ⚠️ Security Issue Fixed

The previous version had hardcoded API keys in the code, which is a **major security risk**. This has been fixed and the system now properly uses environment variables.

## 🚀 How to Set Up Environment Variables in Railway

### Step 1: Get Your API Keys

You'll need these API keys:

1. **GEMINI_API_KEY** - Your Google Gemini API key
2. **PERPLEXITY_API_KEY** - Your Perplexity API key  
3. **GOOGLE_CLIENT_ID** - Google OAuth client ID for calendar
4. **GOOGLE_CLIENT_SECRET** - Google OAuth client secret for calendar

### Step 2: Set Variables in Railway Dashboard

1. Go to your Railway project dashboard
2. Click on the **"Variables"** tab
3. Add each environment variable:

```
GEMINI_API_KEY = your_gemini_api_key_here
PERPLEXITY_API_KEY = your_perplexity_api_key_here
GOOGLE_CLIENT_ID = your_google_client_id_here
GOOGLE_CLIENT_SECRET = your_google_client_secret_here
```

### Step 3: Deploy

After setting the variables:
1. Railway will automatically restart your app
2. The app will use the secure environment variables
3. No API keys are exposed in your code

## 🔒 Security Best Practices

✅ **DO:**
- Store API keys in Railway's Variables tab
- Use environment variables in your code
- Keep your `.env` file local only
- Never commit API keys to git

❌ **DON'T:**
- Hardcode API keys in your source code
- Share API keys in chat/email
- Commit `.env` files to git
- Use the same API key across multiple projects

## 🛠️ Local Development

For local development, create a `.env` file in your project root:

```bash
# .env (DO NOT COMMIT THIS FILE)
GEMINI_API_KEY=your_gemini_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

## 🔍 Verify Setup

Run this command to check your environment variables:

```bash
python railway_env_setup_secure.py
```

This will show you which variables are set (without exposing the actual values).

## 🚨 If You See API Key Errors

If you get "API key is required" errors:

1. Check that all variables are set in Railway dashboard
2. Verify the variable names match exactly (case-sensitive)
3. Make sure there are no extra spaces in the values
4. Redeploy your app after setting variables

## 📞 Support

If you need help:
1. Check Railway logs for specific error messages
2. Verify all environment variables are set correctly
3. Make sure your API keys are valid and active

---

**Remember: Security is everyone's responsibility. Keep your API keys safe!** 🔐
