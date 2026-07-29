#!/bin/bash

# CryoLink - Upload to GitHub Script
# Run this after creating a repository on GitHub

echo "❄️  CryoLink - GitHub Upload Script"
echo "===================================="
echo ""

# Check if remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  No GitHub repository connected yet!"
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Create a repository named: CryoLink"
    echo "3. Copy your repository URL (looks like: https://github.com/YOUR_USERNAME/CryoLink.git)"
    echo ""
    read -p "Paste your GitHub repository URL here: " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✅ Repository connected!"
    else
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
fi

# Show current remote
echo ""
echo "📡 Connected to:"
git remote get-url origin
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Your CryoLink project is now on GitHub!"
    echo ""
    echo "📍 View your repository at:"
    git remote get-url origin | sed 's/:/\//' | sed 's/git@/https:\/\//' | sed 's/.git$//'
    echo ""
    echo "🎉 Happy coding!"
else
    echo ""
    echo "❌ Push failed. Make sure:"
    echo "   1. You're logged into GitHub"
    echo "   2. The repository exists"
    echo "   3. You have permission to push"
    echo ""
fi
