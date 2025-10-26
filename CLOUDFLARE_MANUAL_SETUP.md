# 🚀 Manual Cloudflare Access Setup for PediAssist

Since the automated script had issues, let's set up Cloudflare Access manually using the web dashboard and CLI commands.

## ✅ Prerequisites Checklist

- [ ] Cloudflare account with your domain (`skids.health` or `skids.clinic`)
- [ ] Cloudflare API token with appropriate permissions
- [ ] Current Vercel deployment URL
- [ ] `cloudflared` CLI tool installed (✅ Done)

## 🔧 Step-by-Step Manual Setup

### Step 1: Get Your Cloudflare Credentials

```bash
# Verify cloudflared is working
cloudflared login

# Get your account info (save this for later)
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json"
```

### Step 2: Create Access Application via Dashboard

1. **Go to Cloudflare Dashboard** → https://dash.cloudflare.com
2. **Navigate to Zero Trust** → Click on your profile → "Zero Trust"
3. **Access > Applications** → Click "Add an application"
4. **Select "Self-hosted"**
5. **Configure Application:**
   - **Name**: `PediAssist`
   - **Domain**: `pediassist.skids.clinic` (or your preferred subdomain)
   - **Session Duration**: `24h`
   - **App Launcher**: ✅ Visible

### Step 3: Configure Access Policies

**Create Allow Policy:**
1. **Policy Name**: `Allow Email Access`
2. **Action**: `Allow`
3. **Include Rule**: 
   - **Selector**: `Emails Ending In`
   - **Value**: `@skids.clinic` (or any email domain you want to allow)

**Alternative: Allow Any Email (for testing):**
- **Selector**: `Emails Ending In`
- **Value**: `@*` (allows any email address)

### Step 4: Add DNS Record

**Option A: Via Dashboard**
1. **Go to DNS tab** in Cloudflare dashboard
2. **Add Record:**
   - **Type**: `CNAME`
   - **Name**: `pediassist`
   - **Target**: `pediassist-l1cmhp0v2-satishs-projects-89f8c44c.vercel.app`
   - **Proxy Status**: ✅ Proxied (orange cloud)
   - **TTL**: `Auto`

**Option B: Via CLI**
```bash
# First, get your Zone ID
curl -X GET "https://api.cloudflare.com/client/v4/zones?name=skids.clinic" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json"

# Then create the DNS record (replace ZONE_ID with your actual zone ID)
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records" \
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

### Step 5: Test Your Setup

```bash
# Test basic access
cloudflared access login https://pediassist.skids.clinic

# Test API endpoint
cloudflared access curl https://pediassist.skids.clinic/api/health

# Get access token for API calls
cloudflared access token -app=https://pediassist.skids.clinic
```

## 🎯 Quick Setup Commands

Based on your input from the previous session, here's what we know:

- **Domain**: `skids.clinic`
- **Subdomain**: `pediassist`
- **Full URL**: `https://pediassist.skids.clinic`
- **Vercel URL**: `https://pediassist-l1cmhp0v2-satishs-projects-89f8c44c.vercel.app`

## 🔍 Verification Steps

### 1. Check DNS Propagation
```bash
# Check if DNS is working
dig pediassist.skids.clinic

# Check CNAME record
dig CNAME pediassist.skids.clinic
```

### 2. Test Cloudflare Access
```bash
# This should prompt for authentication
cloudflared access login https://pediassist.skids.clinic

# Test with curl (should redirect to login)
curl -I https://pediassist.skids.clinic
```

### 3. Test API Access
```bash
# Get access token
TOKEN=$(cloudflared access token -app=https://pediassist.skids.clinic)

# Use token to access API
curl -H "cf-access-token: $TOKEN" https://pediassist.skids.clinic/api/health
```

## 🚨 Common Issues & Solutions

### Issue 1: DNS Not Propagating
- **Solution**: Wait 5-15 minutes, check Cloudflare DNS settings
- **Command**: `dig pediassist.skids.clinic @1.1.1.1`

### Issue 2: Access Policy Blocking
- **Solution**: Check Access policies in Cloudflare dashboard
- **Quick Fix**: Temporarily allow any email with `@*` pattern

### Issue 3: CORS Issues
- **Solution**: Configure CORS in Access application settings
- **Settings**: Allow all origins/headers for testing, then restrict

### Issue 4: SSL Certificate Issues
- **Solution**: Ensure "Always Use HTTPS" is enabled in Cloudflare
- **Settings**: SSL/TLS → Overview → Full (Strict)

## 📋 Next Steps After Setup

1. **Configure Identity Providers** (Google, Azure AD, etc.)
2. **Set up device posture rules** (optional)
3. **Add more granular access policies**
4. **Configure WARP for enhanced security** (optional)
5. **Set up monitoring and logging**

## 🎉 Success Indicators

- ✅ DNS resolves to Cloudflare IPs
- ✅ Access login page appears when visiting URL
- ✅ Can authenticate and access application
- ✅ API endpoints work with proper tokens
- ✅ Admin dashboard shows access logs

Ready to proceed with the manual setup? Start with **Step 2** in the Cloudflare dashboard!