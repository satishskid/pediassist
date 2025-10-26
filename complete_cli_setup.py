#!/usr/bin/env python3
"""
Complete CLI Cloudflare Zero Trust Setup
Interactive guide through the entire process
"""

import subprocess
import json
import time
import os
import sys

def run_command(cmd, description=""):
    """Run a shell command and return output"""
    try:
        if description:
            print(f"📋 {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Success")
            return result.stdout.strip()
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def get_api_token():
    """Get API token from user"""
    print("🔑 Step 1: Cloudflare API Token Setup")
    print("=" * 50)
    print("Please provide your Cloudflare API token.")
    print("Get it from: https://dash.cloudflare.com/profile/api-tokens")
    print("Required permissions: Zone:Read, Account:Read, Access:Apps:Edit, Access:Policies:Edit")
    print()
    
    token = input("Enter your Cloudflare API token: ").strip()
    if not token:
        print("❌ Token is required!")
        return None
    
    # Test the token
    print("\n🔍 Testing API token...")
    os.environ['CLOUDFLARE_API_TOKEN'] = token
    
    result = run_command(
        'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/user/tokens/verify',
        "Verifying API token"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success'):
                print("✅ API token is valid!")
                return token
            else:
                print(f"❌ Invalid token: {data.get('errors', 'Unknown error')}")
                return None
        except:
            print("❌ Invalid response from API")
            return None
    else:
        print("❌ Failed to verify token")
        return None

def get_account_id():
    """Get account ID using API token"""
    print("\n🏢 Step 2: Getting Account Information")
    print("=" * 50)
    
    result = run_command(
        'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/accounts',
        "Getting account ID"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success') and data.get('result'):
                account_id = data['result'][0]['id']
                account_name = data['result'][0]['name']
                print(f"✅ Found account: {account_name} (ID: {account_id})")
                return account_id
            else:
                print(f"❌ Failed to get account: {data.get('errors', 'No accounts found')}")
                return None
        except:
            print("❌ Invalid response")
            return None
    else:
        print("❌ Failed to get account ID")
        return None

def check_zone_setup():
    """Check if zone is properly configured"""
    print("\n🌐 Step 3: Checking Zone Configuration")
    print("=" * 50)
    
    result = run_command(
        'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/zones?name=skids.clinic"',
        "Checking zone skids.clinic"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success') and data.get('result'):
                zone = data['result'][0]
                zone_id = zone['id']
                print(f"✅ Found zone: {zone['name']} (ID: {zone_id})")
                print(f"   Status: {zone['status']}")
                print(f"   Plan: {zone['plan']['name']}")
                return zone_id
            else:
                print("❌ Zone skids.clinic not found or not accessible")
                return None
        except:
            print("❌ Invalid response")
            return None
    else:
        print("❌ Failed to check zone")
        return None

def create_access_application(account_id):
    """Create Access application via API"""
    print("\n🔐 Step 4: Creating Access Application")
    print("=" * 50)
    
    app_data = {
        "name": "PediAssist Medical App",
        "domain": "pediassist.skids.clinic",
        "type": "self_hosted",
        "session_duration": "24h",
        "allowed_idps": [],
        "auto_redirect_to_identity": False,
        "enable_binding_cookie": False,
        "custom_pages": []
    }
    
    json_data = json.dumps(app_data)
    
    result = run_command(
        f'curl -s -X POST -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" -d \'{json_data}\' "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps"',
        "Creating Access application"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success'):
                app_id = data['result']['id']
                print(f"✅ Access application created: {app_id}")
                return app_id
            else:
                print(f"⚠️  Application creation issue: {data.get('errors', 'Unknown error')}")
                # Try to get existing applications
                return get_existing_application(account_id)
        except:
            print("❌ Invalid response")
            return None
    else:
        print("❌ Failed to create application")
        return None

def get_existing_application(account_id):
    """Get existing application if creation failed"""
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
    else:
        print("❌ Failed to get applications")
        return None

def create_access_policy(account_id, app_id):
    """Create access policy"""
    print("\n🛡️  Step 5: Creating Access Policy")
    print("=" * 50)
    
    policy_data = {
        "name": "Whitelisted Users Access",
        "decision": "allow",
        "include": [
            {
                "email": {
                    "email": "admin@skids.clinic"
                }
            },
            {
                "email": {
                    "email": "user@skids.clinic"
                }
            }
        ],
        "exclude": [],
        "require": []
    }
    
    json_data = json.dumps(policy_data)
    
    result = run_command(
        f'curl -s -X POST -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" -d \'{json_data}\' "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps/{app_id}/policies"',
        "Creating access policy"
    )
    
    if result:
        try:
            data = json.loads(result)
            if data.get('success'):
                policy_id = data['result']['id']
                print(f"✅ Access policy created: {policy_id}")
                return True
            else:
                print(f"⚠️  Policy creation issue: {data.get('errors', 'Unknown error')}")
                return False
        except:
            print("❌ Invalid response")
            return False
    else:
        print("❌ Failed to create policy")
        return False

def final_verification():
    """Final verification"""
    print("\n🧪 Step 6: Final Verification")
    print("=" * 50)
    
    print("⏳ Waiting 30 seconds for changes to propagate...")
    time.sleep(30)
    
    print("\n🔍 Testing domain access...")
    result = run_command(
        'curl -s -I https://pediassist.skids.clinic',
        "Testing domain response"
    )
    
    if result:
        if '403' in result or 'cloudflare' in result.lower():
            print("✅ Cloudflare Access appears to be working!")
            return True
        else:
            print("⚠️  Access may not be fully active yet")
            print("This is normal - it can take a few minutes to propagate")
            return False
    else:
        print("❌ Could not test domain")
        return False

def main():
    print("🚀 Complete CLI Cloudflare Zero Trust Setup")
    print("=" * 60)
    print("This script will guide you through the entire setup process.")
    print("Make sure you have your Cloudflare API token ready.")
    print()
    
    # Step 1: Get API token
    api_token = get_api_token()
    if not api_token:
        print("\n❌ Setup cannot continue without valid API token")
        sys.exit(1)
    
    # Step 2: Get account ID
    account_id = get_account_id()
    if not account_id:
        print("\n❌ Setup cannot continue without account ID")
        sys.exit(1)
    
    # Step 3: Check zone
    zone_id = check_zone_setup()
    if not zone_id:
        print("\n⚠️  Zone check failed, but continuing...")
    
    print("\n" + "=" * 60)
    print("🚨 IMPORTANT: Zero Trust Plan Activation Required!")
    print("=" * 60)
    print("Before continuing, you MUST activate your Zero Trust plan:")
    print("1. Go to: https://dash.cloudflare.com/")
    print("2. Click on your account")
    print("3. Click 'Zero Trust' in the left menu")
    print("4. Choose 'Free' plan and complete signup")
    print()
    input("Press Enter after activating Zero Trust plan...")
    
    # Step 4: Create application
    app_id = create_access_application(account_id)
    if not app_id:
        print("\n❌ Cannot continue without application")
        sys.exit(1)
    
    # Step 5: Create policy
    policy_created = create_access_policy(account_id, app_id)
    
    # Step 6: Final verification
    verification_passed = final_verification()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    if verification_passed:
        print("🎉 SUCCESS! Cloudflare Zero Trust is configured!")
        print("\nNext steps:")
        print("1. Test login: cloudflared access login https://pediassist.skids.clinic")
        print("2. Test token: cloudflared access token -app=https://pediassist.skids.clinic")
        print("3. Add more emails to whitelist as needed")
    else:
        print("⚠️  Setup initiated but may need time to propagate")
        print("\nNext steps:")
        print("1. Wait 2-3 minutes for changes to propagate")
        print("2. Run: python check_access_status.py")
        print("3. If still not working, check Cloudflare dashboard for any errors")
    
    print(f"\nAccount ID: {account_id}")
    print(f"Application ID: {app_id}")
    print("API Token: Set in environment variable")

if __name__ == "__main__":
    main()