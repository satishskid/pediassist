#!/usr/bin/env python3
"""
Working Cloudflare Access Setup using Zone ID
"""

import requests
import json

API_TOKEN = "fpOTQqerjn01YcKfbcT9TljEDqGIO8vAPtOsqSra"
DOMAIN = "pediassist.skids.clinic"
ZONE_ID = "00ab462d8efb8270e0ce24aecc9cb712"

def main():
    print("🚀 Working Cloudflare Access Setup")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📍 Domain: {DOMAIN}")
    print(f"🆔 Zone ID: {ZONE_ID}")
    
    # Check existing Access applications
    print("\n🔍 Checking existing Access applications...")
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/access/apps"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        apps = response.json()
        print(f"✅ Found {len(apps.get('result', []))} existing applications")
        
        for app in apps.get('result', []):
            print(f"  📋 App: {app.get('name')} - Domain: {app.get('domain')}")
            
        if not apps.get('result'):
            print("📝 No existing applications found")
            
            # Create application
            print("\n📝 Creating Access application...")
            app_data = {
                "name": "PediAssist",
                "domain": DOMAIN,
                "session_duration": "24h",
                "type": "self_hosted"
            }
            
            create_response = requests.post(url, headers=headers, json=app_data)
            
            if create_response.status_code == 200:
                app_result = create_response.json()
                app_id = app_result.get('result', {}).get('id')
                print(f"✅ Created application: {app_id}")
                
                # Create flexible policy
                create_flexible_policy(app_id, headers)
            else:
                print(f"❌ Failed to create application: {create_response.status_code}")
                print(f"Response: {create_response.text}")
        else:
            # Use existing app
            app_id = apps['result'][0]['id']
            print(f"✅ Using existing application: {app_id}")
            create_flexible_policy(app_id, headers)
    else:
        print(f"❌ Failed to check applications: {response.status_code}")
        print(f"Response: {response.text}")

def create_flexible_policy(app_id, headers):
    """Create flexible email-based policy"""
    print("\n🔧 Creating flexible email policy...")
    
    # Whitelisted emails - you can modify this list
    whitelisted_emails = [
        "admin@skids.clinic",
        "user@skids.clinic",
        "customer1@gmail.com",
        "client@business.com"
    ]
    
    # Build email rules
    email_rules = []
    for email in whitelisted_emails:
        email_rules.append({"email": {"email": email}})
    
    policy_data = {
        "name": "Whitelisted Users Access",
        "decision": "allow",
        "include": email_rules,
        "require": [],
        "exclude": []
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/access/apps/{app_id}/policies"
    
    response = requests.post(url, headers=headers, json=policy_data)
    
    if response.status_code == 200:
        print("✅ Successfully created flexible email policy!")
        print(f"📧 Whitelisted emails: {len(whitelisted_emails)}")
        for email in whitelisted_emails:
            print(f"  ✅ {email}")
    else:
        print(f"❌ Failed to create policy: {response.status_code}")
        print(f"Response: {response.text}")
    
    print("\n🧪 Test commands:")
    print(f"cloudflared access login https://{DOMAIN}")
    print(f"cloudflared access token -app=https://{DOMAIN}")

if __name__ == "__main__":
    main()