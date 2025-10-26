# Manual Cloudflare DNS & Access Setup

## ✅ Current Status
- ✅ Vercel deployment working: `pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app`
- ✅ API token working (found 5 domains including skids.clinic)
- ⚠️  Need manual DNS record creation due to permission scope

## 🎯 Goal
Create `pediassist.skids.clinic` → `pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app`

## 📝 Step 1: Manual DNS Record Creation

1. **Go to Cloudflare Dashboard:**
   ```
   https://dash.cloudflare.com
   ```

2. **Find your domain:**
   - Click on `skids.clinic` from your domains list

3. **Navigate to DNS:**
   - Click `DNS` in the left sidebar
   - Click `Records` tab

4. **Add DNS Record:**
   - Click `Add record`
   - **Type:** CNAME
   - **Name:** `pediassist`
   - **Target:** `pediassist-le3zjeric-satishs-projects-89f8c44c.vercel.app`
   - **TTL:** Auto (or 300 seconds)
   - **Proxy status:** 🟢 Proxied (orange cloud)
   - Click `Save`

## 🔐 Step 2: Cloudflare Access Configuration

1. **Navigate to Zero Trust:**
   - Click `Zero Trust` in left sidebar
   - (If first time, may need to accept terms)

2. **Go to Access:**
   - Navigate: `Access` → `Applications`

3. **Add Application:**
   - Click `Add an application`
   - Select `Self-hosted`

4. **Configure Application:**
   ```
   Name: PediAssist
   Domain: pediassist.skids.clinic
   Session Duration: 24h
   ```

5. **Create Policy:**
   - Click `Add a policy`
   - **Policy Name:** `Allow Team Access`
   - **Action:** `Allow`
   - **Include Rule:**
     ```
     Rule Type: Emails ending in
     Value: @skids.clinic
     ```
   - Click `Save policy`

6. **Save Application:**
   - Click `Save application`

## 🧪 Step 3: Test the Setup

### Test 1: DNS Resolution
```bash
# Check DNS propagation (takes 1-5 minutes)
dig +short pediassist.skids.clinic

# Should return Cloudflare IPs like:
# 104.21.x.x
# 172.67.x.x
```

### Test 2: Access Authentication
```bash
# Test Access login
cloudflared access login https://pediassist.skids.clinic

# Get access token
cloudflared access token -app=https://pediassist.skids.clinic

# Test API with token
TOKEN=$(cloudflared access token -app=https://pediassist.skids.clinic)
curl -H "cf-access-token: $TOKEN" https://pediassist.skids.clinic/api/health
```

### Test 3: Web Browser Test
1. Open browser to: `https://pediassist.skids.clinic`
2. Should redirect to Cloudflare Access login
3. Enter email with @skids.clinic domain
4. Should grant access to PediAssist application

## 🚨 Common Issues

### Issue: DNS not resolving
- **Solution:** Wait 5-10 minutes for propagation
- **Check:** Verify record in Cloudflare DNS dashboard
- **Test:** Use `dig` or `nslookup`

### Issue: Access policy not working
- **Solution:** Check email domain in policy matches your email
- **Alternative:** Use "Emails" rule instead of "Emails ending in"
- **Debug:** Check Access logs in Cloudflare dashboard

### Issue: Token generation fails
- **Solution:** Ensure cloudflared is authenticated
- **Check:** Run `cloudflared tunnel list`
- **Re-auth:** Run `cloudflared tunnel login`

## ✅ Success Indicators

1. **DNS:** `dig pediassist.skids.clinic` returns Cloudflare IPs
2. **Access:** Browser shows Cloudflare Access login page
3. **Auth:** Email with @skids.clinic domain grants access
4. **API:** Health endpoint returns 200 OK with valid token

## 📞 Need Help?

If you encounter issues:
1. Check Cloudflare Access logs in dashboard
2. Verify DNS record is proxied (orange cloud)
3. Test with `cloudflared access login` command
4. Check Vercel deployment is still active

## 🎉 Next Steps After Success

1. Share `https://pediassist.skids.clinic` with your team
2. Add team members with @skids.clinic emails
3. Monitor Access logs for usage
4. Consider setting up additional security policies