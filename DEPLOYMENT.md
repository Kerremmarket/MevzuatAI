# 🚀 Railway Deployment Guide for mevzuatAI

## 🎯 Overview
This guide sets up **automatic deployment** from GitHub to Railway. Your app will work seamlessly in both **localhost** and **production** without code changes.

## ✅ Features
- **Auto-detects environment** (localhost vs Railway)
- **Dynamic API endpoints** (no hardcoded URLs)
- **One-click deployment** from GitHub
- **Environment-specific settings** (debug mode, host, port)
- **Instant updates** when you push to GitHub

---

## 🔧 Setup Instructions

### 1. **Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Connect your GitHub account

### 2. **Deploy from GitHub**
1. Click **"New Project"** in Railway
2. Select **"Deploy from GitHub repo"**
3. Choose your `mevzuatAI` repository
4. Railway will automatically detect it's a Python Flask app

### 3. **Set Environment Variables**
In Railway dashboard, go to **Variables** and add:
```
OPENAI_API_KEY=your-actual-openai-key-here
ENVIRONMENT=production
```

### 4. **Domain Setup (Optional)**
- Railway gives you a free `.railway.app` subdomain
- You can add your custom domain later in **Settings > Domains**

---

## 🔄 How It Works

### **Local Development:**
```bash
# Your app runs on localhost:5000
python frontend/app.py
```
- ✅ Debug mode ON
- ✅ Host: localhost
- ✅ API calls: `http://localhost:5000/api/ask`

### **Production (Railway):**
- ✅ Debug mode OFF
- ✅ Host: 0.0.0.0 (Railway's requirement)
- ✅ Port: Auto-detected from Railway
- ✅ API calls: `https://your-app.railway.app/api/ask`

---

## 🚀 Deployment Workflow

1. **Develop locally** - Test everything on `localhost:5000`
2. **Push to GitHub** - Your changes go to your repo
3. **Auto-deploy** - Railway automatically deploys the latest version
4. **Live in ~2 minutes** - Your app is updated on Railway

### Example:
```bash
# 1. Make changes locally and test
git add .
git commit -m "Added new feature"

# 2. Push to GitHub
git push origin main

# 3. Railway automatically deploys! ✨
# Check your Railway dashboard for deployment status
```

---

## 📁 Files Added for Deployment

- `railway.toml` - Railway configuration
- `Procfile` - Start command for Railway
- `.gitignore` - What not to upload to GitHub
- `DEPLOYMENT.md` - This guide

---

## 🛠️ Troubleshooting

### **If deployment fails:**
1. Check Railway logs in dashboard
2. Verify all files are in `the_project/` folder
3. Make sure `requirements.txt` is complete

### **If API calls fail:**
- Check browser console for errors
- Verify the app is running in Railway dashboard
- Check environment variables are set

### **Local testing:**
```bash
# Always test locally first
cd the_project
python frontend/app.py
# Open http://localhost:5000
```

---

## 🎉 Benefits

✅ **No more manual config changes**  
✅ **Test locally, deploy instantly**  
✅ **Automatic HTTPS on Railway**  
✅ **Free Railway tier for demos**  
✅ **Perfect for ad network requirements**  

Your mevzuatAI is now ready for professional deployment! 🚀📚⚖️