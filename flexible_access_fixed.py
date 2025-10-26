#!/usr/bin/env python3
"""
Flexible Cloudflare Access Policy Setup - Fixed Version
Allows whitelisted email addresses to access the application
"""

import requests
import json

def main():
    print("🚀 Flexible Cloudflare Access Policy Setup")
    print("=" * 50)
    
    # Configuration
    api_token = "fpOTQqerjn01YcKfbcT9TljEDqGIO8vAPtOsqSra"
    domain = "pediassist.skids.clinic"
    
    # Whitelisted emails - EDIT THIS LIST with your customer emails
    whitelisted_emails = [
        "admin@skids.clinic",
        "user@skids.clinic",
        # Add your customer emails here:
        # "customer1@gmail.com",
        # "client@business.com",
        # "doctor@hospital.org"
    ]
    
    print(f"📍 Domain: {domain}")
    print(f"📧 Whitelisted emails: {len(whitelisted_emails)}")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Get Account ID
    print(f"\n🔍 Getting account information...")
    try:
        response = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify", headers=headers)
        result = response.json()
        
        if result.get("success") and result.get("result"):
            account_id = result["result"]["status"]["account"]["id"]
            print(f"✅ Account ID: {account_id}")
        else:
            print("❌ Failed to get account ID")
            print(f"Response: {result}")
            return
    except Exception as e:
        print(f"❌ Error getting account ID: {e}")
        return
    
    # Step 2: Check existing Access Applications
    print(f"\n🔍 Checking existing Access Applications...")
    try:
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps",
            headers=headers
        )
        result = response.json()
        
        if result.get("success"):
            apps = result.get("result", [])
            existing_app = None
            for app in apps:
                if app.get("domain") == domain:
                    existing_app = app
                    break
            
            if existing_app:
                print(f"✅ Found existing application: {existing_app['id']}")
                app_id = existing_app['id']
            else:
                print("⚠️  No existing application found. Please create it manually in the dashboard.")
                print("   Go to: Zero Trust → Access → Applications → Add Application")
                print("   Set domain: pediassist.skids.clinic")
                return
        else:
            print(f"❌ Failed to get applications: {result.get('errors')}")
            return
    except Exception as e:
        print(f"❌ Error checking applications: {e}")
        return
    
    # Step 3: Create Access Policy with Whitelisted Emails
    print(f"\n🔐 Creating Flexible Access Policy...")
    
    # Build policy rules for whitelisted emails
    policy_rules = []
    for email in whitelisted_emails:
        policy_rules.append({
            "email": {"email": email}
        })
    
    policy_data = {
        "name": "Whitelisted Users Access",
        "decision": "allow",
        "include": policy_rules,
        "require": [],
        "exclude": []
    }
    
    try:
        response = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps/{app_id}/policies",
            headers=headers,
            json=policy_data
        )
        result = response.json()
        
        if result.get("success"):
            policy_id = result["result"]["id"]
            print(f"✅ Access Policy created: {policy_id}")
        else:
            print(f"⚠️  Policy creation result: {result.get('errors', 'Unknown error')}")
            if result.get("errors") and any("already exists" in str(e).lower() for e in result["errors"]):
                print("ℹ️  Policy might already exist")
            else:
                return
    except Exception as e:
        print(f"❌ Error creating policy: {e}")
        return
    
    # Step 4: Provide management information
    print("\n" + "=" * 60)
    print("🎉 ACCESS POLICY SETUP COMPLETE!")
    print("=" * 60)
    print(f"✅ Application: {domain}")
    print(f"✅ Whitelisted users: {len(whitelisted_emails)}")
    print(f"✅ Policy: Whitelisted Users Access")
    
    print("\n" + "📋 CURRENT WHITELISTED USERS")
    print("=" * 60)
    for email in whitelisted_emails:
        print(f"  ✅ {email}")
    
    print("\n" + "🔧 TO ADD MORE USERS")
    print("=" * 60)
    print("1. Edit the 'whitelisted_emails' list in this script")
    print("2. Run this script again")
    print("3. Or manually add users in Cloudflare dashboard:")
    print("   Zero Trust → Access → Applications → PediAssist → Policies")
    
    print("\n" + "🧪 TEST COMMANDS")
    print("=" * 60)
    print(f"# Test Access")
    print(f"cloudflared access login https://{domain}")
    print(f"cloudflared access token -app=https://{domain}")
    print(f"curl -H 'cf-access-token: TOKEN' https://{domain}/api/health")
    
    print(f"\n✅ Setup complete! Whitelisted users can now access https://{domain}")
    print(f"✅ The policy allows flexible email-based access control")

if __name__ == "__main__":
    main()