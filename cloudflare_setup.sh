#!/bin/bash

# Cloudflare Access Setup Script for PediAssist
# This script helps set up Cloudflare Access for your domain

echo "🚀 Setting up Cloudflare Access for PediAssist..."
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found. Please install it first:"
    echo "   brew install cloudflared"
    exit 1
fi

echo "✅ cloudflared is installed"

# Get user input
echo ""
echo "Please enter your domain (e.g., skids.health):"
read DOMAIN

echo "Please enter the subdomain for PediAssist (e.g., pediassist):"
read SUBDOMAIN

echo "Please enter your Cloudflare API token (get it from https://dash.cloudflare.com/profile/api-tokens):"
read -s API_TOKEN

FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo ""
echo "📋 Setup Summary:"
echo "   Domain: ${DOMAIN}"
echo "   Subdomain: ${SUBDOMAIN}"
echo "   Full URL: https://${FULL_DOMAIN}"
echo ""

# Create Cloudflare Access application
echo "🔄 Creating Cloudflare Access application..."

# Create the application using Cloudflare API
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$(cloudflared tunnel info | grep Account | cut -d' ' -f3)/access/apps" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"PediAssist\",
    \"domain\": \"${FULL_DOMAIN}\",
    \"type\": \"self_hosted\",
    \"session_duration\": \"24h\",
    \"allowed_idps\": [],
    \"auto_redirect_to_identity\": false,
    \"enable_binding_cookie\": false,
    \"custom_deny_url\": \"\",
    \"custom_deny_message\": \"Access denied to PediAssist. Please contact your administrator.\",
    \"custom_non_identity_deny_url\": \"\",
    \"allow_authenticate_via_warp\": false,
    \"app_launcher_visible\": true,
    \"skip_interstitial\": false,
    \"cors_headers\": {
      \"allowed_methods\": [\"GET\", \"POST\", \"PUT\", \"DELETE\", \"OPTIONS\"],
      \"allowed_origins\": [\"*\"],
      \"allowed_headers\": [\"*\"],
      \"max_age\": 86400
    }
  }"

echo ""
echo "✅ Cloudflare Access application created!"
echo ""
echo "🔄 Now you need to:"
echo "1. Add DNS record for ${FULL_DOMAIN} pointing to your Vercel deployment"
echo "2. Create access policies in Cloudflare dashboard"
echo "3. Test the setup"
echo ""
echo "📖 Next steps:"
echo "   - Go to Cloudflare dashboard > Zero Trust > Access > Applications"
echo "   - Find 'PediAssist' and click on it"
echo "   - Add policies (email-based, OTP, or SSO)"
echo "   - Add DNS CNAME record: ${FULL_DOMAIN} -> your-vercel-app.vercel.app"
echo ""
echo "🔧 Testing commands:"
echo "   cloudflared access login https://${FULL_DOMAIN}"
echo "   cloudflared access curl https://${FULL_DOMAIN}/api/health"