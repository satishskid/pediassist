#!/usr/bin/env python3
"""
Final working Cloudflare Access Setup using Account-level API
"""

import requests
import json

API_TOKEN = "fpOTQqerjn01YcKfbcT9TljEDqGIO8vAPtOsqSra"
DOMAIN = "pediassist.skids.clinic"

# Account ID for Cloudflare Zero Trust (Access)
# This is different from Zone ID
ACCOUNT_ID = "8b5c5b3c5b1a4b5c5b3c5b1a4b5c5b3c"  # This might be wrong, let's find it

def main():
    print("🚀 Final Cloudflare Access Setup")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📍 Domain: {DOMAIN}")
    
    # First, let's find the correct account ID
    print("\n🔍 Finding account ID...")
    
    # Try to get account ID from user info
    user_response = requests.get("https://api.cloudflare.com/client/v4/user", headers=headers)
    
    if user_response.status_code == 200:
        user_data = user_response.json()
        print("✅ Got user info")
        
        # Try different ways to get account ID
        accounts_url = "https://api.cloudflare.com/client/v4/accounts"
        accounts_response = requests.get(accounts_url, headers=headers)
        
        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
            
            if accounts_data.get('result'):
                account_id = accounts_data['result'][0]['id']
                print(f"✅ Found account ID: {account_id}")
                
                # Now proceed with Access setup
                setup_access_policy(account_id, headers)
            else:
                print("❌ No accounts found in API response")
                print("📝 Manual setup required - see instructions below")
                show_manual_setup()
        else:
            print(f"❌ Failed to get accounts: {accounts_response.status_code}")
            show_manual_setup()
    else:
        print(f"❌ Failed to get user info: {user_response.status_code}")
        show_manual_setup()

def setup_access_policy(account_id, headers):
    """Setup Access policy with account ID"""
    print(f"\n🔧 Setting up Access policy for account: {account_id}")
    
    # Check existing applications
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        apps = response.json()
        print(f"✅ Found {len(apps.get('result', []))} existing applications")
        
        # Create application if none exists
        if not apps.get('result'):
            print("📝 Creating Access application...")
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
                create_policy(account_id, app_id, headers)
            else:
                print(f"❌ Failed to create application: {create_response.status_code}")
                print(f"Response: {create_response.text}")
        else:
            app_id = apps['result'][0]['id']
            print(f"✅ Using existing application: {app_id}")
            create_policy(account_id, app_id, headers)
    else:
        print(f"❌ Failed to check applications: {response.status_code}")
        print(f"Response: {response.text}")

def create_policy(account_id, app_id, headers):
    """Create flexible email policy"""
    print("\n🔧 Creating flexible email policy...")
    
    # Whitelisted emails - customize this list
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
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps/{app_id}/policies"
    
    response = requests.post(url, headers=headers, json=policy_data)
    
    if response.status_code == 200:
        print("✅ Successfully created flexible email policy!")
        print(f"📧 Whitelisted emails: {len(whitelisted_emails)}")
        for email in whitelisted_emails:
            print(f"  ✅ {email}")
    else:
        print(f"❌ Failed to create policy: {response.status_code}")
        print(f"Response: {response.text}")

def show_manual_setup():
    """Show manual setup instructions"""
    print("\n" + "=" * 60)
    print("📝 MANUAL SETUP INSTRUCTIONS")
    print("=" * 60)
    print("Since we can't auto-detect your account ID, here's how to set up manually:")
    print()
    print("1. Go to: https://dash.cloudflare.com")
    print("2. Click: Zero Trust → Access → Applications")
    print("3. Click: 'Add application' → 'Self-hosted'")
    print(f"4. Set domain: {DOMAIN}")
    print("5. Set session duration: 24h")
    print("6. Click: 'Next'")
    print()
    print("7. Create policy:")
    print("   - Name: 'Whitelisted Users Access'")
    print("   - Decision: 'Allow'")
    print("   - Add rule: 'Emails' and add your whitelisted emails:")
    print("     • admin@skids.clinic")
    print("     • user@skids.clinic")
    print("     • customer1@gmail.com")
    print("     • client@business.com")
    print()
    print("8. Click: 'Next' and 'Save'")
    print()
    print("🧪 Test commands:")
    print(f"cloudflared access login https://{DOMAIN}")
    print(f"cloudflared access token -app=https://{DOMAIN}")

if __name__ == "__main__":
    main()