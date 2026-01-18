#!/bin/bash
echo "🚀 Deploying to GitHub..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit: Face recognition app"
fi

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/face-recognition-app.git
git branch -M main

# Push to GitHub
git push -u origin main

echo "✅ Code pushed to GitHub!"
echo "🌐 Now go to render.com to deploy"
