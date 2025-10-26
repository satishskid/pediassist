#!/usr/bin/env python3
"""
Direct CLI Setup for Cloudflare Access
Provides commands to manually configure flexible access
"""

import subprocess
import json

def main():
    print("🚀 Direct CLI Setup for Cloudflare Access")
    print("=" * 50)
    
    api_token = "fpOTQqerjn01YcKfbcT9TljEDqGIO8vAPtOsqSra"
    domain = "pediassist.skids.clinic"
    
    print(f"📍 Domain: {domain}")
    print(f"🔑 API Token: {api_token[:10]}...")
    
    print("\n" + "=" * 60)
    print("🔧 STEP 1: Get Account ID")
    print("=" * 60)
    print("Run this command to get your account ID:")
    print(f"""
curl -X GET "https://api.cloudflare.com/client/v4/accounts" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json"
""")
    
    print("\n" + "=" * 60)
    print("🔧 STEP 2: Check Existing Applications")
    print("=" * 60)
    print("After getting account ID, run this to check existing apps:")
    print(f"""
curl -X GET "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/access/apps" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json"
""")
    
    print("\n" + "=" * 60)
    print("🔧 STEP 3: Create Application (if needed)")
    print("=" * 60)
    print("If no application exists, create it:")
    print(f"""
curl -X POST "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/access/apps" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "PediAssist",
    "domain": "{domain}",
    "session_duration": "24h",
    "type": "self_hosted"
  }}'
""")
    
    print("\n" + "=" * 60)
    print("🔧 STEP 4: Create Flexible Policy")
    print("=" * 60)
    print("Create policy with whitelisted emails:")
    
    # Example with multiple emails
    whitelisted_emails = [
        "admin@skids.clinic",
        "user@skids.clinic",
        "customer1@gmail.com",
        "client@business.com"
    ]
    
    # Build email rules
    email_rules = []
    for email in whitelisted_emails:
        email_rules.append(f'    {{"email": {{"email": "{email}"}}}}')
    
    email_rules_str = ",\n".join(email_rules)
    
    print(f"""
curl -X POST "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/access/apps/YOUR_APP_ID/policies" \\
  -H "Authorization: Bearer {api_token}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "Whitelisted Users Access",
    "decision": "allow",
    "include": [
{email_rules_str}
    ],
    "require": [],
    "exclude": []
  }}'
""")
    
    print("\n" + "=" * 60)
    print("📋 CURRENT WHITELISTED EMAILS")
    print("=" * 60)
    for email in whitelisted_emails:
        print(f"  ✅ {email}")
    
    print("\n" + "🧪 TEST COMMANDS")
    print("=" * 60)
    print("After setup, test with:")
    print(f"cloudflared access login https://{domain}")
    print(f"cloudflared access token -app=https://{domain}")
    print(f"curl -H 'cf-access-token: TOKEN' https://{domain}/api/health")
    
    print("\n" + "📝 MANUAL ALTERNATIVE")
    print("=" * 60)
    print("If CLI is complex, use the dashboard:")
    print("1. Go to: https://dash.cloudflare.com")
    print("2. Click: Zero Trust → Access → Applications")
    print("3. Add: Self-hosted application")
    print("4. Domain: pediassist.skids.clinic")
    print("5. Policy: Allow specific email addresses")
    
    print(f"\n✅ Use the commands above to set up flexible email-based access!")
    print(f"✅ Replace YOUR_ACCOUNT_ID and YOUR_APP_ID with actual values from API responses")

if __name__ == "__main__":
    main()