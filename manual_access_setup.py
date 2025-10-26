#!/usr/bin/env python3
"""
Manual Cloudflare Access setup guide with verification
"""

import time
import subprocess
import json

def check_domain_status():
    """Check current domain status"""
    print("🔍 Checking current domain status...")
    
    try:
        result = subprocess.run(['curl', '-s', '-I', 'https://pediassist.skids.clinic'], 
                                capture_output=True, text=True)
        
        if 'DEPLOYMENT_NOT_FOUND' in result.stdout:
            print("❌ Vercel deployment not found - DNS issue")
            print("   The domain is pointing to Cloudflare but Vercel can't find the deployment")
        elif 'Authentication Required' in result.stdout:
            print("✅ Cloudflare Access is working!")
            return True
        else:
            print(f"🤔 Current response: {result.stdout[:200]}...")
            
        # Check for Cloudflare headers
        if 'cloudflare' in result.stdout.lower():
            print("✅ DNS is proxied through Cloudflare")
        else:
            print("⚠️  DNS may not be proxied")
            
    except Exception as e:
        print(f"❌ Error checking domain: {e}")
    
    return False

def provide_step_by_step_guide():
    """Provide detailed step-by-step setup instructions"""
    print("\n" + "="*60)
    print("🚀 CLOUDFLARE ACCESS SETUP GUIDE")
    print("="*60)
    
    print("\n📋 STEP 1: Activate Cloudflare Zero Trust")
    print("   1. Go to: https://dash.cloudflare.com/")
    print("   2. Click your account name in the top left")
    print("   3. Click 'Zero Trust' in the left sidebar")
    print("   4. Choose 'Free' plan (requires payment method)")
    print("   5. Complete the signup process")
    
    print("\n📋 STEP 2: Create Access Application")
    print("   1. In Zero Trust dashboard, go to: Access → Applications")
    print("   2. Click 'Add application'")
    print("   3. Select 'Self-hosted'")
    print("   4. Configure application:")
    print("      • Name: PediAssist Medical App")
    print("      • Domain: pediassist.skids.clinic")
    print("      • Session Duration: 24h")
    print("      • Click 'Next'")
    
    print("\n📋 STEP 3: Create Access Policy")
    print("   1. Policy Name: 'Whitelisted Users Access'")
    print("   2. Action: 'Allow'")
    print("   3. Add Rule:")
    print("      • Rule Type: 'Emails'")
    print("      • Add your email addresses:")
    print("        - admin@skids.clinic")
    print("        - user@skids.clinic")
    print("        - Add your actual email here!")
    print("   4. Click 'Next' then 'Add Application'")
    
    print("\n📋 STEP 4: Verify DNS Configuration")
    print("   1. Go to: DNS → Records")
    print("   2. Find 'pediassist' CNAME record")
    print("   3. Ensure it shows 🟠 'Proxied' (orange cloud)")
    print("   4. If it's gray, click the cloud to enable proxy")
    
    print("\n⏰ Wait 2-3 minutes after completing all steps")
    
    print("\n📋 STEP 5: Test the Setup")
    print("   Run this command to test:")
    print("   cloudflared access login https://pediassist.skids.clinic")
    print("   OR")
    print("   python check_access_status.py")

def main():
    print("🚀 Starting Cloudflare Access Setup Verification")
    print("="*60)
    
    # Check current status
    access_working = check_domain_status()
    
    if access_working:
        print("\n✅ Cloudflare Access appears to be working!")
        print("You should be able to access the application.")
    else:
        print("\n❌ Cloudflare Access is not working yet.")
        provide_step_by_step_guide()
        
        print("\n🔄 After completing the manual setup, run:")
        print("   python check_access_status.py")
        print("   to verify everything is working correctly.")

if __name__ == "__main__":
    main()