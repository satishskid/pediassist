#!/usr/bin/env python3
"""
Interactive Cloudflare Access Setup
Simple step-by-step setup for PediAssist
"""

import subprocess
import json
import time

def run_command(cmd, description=""):
    """Run a shell command and return output"""
    print(f"\n🔄 {description}")
    print(f"   Command: {cmd}")
    
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

def main():
    print("🚀 Cloudflare Access Setup for PediAssist")
    print("=" * 50)
    
    # Configuration
    vercel_url = "pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app"
    domain = "skids.clinic"
    subdomain = "pediassist"
    full_domain = f"{subdomain}.{domain}"
    
    print(f"📍 Vercel URL: https://{vercel_url}")
    print(f"🌐 Target Domain: https://{full_domain}")
    print("\n" + "=" * 50)
    
    # Step 1: Get API Token
    print("\n🔑 Step 1: Cloudflare API Token")
    print("   1. Go to: https://dash.cloudflare.com/profile/api-tokens")
    print("   2. Create a token with these permissions:")
    print("      - Zone:Read")
    print("      - Zone.DNS:Edit")
    print("      - Access:Apps and Policies:Edit")
    
    api_token = input("\n   Enter your API token: ").strip()
    
    if not api_token:
        print("❌ API token is required")
        return
    
    # Step 2: Test API Token
    print("\n🔍 Step 2: Testing API Token")
    cmd = f'curl -s -H "Authorization: Bearer {api_token}" -H "Content-Type: application/json" "https://api.cloudflare.com/client/v4/user/tokens/verify"'
    result = run_command(cmd, "Testing API token")
    
    if not result:
        print("❌ API token test failed")
        return
    
    try:
        data = json.loads(result)
        if not data.get("success"):
            print("❌ Invalid API token")
            return
    except:
        print("❌ Invalid response from API")
        return
    
    print("✅ API token is valid!")
    
    # Step 3: Get Zone ID
    print("\n🌍 Step 3: Getting Zone Information")
    cmd = f'curl -s -H "Authorization: Bearer {api_token}" -H "Content-Type: application/json" "https://api.cloudflare.com/client/v4/zones?name={domain}"'
    result = run_command(cmd, f"Getting zone info for {domain}")
    
    if not result:
        print("❌ Failed to get zone information")
        return
    
    try:
        data = json.loads(result)
        if not data.get("success") or not data.get("result"):
            print(f"❌ Zone {domain} not found in your account")
            return
        
        zone_id = data["result"][0]["id"]
        print(f"✅ Zone ID: {zone_id}")
    except:
        print("❌ Failed to parse zone information")
        return
    
    # Step 4: Create DNS Record
    print(f"\n📝 Step 4: Creating DNS Record")
    print(f"   Creating: {full_domain} → {vercel_url}")
    
    dns_data = {
        "type": "CNAME",
        "name": subdomain,
        "content": vercel_url,
        "ttl": 300,
        "proxied": True
    }
    
    cmd = f'''curl -s -X POST -H "Authorization: Bearer {api_token}" -H "Content-Type: application/json" \
        -d '{json.dumps(dns_data)}' \
        "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"'''
    
    result = run_command(cmd, "Creating DNS record")
    
    if not result:
        print("❌ Failed to create DNS record")
        return
    
    try:
        data = json.loads(result)
        if data.get("success"):
            print("✅ DNS record created successfully!")
        else:
            print(f"⚠️  DNS record creation: {data.get('errors', ['Unknown error'])}")
    except:
        print("⚠️  DNS record response unclear, check dashboard")
    
    # Step 5: Wait for DNS Propagation
    print(f"\n⏳ Step 5: Waiting for DNS Propagation")
    print("   Waiting 30 seconds for DNS to propagate...")
    time.sleep(30)
    
    # Step 6: Test DNS
    print(f"\n🧪 Step 6: Testing DNS")
    cmd = f"dig +short {full_domain}"
    result = run_command(cmd, "Testing DNS resolution")
    
    if result:
        print(f"   DNS resolves to: {result}")
    
    # Step 7: Manual Access Setup Instructions
    print("\n" + "=" * 60)
    print("🎉 DNS SETUP COMPLETE!")
    print("=" * 60)
    print(f"✅ DNS Record: {full_domain} → {vercel_url}")
    print(f"✅ URL: https://{full_domain}")
    
    print("\n" + "🔐 NEXT: Manual Access Setup")
    print("=" * 60)
    print("1. Go to: https://dash.cloudflare.com")
    print("2. Click: Zero Trust (in left sidebar)")
    print("3. Navigate: Access > Applications")
    print("4. Click: Add an application")
    print("5. Select: Self-hosted")
    print("6. Configure:")
    print(f"   - Name: PediAssist")
    print(f"   - Domain: {full_domain}")
    print("   - Session Duration: 24h")
    print("7. Create Policy:")
    print("   - Name: Allow Email Access")
    print("   - Action: Allow")
    print("   - Include Rule: Emails Ending In @skids.clinic")
    print("8. Save and test!")
    
    print("\n" + "🧪 TEST COMMANDS")
    print("=" * 60)
    print(f"cloudflared access login https://{full_domain}")
    print(f"cloudflared access token -app=https://{full_domain}")
    print(f"curl -H 'cf-access-token: TOKEN' https://{full_domain}/api/health")
    
    print("\n✅ Setup will be complete after manual configuration!")

if __name__ == "__main__":
    main()