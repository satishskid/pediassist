# 🚀 Netlify Deployment Setup for PediAssist

## Quick Start Guide

### 1. Connect to Netlify

#### Option A: Connect via Git Repository
1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Click "New site from Git"
3. Choose your Git provider (GitHub/GitLab/Bitbucket)
4. Select your PediAssist repository
5. Configure build settings:
   - **Build command:** `pip install -r requirements-netlify.txt`
   - **Publish directory:** `./`
   - **Functions directory:** `netlify/functions/`

#### Option B: Deploy via CLI
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy to Netlify
netlify deploy --prod --dir=. --functions=netlify/functions/
```

### 2. Configure Custom Domain

1. In Netlify dashboard, go to **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Enter: `pediassist-netlify.ap`
4. Follow DNS configuration instructions

### 3. Environment Variables

Set these in Netlify dashboard under **Site settings** → **Environment variables**:

```env
ENVIRONMENT=production
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

### 4. GitHub Actions Setup (Optional)

For automated deployments:

1. Get your Netlify credentials:
   - **Personal Access Token:** [Netlify Applications](https://app.netlify.com/user/applications/personal)
   - **Site ID:** Found in Netlify dashboard → Site settings → Site details

2. Add to GitHub repository secrets:
   - `NETLIFY_AUTH_TOKEN`: Your personal access token
   - `NETLIFY_SITE_ID`: Your site ID

### 5. Manual Deployment Commands

```bash
# Deploy to staging
netlify deploy --dir=. --functions=netlify/functions/

# Deploy to production
netlify deploy --prod --dir=. --functions=netlify/functions/

# Deploy with custom message
netlify deploy --prod --dir=. --functions=netlify/functions/ --message="Deploy medical app updates"
```

## 🏗️ Build Configuration

### Files Created:
- `netlify.toml` - Main build configuration
- `netlify/functions/app.py` - Function handler
- `requirements-netlify.txt` - Dependencies
- `.github/workflows/netlify-deploy.yml` - CI/CD pipeline

### Build Process:
1. Netlify installs Python dependencies
2. Functions are built and deployed
3. Site is served via Netlify Functions
4. Custom domain: `pediassist-netlify.ap`

## 🔧 Troubleshooting

### Common Issues:
1. **Build fails:** Check Python version in netlify.toml
2. **Function errors:** Verify imports in netlify/functions/app.py
3. **Domain issues:** Ensure DNS is properly configured
4. **Dependencies:** Use requirements-netlify.txt for production

### Logs:
- Check Netlify deploy logs in dashboard
- Use `netlify logs --site YOUR_SITE_ID` for CLI logs

## 📋 Deployment Checklist

- [ ] Repository connected to Netlify
- [ ] Custom domain: `pediassist-netlify.ap` configured
- [ ] Environment variables set
- [ ] GitHub Actions secrets configured (optional)
- [ ] Test deployment successful
- [ ] Domain DNS configured
- [ ] SSL certificate active

## 🌐 Access URLs

After deployment:
- **Production:** `https://pediassist-netlify.ap`
- **Deploy Preview:** Available in pull requests
- **Branch Deploy:** For testing branches

## 🚀 Next Steps

1. Test the deployment
2. Configure monitoring
3. Set up custom email notifications
4. Configure backup strategies

Need help? Check Netlify documentation or run:
```bash
netlify help
```