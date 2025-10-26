#!/usr/bin/env python3
"""
🚀 PediAssist Netlify Git CI/CD Summary
Quick summary for deploying via Git push with automatic CI/CD
"""

import os
import subprocess

def check_git_status():
    """Check current Git repository status"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def check_git_branch():
    """Check current Git branch"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def main():
    print("🚀 PediAssist Netlify Git CI/CD Deployment Summary")
    print("=" * 55)
    print()
    
    print("📋 Files Created for Git Deployment:")
    print("- .github/workflows/netlify-git-deploy.yml")
    print("- NETLIFY_GIT_CICD_SETUP.md")
    print("- git_deploy.sh")
    print("- netlify.toml")
    print("- netlify/functions/app.py")
    print("- requirements-netlify.txt")
    print()
    
    print("🎯 Custom Domain: pediassist-netlify.ap")
    print()
    
    # Check Git status
    current_branch = check_git_branch()
    git_changes = check_git_status()
    
    if current_branch:
        print(f"🌿 Current Git Branch: {current_branch}")
        if git_changes:
            print(f"📊 Uncommitted Changes: {len(git_changes.split(chr(10)))} files")
        else:
            print("✅ No uncommitted changes")
    else:
        print("⚠️  Git repository not found or not initialized")
    print()
    
    print("🚀 Quick Deployment Steps:")
    print("1. Set up GitHub Secrets (one-time setup):")
    print("   - NETLIFY_AUTH_TOKEN: Your Netlify personal access token")
    print("   - NETLIFY_SITE_ID: Your Netlify site ID")
    print()
    print("2. Connect repository to Netlify (one-time setup):")
    print("   - Go to Netlify Dashboard")
    print("   - Click 'New site from Git'")
    print("   - Connect your repository")
    print()
    print("3. Deploy with Git push:")
    print("   git add .")
    print("   git commit -m 'Deploy PediAssist'")
    print("   git push origin main")
    print()
    
    print("🔧 Alternative: Use the deployment script")
    print("   ./git_deploy.sh")
    print()
    
    print("📊 Deployment Triggers:")
    print("- main/master branch → Production deployment")
    print("- develop branch → Development deployment")
    print("- Pull requests → Preview deployment with comments")
    print("- Any branch → Branch-specific deployment")
    print()
    
    print("🌐 Final URLs:")
    print("- Production: https://pediassist-netlify.ap")
    print("- Deploy previews: Available in pull requests")
    print("- Branch deploys: For testing features")
    print()
    
    print("📈 Monitoring:")
    print("- GitHub Actions: Check Actions tab in repository")
    print("- Netlify Dashboard: https://app.netlify.com")
    print("- Deploy logs: Available in both platforms")
    print()
    
    print("⚡ Next Steps:")
    if current_branch:
        print(f"1. Commit your changes: git commit -m 'Deploy to Netlify'")
        print(f"2. Push to {current_branch}: git push origin {current_branch}")
    else:
        print("1. Initialize Git: git init")
        print("2. Add remote: git remote add origin YOUR_REPO_URL")
        print("3. Commit and push your code")
    print("3. Monitor deployment in GitHub Actions")
    print("4. Visit your app at: https://pediassist-netlify.ap")
    print()
    
    print("🎉 Ready to deploy! Just push to your Git repository.")

if __name__ == "__main__":
    main()