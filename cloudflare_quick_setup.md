# 🚀 Cloudflare Access Quick Setup for PediAssist

## Prerequisites
- Cloudflare account with `skids.health` domain
- Cloudflare API token (get from: https://dash.cloudflare.com/profile/api-tokens)
- Current Vercel deployment URL

## Step 1: Get Cloudflare Account ID
```bash
# Get your account ID
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json"
```

## Step 2: Create Access Application
```bash
# Create PediAssist application
curl -X POST "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/access/apps" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PediAssist",
    "domain": "pediassist.skids.health",
    "type": "self_hosted",
    "session_duration": "24h",
    "app_launcher_visible": true,
    "cors_headers": {
      "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      "allowed_origins": ["*"],
      "allowed_headers": ["*"],
      "max_age": 86400
    }
  }'
```

## Step 3: Create Access Policy (Email-based)
```bash
# Create email-based access policy
curl -X POST "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/access/apps/YOUR_APP_ID/policies" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Allow Email Domain",
    "decision": "allow",
    "include": [
      {
        "email_domain": {
          "domain": "skids.health"
        }
      }
    ]
  }'
```

## Step 4: Add DNS Record
```bash
# Add CNAME record pointing to Vercel
curl -X POST "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CNAME",
    "name": "pediassist",
    "content": "pediassist-l1cmhp0v2-satishs-projects-89f8c44c.vercel.app",
    "ttl": 300,
    "proxied": true
  }'
```

## Step 5: Test Access
```bash
# Test login
cloudflared access login https://pediassist.skids.health

# Test API access
cloudflared access curl https://pediassist.skids.health/api/health

# Get access token
cloudflared access token -app=https://pediassist.skids.health
```

## CLI Management Commands
```bash
# List access applications
cloudflared tunnel list

# Check access status
cloudflared access status https://pediassist.skids.health

# Generate service token (for API access)
cloudflared access token -app=https://pediassist.skids.health
```

## Troubleshooting
- If DNS doesn't resolve, check DNS propagation: `dig pediassist.skids.health`
- If access is blocked, check Cloudflare Access logs in dashboard
- If CORS issues, verify CORS headers in application settings

## Next Steps
1. Configure identity providers (Google, Azure AD, etc.)
2. Set up device posture rules
3. Add more granular access policies
4. Configure WARP for enhanced security