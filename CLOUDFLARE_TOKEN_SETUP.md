# 🔑 Cloudflare API Token Setup Guide

## Step 1: Create API Token

1. **Go to**: https://dash.cloudflare.com/profile/api-tokens
2. **Click**: "Create Token"
3. **Use Template**: "Zone: Read" (or create custom token)
4. **Permissions needed**:
   - `Zone:Read`
   - `Zone.Zone:Read`
   - `Zone.Zone.Settings:Read`
   - `Zone.DNS:Edit` (for creating DNS records)
5. **Zone Resources**: Include your domain `skids.clinic`
6. **Create Token** and copy it

## Step 2: Test Your Token

```bash
# Test your token (replace YOUR_TOKEN_HERE with your actual token)
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

## Step 3: Get Account ID

```bash
# Get account info
curl -X GET "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

## Step 4: Get Zone ID

```bash
# Get zone ID for your domain
curl -X GET "https://api.cloudflare.com/client/v4/zones?name=skids.clinic" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```