#!/bin/bash

# PediAssist Netlify Deployment Script
# Deploys to custom domain: pediassist-netlify.ap

set -e

echo "🚀 PediAssist Netlify Deployment"
echo "================================"

# Check if netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo "❌ Netlify CLI not found. Installing..."
    npm install -g netlify-cli
fi

# Check if user is logged in
if ! netlify status &> /dev/null; then
    echo "🔐 Please login to Netlify first:"
    netlify login
fi

echo "📦 Preparing deployment..."

# Validate configuration files
if [ ! -f "netlify.toml" ]; then
    echo "❌ netlify.toml not found!"
    exit 1
fi

if [ ! -f "netlify/functions/app.py" ]; then
    echo "❌ Netlify function not found!"
    exit 1
fi

echo "✅ Configuration files validated"

# Test the application locally first
echo "🧪 Testing application locally..."
python -c "from pediassist.web_app import app; print('✅ Flask app imports successfully')" || {
    echo "❌ Application test failed!"
    exit 1
}

# Ask for deployment type
echo ""
echo "Choose deployment type:"
echo "1) Deploy to staging (preview)"
echo "2) Deploy to production (pediassist-netlify.ap)"
echo "3) Setup custom domain only"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Deploying to staging..."
        netlify deploy --dir=. --functions=netlify/functions/ --message="PediAssist staging deploy $(date)"
        ;;
    2)
        echo "🚀 Deploying to production..."
        netlify deploy --prod --dir=. --functions=netlify/functions/ --message="PediAssist production deploy $(date)"
        echo "🌐 Site will be available at: https://pediassist-netlify.ap"
        ;;
    3)
        echo "🔧 Setting up custom domain..."
        echo "Please configure 'pediassist-netlify.ap' in your Netlify dashboard:"
        echo "Site Settings → Domain Management → Add Custom Domain"
        echo "Then configure DNS to point to Netlify"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment complete!"
echo "📖 Check NETLIFY_SETUP.md for detailed instructions"
echo "🌐 Your app will be available at: https://pediassist-netlify.ap"
echo ""
echo "Next steps:"
echo "1. Test the deployment"
echo "2. Configure custom domain in Netlify dashboard"
echo "3. Set up environment variables if needed"