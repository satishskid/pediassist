# 🚀 Netlify Git CI/CD Deployment Setup

## Overview
This setup enables automatic deployment to Netlify whenever you push to your Git repository, with the custom domain `pediassist-netlify.ap`.

## 🔧 Quick Setup Steps

### 1. Connect to Netlify

#### Option A: Connect via Netlify Dashboard (Recommended)
1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Click "New site from Git"
3. Choose your Git provider (GitHub/GitLab/Bitbucket)
4. Select your PediAssist repository
5. **Important:** Use these build settings:
   - **Build command:** `pip install -r requirements-netlify.txt`
   - **Publish directory:** `./`
   - **Functions directory:** `netlify/functions/`

#### Option B: Manual Setup
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize site
netlify init
```

### 2. Configure Netlify Site

After connecting, get your site credentials:

1. Go to your Netlify dashboard
2. Select your PediAssist site
3. Go to **Site settings** → **Site details**
4. Copy your **Site ID**
5. Go to **User settings** → **Applications** → **Personal access tokens**
6. Create a new token and copy it

### 3. Set Up GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

```
NETLIFY_AUTH_TOKEN: your-personal-access-token
NETLIFY_SITE_ID: your-site-id
```

### 4. Configure Custom Domain

1. In Netlify dashboard, go to **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Enter: `pediassist-netlify.ap`
4. Follow the DNS configuration instructions

## 🎯 Deployment Triggers

The GitHub Actions workflow will automatically deploy when you:

- **Push to `main` or `master`:** Production deployment
- **Push to `develop`:** Development deployment
- **Create pull request:** Preview deployment with PR comments
- **Push to any branch:** Branch deployment

## 📋 Git Push Deployment Commands

```bash
# Deploy to production (main branch)
git add .
git commit -m "Deploy PediAssist to production"
git push origin main

# Deploy to development (develop branch)
git add .
git commit -m "Test new features"
git push origin develop

# Create preview deployment (pull request)
git add .
git commit -m "Add new feature"
git push origin feature-branch
# Then create pull request on GitHub
```

## 🔍 Monitoring Deployments

### GitHub Actions
- Check **Actions** tab in your GitHub repository
- View deployment logs and status
- See deployment history

### Netlify Dashboard
- View deploy logs in real-time
- Check site analytics
- Manage domain settings
- Configure environment variables

## 🚨 Environment Variables

Set these in your Netlify dashboard (**Site settings** → **Environment variables**):

```env
ENVIRONMENT=production
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
NETLIFY_SITE_URL=https://pediassist-netlify.ap
```

## 🛠️ Troubleshooting

### Common Issues

1. **Build fails:** Check Python version in `netlify.toml`
2. **Function errors:** Verify `netlify/functions/app.py` imports
3. **Domain not working:** Check DNS configuration
4. **GitHub Actions fails:** Verify secrets are set correctly

### Debug Commands
```bash
# Test locally
python -m pediassist.web_app

# Check Netlify status
netlify status

# View deploy logs
netlify logs --site YOUR_SITE_ID

# Test build locally
netlify build
```

## 🌐 Final URLs

After successful setup:
- **Production:** `https://pediassist-netlify.ap`
- **Deploy Previews:** Available in pull requests
- **Branch Deploys:** For testing features

## 📊 Deployment Status

You can check deployment status in:
1. GitHub Actions tab
2. Netlify dashboard
3. Pull request comments (automatic)

## 🚀 Quick Test

Once everything is set up, test with:
```bash
# Push to trigger deployment
git add .
git commit -m "Test automatic deployment"
git push origin main
```

Then check:
- GitHub Actions for build status
- Netlify dashboard for deploy status
- Your custom domain: `https://pediassist-netlify.ap`

## 💡 Pro Tips

1. **Use staging first:** Push to `develop` branch to test
2. **Check PR previews:** Every pull request gets a preview URL
3. **Monitor logs:** Both GitHub Actions and Netlify provide detailed logs
4. **Set up notifications:** Configure deployment notifications in Netlify
5. **Use environment variables:** Separate staging and production settings

Ready to deploy? Just push to your Git repository and watch the magic happen! 🎉