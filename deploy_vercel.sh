#!/bin/bash
# Easy Vercel Deployment Script for PediAssist

echo "🚀 Deploying PediAssist to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm i -g vercel
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel deploy --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be accessible at:"
echo "   https://[your-deployment-url].vercel.app/simple"
echo "   https://[your-deployment-url].vercel.app"
