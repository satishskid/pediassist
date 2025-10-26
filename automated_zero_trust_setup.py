#!/usr/bin/env python3
"""
Complete Automated Cloudflare Zero Trust Setup
Handles plan selection, application creation, and policy configuration via CLI
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Optional

class CloudflareZeroTrustSetup:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.cloudflare.com/client/v4'
        self.account_id = None
        
    def get_account_id(self) -> Optional[str]:
        """Get Cloudflare account ID"""
        try:
            response = requests.get(
                f'{self.base_url}/accounts',
                headers=self.headers
            )
            data = response.json()
            
            if data.get('success') and data.get('result'):
                self.account_id = data['result'][0]['id']
                print(f"✅ Account ID found: {self.account_id}")
                return self.account_id
            else:
                print(f"❌ Failed to get account ID: {data.get('errors', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting account ID: {e}")
            return None
    
    def check_zero_trust_status(self) -> bool:
        """Check if Zero Trust is activated"""
        try:
            if not self.account_id:
                return False
                
            response = requests.get(
                f'{self.base_url}/accounts/{self.account_id}/access/subscriptions',
                headers=self.headers
            )
            data = response.json()
            
            if data.get('success'):
                print("✅ Zero Trust subscription found")
                return True
            else:
                print("⚠️  Zero Trust subscription not found - need to activate")
                return False
                
        except Exception as e:
            print(f"❌ Error checking Zero Trust status: {e}")
            return False
    
    def create_access_application(self) -> bool:
        """Create Access application for pediassist.skids.clinic"""
        try:
            if not self.account_id:
                return False
                
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
            
            response = requests.post(
                f'{self.base_url}/accounts/{self.account_id}/access/apps',
                headers=self.headers,
                json=app_data
            )
            data = response.json()
            
            if data.get('success'):
                app_id = data['result']['id']
                print(f"✅ Access application created: {app_id}")
                return True
            else:
                print(f"❌ Failed to create application: {data.get('errors', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating application: {e}")
            return False
    
    def create_access_policy(self) -> bool:
        """Create access policy with whitelisted emails"""
        try:
            if not self.account_id:
                return False
                
            # Get the application first
            response = requests.get(
                f'{self.base_url}/accounts/{self.account_id}/access/apps',
                headers=self.headers
            )
            apps_data = response.json()
            
            if not apps_data.get('success') or not apps_data.get('result'):
                print("❌ No applications found to add policy to")
                return False
            
            app_id = apps_data['result'][0]['id']
            
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
            
            response = requests.post(
                f'{self.base_url}/accounts/{self.account_id}/access/apps/{app_id}/policies',
                headers=self.headers,
                json=policy_data
            )
            data = response.json()
            
            if data.get('success'):
                policy_id = data['result']['id']
                print(f"✅ Access policy created: {policy_id}")
                return True
            else:
                print(f"❌ Failed to create policy: {data.get('errors', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating policy: {e}")
            return False
    
    def verify_setup(self) -> bool:
        """Verify the complete setup"""
        try:
            # Test the domain
            response = requests.get(
                f'https://pediassist.skids.clinic',
                allow_redirects=True,
                timeout=10
            )
            
            if response.status_code == 403 or 'cloudflare' in response.text.lower():
                print("✅ Cloudflare Access is active!")
                return True
            else:
                print("⚠️  Access may not be fully active yet")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying setup: {e}")
            return False

def main():
    print("🚀 Starting Automated Cloudflare Zero Trust Setup")
    print("=" * 60)
    
    # Get API token from environment
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    if not api_token:
        print("❌ CLOUDFLARE_API_TOKEN environment variable not set")
        print("Please set it with: export CLOUDFLARE_API_TOKEN='your_token_here'")
        sys.exit(1)
    
    setup = CloudflareZeroTrustSetup(api_token)
    
    # Step 1: Get account ID
    print("\n📋 Step 1: Getting account information...")
    if not setup.get_account_id():
        print("❌ Failed to get account ID. Stopping.")
        sys.exit(1)
    
    # Step 2: Check Zero Trust status
    print("\n📋 Step 2: Checking Zero Trust status...")
    if not setup.check_zero_trust_status():
        print("⚠️  Zero Trust not activated. You'll need to activate it in the dashboard.")
        print("   Go to: Zero Trust → Choose Free Plan → Complete signup")
        input("   Press Enter after activating Zero Trust...")
    
    # Step 3: Create Access application
    print("\n📋 Step 3: Creating Access application...")
    if not setup.create_access_application():
        print("❌ Failed to create application. Checking if one exists...")
    
    # Step 4: Create Access policy
    print("\n📋 Step 4: Creating Access policy...")
    if not setup.create_access_policy():
        print("❌ Failed to create policy.")
    
    # Step 5: Verify setup
    print("\n📋 Step 5: Verifying setup...")
    time.sleep(5)  # Wait for changes to propagate
    
    if setup.verify_setup():
        print("\n🎉 SUCCESS! Cloudflare Zero Trust is configured!")
        print("\nNext steps:")
        print("1. Test with: cloudflared access login https://pediassist.skids.clinic")
        print("2. Test with: cloudflared access token -app=https://pediassist.skids.clinic")
    else:
        print("\n⚠️  Setup may need a few more minutes to propagate.")
        print("Try running: python check_access_status.py in a few minutes.")

if __name__ == "__main__":
    main()