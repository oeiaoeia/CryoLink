# Quick Deployment Guide

## 🚀 Deploy to Vercel

### Prerequisites
1. **PostgreSQL Database** (SQLite won't work on Vercel)
   - Create free DB at: https://neon.tech
   - Copy connection string

2. **Vercel Account**
   - Sign up at: https://vercel.com

### Deploy Steps

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Run deployment script
./deploy-vercel.sh
```

### Environment Variables (Set in Vercel Dashboard)

Go to: Project Settings → Environment Variables

```
FLASK_ENV=production
SECRET_KEY=your-unique-secret-key-here
DATABASE_URL=postgresql://user:pass@host.neon.tech:5432/dbname
```

---

## 🎯 EASIER: Deploy to Railway (Recommended)

**Railway is better for Flask apps!**

✅ SQLite works (persistent storage)  
✅ Auto-detects Flask  
✅ No configuration needed  
✅ Free $5/month credit  

### Deploy Steps

1. Go to https://railway.app
2. Click "New Project"
3. "Deploy from GitHub repo"
4. Select your repository
5. **Done!** (Takes 2 minutes)

No database setup needed - uses SQLite by default!

---

## 📊 Platform Comparison

| Feature | Vercel | Railway |
|---------|--------|---------|
| Best For | Next.js/React | Flask/Django |
| Database | PostgreSQL only | SQLite + PostgreSQL |
| Setup Time | 10-15 min | 2-5 min |
| Configuration | Manual | Auto |
| Free Tier | ✅ Yes | ✅ $5 credit |

---

## 🐛 Common Issues

### "Database disk image is malformed"
**Cause:** Using SQLite on Vercel  
**Fix:** Use PostgreSQL (Neon.tech or Supabase)

### "Module not found: dotenv"
**Fix:** Make sure `python-dotenv==1.0.0` is in requirements.txt ✅ (Already added)

### App crashes after deployment
**Fix:** Check logs
```bash
vercel logs <your-deployment-url>
```

---

## ✅ Pre-Deployment Checklist

- [ ] PostgreSQL database created (for Vercel)
- [ ] DATABASE_URL set in environment variables
- [ ] SECRET_KEY changed from default
- [ ] requirements.txt has all dependencies
- [ ] Tested locally first

---

**Need help?** See `VERCEL_DEPLOYMENT.md` for detailed guide.
