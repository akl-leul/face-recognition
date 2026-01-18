#!/bin/bash
# Build React frontend for production
echo "🏗️  Building React frontend..."
cd react-frontend
npm run build
echo "✅ Frontend built successfully!"
echo "📁 Static files are in react-frontend/dist/"
echo "🌐 Flask will serve these files automatically"
