# 🚀 Vercel Deployment Guide for Genie Backend

## ⚠️ Important Notes

**Vercel is primarily designed for frontend applications and serverless functions.** Your Genie Backend is a full Flask application with persistent state, which has some limitations on Vercel:

### **Vercel Limitations:**
- ⏱️ **10-second timeout** for serverless functions
- 📁 **No persistent file system** (files reset on each request)
- 🔄 **No background processes**
- 🏗️ **Stateless architecture** required

### **What This Means:**
- ✅ **Basic API endpoints** will work
- ✅ **Task CRUD operations** will work (in-memory)
- ❌ **Persistent storage** will not work (tasks reset on each request)
- ❌ **Google Calendar integration** may have timeout issues
- ❌ **Complex AI workflows** may timeout

## 🛠️ Deployment Steps

### **Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

### **Step 2: Login to Vercel**
```bash
vercel login
```

### **Step 3: Deploy from GitHub**
1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "New Project"**
3. **Import from GitHub**: Select your `genie` repository
4. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `/` (default)
   - **Build Command**: `pip install -r requirements-vercel.txt`
   - **Output Directory**: `/` (default)

### **Step 4: Set Environment Variables**
In Vercel Dashboard → Project Settings → Environment Variables:

```
GEMINI_API_KEY=your_gemini_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-vercel-app.vercel.app/auth/callback
```

### **Step 5: Deploy**
```bash
vercel --prod
```

## 🔧 Alternative: Full-Featured Deployment

For the complete Genie Backend experience, consider these alternatives:

### **Option 1: Railway (Recommended)**
- ✅ **Full Flask support**
- ✅ **Persistent storage**
- ✅ **Background processes**
- ✅ **Free tier available**

### **Option 2: Heroku**
- ✅ **Full Flask support**
- ✅ **Persistent storage**
- ✅ **Background processes**
- ⚠️ **Paid plans only**

### **Option 3: DigitalOcean App Platform**
- ✅ **Full Flask support**
- ✅ **Persistent storage**
- ✅ **Background processes**
- ✅ **Reasonable pricing**

## 📁 Vercel-Compatible Files

The following files have been created for Vercel deployment:

- `vercel.json` - Vercel configuration
- `vercel_server.py` - Simplified Flask server
- `api/` - Serverless function endpoints
- `requirements-vercel.txt` - Minimal dependencies

## 🧪 Testing Vercel Deployment

### **Local Testing:**
```bash
# Install Vercel CLI
npm install -g vercel

# Test locally
vercel dev
```

### **API Endpoints:**
- `GET /api/health` - Health check
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task

## 🚨 Limitations in Vercel Version

### **What's Missing:**
- ❌ **Persistent task storage** (tasks reset on each request)
- ❌ **Google Calendar integration** (timeout issues)
- ❌ **AI-powered task prioritization** (complex workflows)
- ❌ **Background processing** (scheduling, notifications)
- ❌ **File-based storage** (JSON files)

### **What Works:**
- ✅ **Basic task CRUD operations**
- ✅ **REST API endpoints**
- ✅ **Health monitoring**
- ✅ **CORS support**
- ✅ **Error handling**

## 🔄 Migration to Full-Featured Platform

To get the complete Genie Backend experience:

1. **Use Railway/Heroku/DigitalOcean** instead of Vercel
2. **Keep the original `web_server.py`** and `main.py`
3. **Use the full `requirements.txt`**
4. **Enable persistent storage** and background processes

## 📞 Support

If you need help with deployment or want to migrate to a full-featured platform, the original deployment guides are available:

- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment options
- `Dockerfile` - Docker deployment
- `docker-compose.yml` - Local Docker setup

---

**Note**: This Vercel deployment is a simplified version for demonstration purposes. For production use with full features, consider Railway, Heroku, or DigitalOcean.
