#!/usr/bin/env python3
"""
Diagnostic script to check Cloudflare setup status
"""

import os
import json
import subprocess

def run_curl_command(cmd, description=""):
    """Run curl command and return parsed JSON"""
    try:
        if description:
            print(f"📋 {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {result.stdout.strip()[:200]}")
                return None
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    api_token = "jyt_RB4MI27f2f514327f6ec9f477357f545b58afM0L6aYJt0G7it31znnv5WBj3DIm6hhi"
    os.environ['CLOUDFLARE_API_TOKEN'] = api_token
    
    print("🔍 Cloudflare Setup Diagnostic")
    print("=" * 50)
    
    # Test token validity
    print("\n1️⃣ Testing API Token...")
    user_info = run_curl_command(
        f'curl -s -H "Authorization: Bearer {api_token}" https://api.cloudflare.com/client/v4/user',
        "Getting user information"
    )
    
    if user_info and user_info.get('success'):
        user = user_info['result']
        print(f"✅ Token valid - User: {user.get('email', 'Unknown')}")
        print(f"✅ User ID: {user.get('id')}")
    else:
        print("❌ Token invalid or expired")
        return
    
    # List all zones
    print("\n2️⃣ Listing All Zones...")
    zones_info = run_curl_command(
        f'curl -s -H "Authorization: Bearer {api_token}" https://api.cloudflare.com/client/v4/zones',
        "Getting all zones"
    )
    
    if zones_info and zones_info.get('success'):
        zones = zones_info.get('result', [])
        if zones:
            print(f"✅ Found {len(zones)} zone(s):")
            for zone in zones:
                print(f"   • {zone['name']} (ID: {zone['id']})")
                if zone['name'] == 'skids.clinic':
                    print(f"     🎯 Found skids.clinic!")
                    print(f"     Account ID: {zone['account']['id']}")
                    print(f"     Zone ID: {zone['id']}")
                    print(f"     Status: {zone.get('status', 'Unknown')}")
        else:
            print("❌ No zones found")
    else:
        print(f"❌ Failed to get zones: {zones_info.get('errors', 'Unknown error')}")
    
    # Check specific zone
    print("\n3️⃣ Checking skids.clinic specifically...")
    skids_zone = run_curl_command(
        f'curl -s -H "Authorization: Bearer {api_token}" "https://api.cloudflare.com/client/v4/zones?name=skids.clinic"',
        "Checking skids.clinic zone"
    )
    
    if skids_zone:
        print(f"Response: {json.dumps(skids_zone, indent=2)[:500]}...")
    
    # Check DNS records for skids.clinic
    if zones_info and zones_info.get('success'):
        for zone in zones_info.get('result', []):
            if zone['name'] == 'skids.clinic':
                zone_id = zone['id']
                print(f"\n4️⃣ DNS Records for {zone['name']}...")
                dns_info = run_curl_command(
                    f'curl -s -H "Authorization: Bearer {api_token}" "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"',
                    "Getting DNS records"
                )
                
                if dns_info and dns_info.get('success'):
                    records = dns_info.get('result', [])
                    if records:
                        print(f"✅ Found {len(records)} DNS record(s):")
                        for record in records:
                            print(f"   • {record['name']} ({record['type']}) -> {record['content']}")
                            if 'pediassist' in record['name']:
                                print(f"     🎯 Found pediassist record!")
                                print(f"     Proxied: {'Yes' if record.get('proxied') else 'No'}")
                    else:
                        print("❌ No DNS records found")
                break
    
    print("\n5️⃣ Current Status Check...")
    print("Domain: pediassist.skids.clinic")
    print("Expected CNAME: pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app")
    print("Expected Proxy: Enabled (orange cloud)")
    
    # Test current domain response
    print("\n6️⃣ Testing domain response...")
    domain_test = run_curl_command(
        'curl -s -I https://pediassist.skids.clinic',
        "Testing domain response"
    )

if __name__ == "__main__":
    main()