# 🔑 GitHub Secrets Setup - JobSprint CI/CD

## 📋 **STEP-BY-STEP INSTRUCTIONS**

### **1. Go to Your GitHub Repository**
- Navigate to: https://github.com/MANNEMPRATAPVARUN/Linked-in
- Click: **Settings** tab (top right)
- Click: **Secrets and variables** → **Actions** (left sidebar)
- Click: **New repository secret** button

### **2. Add These Secrets One by One**

Copy each secret name and value exactly as shown below:

---

#### 🚂 **Railway Secrets**

**Secret Name:** `RAILWAY_TOKEN`  
**Value:** `eee37699-236b-4ab3-a0e2-5cd52b6ae206`

**Secret Name:** `RAILWAY_PROJECT_ID`  
**Value:** `865b69d0-7919-465a-b316-5b00610cc752`

**Secret Name:** `RAILWAY_SERVICE_ID`  
**Value:** `b39256fa-8795-445c-a08d-ba30ea024666`

---

#### 🌐 **Vercel Secrets**

**Secret Name:** `VERCEL_TOKEN`  
**Value:** `JbUY8K2oYHEYm7fYG2gaailI`

**Secret Name:** `VERCEL_PROJECT_ID`  
**Value:** `prj_lsXxzDtgFIWZw9bW95hy20iFyzKh`

**Secret Name:** `VERCEL_ORG_ID`  
**Value:** `team_DX65vHOZhToSaUYSOBuKTmf0`

---

#### 🗄️ **Supabase Secrets**

**Secret Name:** `SUPABASE_ACCESS_TOKEN`  
**Value:** `sbp_4ccf67d1b68f9566260a5ce2bf312e22148a30b4`

**Secret Name:** `SUPABASE_PROJECT_REF`  
**Value:** `eazuowqlkqijpmcimkcz`

---

## ✅ **Verification Checklist**

After adding all secrets, you should have **8 secrets total**:

- [ ] RAILWAY_TOKEN
- [ ] RAILWAY_PROJECT_ID  
- [ ] RAILWAY_SERVICE_ID
- [ ] VERCEL_TOKEN
- [ ] VERCEL_PROJECT_ID
- [ ] VERCEL_ORG_ID
- [ ] SUPABASE_ACCESS_TOKEN
- [ ] SUPABASE_PROJECT_REF

## 🚀 **Next Steps**

1. **Add all 8 secrets** to GitHub (takes 5 minutes)
2. **Push any change** to main branch to trigger first deployment
3. **Monitor** the Actions tab for deployment progress
4. **Test** your app at https://jobsprint-frontend.vercel.app

## 🎯 **Test Deployment**

After adding secrets, create a test commit:

```bash
git add .
git commit -m "🚀 Activate CI/CD - Full deployment sync"
git push origin main
```

Then watch the magic happen in your GitHub Actions tab! 🎉

---

## 🔒 **Security Note**
These secrets are safely stored in GitHub and never exposed in your code. The CI/CD system will use them automatically for deployments.

## 🆘 **Need Help?**
If any deployment fails, check the Actions tab for detailed logs and error messages.
