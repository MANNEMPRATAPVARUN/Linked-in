# 🚀 JobSprint CI/CD Setup Guide

This guide will help you set up automated deployments for JobSprint across all three platforms: Railway (backend), Vercel (frontend), and Supabase (database).

## 📋 Prerequisites

1. **GitHub Repository** with your JobSprint code
2. **Railway Account** with your API deployed
3. **Vercel Account** with your frontend deployed  
4. **Supabase Account** with your database set up

## 🔑 Step 1: GitHub Secrets Setup

Add these secrets to your GitHub repository:

### Go to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

#### Railway Secrets:
```
RAILWAY_TOKEN=your_railway_token_here
RAILWAY_PROJECT_ID=your_project_id_here  
RAILWAY_SERVICE_ID=your_service_id_here
```

#### Vercel Secrets:
```
VERCEL_TOKEN=your_vercel_token_here
VERCEL_ORG_ID=your_org_id_here
VERCEL_PROJECT_ID=your_project_id_here
```

#### Supabase Secrets:
```
SUPABASE_ACCESS_TOKEN=your_supabase_token_here
SUPABASE_PROJECT_REF=your_project_ref_here
```

## 🔍 How to Get These Values

### Railway Tokens:
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click your profile → `Account Settings` → `Tokens`
3. Create new token → Copy `RAILWAY_TOKEN`
4. Go to your project → Settings → Copy `Project ID` and `Service ID`

### Vercel Tokens:
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Settings → Tokens → Create new token → Copy `VERCEL_TOKEN`
3. Go to your project → Settings → General → Copy `Project ID`
4. Account Settings → Copy `Team ID` (this is your `ORG_ID`)

### Supabase Tokens:
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Account → Access Tokens → Create new token → Copy `SUPABASE_ACCESS_TOKEN`
3. Your project → Settings → General → Reference ID → Copy `SUPABASE_PROJECT_REF`

## 🚀 Step 2: Enable GitHub Actions

1. **Push the workflow file** (already created in `.github/workflows/deploy.yml`)
2. **Go to your GitHub repo** → `Actions` tab
3. **Enable workflows** if prompted
4. **Push to main branch** to trigger first deployment

## 🛠️ Step 3: Manual Deployment Script

For local deployments, use the sync script:

```bash
# Make script executable
chmod +x deploy_sync.py

# Run deployment sync
python deploy_sync.py

# Force deploy all services
python deploy_sync.py --force
```

### Prerequisites for Manual Script:
```bash
# Install Vercel CLI
npm install -g vercel

# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login to services
vercel login
railway login
```

## 🔄 How It Works

### Automatic Triggers:
- **Push to main branch** → Deploys all services
- **Pull request** → Runs tests only
- **Manual trigger** → Deploy with force option

### Health Checks:
- ✅ **Frontend**: https://jobsprint-frontend.vercel.app/health
- ✅ **Backend**: https://web-production-f50b3.up.railway.app/health
- ✅ **Integration tests** verify all endpoints work

### Deployment Flow:
1. **Health Check** → Check current service status
2. **Deploy Backend** → Railway deployment
3. **Deploy Frontend** → Vercel deployment  
4. **Migrate Database** → Supabase schema updates
5. **Integration Tests** → Verify everything works
6. **Summary Report** → GitHub Actions summary

## 📊 Monitoring

### GitHub Actions Dashboard:
- Go to your repo → `Actions` tab
- View deployment status and logs
- See detailed summary reports

### Service URLs:
- 🏠 **Main App**: https://jobsprint-frontend.vercel.app
- 🔐 **Admin Login**: admin@jobsprint.com / admin123
- 📊 **API Health**: https://web-production-f50b3.up.railway.app/health

## 🐛 Troubleshooting

### Common Issues:

#### 1. Railway Deployment Fails:
```bash
# Check Railway status
railway status

# View logs
railway logs

# Redeploy manually
railway up
```

#### 2. Vercel Deployment Fails:
```bash
# Check Vercel status
vercel ls

# View logs
vercel logs

# Redeploy manually
cd frontend && vercel --prod
```

#### 3. GitHub Actions Fails:
- Check the `Actions` tab for detailed error logs
- Verify all secrets are set correctly
- Check service quotas and limits

### Manual Sync:
If automated deployment fails, run manual sync:
```bash
python deploy_sync.py --force
```

## 🎯 Next Steps

1. **Test the setup** by pushing a small change to main branch
2. **Monitor the Actions tab** to see deployment progress
3. **Verify all services** are working after deployment
4. **Set up notifications** (optional) for deployment failures

## 🔔 Optional: Slack/Discord Notifications

Add webhook URLs to GitHub secrets for deployment notifications:
```
SLACK_WEBHOOK_URL=your_slack_webhook
DISCORD_WEBHOOK_URL=your_discord_webhook
```

---

## 🎉 Success!

Once set up, every push to main will automatically:
- ✅ Deploy your backend to Railway
- ✅ Deploy your frontend to Vercel  
- ✅ Update your database schema
- ✅ Run integration tests
- ✅ Provide detailed deployment reports

**Your JobSprint system will always be in sync across all platforms!** 🚀
