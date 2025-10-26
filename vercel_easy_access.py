#!/usr/bin/env python3
"""
Vercel Easy Access Configuration Helper
Makes the PediAssist application easily accessible via Vercel URL
"""

import json
import subprocess
import os

def create_vercel_config():
    """Create optimized Vercel configuration for easy access"""
    
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "api/index.py",
                "use": "@vercel/python",
                "config": {
                    "maxLambdaSize": "15mb"
                }
            }
        ],
        "routes": [
            {
                "src": "/simple",
                "dest": "api/index.py"
            },
            {
                "src": "/api/(.*)",
                "dest": "api/index.py"
            },
            {
                "src": "/(.*)",
                "dest": "api/index.py"
            }
        ],
        "env": {
            "ENVIRONMENT": "production",
            "PYTHON_VERSION": "3.9"
        },
        "functions": {
            "api/index.py": {
                "maxDuration": 30
            }
        }
    }
    
    # Backup existing config
    if os.path.exists('vercel.json'):
        with open('vercel.json', 'r') as f:
            backup = f.read()
        with open('vercel.json.backup', 'w') as f:
            f.write(backup)
        print("📋 Backed up existing vercel.json to vercel.json.backup")
    
    # Write new config
    with open('vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print("✅ Created optimized Vercel configuration")
    return True

def create_vercelignore():
    """Create .vercelignore to optimize deployment"""
    
    vercelignore_content = """
# Development files
.git/
.gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Environment
.env
.venv/
venv/

# Documentation
*.md
!README.md
!DEPLOYMENT.md

# Docker files (not needed for Vercel)
Dockerfile
docker-compose.yml
docker/

# Test files
test_*.py
*test*.py

# Local data
*.log
*.sqlite
*.db

# Cloudflare setup files (not needed for Vercel)
cloudflare_*
*cloudflare*
*access*
*setup*.py

# Backup files
*.backup
*.bak
"""
    
    with open('.vercelignore', 'w') as f:
        f.write(vercelignore_content.strip())
    
    print("✅ Created .vercelignore for optimized deployment")
    return True

def create_deployment_script():
    """Create deployment script for easy Vercel deployment"""
    
    deploy_script = """#!/bin/bash
# Easy Vercel Deployment Script for PediAssist

echo "🚀 Deploying PediAssist to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm i -g vercel
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel deploy --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be accessible at:"
echo "   https://[your-deployment-url].vercel.app/simple"
echo "   https://[your-deployment-url].vercel.app"
"""
    
    with open('deploy_vercel.sh', 'w') as f:
        f.write(deploy_script)
    
    os.chmod('deploy_vercel.sh', 0o755)
    print("✅ Created deployment script: deploy_vercel.sh")
    return True

def check_current_deployment():
    """Check current Vercel deployment status"""
    
    print("🔍 Checking current deployment status...")
    
    # Check if we can access the simple interface
    try:
        result = subprocess.run([
            'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
            'https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app/simple'
        ], capture_output=True, text=True)
        
        if result.stdout.strip() == '200':
            print("✅ Simple interface is accessible!")
            return True
        else:
            print(f"❌ Simple interface returned HTTP {result.stdout.strip()}")
            
            # Try without /simple
            result2 = subprocess.run([
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                'https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app'
            ], capture_output=True, text=True)
            
            print(f"❌ Root path returned HTTP {result2.stdout.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")
        return False

def create_easy_access_guide():
    """Create easy access guide"""
    
    guide_content = """
# 🚀 PediAssist Vercel Easy Access Guide

## Current Deployment Status
Your app is deployed at: `https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app`

## Quick Access URLs
- Simple Interface: https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app/simple
- API Endpoint: https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app/api
- Full App: https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app

## Making a New Deployment
If you need to redeploy with updates:

1. **Using the script:**
   ```bash
   ./deploy_vercel.sh
   ```

2. **Manual deployment:**
   ```bash
   vercel deploy --prod
   ```

3. **Install Vercel CLI if needed:**
   ```bash
   npm i -g vercel
   ```

## Configuration Files
- `vercel.json` - Main Vercel configuration
- `.vercelignore` - Files to exclude from deployment
- `deploy_vercel.sh` - Deployment script

## Troubleshooting
If you get 401 errors:
1. Check if the deployment is public in Vercel dashboard
2. Verify the routes in vercel.json
3. Check the deployment logs in Vercel dashboard

## Next Steps
1. Test the simple interface: https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app/simple
2. If working, you can bookmark this URL for easy access
3. Consider setting up a custom domain later if needed
"""
    
    with open('VERCEL_EASY_ACCESS.md', 'w') as f:
        f.write(guide_content)
    
    print("✅ Created easy access guide: VERCEL_EASY_ACCESS.md")
    return True

def main():
    print("🚀 Vercel Easy Access Configuration")
    print("="*50)
    
    # Check current deployment
    working = check_current_deployment()
    
    if working:
        print("\n✅ Current deployment is working!")
    else:
        print("\n⚠️  Current deployment has issues, but we'll optimize the config anyway")
    
    # Create optimized configuration
    print("\n📋 Creating optimized Vercel configuration...")
    create_vercel_config()
    create_vercelignore()
    create_deployment_script()
    create_easy_access_guide()
    
    print("\n" + "="*50)
    print("🎯 NEXT STEPS:")
    print("="*50)
    
    if working:
        print("✅ Your app is accessible at:")
        print("   https://pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app/simple")
        print("\n📖 Check VERCEL_EASY_ACCESS.md for full guide")
    else:
        print("1. Check VERCEL_EASY_ACCESS.md for troubleshooting")
        print("2. Consider redeploying with: ./deploy_vercel.sh")
        print("3. Or check Vercel dashboard for deployment issues")
    
    print("\n💡 Bookmark the simple interface URL for easy access!")

if __name__ == "__main__":
    main()