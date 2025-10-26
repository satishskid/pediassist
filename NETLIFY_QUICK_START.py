#!/usr/bin/env python3
"""
Netlify Quick Start Guide for PediAssist
Custom Domain: pediassist-netlify.ap
"""

import os
import subprocess
import json

def show_setup_summary():
    """Show complete setup summary"""
    print("🚀 PediAssist Netlify Deployment - Quick Start")
    print("=" * 50)
    
    print("""
✅ FILES CREATED:
   📄 netlify.toml              - Build configuration
   📄 netlify/functions/app.py  - Function handler
   📄 requirements-netlify.txt  - Dependencies
   📄 deploy_netlify.sh         - Deployment script
   📄 NETLIFY_SETUP.md          - Complete guide
   📄 .github/workflows/        - CI/CD pipeline

🎯 CUSTOM DOMAIN: pediassist-netlify.ap

📋 QUICK DEPLOYMENT STEPS:
""")
    
    steps = [
        ("1", "Install Netlify CLI", "npm install -g netlify-cli"),
        ("2", "Login to Netlify", "netlify login"),
        ("3", "Deploy to staging", "./deploy_netlify.sh (choose option 1)"),
        ("4", "Deploy to production", "./deploy_netlify.sh (choose option 2)"),
        ("5", "Configure custom domain", "Set 'pediassist-netlify.ap' in Netlify dashboard"),
    ]
    
    for step_num, description, command in steps:
        print(f"   {step_num}. {description}")
        print(f"      {command}")
        print()

def test_configuration():
    """Test the configuration files"""
    print("🔍 Testing Configuration...")
    
    # Test files exist
    files_to_check = [
        'netlify.toml',
        'netlify/functions/app.py', 
        'requirements-netlify.txt',
        'deploy_netlify.sh'
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing!")
            all_good = False
    
    # Test Python imports
    print("\\n🔍 Testing Python Environment...")
    try:
        subprocess.run([
            'python', '-c', 
            'from pediassist.web_app import app; print("✅ Flask app imports successfully")'
        ], check=True, capture_output=True)
        print("   ✅ Flask application imports correctly")
    except subprocess.CalledProcessError:
        print("   ❌ Flask application import failed")
        all_good = False
    
    return all_good

def show_next_actions():
    """Show next actions user can take"""
    print("""
🚀 READY TO DEPLOY!

Choose your deployment method:

OPTION A - Quick Deploy (Recommended):
   ./deploy_netlify.sh

OPTION B - Manual Deploy:
   netlify deploy --prod --dir=. --functions=netlify/functions/

OPTION C - Staging First:
   netlify deploy --dir=. --functions=netlify/functions/

📖 For detailed instructions, see: NETLIFY_SETUP.md

💡 Pro Tips:
   • Test locally first with: python -m pediassist.web_app
   • Use staging deploy to test before production
   • Set up GitHub Actions for automatic deployments
   • Configure custom domain in Netlify dashboard after first deploy
""")

def main():
    show_setup_summary()
    
    if test_configuration():
        print("✅ All configuration files are ready!")
        show_next_actions()
    else:
        print("❌ Some configuration issues found. Please check the files above.")
    
    print("\\n🌐 Your app will be available at: https://pediassist-netlify.ap")
    print("📱 Happy deploying!")

if __name__ == "__main__":
    main()