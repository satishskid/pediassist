#!/usr/bin/env python3
"""
Interactive Cloudflare Access Setup Script for PediAssist
This script helps you set up Cloudflare Access protection for your PediAssist application.
"""

import json
import subprocess
import sys
import requests
from typing import Optional, Dict, Any

class CloudflareAccessSetup:
    def __init__(self):
        self.api_token = None
        self.account_id = None
        self.zone_id = None
        self.domain = None
        self.subdomain = None
        self.vercel_url = None
        
    def get_user_input(self):
        """Get required information from user"""
        print("🚀 Cloudflare Access Setup for PediAssist")
        print("=" * 50)
        
        self.api_token = input("Enter your Cloudflare API token: ").strip()
        self.domain = input("Enter your domain (e.g., skids.health): ").strip()
        self.subdomain = input("Enter subdomain for PediAssist (e.g., pediassist): ").strip()
        self.vercel_url = input("Enter your Vercel deployment URL: ").strip()
        
        self.full_domain = f"{self.subdomain}.{self.domain}"
        
        print(f"\n📋 Setup Summary:")
        print(f"   Domain: {self.domain}")
        print(f"   Subdomain: {self.subdomain}")
        print(f"   Full URL: https://{self.full_domain}")
        print(f"   Vercel URL: {self.vercel_url}")
        
        confirm = input("\nProceed with setup? (y/N): ").strip().lower()
        return confirm == 'y'
    
    def make_api_request(self, method: str, url: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request to Cloudflare"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            else:
                return None
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
    
    def get_account_id(self) -> bool:
        """Get Cloudflare account ID"""
        print("🔍 Getting account ID...")
        
        url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
        result = self.make_api_request("GET", url)
        
        if result and isinstance(result, dict) and result.get("success"):
            self.account_id = result.get("result", {}).get("status", {}).get("account", {}).get("id")
            if self.account_id:
                print(f"✅ Account ID: {self.account_id}")
                return True
        
        print("❌ Failed to get account ID")
        print("   Please make sure your API token is valid and has the required permissions")
        return False
    
    def get_zone_id(self) -> bool:
        """Get zone ID for the domain"""
        print(f"🔍 Getting zone ID for {self.domain}...")
        
        url = f"https://api.cloudflare.com/client/v4/zones?name={self.domain}"
        result = self.make_api_request("GET", url)
        
        if result and result.get("success") and result.get("result"):
            self.zone_id = result["result"][0]["id"]
            print(f"✅ Zone ID: {self.zone_id}")
            return True
        
        print(f"❌ Zone not found for {self.domain}")
        print("   Make sure your domain is added to Cloudflare first")
        return False
    
    def create_access_app(self) -> Optional[str]:
        """Create Cloudflare Access application"""
        print(f"🔄 Creating Access application for {self.full_domain}...")
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/access/apps"
        
        app_data = {
            "name": "PediAssist",
            "domain": self.full_domain,
            "type": "self_hosted",
            "session_duration": "24h",
            "app_launcher_visible": True,
            "cors_headers": {
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allowed_origins": ["*"],
                "allowed_headers": ["*"],
                "max_age": 86400
            }
        }
        
        result = self.make_api_request("POST", url, app_data)
        
        if result and result.get("success"):
            app_id = result["result"]["id"]
            print(f"✅ Access application created: {app_id}")
            return app_id
        
        print("❌ Failed to create Access application")
        return None
    
    def create_access_policy(self, app_id: str) -> bool:
        """Create access policy for the application"""
        print("🔄 Creating access policy...")
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/access/apps/{app_id}/policies"
        
        policy_data = {
            "name": "Allow Email Access",
            "decision": "allow",
            "include": [
                {
                    "email": {
                        "email": "*@*"  # Allow any email - you can restrict this
                    }
                }
            ]
        }
        
        result = self.make_api_request("POST", url, policy_data)
        
        if result and result.get("success"):
            print("✅ Access policy created")
            return True
        
        print("❌ Failed to create access policy")
        return False
    
    def create_dns_record(self) -> bool:
        """Create DNS CNAME record"""
        print(f"🔄 Creating DNS record for {self.full_domain}...")
        
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records"
        
        dns_data = {
            "type": "CNAME",
            "name": self.subdomain,
            "content": self.vercel_url.replace("https://", "").replace("http://", ""),
            "ttl": 300,
            "proxied": True  # Enable Cloudflare proxy
        }
        
        result = self.make_api_request("POST", url, dns_data)
        
        if result and result.get("success"):
            print("✅ DNS record created")
            return True
        
        print("❌ Failed to create DNS record")
        return False
    
    def test_access(self):
        """Test Cloudflare Access setup"""
        print("🧪 Testing Cloudflare Access...")
        
        print(f"   Test URL: https://{self.full_domain}")
        print(f"   CLI command: cloudflared access login https://{self.full_domain}")
        print(f"   API test: cloudflared access curl https://{self.full_domain}/api/health")
    
    def run_setup(self):
        """Run the complete setup process"""
        if not self.get_user_input():
            print("❌ Setup cancelled")
            return False
        
        if not self.get_account_id():
            return False
        
        if not self.get_zone_id():
            return False
        
        app_id = self.create_access_app()
        if not app_id:
            return False
        
        if not self.create_access_policy(app_id):
            return False
        
        if not self.create_dns_record():
            return False
        
        print("\n🎉 Cloudflare Access setup completed!")
        print(f"   Your app is now protected at: https://{self.full_domain}")
        print(f"   Vercel deployment: {self.vercel_url}")
        
        self.test_access()
        
        return True

def main():
    """Main function"""
    setup = CloudflareAccessSetup()
    
    try:
        success = setup.run_setup()
        if success:
            print("\n✅ Setup successful! Your PediAssist app is now protected by Cloudflare Access.")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()