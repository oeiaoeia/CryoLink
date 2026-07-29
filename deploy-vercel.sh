#!/bin/bash
# CryoLink Vercel Deployment Script

echo "🚀 CryoLink Vercel Deployment"
echo "=============================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if logged in
echo "🔐 Checking Vercel login..."
vercel whoami 2>/dev/null
if [ $? -ne 0 ]; then
    echo "🔑 Please login to Vercel..."
    vercel login
fi

# Link project
echo "🔗 Linking project..."
vercel link

# Pull environment variables
echo "📥 Pulling environment variables..."
vercel env pull

# Check DATABASE_URL
if ! grep -q "DATABASE_URL=postgresql://" .env.local 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: DATABASE_URL is not set to PostgreSQL!"
    echo "   SQLite will NOT work on Vercel!"
    echo ""
    echo "   Please set DATABASE_URL in Vercel dashboard:"
    echo "   1. Go to vercel.com/dashboard"
    echo "   2. Select your project"
    echo "   3. Settings → Environment Variables"
    echo "   4. Add DATABASE_URL with PostgreSQL connection string"
    echo ""
    echo "   Recommended: Create free DB at https://neon.tech"
    echo ""
    read -p "Continue anyway? (y/n): " choice
    if [[ ! $choice =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy
echo ""
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo "   Run 'vercel --prod' to redeploy"
