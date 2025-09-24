# 🚀 Railway Deployment Guide for Genie Backend

## ✅ Perfect Match for Your Flask App!

Railway is ideal for your Genie Backend because it supports:
- ✅ **Full Flask applications**
- ✅ **Docker deployment**
- ✅ **Persistent storage**
- ✅ **Background processes**
- ✅ **Environment variables**
- ✅ **Free tier available**

## 🎯 Quick Deployment Steps

### **Step 1: Go to Railway**
Visit: https://railway.app

### **Step 2: Sign Up/Login**
- Use GitHub account (recommended)
- Or email signup

### **Step 3: Create New Project**
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **`genie`** repository
4. Click **"Deploy Now"**

### **Step 4: Railway Auto-Detection**
Railway will automatically detect:
- ✅ **Dockerfile** (uses it for deployment)
- ✅ **Python application**
- ✅ **Port configuration**

### **Step 5: Set Environment Variables**
In Railway Dashboard → Variables tab:

```
GEMINI_API_KEY=your_gemini_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=https://your-app-name.railway.app/auth/callback
FLASK_ENV=production
PYTHONPATH=/app
```

### **Step 6: Deploy!**
- Railway will build and deploy automatically
- Watch the build logs
- Get your live URL!

## 🔧 Configuration Files

### **Dockerfile** (Already Ready)
- ✅ Uses Python 3.9
- ✅ Installs all dependencies
- ✅ Configures for Railway's dynamic port
- ✅ Includes health checks

### **railway.json** (Added)
- ✅ Railway-specific configuration
- ✅ Health check settings
- ✅ Restart policies

### **requirements.txt** (Ready)
- ✅ All Flask dependencies
- ✅ Google Calendar API
- ✅ AI integrations
- ✅ Production server (Gunicorn)

## 🌐 Your Live URL

After deployment, you'll get:
- **Live URL**: `https://your-app-name.railway.app`
- **Health Check**: `https://your-app-name.railway.app/health`
- **API**: `https://your-app-name.railway.app/api/`

## 📊 Railway Free Tier

### **What's Included:**
- ✅ **$5 credit monthly** (usually enough for small apps)
- ✅ **512MB RAM**
- ✅ **1GB storage**
- ✅ **Custom domains**
- ✅ **Environment variables**
- ✅ **GitHub integration**

### **Usage Monitoring:**
- Check usage in Railway dashboard
- Upgrade if needed (very reasonable pricing)

## 🔍 Troubleshooting

### **Build Issues:**
```bash
# Check build logs in Railway dashboard
# Common fixes:
# 1. Ensure all dependencies in requirements.txt
# 2. Check Dockerfile syntax
# 3. Verify environment variables
```

### **Runtime Issues:**
```bash
# Check application logs
# Common fixes:
# 1. Verify environment variables are set
# 2. Check port configuration
# 3. Ensure health check endpoint works
```

### **Health Check:**
Visit: `https://your-app-name.railway.app/health`

Should return:
```json
{
  "status": "healthy",
  "service": "Genie Backend",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🚀 Advanced Features

### **Custom Domain:**
1. Go to Railway Dashboard → Settings
2. Add custom domain
3. Update DNS records
4. SSL automatically configured

### **Database (Optional):**
Railway offers PostgreSQL add-ons:
1. Add PostgreSQL service
2. Get connection string
3. Update your app to use database instead of JSON files

### **Monitoring:**
- Built-in metrics
- Log aggregation
- Performance monitoring

## 🔄 Updates

### **Automatic Deployments:**
- Push to GitHub → Auto-deploy
- No manual intervention needed

### **Manual Deployments:**
- Railway Dashboard → Deployments
- Click "Redeploy" if needed

## 💡 Pro Tips

1. **Environment Variables**: Set them in Railway dashboard, not in code
2. **Logs**: Check Railway dashboard for real-time logs
3. **Scaling**: Railway auto-scales based on traffic
4. **Backups**: Railway handles infrastructure backups
5. **Security**: HTTPS enabled by default

## 🎉 Success!

Once deployed, your Genie Backend will have:
- ✅ **Full AI-powered task management**
- ✅ **Google Calendar integration**
- ✅ **Persistent storage**
- ✅ **Background processes**
- ✅ **Production-ready performance**
- ✅ **Automatic scaling**

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Community**: https://discord.gg/railway
- **Status**: https://status.railway.app

---

**Your Genie Backend is perfect for Railway! 🚀**
