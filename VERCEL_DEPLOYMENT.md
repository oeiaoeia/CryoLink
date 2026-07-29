# CryoLink Vercel Deployment Guide

## ⚠️ Critical: Database Requirement

**Vercel is serverless - SQLite data will be lost after each request!**

You **MUST** use PostgreSQL for Vercel deployment.

---

## 📋 Step-by-Step Deployment

### **Step 1: Create PostgreSQL Database (FREE)**

#### Option A: Neon.tech (Recommended)
1. Go to https://neon.tech
2. Sign up with GitHub
3. Create new project: `cryolink`
4. Copy the connection string (looks like `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname`)

#### Option B: Supabase
1. Go to https://supabase.com
2. Create new project
3. Go to Settings → Database
4. Copy the "Connection string (URI)"

---

### **Step 2: Update Environment Variables**

In Vercel Dashboard → Project Settings → Environment Variables:

```bash
FLASK_ENV=production
SECRET_KEY=super-secret-key-CHANGE-THIS-UNIQUE-KEY
DATABASE_URL=postgresql://user:pass@host.neon.tech:5432/cryolink
```

**⚠️ IMPORTANT:** Use a strong unique SECRET_KEY for production!

---

### **Step 3: Update vercel.json (Already Done)**

The `vercel.json` is configured to use `main.py` as entry point.

---

### **Step 4: Initialize Database**

After first deployment, you need to initialize the database:

1. Go to Vercel Dashboard → Your Project
2. Click "Functions" tab
3. Or use Vercel CLI:

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Run database initialization
vercel env pull  # Pull environment variables
source .env.local
python init_db.py
```

---

### **Step 5: Deploy**

```bash
# Install Vercel CLI (if not installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

---

## 🔧 Alternative: Use Railway (EASIER - Recommended)

**Railway is MUCH better for Flask apps like CryoLink:**

✅ Free tier ($5/month credit)  
✅ SQLite works fine (persistent storage)  
✅ Auto-detects Flask  
✅ Built-in PostgreSQL option  
✅ No configuration needed  

### Deploy to Railway:

1. Go to https://railway.app
2. Click "New Project"
3. "Deploy from GitHub repo"
4. Select your CryoLink repository
5. Railway auto-deploys!

**That's it!** No database configuration needed (uses SQLite by default).

To add PostgreSQL on Railway:
1. Click "New" → "Database" → "PostgreSQL"
2. Add `DATABASE_URL` variable to your service
3. Railway connects automatically

---

## 📊 Platform Comparison

| Feature | Vercel | Railway |
|---------|--------|---------|
| Free Tier | ✅ Yes | ✅ $5 credit |
| SQLite Support | ❌ No | ✅ Yes |
| Flask Support | ⚠️ Limited | ✅ Full |
| Setup Complexity | 🔴 High | 🟢 Low |
| Database Included | ❌ Need external | ✅ Built-in |
| Deployment Speed | 2-5 min | 1-2 min |

---

## 🎯 Recommendation

**Use Railway for CryoLink** - It's designed for traditional web apps like Flask!

Vercel is best for:
- Next.js / React frontends
- Static sites
- API-only backends

Railway is best for:
- Flask/Django apps
- Apps with SQLite
- Traditional server apps

---

## 🐛 Troubleshooting

### Error: "No module named 'dotenv'"
```bash
# Make sure requirements.txt has:
python-dotenv==1.0.0
```

### Error: "database disk image is malformed"
**Cause:** Using SQLite on Vercel (doesn't persist)  
**Solution:** Switch to PostgreSQL (Neon.tech or Supabase)

### Error: "DATABASE_URL not set"
1. Go to Vercel Dashboard → Project Settings
2. Add `DATABASE_URL` environment variable
3. Redeploy: `vercel --prod`

### App loads but shows errors
Check logs:
```bash
vercel logs <deployment-url>
```

---

## ✅ Quick Checklist for Vercel

- [ ] Created PostgreSQL database (Neon/Supabase)
- [ ] Added `DATABASE_URL` to Vercel env vars
- [ ] Added `SECRET_KEY` to Vercel env vars
- [ ] Set `FLASK_ENV=production`
- [ ] Installed Vercel CLI
- [ ] Ready to deploy!

---

## 🚀 Deploy Commands

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Link to your project
vercel link

# 4. Pull environment variables
vercel env pull

# 5. Deploy
vercel --prod
```

---

**Need help?** Check Vercel logs: `vercel logs --follow`
