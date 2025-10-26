#!/usr/bin/env python3
"""
Script to fix DNS configuration and guide through Cloudflare Access setup
"""

import subprocess
import time

def run_command(cmd, description=""):
    """Run a shell command"""
    try:
        if description:
            print(f"📋 {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_current_dns():
    """Check current DNS configuration"""
    print("🔍 Checking current DNS configuration...")
    
    # Check current records
    stdout, stderr, code = run_command("dig +short pediassist.skids.clinic")
    if stdout:
        print(f"Current DNS resolution: {stdout}")
    
    # Check CNAME specifically
    stdout, stderr, code = run_command("dig +short CNAME pediassist.skids.clinic")
    if stdout:
        print(f"CNAME record: {stdout}")
    else:
        print("No CNAME record found - likely using A records")
    
    return stdout

def verify_target_deployment():
    """Verify the target Vercel deployment is working"""
    print("\n🔍 Verifying target Vercel deployment...")
    
    target_url = "https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app"
    
    stdout, stderr, code = run_command(f"curl -s -I {target_url}")
    
    if "401" in stdout:
        print("✅ Target Vercel deployment is working (401 is expected)")
        return True
    elif "404" in stdout:
        print("❌ Target Vercel deployment not found")
        return False
    else:
        print(f"🤔 Target response: {stdout[:200]}")
        return False

def provide_dns_fix_instructions():
    """Provide instructions to fix DNS configuration"""
    print("\n" + "="*60)
    print("🔧 DNS CONFIGURATION FIX NEEDED")
    print("="*60)
    
    print("\n📋 Current Issue:")
    print("   The domain pediassist.skids.clinic is pointing to Cloudflare IPs")
    print("   but not to the correct Vercel deployment.")
    
    print("\n📋 Solution - Update DNS Record:")
    print("   1. Go to: https://dash.cloudflare.com/")
    print("   2. Select your domain: skids.clinic")
    print("   3. Go to: DNS → Records")
    print("   4. Find the 'pediassist' record")
    print("   5. Update it to:")
    print("      • Type: CNAME")
    print("      • Name: pediassist")
    print("      • Target: pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app")
    print("      • Proxy status: 🟠 Proxied (orange cloud)")
    print("      • TTL: Auto")
    
    print("\n📋 Alternative if CNAME doesn't work:")
    print("   Some DNS configurations don't allow CNAME on root subdomains.")
    print("   If CNAME fails, try:")
    print("   • Type: A")
    print("   • Name: pediassist")
    print("   • IPv4 address: 76.76.19.61")  # Vercel's IP
    print("   • Proxy status: 🟠 Proxied (orange cloud)")

def provide_access_setup_instructions():
    """Provide Cloudflare Access setup instructions"""
    print("\n" + "="*60)
    print("🔐 CLOUDFLARE ACCESS SETUP")
    print("="*60)
    
    print("\n📋 Prerequisites:")
    print("   ✅ DNS must be fixed first (see instructions above)")
    print("   ✅ Domain should resolve correctly")
    
    print("\n📋 Step 1: Activate Zero Trust")
    print("   1. Go to: https://dash.cloudflare.com/")
    print("   2. Click your account name")
    print("   3. Click 'Zero Trust' in left menu")
    print("   4. Choose 'Free' plan")
    print("   5. Complete signup")
    
    print("\n📋 Step 2: Create Access Application")
    print("   1. In Zero Trust: Access → Applications")
    print("   2. Click 'Add application'")
    print("   3. Select 'Self-hosted'")
    print("   4. Configure:")
    print("      • Name: PediAssist Medical App")
    print("      • Domain: pediassist.skids.clinic")
    print("      • Session Duration: 24h")
    print("   5. Click 'Next'")
    
    print("\n📋 Step 3: Create Access Policy")
    print("   1. Policy Name: 'Whitelisted Users Access'")
    print("   2. Action: 'Allow'")
    print("   3. Include: Email addresses of allowed users")
    print("   4. Add emails like:")
    print("      • admin@skids.clinic")
    print("      • your-email@domain.com")
    print("   5. Click 'Next' then 'Add Application'")

def main():
    print("🚀 Cloudflare DNS & Access Setup Helper")
    print("="*60)
    
    # Check current DNS
    check_current_dns()
    
    # Verify target deployment
    deployment_working = verify_target_deployment()
    
    if not deployment_working:
        print("\n❌ Target Vercel deployment is not working!")
        print("Please verify the deployment URL is correct.")
        return
    
    print("\n✅ Target deployment is working!")
    
    # Provide DNS fix instructions
    provide_dns_fix_instructions()
    
    # Provide Access setup instructions
    provide_access_setup_instructions()
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60)
    print("1. Fix DNS configuration (see instructions above)")
    print("2. Wait 2-3 minutes for DNS changes")
    print("3. Set up Cloudflare Access (see instructions above)")
    print("4. Wait 2-3 minutes for Access to activate")
    print("5. Test with: python check_access_status.py")
    print("6. Test login with: cloudflared access login https://pediassist.skids.clinic")
    
    print("\n⚠️  Important:")
    print("   • DNS changes can take a few minutes to propagate")
    print("   • Cloudflare Access changes can take a few minutes")
    print("   • Make sure DNS record is 'Proxied' (orange cloud)")

if __name__ == "__main__":
    main()