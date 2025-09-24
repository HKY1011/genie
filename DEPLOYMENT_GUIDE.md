# 🚀 Genie Backend Deployment Guide

This guide covers multiple deployment options for your Genie Backend system.

## 📋 Prerequisites

1. **API Keys Setup**:
   - Google Gemini API key
   - Perplexity API key
   - Google Calendar API credentials

2. **Google Calendar Setup**:
   - Download `credentials.json` from Google Cloud Console
   - Place it in the project root directory

## 🎯 Deployment Options

### Option 1: Local Development Server

**Best for**: Development and testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Run the development server
python web_server.py
```

**Access**: http://localhost:5000

---

### Option 2: Docker Deployment

**Best for**: Easy deployment, consistent environment

#### Single Container:
```bash
# Build and run
docker build -t genie-backend .
docker run -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  -e PERPLEXITY_API_KEY=your_key \
  -v $(pwd)/storage:/app/storage \
  -v $(pwd)/credentials.json:/app/credentials.json \
  genie-backend
```

#### Docker Compose (Recommended):
```bash
# Set up environment
cp env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# View logs
docker-compose logs -f genie-backend
```

**Access**: http://localhost:5000

---

### Option 3: Cloud Deployment

#### A. Heroku (Easiest)

1. **Install Heroku CLI**
2. **Create Heroku app**:
   ```bash
   heroku create your-genie-app
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set PERPLEXITY_API_KEY=your_key
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

5. **Add Google Calendar credentials**:
   ```bash
   # Upload credentials.json
   heroku run bash
   # Then upload your credentials.json file
   ```

**Access**: https://your-genie-app.herokuapp.com

#### B. DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Configure environment variables** in the dashboard
3. **Upload credentials.json** via file upload
4. **Deploy automatically**

#### C. AWS EC2

1. **Launch EC2 instance** (Ubuntu 20.04+)
2. **Install Docker**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker ubuntu
   ```

3. **Clone and deploy**:
   ```bash
   git clone your-repo
   cd genie_backend
   cp env.example .env
   # Edit .env
   docker-compose up -d
   ```

4. **Configure security groups** (open ports 80, 443, 22)

#### D. Google Cloud Run

1. **Build and push to Google Container Registry**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/genie-backend
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy genie-backend \
     --image gcr.io/PROJECT-ID/genie-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

---

### Option 4: VPS Deployment (DigitalOcean, Linode, etc.)

**Best for**: Full control, cost-effective

1. **Set up VPS** (Ubuntu 20.04+)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx certbot python3-certbot-nginx
   ```

3. **Deploy application**:
   ```bash
   git clone your-repo
   cd genie_backend
   pip3 install -r requirements.txt
   ```

4. **Set up systemd service**:
   ```bash
   sudo nano /etc/systemd/system/genie-backend.service
   ```

   ```ini
   [Unit]
   Description=Genie Backend
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/genie_backend
   Environment=PATH=/home/ubuntu/genie_backend/venv/bin
   ExecStart=/home/ubuntu/genie_backend/venv/bin/gunicorn --bind 0.0.0.0:5000 web_server:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Configure Nginx**:
   ```bash
   sudo nano /etc/nginx/sites-available/genie-backend
   ```

   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

6. **Enable SSL**:
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

---

## 🔧 Production Configuration

### Environment Variables

Create `.env` file with:
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
FLASK_ENV=production
SECRET_KEY=your_secret_key

# Optional
HOST=0.0.0.0
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
```

### Security Considerations

1. **Never commit** `.env`, `credentials.json`, or `token.json`
2. **Use HTTPS** in production
3. **Set up proper CORS** origins
4. **Regular backups** of storage directory
5. **Monitor logs** for errors

### Monitoring

1. **Health checks**: `/health` endpoint
2. **Logs**: Check application logs regularly
3. **Uptime monitoring**: Use services like UptimeRobot
4. **Error tracking**: Consider Sentry integration

---

## 🚀 Quick Start Commands

### Local Development:
```bash
pip install -r requirements.txt
cp env.example .env
# Edit .env
python web_server.py
```

### Docker:
```bash
cp env.example .env
# Edit .env
docker-compose up -d
```

### Production (VPS):
```bash
git clone your-repo
cd genie_backend
pip3 install -r requirements.txt
cp env.example .env
# Edit .env
gunicorn --bind 0.0.0.0:5000 web_server:app
```

---

## 🔍 Troubleshooting

### Common Issues:

1. **Google Calendar API errors**:
   - Check `credentials.json` is in project root
   - Verify OAuth2 consent screen is configured
   - Delete `token.json` to re-authenticate

2. **API key errors**:
   - Verify API keys in `.env` file
   - Check API quotas and billing

3. **Port conflicts**:
   - Change port in configuration
   - Check if port 5000 is already in use

4. **Permission errors**:
   - Ensure proper file permissions
   - Check Docker volume mounts

### Logs:
```bash
# Docker
docker-compose logs -f genie-backend

# Systemd
sudo journalctl -u genie-backend -f

# Direct
tail -f genie_production.log
```

---

## 📞 Support

If you encounter issues:
1. Check the logs
2. Verify environment variables
3. Test API connections
4. Check Google Calendar setup

**Happy Deploying! 🎉**
