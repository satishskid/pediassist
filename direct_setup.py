#!/usr/bin/env python3
"""
Direct Cloudflare Access Setup
Uses the working token to set up everything
"""

import requests
import json
import time

def main():
    print("🚀 Direct Cloudflare Access Setup")
    print("=" * 50)
    
    # Configuration
    api_token = "fpOTQqerjn01YcKfbcT9TljEDqGIO8vAPtOsqSra"  # Your working token
    domain = "skids.clinic"
    subdomain = "pediassist"
    vercel_target = "pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app"
    
    print(f"📍 Domain: {domain}")
    print(f"🎯 Subdomain: {subdomain}.{domain}")
    print(f"🔗 Target: {vercel_target}")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Get Zone ID
    print(f"\n🔍 Getting zone ID for {domain}...")
    try:
        response = requests.get(f"https://api.cloudflare.com/client/v4/zones?name={domain}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result"):
                zone_id = data["result"][0]["id"]
                print(f"✅ Zone ID: {zone_id}")
            else:
                print("❌ Zone not found")
                return
        else:
            print(f"❌ Failed to get zone: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting zone: {e}")
        return
    
    # Step 2: Check existing DNS records
    print(f"\n🔍 Checking existing DNS records...")
    try:
        response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={subdomain}.{domain}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result"):
                existing = data["result"][0]
                print(f"⚠️  Found existing record: {existing['name']} → {existing['content']}")
                print(f"   Record ID: {existing['id']}")
                
                # Update existing record
                print(f"\n📝 Updating existing DNS record...")
                update_data = {
                    "type": "CNAME",
                    "name": subdomain,
                    "content": vercel_target,
                    "ttl": 300,
                    "proxied": True
                }
                
                response = requests.put(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{existing['id']}", 
                                      headers=headers, json=update_data)
                if response.status_code == 200:
                    print("✅ DNS record updated successfully!")
                else:
                    print(f"❌ Failed to update DNS record: {response.status_code}")
                    return
            else:
                # Create new record
                print(f"\n📝 Creating new DNS record...")
                dns_data = {
                    "type": "CNAME",
                    "name": subdomain,
                    "content": vercel_target,
                    "ttl": 300,
                    "proxied": True
                }
                
                response = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", 
                                       headers=headers, json=dns_data)
                if response.status_code == 200:
                    print("✅ DNS record created successfully!")
                else:
                    print(f"❌ Failed to create DNS record: {response.status_code}")
                    return
        else:
            print(f"❌ Failed to check DNS records: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error with DNS record: {e}")
        return
    
    # Step 3: Wait for DNS propagation
    print(f"\n⏳ Waiting for DNS propagation...")
    time.sleep(15)
    
    # Step 4: Test DNS
    print(f"\n🧪 Testing DNS resolution...")
    try:
        import subprocess
        result = subprocess.run(f"dig +short {subdomain}.{domain}", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ DNS resolves to: {result.stdout.strip()}")
        else:
            print(f"⚠️  DNS test failed, but record may still propagate")
    except:
        print(f"⚠️  Could not test DNS resolution")
    
    # Step 5: Manual Access Setup Instructions
    print("\n" + "=" * 60)
    print("🎉 DNS SETUP COMPLETE!")
    print("=" * 60)
    print(f"✅ DNS Record: {subdomain}.{domain} → {vercel_target}")
    print(f"✅ URL: https://{subdomain}.{domain}")
    
    print("\n" + "🔐 NEXT: Manual Access Setup")
    print("=" * 60)
    print("1. Go to: https://dash.cloudflare.com")
    print("2. Click: Zero Trust (in left sidebar)")
    print("3. Navigate: Access → Applications")
    print("4. Click: Add an application")
    print("5. Select: Self-hosted")
    print("6. Configure:")
    print(f"   - Name: PediAssist")
    print(f"   - Domain: {subdomain}.{domain}")
    print("   - Session Duration: 24h")
    print("7. Create Policy:")
    print("   - Name: Allow Team Access")
    print("   - Action: Allow")
    print("   - Include Rule: Emails Ending In @skids.clinic")
    print("8. Save Application")
    
    print("\n" + "🧪 TEST COMMANDS")
    print("=" * 60)
    print(f"cloudflared access login https://{subdomain}.{domain}")
    print(f"cloudflared access token -app=https://{subdomain}.{domain}")
    print(f"curl -H 'cf-access-token: TOKEN' https://{subdomain}.{domain}/api/health")
    
    print("\n✅ Setup will be complete after manual Access configuration!")

if __name__ == "__main__":
    main()