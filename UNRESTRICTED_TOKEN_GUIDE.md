# 🔑 Creating Cloudflare API Token Without IP Restrictions

## Step-by-Step Guide

### 1. Go to Cloudflare API Tokens
- **URL**: https://dash.cloudflare.com/profile/api-tokens
- **Click**: "Create Token" button

### 2. Use Custom Token (Recommended)
- **Select**: "Create Custom Token" (not the templates)

### 3. Configure Token Permissions

**Token Name**: `PediAssist Setup Token`

**Permissions** (Add these one by one):
```
Zone → Read
Zone → DNS → Edit  
Access: Apps and Policies → Edit
Access: Organizations, Identity Providers, and Groups → Read
Account → Read
```

**Zone Resources**:
- **Include**: All zones (or select specific domains like `skids.clinic`, `skids.health`)
- **Or**: Specific zones if you want to limit scope

**Account Resources**:
- **Include**: All accounts (or select your specific account)

**Client IP Address Filtering**:
- **IMPORTANT**: Leave this section EMPTY (no IP restrictions)
- **Do NOT**: Add any IP addresses or ranges

**TTL**:
- **Leave**: Default (no expiration) or set as needed

### 4. Create Token
- **Click**: "Continue to summary"
- **Review**: All permissions look correct
- **Click**: "Create Token"
- **Copy**: The token immediately (you won't see it again)

## 🔍 Token Configuration Summary

```
Name: PediAssist Setup Token
Permissions:
  - Zone:Read (All zones)
  - Zone.DNS:Edit (All zones)  
  - Access:Apps and Policies:Edit (All zones)
  - Access:Organizations, Identity Providers, and Groups:Read (All accounts)
  - Account:Read (All accounts)

Zone Resources: All zones (or specific domains)
Account Resources: All accounts (or specific account)
Client IP Address Filtering: NONE (leave empty)
TTL: No expiration (or your preference)
```

## ✅ Verification Steps

After creating the token, test it:

```bash
# Test your new token (replace YOUR_NEW_TOKEN)
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_NEW_TOKEN" \
  -H "Content-Type: application/json"

# Should return: {"success":true,...}

# Test zones endpoint
curl -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer YOUR_NEW_TOKEN" \
  -H "Content-Type: application/json"

# Should return your zones without IP restriction errors
```

## 🚨 Important Notes

- **Security**: This token has broad permissions, store it securely
- **Scope**: Consider limiting to specific zones if security is a concern
- **Expiration**: Set an expiration date if you want automatic revocation
- **IP Restrictions**: Only add if you specifically need them

## 🎯 Next Steps

Once you have the working token, we can:
1. Create DNS records via API
2. Set up Cloudflare Access programmatically
3. Test the complete setup

**Ready to test your new token?** Share it when you have it created!