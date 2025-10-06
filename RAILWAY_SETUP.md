# Railway Deployment - Step by Step Guide

## 🚀 Quick Start (Web Interface)

### 1. Open Railway Dashboard
Go to: **https://railway.app/new**

### 2. Deploy from GitHub

Click **"Deploy from GitHub repo"**

- Select repository: `mahirkurt/medicines-patent-api`
- Railway will auto-detect: Node.js project
- Click **"Deploy Now"**

### 3. Wait for Build

Railway will automatically:
- ✅ Clone GitHub repository
- ✅ Run `npm install`
- ✅ Execute `npm start` (node server.js)
- ✅ Assign public URL

Build time: ~2-3 minutes

### 4. Generate Domain

Once deployed:
- Go to **Settings** → **Networking**
- Click **"Generate Domain"**
- Your URL: `https://[random-name].railway.app`

### 5. Test Deployment

```bash
# Replace with your Railway URL
export API_URL="https://your-app.railway.app"

# Health check
curl $API_URL/health

# Expected response:
{
  "status": "healthy",
  "dataSource": "cortellis",
  "counts": {
    "patents": 77767,
    "drugs": 13023,
    "relationships": 33650
  }
}
```

---

## 🔧 Using Railway CLI

### Install CLI

```bash
npm install -g @railway/cli
```

### Login

```bash
railway login
```

### Deploy Options

#### Option 1: Interactive Script
```bash
cd services/cortellis
bash deploy-railway.sh
```

#### Option 2: Manual Commands
```bash
# Create new project
railway init

# Deploy
railway up

# Generate domain
railway domain
```

---

## ⚠️ Important: Data Files

Large data files are **excluded** from git:
- `cortellis_patents.xlsx` (81 MB)
- `cortellis_drugs.xlsx` (21 MB)
- `processed_data/patents_processed.json` (133 MB)
- `processed_data/drugs_processed.json` (22 MB)

### Solution 1: Use Existing Processed Data

The repository includes smaller processed files that will work:
- ✅ `processed_data/relationships.json`
- ✅ `processed_data/patent_statistics.json`
- ✅ `processed_data/drug_statistics.json`
- ✅ `processed_data/master_index.json`

Server will load available data.

### Solution 2: Upload Via Railway Volumes

1. Go to Railway dashboard
2. Your service → **Data** → **Add Volume**
3. Mount path: `/app/processed_data`
4. Upload files via Railway CLI or dashboard

### Solution 3: Regenerate on Railway

Add to `package.json`:
```json
{
  "scripts": {
    "build": "python process_cortellis_data.py",
    "start": "node server.js"
  }
}
```

---

## 🔐 Environment Variables

No required environment variables for basic operation.

Optional:
```bash
# Set via Railway dashboard or CLI
railway variables set PORT=3005
railway variables set SERPAPI_KEY=your_key_here
```

---

## 📊 Monitor Deployment

### View Logs
```bash
railway logs
```

Or in dashboard: **Deployments** → **View Logs**

### Check Status
```bash
railway status
```

### Service Info
```bash
railway service
```

---

## 🧪 Testing

### Run Test Suite Locally
```bash
bash test-api.sh http://localhost:3005
```

### Test Production
```bash
bash test-api.sh https://your-app.railway.app
```

Expected: **17/17 tests pass ✅**

---

## 🔄 Auto-Deploy on Git Push

Once connected to GitHub:

```bash
git add .
git commit -m "Update API"
git push origin master
```

Railway will automatically:
1. Detect push
2. Build new version
3. Deploy if build succeeds
4. Switch traffic to new deployment

---

## 💰 Pricing Estimate

Railway Pricing:
- **Hobby Plan**: $5/month
- **Pro Plan**: $20/month

This API usage:
- **Estimated**: ~$3-5/month
- **Memory**: ~512MB-1GB
- **Build time**: 2-3 minutes
- **Always running**: Yes

---

## 🐛 Troubleshooting

### Build Fails

**Check logs:**
```bash
railway logs --deployment
```

**Common issues:**
- Node.js version mismatch → Add `engines` to package.json
- Missing dependencies → Check package.json
- Build timeout → Increase Railway plan

### API Returns Empty Results

**Cause**: Data files not uploaded

**Solution**:
1. Check health endpoint: `/health`
2. If counts are 0, upload data files
3. Or regenerate with Python scripts

### Memory Issues

**Increase memory:**
- Dashboard → Settings → Resources
- Set to 1GB or 2GB

### Connection Timeout

**Check**:
- Service is running: `railway status`
- Logs for errors: `railway logs`
- Health endpoint: `curl $API_URL/health`

---

## 📝 Deployment Checklist

- [ ] GitHub repo pushed
- [ ] Railway account created
- [ ] Project created from GitHub
- [ ] Build completed successfully
- [ ] Domain generated
- [ ] Health endpoint returns 200
- [ ] Statistics show data counts
- [ ] Test searches return results
- [ ] Web interface loads
- [ ] Auto-deploy enabled

---

## 🎉 Success!

Your Patent Database API is now live!

**Next Steps:**
1. Share your Railway URL
2. Update API documentation with production URL
3. Monitor usage in Railway dashboard
4. Set up custom domain (optional)

**API Documentation**: `https://your-app.railway.app/`

**Web Interface**: Open URL in browser

---

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **GitHub Repo**: https://github.com/mahirkurt/medicines-patent-api
- **Railway Community**: https://discord.gg/railway

