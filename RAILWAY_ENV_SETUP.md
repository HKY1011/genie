# 🔑 Railway Environment Variables Setup

## ❌ Current Issue
Railway can't access your API keys because they're not set as environment variables.

## ✅ Solution: Set Environment Variables in Railway

### **Step 1: Go to Railway Dashboard**
1. Visit: https://railway.app
2. Login to your account
3. Click on your **Genie Backend** project

### **Step 2: Add Environment Variables**
1. Click on the **"Variables"** tab
2. Click **"New Variable"** for each API key

### **Step 3: Add These Variables**

#### **Required API Keys:**
```
GEMINI_API_KEY = your_gemini_api_key_here
PERPLEXITY_API_KEY = your_perplexity_api_key_here
GOOGLE_CLIENT_ID = your_google_client_id_here
GOOGLE_CLIENT_SECRET = your_google_client_secret_here
```

#### **Optional Configuration:**
```
FLASK_ENV = production
PYTHONPATH = /app
GOOGLE_REDIRECT_URI = https://your-app-name.railway.app/auth/callback
```

### **Step 4: Get Your API Keys**

#### **Gemini API Key:**
1. Go to: https://aistudio.google.com/
2. Click **"Get API Key"**
3. Create a new API key
4. Copy the key

#### **Perplexity API Key:**
1. Go to: https://www.perplexity.ai/settings/api
2. Create a new API key
3. Copy the key

#### **Google Calendar API:**
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth2 credentials
5. Get Client ID and Client Secret

### **Step 5: Redeploy**
After adding all environment variables:
1. Railway will automatically redeploy
2. Or click **"Redeploy"** button manually

## 🔍 Verify Environment Variables

### **Check Railway Logs:**
1. Go to Railway Dashboard → Your Project
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. Check the logs for environment variable status

### **Test Your App:**
Visit: `https://your-app-name.railway.app/health`

Should return:
```json
{
  "status": "healthy",
  "apis": {
    "gemini_api": true,
    "perplexity_api": true,
    "calendar_api": true,
    "storage": true
  }
}
```

## 🚨 Common Issues

### **Issue 1: "API key not found"**
**Solution:** Make sure you added the exact variable name in Railway:
- `GEMINI_API_KEY` (not `gemini_api_key`)
- `PERPLEXITY_API_KEY` (not `perplexity_api_key`)

### **Issue 2: "Invalid API key"**
**Solution:** 
- Check if you copied the key correctly
- Make sure there are no extra spaces
- Verify the key is active in the API provider's dashboard

### **Issue 3: "Environment variable not loaded"**
**Solution:**
- Redeploy your Railway project
- Check Railway logs for errors
- Verify variable names match exactly

## 📋 Environment Variables Checklist

- [ ] `GEMINI_API_KEY` - Gemini API key from Google AI Studio
- [ ] `PERPLEXITY_API_KEY` - Perplexity API key from Perplexity AI
- [ ] `GOOGLE_CLIENT_ID` - Google OAuth2 Client ID
- [ ] `GOOGLE_CLIENT_SECRET` - Google OAuth2 Client Secret
- [ ] `FLASK_ENV` - Set to "production"
- [ ] `PYTHONPATH` - Set to "/app"

## 🎯 Quick Test

Run this in your local terminal to test environment variables:
```bash
python env_helper.py
```

This will check if all required environment variables are set.

## 📞 Need Help?

1. **Check Railway Logs** for specific error messages
2. **Verify API Keys** in their respective dashboards
3. **Redeploy** after adding environment variables
4. **Test Health Endpoint** to verify all APIs are working

---

**After setting these environment variables, your Genie Backend should work perfectly on Railway! 🚀**
