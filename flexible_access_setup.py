#!/usr/bin/env python3
"""
Flexible Cloudflare Access Policy Setup
Allows whitelisted email addresses to access the application
"""

import requests
import json
import sys

def main():
    print("🚀 Flexible Cloudflare Access Policy Setup")
    print("=" * 50)
    
    # Configuration
    api_token = "fpOTQqerjn01YcKfbcT9TljEDqGIO8vAPtOsqSra"
    domain = "pediassist.skids.clinic"
    
    # Whitelisted emails (you can modify this list)
    whitelisted_emails = [
        "admin@skids.clinic",
        "user@skids.clinic",
        # Add customer emails here as needed
        # "customer1@gmail.com",
        # "client@business.com"
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
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                account_id = data["result"]["status"]["account"]["id"]
                print(f"✅ Account ID: {account_id}")
            else:
                print("❌ Failed to get account ID")
                return
        else:
            print(f"❌ Failed to verify token: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting account ID: {e}")
        return
    
    # Step 2: Create Access Application
    print(f"\n🔐 Creating Access Application...")
    app_data = {
        "name": "PediAssist",
        "domain": domain,
        "session_duration": "24h",
        "type": "self_hosted"
    }
    
    try:
        response = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps",
            headers=headers,
            json=app_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                app_id = data["result"]["id"]
                print(f"✅ Access Application created: {app_id}")
            else:
                print(f"⚠️  Application might already exist or error: {data.get('errors')}")
                # Try to get existing app
                response = requests.get(
                    f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps",
                    headers=headers
                )
                if response.status_code == 200:
                    apps = response.json().get("result", [])
                    app_id = next((app["id"] for app in apps if app["domain"] == domain), None)
                    if app_id:
                        print(f"✅ Found existing application: {app_id}")
                    else:
                        print("❌ Could not find application")
                        return
                else:
                    print("❌ Could not get applications")
                    return
        else:
            print(f"❌ Failed to create application: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating application: {e}")
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
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                policy_id = data["result"]["id"]
                print(f"✅ Access Policy created: {policy_id}")
            else:
                print(f"⚠️  Policy might already exist or error: {data.get('errors')}")
        else:
            print(f"❌ Failed to create policy: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating policy: {e}")
        return
    
    # Step 4: Provide management commands
    print("\n" + "=" * 60)
    print("🎉 ACCESS SETUP COMPLETE!")
    print("=" * 60)
    print(f"✅ Application: {domain}")
    print(f"✅ Whitelisted users: {len(whitelisted_emails)}")
    print(f"✅ Policy: Whitelisted Users Access")
    
    print("\n" + "🔧 MANAGEMENT COMMANDS")
    print("=" * 60)
    print("To add more users, edit this script and run again, or use:")
    print(f"# Add individual user via API")
    print(f"curl -X POST 'https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps/{app_id}/policies' \\")
    print(f"  -H 'Authorization: Bearer {api_token}' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"name\": \"New User\", \"decision\": \"allow\", \"include\": [{{\"email\": {{\"email\": \"newuser@example.com\"}}}}]}}'")
    
    print("\n" + "🧪 TEST COMMANDS")
    print("=" * 60)
    print(f"# Test Access")
    print(f"cloudflared access login https://{domain}")
    print(f"cloudflared access token -app=https://{domain}")
    print(f"curl -H 'cf-access-token: TOKEN' https://{domain}/api/health")
    
    print("\n" + "📋 CURRENT WHITELISTED USERS")
    print("=" * 60)
    for email in whitelisted_emails:
        print(f"  ✅ {email}")
    
    print(f"\n✅ Setup complete! Users can now access https://{domain}")
    print(f"✅ Edit the 'whitelisted_emails' list in this script to add more users")

if __name__ == "__main__":
    main()