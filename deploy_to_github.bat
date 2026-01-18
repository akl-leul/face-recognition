@echo off
echo 🚀 Deploying to GitHub...

REM Initialize git if not already done
if not exist ".git" (
    git init
    git add .
    git commit -m "Initial commit: Face recognition app"
)

REM Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/face-recognition-app.git
git branch -M main

REM Push to GitHub
git push -u origin main

echo ✅ Code pushed to GitHub!
echo 🌐 Now go to render.com to deploy
pause
