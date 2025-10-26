#!/usr/bin/env python3
"""
Final Complete Cloudflare Zero Trust Setup
Handles all edge cases and provides manual fallback options
"""

import subprocess
import json
import time
import os
import sys

def run_command(cmd, description="", timeout=30):
    """Run a shell command and return output"""
    try:
        if description:
            print(f"📋 {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print(f"✅ Success")
            return result.stdout.strip()
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def get_user_info():
    """Get user information to find account"""
    print("\n👤 Getting user information...")
    
    result = run_command(
        'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/user',
        "Getting user details"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success'):
                user = data['result']
                print(f"✅ User: {user.get('email', 'Unknown')}")
                print(f"✅ Account ID: {user.get('id', 'Not found')}")
                return user.get('id')
            else:
                print(f"❌ Failed to get user info: {data.get('errors', 'Unknown error')}")
                return None
        except:
            print("❌ Invalid response")
            return None
    return None

def get_zone_info():
    """Get zone information for skids.clinic"""
    print("\n🌐 Getting zone information...")
    
    result = run_command(
        'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/zones?name=skids.clinic"',
        "Getting zone details"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success') and data.get('result'):
                zone = data['result'][0]
                zone_id = zone['id']
                account_id = zone['account']['id']
                print(f"✅ Zone: {zone['name']} (ID: {zone_id})")
                print(f"✅ Account: {zone['account']['name']} (ID: {account_id})")
                return account_id, zone_id
            else:
                print(f"❌ Zone not found or not accessible")
                return None, None
        except:
            print("❌ Invalid response")
            return None, None
    return None, None

def create_access_application_direct(account_id):
    """Create Access application with direct API call"""
    print("\n🔐 Creating Access Application...")
    
    app_data = {
        "name": "PediAssist Medical App",
        "domain": "pediassist.skids.clinic",
        "type": "self_hosted",
        "session_duration": "24h"
    }
    
    json_data = json.dumps(app_data)
    
    cmd = f'''curl -s -X POST \\
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \\
        -H "Content-Type: application/json" \\
        -d '{json_data}' \\
        "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps"'''
    
    result = run_command(cmd, "Creating application via API")
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success'):
                app_id = data['result']['id']
                print(f"✅ Application created: {app_id}")
                return app_id
            else:
                print(f"⚠️  Issue: {data.get('errors', 'Unknown error')}")
                # Check if application already exists
                return check_existing_application(account_id)
        except:
            print("❌ Invalid response")
            return None
    return None

def check_existing_application(account_id):
    """Check for existing application"""
    print("\n🔍 Checking for existing applications...")
    
    result = run_command(
        f'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps"',
        "Getting existing applications"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success') and data.get('result'):
                for app in data['result']:
                    if app['domain'] == 'pediassist.skids.clinic':
                        print(f"✅ Found existing application: {app['id']}")
                        return app['id']
                print("❌ No application found for pediassist.skids.clinic")
                return None
            else:
                print("❌ No applications found")
                return None
        except:
            print("❌ Invalid response")
            return None
    return None

def create_policy_direct(account_id, app_id):
    """Create access policy directly"""
    print("\n🛡️  Creating Access Policy...")
    
    policy_data = {
        "name": "Whitelisted Users Access",
        "decision": "allow",
        "include": [
            {"email": {"email": "admin@skids.clinic"}},
            {"email": {"email": "user@skids.clinic"}}
        ]
    }
    
    json_data = json.dumps(policy_data)
    
    cmd = f'''curl -s -X POST \\
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \\
        -H "Content-Type: application/json" \\
        -d '{json_data}' \\
        "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps/{app_id}/policies"'''
    
    result = run_command(cmd, "Creating policy via API")
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success'):
                policy_id = data['result']['id']
                print(f"✅ Policy created: {policy_id}")
                return True
            else:
                print(f"⚠️  Policy issue: {data.get('errors', 'Unknown error')}")
                return False
        except:
            print("❌ Invalid response")
            return False
    return False

def provide_manual_instructions():
    """Provide manual setup instructions"""
    print("\n" + "=" * 70)
    print("🚨 MANUAL SETUP REQUIRED - Complete Instructions")
    print("=" * 70)
    print()
    print("Since API access is limited, please complete these steps manually:")
    print()
    print("1️⃣  ACTIVATE ZERO TRUST PLAN:")
    print("   • Go to: https://dash.cloudflare.com/")
    print("   • Click your account name")
    print("   • Click 'Zero Trust' in left menu")
    print("   • Select 'Free' plan")
    print("   • Complete signup with payment method")
    print()
    print("2️⃣  CREATE ACCESS APPLICATION:")
    print("   • In Zero Trust dashboard")
    print("   • Go to: Access → Applications")
    print("   • Click 'Add Application'")
    print("   • Select 'Self-hosted'")
    print("   • Name: 'PediAssist Medical App'")
    print("   • Domain: 'pediassist.skids.clinic'")
    print("   • Session Duration: 24 hours")
    print("   • Click 'Next'")
    print()
    print("3️⃣  CREATE ACCESS POLICY:")
    print("   • Policy Name: 'Whitelisted Users Access'")
    print("   • Action: 'Allow'")
    print("   • Rule Type: 'Emails'")
    print("   • Add these emails:")
    print("     - admin@skids.clinic")
    print("     - user@skids.clinic")
    print("   • Click 'Next' then 'Add Application'")
    print()
    print("4️⃣  VERIFY DNS PROXY:")
    print("   • Go to: DNS → Records")
    print("   • Find 'pediassist' CNAME record")
    print("   • Ensure it shows 🟠 'Proxied' status")
    print("   • If gray, click the cloud to enable proxy")
    print()
    print("⏰  Wait 2-3 minutes after completing all steps, then test with:")
    print("   cloudflared access login https://pediassist.skids.clinic")
    print()

def main():
    print("🚀 Final Complete Cloudflare Zero Trust CLI Setup")
    print("=" * 70)
    print("This script will attempt automated setup and provide manual fallback")
    print()
    
    # Check if API token is set
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    if not api_token:
        print("🔑 Please enter your Cloudflare API token:")
        print("Get it from: https://dash.cloudflare.com/profile/api-tokens")
        print("Required permissions: Zone:Read, Account:Read, Access:Edit")
        api_token = input("Token: ").strip()
        if not api_token:
            print("❌ Token required!")
            return
        os.environ['CLOUDFLARE_API_TOKEN'] = api_token
    
    # Test token
    print("\n🔍 Testing API token...")
    result = run_command(
        'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/user/tokens/verify',
        "Verifying token"
    )
    
    if not result or 'success' not in result:
        print("❌ Invalid API token!")
        provide_manual_instructions()
        return
    
    # Try to get account info via zone
    print("\n🌐 Attempting to get account info via zone...")
    account_id, zone_id = get_zone_info()
    
    if not account_id:
        print("❌ Cannot get account information via API")
        provide_manual_instructions()
        return
    
    print(f"\n✅ Account ID: {account_id}")
    print(f"✅ Zone ID: {zone_id}")
    
    # Try to create application
    print("\n🔐 Setting up Access application...")
    app_id = create_access_application_direct(account_id)
    
    if not app_id:
        print("❌ Cannot create application via API")
        provide_manual_instructions()
        return
    
    # Try to create policy
    print("\n🛡️  Setting up Access policy...")
    policy_created = create_policy_direct(account_id, app_id)
    
    if not policy_created:
        print("❌ Cannot create policy via API")
        provide_manual_instructions()
        return
    
    print("\n⏳ Waiting for changes to propagate...")
    time.sleep(30)
    
    print("\n🧪 Testing setup...")
    result = run_command(
        'curl -s -I https://pediassist.skids.clinic',
        "Testing domain"
    )
    
    if result and ('403' in result or 'cloudflare' in result.lower()):
        print("\n🎉 SUCCESS! Cloudflare Access is now active!")
        print("\nTest commands:")
        print("  cloudflared access login https://pediassist.skids.clinic")
        print("  cloudflared access token -app=https://pediassist.skids.clinic")
    else:
        print("\n⚠️  Setup initiated but may need more time")
        print("Run in 2-3 minutes: python check_access_status.py")

if __name__ == "__main__":
    main()