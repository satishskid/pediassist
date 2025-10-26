#!/usr/bin/env python3
"""
Simple Cloudflare Access Setup Tool
CLI-based setup for PediAssist with Cloudflare Access
"""

import subprocess
import json
import time
import sys
from pathlib import Path

class CloudflareSetup:
    def __init__(self):
        self.vercel_url = "https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app"
        self.domain = "skids.clinic"
        self.subdomain = "pediassist"
        self.full_url = f"https://{self.subdomain}.{self.domain}"
        
    def run_command(self, cmd, description=""):
        """Run a shell command and return output"""
        print(f"\n🔄 {description}")
        print(f"   Running: {cmd}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Success")
                return result.stdout.strip()
            else:
                print(f"   ❌ Error: {result.stderr}")
                return None
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return None
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check cloudflared
        result = self.run_command("which cloudflared", "Checking cloudflared installation")
        if not result:
            print("❌ cloudflared not found. Please install with: brew install cloudflared")
            return False
        
        # Check if cloudflared is logged in
        print("\n🔍 Checking cloudflared authentication...")
        result = self.run_command("cloudflared tunnel list", "Checking cloudflared authentication")
        if result is None:
            print("⚠️  cloudflared not authenticated. Please run: cloudflared login")
            return False
            
        print("✅ All prerequisites met!")
        return True
    
    def get_cloudflare_account_id(self):
        """Get Cloudflare account ID"""
        print("\n📋 Getting Cloudflare account information...")
        
        # This will prompt user for API token
        print("\n🔑 Please provide your Cloudflare API token.")
        print("   Create one at: https://dash.cloudflare.com/profile/api-tokens")
        print("   Required permissions: Zone:Read, Zone.Zone:Read, Zone.Zone.Settings:Read")
        
        api_token = input("\n   Enter API token: ").strip()
        
        if not api_token:
            print("❌ API token is required")
            return None
            
        # Test the API token
        cmd = f'curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" -H "Authorization: Bearer {api_token}" -H "Content-Type: application/json"'
        result = self.run_command(cmd, "Testing API token")
        
        if result:
            try:
                data = json.loads(result)
                if data.get("success"):
                    account_id = data.get("result", {}).get("status", {}).get("account", {}).get("id")
                    if account_id:
                        print(f"✅ Account ID: {account_id}")
                        return api_token, account_id
            except json.JSONDecodeError:
                pass
        
        print("❌ Invalid API token or insufficient permissions")
        return None
    
    def get_zone_id(self, api_token, account_id):
        """Get zone ID for the domain"""
        print(f"\n🔍 Getting zone ID for {self.domain}...")
        
        cmd = f'curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name={self.domain}" -H "Authorization: Bearer {api_token}" -H "Content-Type: application/json"'
        result = self.run_command(cmd, f"Getting zone ID for {self.domain}")
        
        if result:
            try:
                data = json.loads(result)
                if data.get("success") and data.get("result"):
                    zone_id = data["result"][0]["id"]
                    print(f"✅ Zone ID: {zone_id}")
                    return zone_id
            except (json.JSONDecodeError, IndexError, KeyError):
                pass
        
        print(f"❌ Could not find zone for {self.domain}")
        return None
    
    def create_dns_record(self, api_token, zone_id):
        """Create DNS CNAME record"""
        print(f"\n🌐 Creating DNS record: {self.subdomain}.{self.domain} → {self.vercel_url}")
        
        cmd = f'''curl -s -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
            -H "Authorization: Bearer {api_token}" \
            -H "Content-Type: application/json" \
            -d '{{
                "type": "CNAME",
                "name": "{self.subdomain}",
                "content": "pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app",
                "ttl": 300,
                "proxied": true
            }}' '''
        
        result = self.run_command(cmd, "Creating DNS record")
        
        if result:
            try:
                data = json.loads(result)
                if data.get("success"):
                    print("✅ DNS record created successfully!")
                    return True
            except json.JSONDecodeError:
                pass
        
        print("❌ Failed to create DNS record")
        return False
    
    def test_setup(self):
        """Test the setup"""
        print(f"\n🧪 Testing setup...")
        print(f"   Target URL: {self.full_url}")
        
        # Wait a moment for DNS propagation
        print("   Waiting 10 seconds for DNS propagation...")
        time.sleep(10)
        
        # Test DNS resolution
        cmd = f"dig +short {self.subdomain}.{self.domain}"
        result = self.run_command(cmd, "Testing DNS resolution")
        
        if result:
            print(f"   DNS resolves to: {result}")
        
        # Test HTTP access (should redirect to login)
        cmd = f"curl -I {self.full_url}"
        result = self.run_command(cmd, "Testing HTTP access")
        
        if result:
            print("   ✅ HTTP access working (expected redirect to login)")
        
        return True
    
    def print_summary(self):
        """Print setup summary"""
        print("\n" + "="*60)
        print("🎉 CLOUDFLARE ACCESS SETUP SUMMARY")
        print("="*60)
        print(f"📍 Vercel URL: {self.vercel_url}")
        print(f"🌐 Cloudflare URL: {self.full_url}")
        print(f"🔗 DNS Record: {self.subdomain}.{self.domain}")
        print("\n📋 Next Steps:")
        print("1. Go to https://dash.cloudflare.com")
        print("2. Navigate to Zero Trust > Access > Applications")
        print("3. Click 'Add an application'")
        print("4. Select 'Self-hosted'")
        print("5. Configure with these settings:")
        print(f"   - Name: PediAssist")
        print(f"   - Domain: {self.subdomain}.{self.domain}")
        print("   - Session Duration: 24h")
        print("6. Create an access policy:")
        print("   - Name: Allow Email Access")
        print("   - Action: Allow")
        print("   - Include Rule: Emails Ending In @skids.clinic")
        print("\n🧪 Test the setup:")
        print(f"   cloudflared access login {self.full_url}")
        print(f"   cloudflared access token -app={self.full_url}")
        print("="*60)
    
    def run(self):
        """Run the complete setup"""
        print("🚀 Starting Cloudflare Access setup for PediAssist")
        print("="*60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Get credentials
        credentials = self.get_cloudflare_account_id()
        if not credentials:
            return False
        
        api_token, account_id = credentials
        
        # Get zone ID
        zone_id = self.get_zone_id(api_token, account_id)
        if not zone_id:
            return False
        
        # Create DNS record
        if not self.create_dns_record(api_token, zone_id):
            return False
        
        # Test setup
        self.test_setup()
        
        # Print summary
        self.print_summary()
        
        return True

if __name__ == "__main__":
    setup = CloudflareSetup()
    success = setup.run()
    
    if success:
        print("\n✅ Setup completed! Follow the manual steps above to finish configuration.")
    else:
        print("\n❌ Setup failed. Check the errors above and try again.")
        sys.exit(1)