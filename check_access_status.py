#!/usr/bin/env python3
"""
Quick Cloudflare Access Status Checker
Helps verify your Zero Trust setup
"""

import requests
import json
from urllib.parse import urlparse

def check_access_status(domain):
    """Check if Cloudflare Access is working on a domain"""
    print(f"🔍 Checking Cloudflare Access status for: {domain}")
    print("=" * 50)
    
    try:
        # Test direct access
        response = requests.get(f"https://{domain}", allow_redirects=True, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"🌐 Final URL: {response.url}")
        print(f"📄 Content Length: {len(response.text)} bytes")
        
        # Check for Cloudflare Access headers
        cf_headers = {k: v for k, v in response.headers.items() if 'cf' in k.lower() or 'access' in k.lower()}
        if cf_headers:
            print("\n🔒 Cloudflare Headers Found:")
            for key, value in cf_headers.items():
                print(f"  {key}: {value}")
        else:
            print("\n⚠️  No Cloudflare Access headers detected")
        
        # Check for Access login page
        if 'cloudflare' in response.text.lower() and 'access' in response.text.lower():
            print("\n✅ Cloudflare Access login page detected!")
            return True
        elif 'DEPLOYMENT_NOT_FOUND' in response.text:
            print("\n❌ Vercel deployment not found - DNS issue")
            return False
        else:
            print(f"\n📝 Response preview: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection error: {e}")
        return False

def main():
    domain = "pediassist.skids.clinic"
    
    print("🚀 Cloudflare Access Status Checker")
    print("=" * 50)
    
    # Check current status
    is_protected = check_access_status(domain)
    
    print("\n" + "=" * 50)
    if is_protected:
        print("✅ SUCCESS: Cloudflare Access is protecting your domain!")
        print("\nNext step: Test with:")
        print(f"  cloudflared access login https://{domain}")
    else:
        print("❌ ISSUE: Cloudflare Access is not active")
        print("\nPlease check:")
        print("1. ✅ Zero Trust plan is activated")
        print("2. ✅ Access application is configured")
        print("3. ✅ DNS record is proxied (orange cloud)")
        print("4. ✅ Application domain matches exactly")

if __name__ == "__main__":
    main()