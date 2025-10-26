# 🚀 Complete Cloudflare Access Setup for PediAssist

## Current Status ✅
- **Vercel Deployment**: `https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app`
- **Status**: ✅ Working (protected by Vercel auth)
- **cloudflared CLI**: ✅ Installed and authenticated

## 🎯 Goal
Set up Cloudflare Access to create a clean URL like `https://pediassist.skids.clinic` with access control.

## 📋 Step-by-Step Manual Setup

### Step 1: Create Cloudflare API Token
1. **Go to**: https://dash.cloudflare.com/profile/api-tokens
2. **Click**: "Create Token"
3. **Use Custom Token** with these permissions:
   - `Zone:Read` (for your domain)
   - `Zone.DNS:Edit` (for creating DNS records)
   - `Access:Apps and Policies:Edit` (for Access setup)
4. **Zone Resources**: Include your domain
5. **Client IP Address Filtering**: Add your current IP if needed
6. **Create Token** and save it securely

### Step 2: Add Your Domain to Cloudflare
If `skids.clinic` or `skids.health` isn't in your Cloudflare account:
1. **Go to**: https://dash.cloudflare.com
2. **Click**: "Add a Site"
3. **Enter**: Your domain name
4. **Follow**: The setup wizard to change nameservers

### Step 3: Create DNS Record via Dashboard
1. **Go to**: https://dash.cloudflare.com → Your Domain → DNS
2. **Click**: "Add Record"
3. **Configure**:
   ```
   Type: CNAME
   Name: pediassist
   Target: pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app
   TTL: Auto
   Proxy Status: ✅ Proxied (orange cloud)
   ```
4. **Save**

### Step 4: Set Up Cloudflare Access
1. **Go to**: https://dash.cloudflare.com → Zero Trust
2. **Navigate**: Access → Applications
3. **Click**: "Add an application"
4. **Select**: "Self-hosted"
5. **Configure Application**:
   ```
   Name: PediAssist
   Domain: pediassist.skids.clinic
   Session Duration: 24h
   App Launcher: ✅ Visible
   ```
6. **Create Policy**:
   ```
   Policy Name: Allow Team Access
   Action: Allow
   Include Rule: 
     - Selector: "Emails Ending In"
     - Value: "@skids.clinic"
   ```
7. **Save**

### Step 5: Test the Setup
```bash
# Test DNS resolution
dig pediassist.skids.clinic

# Test access (should redirect to login)
curl -I https://pediassist.skids.clinic

# Test with cloudflared
cloudflared access login https://pediassist.skids.clinic

# Get access token
cloudflared access token -app=https://pediassist.skids.clinic

# Test API with token
TOKEN=$(cloudflared access token -app=https://pediassist.skids.clinic)
curl -H "cf-access-token: $TOKEN" https://pediassist.skids.clinic/api/health
```

## 🛠️ Alternative: CLI-Based DNS Setup

If you want to use CLI after setting up the API token properly:

```bash
# Set your API token
export CF_API_TOKEN="your_api_token_here"

# Get zone ID
ZONE_ID=$(curl -s -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones?name=skids.clinic" | \
  python3 -c "import json,sys;data=json.load(sys.stdin);print(data['result'][0]['id'] if data.get('result') else '')")

# Create DNS record
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CNAME",
    "name": "pediassist",
    "content": "pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app",
    "ttl": 300,
    "proxied": true
  }'
```

## 🔧 Troubleshooting

### Issue 1: Domain Not Found
- **Solution**: Add your domain to Cloudflare first
- **Check**: https://dash.cloudflare.com → "Add a Site"

### Issue 2: API Token Invalid
- **Solution**: Check IP restrictions and permissions
- **Test**: Create token without IP restrictions first

### Issue 3: DNS Not Propagating
- **Solution**: Wait 5-15 minutes, check with `dig`
- **Check**: `dig pediassist.skids.clinic @1.1.1.1`

### Issue 4: Access Policy Blocking
- **Solution**: Check Access policies in Zero Trust dashboard
- **Quick Fix**: Allow any email with `@*` pattern for testing

## 🎉 Success Indicators

- ✅ DNS resolves to Cloudflare IPs
- ✅ Access login page appears at your custom domain
- ✅ Can authenticate and access application
- ✅ API endpoints work with proper tokens
- ✅ Admin dashboard shows access logs

## 📋 Next Steps After Setup

1. **Configure Identity Providers** (Google, Azure AD, etc.)
2. **Add more granular access policies**
3. **Set up device posture rules** (optional)
4. **Configure WARP for enhanced security** (optional)
5. **Monitor access logs**

## 🚀 Ready to Start?

1. **First**: Create your API token at https://dash.cloudflare.com/profile/api-tokens
2. **Then**: Follow Step 3 to create the DNS record via dashboard
3. **Finally**: Set up Access in Zero Trust dashboard

Need help with any step? Let me know!