#!/usr/bin/env python3
"""
Simple Cloudflare API Token Tester
Test your token and show available domains
"""

import requests
import json

def test_token(api_token):
    """Test the Cloudflare API token"""
    print("🔍 Testing Cloudflare API Token...")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Test token validation
    try:
        response = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Token is valid!")
                
                # Get account info
                account_response = requests.get("https://api.cloudflare.com/client/v4/accounts", headers=headers)
                if account_response.status_code == 200:
                    account_data = account_response.json()
                    if account_data.get("success") and account_data.get("result"):
                        account = account_data["result"][0]
                        print(f"✅ Account: {account.get('name', 'Unknown')} ({account.get('id', 'N/A')})")
                
                # Get zones
                zones_response = requests.get("https://api.cloudflare.com/client/v4/zones", headers=headers)
                if zones_response.status_code == 200:
                    zones_data = zones_response.json()
                    if zones_data.get("success") and zones_data.get("result"):
                        print(f"\n🌍 Found {len(zones_data['result'])} domains:")
                        for zone in zones_data["result"]:
                            print(f"   - {zone['name']} (ID: {zone['id'][:8]}...)")
                        return zones_data["result"]
                    else:
                        print("⚠️  No domains found")
                        return []
                else:
                    print(f"❌ Zones request failed: {zones_response.status_code}")
                    return []
            else:
                print(f"❌ Token invalid: {data.get('errors', ['Unknown error'])}")
                return []
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Token test failed: {response.status_code}")
            if error_data.get('errors'):
                for error in error_data['errors']:
                    print(f"   Error: {error.get('message', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return []

def main():
    print("🚀 Cloudflare API Token Tester")
    print("=" * 50)
    
    api_token = input("Enter your Cloudflare API token: ").strip()
    
    if not api_token:
        print("❌ No token provided")
        return
    
    zones = test_token(api_token)
    
    if zones:
        print(f"\n✅ Token working! Found {len(zones)} domains.")
        
        # Ask if they want to proceed with setup
        proceed = input("\nProceed with Cloudflare Access setup? (y/n): ").lower()
        if proceed == 'y':
            print("\n🎉 Great! Let's proceed with the setup.")
            print("Run: python3 cloudflare_setup_simple.py")
            print("Or follow the manual guide in COMPLETE_CLOUDFLARE_SETUP.md")
    else:
        print("\n❌ Token not working. Please create a new token without IP restrictions.")
        print("See: UNRESTRICTED_TOKEN_GUIDE.md")

if __name__ == "__main__":
    main()