#!/bin/bash

# 🚀 PediAssist Netlify Git Deployment Script
# This script guides you through deploying to Netlify using Git push

set -e

echo "🚀 PediAssist Netlify Git Deployment"
echo "======================================"
echo ""

# Check if Git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a Git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a Git repository. Please initialize Git first:"
    echo "   git init"
    echo "   git remote add origin YOUR_REPOSITORY_URL"
    exit 1
fi

# Show current status
echo "📊 Current Git Status:"
echo "======================"
git status
echo ""

# Check current branch
current_branch=$(git branch --show-current)
echo "🌿 Current branch: $current_branch"
echo ""

# Show deployment options
echo "🎯 Deployment Options:"
echo "======================"
echo "1. Deploy to Production (main/master branch)"
echo "2. Deploy to Development (develop branch)"
echo "3. Create Feature Branch and Deploy"
echo "4. Test deployment locally first"
echo ""

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo "🚀 Deploying to Production..."
        target_branch="main"
        if [[ "$current_branch" != "$target_branch" ]]; then
            echo "Switching to main branch..."
            git checkout main || git checkout -b main
        fi
        ;;
    2)
        echo "🔧 Deploying to Development..."
        target_branch="develop"
        if [[ "$current_branch" != "$target_branch" ]]; then
            echo "Switching to develop branch..."
            git checkout develop || git checkout -b develop
        fi
        ;;
    3)
        echo "🌟 Creating Feature Branch..."
        read -p "Enter feature branch name (e.g., feature/new-feature): " feature_name
        git checkout -b "$feature_name"
        target_branch="$feature_name"
        ;;
    4)
        echo "🧪 Testing deployment locally..."
        echo "Running local tests..."
        python -c "import pediassist; print('✅ PediAssist imports successfully')"
        python -c "from pediassist.web_app import app; print('✅ Flask app loads successfully')"
        echo "✅ Local tests passed!"
        read -p "Continue with Git deployment? (y/n): " continue_deploy
        if [[ "$continue_deploy" != "y" ]]; then
            echo "Deployment cancelled."
            exit 0
        fi
        ;;
    *)
        echo "❌ Invalid option. Exiting."
        exit 1
        ;;
esac

# Check for uncommitted changes
echo ""
echo "🔍 Checking for uncommitted changes..."
if [[ -n $(git status --porcelain) ]]; then
    echo "📋 Uncommitted changes found:"
    git status --short
    echo ""
    read -p "Add and commit all changes? (y/n): " commit_all
    if [[ "$commit_all" == "y" ]]; then
        read -p "Enter commit message (or press Enter for default): " commit_msg
        if [[ -z "$commit_msg" ]]; then
            commit_msg="Deploy PediAssist to $target_branch"
        fi
        git add .
        git commit -m "$commit_msg"
        echo "✅ Changes committed: $commit_msg"
    else
        echo "Please commit your changes manually and run this script again."
        exit 0
    fi
else
    echo "✅ No uncommitted changes found."
fi

# Push to remote
echo ""
echo "☁️  Pushing to remote repository..."
echo "Branch: $target_branch"
echo ""

# Check if remote exists
if git remote | grep -q origin; then
    git push origin "$target_branch"
    echo "✅ Successfully pushed to origin/$target_branch"
else
    echo "❌ No remote repository configured."
    echo "Please set up your remote repository first:"
    echo "   git remote add origin YOUR_REPOSITORY_URL"
    echo "   git push -u origin $target_branch"
    exit 1
fi

# Show deployment status
echo ""
echo "🎯 Deployment Status:"
echo "======================"
echo "✅ Git push completed!"
echo "🔄 GitHub Actions will automatically deploy to Netlify"
echo ""
echo "📊 Next Steps:"
echo "1. Check GitHub Actions tab in your repository"
echo "2. Monitor deployment progress"
echo "3. Visit your app at: https://pediassist-netlify.ap"
echo ""
echo "🔗 Quick Links:"
echo "- GitHub Actions: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:\/]\(.*\)\.git/\1/')/actions"
echo "- Netlify Dashboard: https://app.netlify.com"
echo "- Your App: https://pediassist-netlify.ap"
echo ""
echo "🚀 Deployment initiated! Check GitHub Actions for progress."