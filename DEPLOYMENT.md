# Patent Database API - Deployment Guide

## 🚀 Quick Deploy to Railway

### Method 1: Railway Web Interface (Recommended)

1. **Login to Railway**
   - Go to https://railway.app
   - Login with GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `mahirkurt/medicines-patent-api`

3. **Configure Service**
   - Railway auto-detects Node.js
   - Build command: `npm install`
   - Start command: `node server.js` (from package.json)
   - Port: 3005 (auto-assigned by Railway)

4. **Deploy**
   - Railway will automatically build and deploy
   - You'll get a public URL like: `https://your-app.railway.app`

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to project directory
cd services/cortellis

# Link to Railway project
railway link

# Deploy
railway up
```

## 📦 Important: Data Files

Large data files are excluded from Git:
- `cortellis_patents.xlsx` (81 MB)
- `cortellis_drugs.xlsx`
- `processed_data/patents_processed.json` (133 MB)
- `processed_data/drugs_processed.json`

### Option 1: Upload to Railway (Manual)

1. After deployment, use Railway dashboard
2. Go to your service → Variables
3. Add persistent volume or use Railway's file upload feature
4. Upload the processed JSON files to `/app/processed_data/`

### Option 2: Regenerate Data on Railway

Add build command in Railway:
```bash
python process_cortellis_data.py && npm start
```

**Note:** This requires uploading source Excel files first.

## 🔧 Environment Variables

Railway auto-assigns `PORT` variable. No additional env vars needed for basic operation.

Optional:
- `SERPAPI_KEY` - For Google Patents integration (if using)

## 📊 Testing Deployed API

Once deployed, test your Railway URL:

```bash
# Replace YOUR_RAILWAY_URL with your actual URL
export API_URL="https://your-app.railway.app"

# Health check
curl $API_URL/health

# Get statistics
curl $API_URL/api/statistics

# Search patents
curl "$API_URL/api/patents/search?q=cancer&limit=5"

# Search drugs
curl "$API_URL/api/drugs/search?q=remdesivir"

# Analysis
curl "$API_URL/api/analysis/drug-pipeline"
```

## 🌐 Web Interface

After deployment, access the web interface at:
```
https://your-app.railway.app/
```

Open `index.html` in browser or serve it via the Node.js server.

## 📈 Performance Optimization

### For Railway Deployment:

1. **Memory**: Increase if needed (default: 512MB)
   - Go to Settings → Resources
   - Recommended: 1GB for large dataset

2. **Enable Caching**
   - Data is cached in memory for 5 minutes
   - No additional configuration needed

3. **Persistent Storage** (Optional)
   - Add Railway volume for data persistence
   - Mount at `/app/processed_data`

## 🔄 Updating Deployment

### Auto-deploy on Git Push:
```bash
git add .
git commit -m "Update API"
git push origin master
```

Railway will automatically rebuild and deploy.

### Manual Redeploy:
- Go to Railway dashboard
- Click "Deploy" → "Redeploy"

## 🐛 Troubleshooting

### Build Fails
- Check Railway build logs
- Ensure `package.json` has correct dependencies
- Verify Node.js version (18+ required)

### Data Not Loading
- Check if processed_data files exist
- Verify file paths in server.js
- Check Railway logs for file access errors

### API Returns Empty Results
- Data files might not be uploaded
- Check `/health` endpoint for data counts
- Upload processed JSON files manually

### Memory Issues
- Increase Railway service memory
- Consider implementing pagination
- Enable response compression

## 📚 API Documentation

Full API documentation available at root endpoint:
```
GET https://your-app.railway.app/
```

## 🔐 Security Considerations

1. **Rate Limiting**: Built-in (100 requests per 15 min)
2. **CORS**: Enabled for all origins (configure in production)
3. **Input Validation**: Basic query sanitization implemented

## 💰 Railway Pricing

- **Free Tier**: $5 credit/month
- **Hobby Plan**: $5/month for larger apps
- **Pro Plan**: $20/month for production

Estimated usage: ~$3-5/month for this API

## 📞 Support

- GitHub Repo: https://github.com/mahirkurt/medicines-patent-api
- Railway Docs: https://docs.railway.app
- Issues: Create issue on GitHub repo

---

## ✅ Deployment Checklist

- [ ] GitHub repo created and pushed
- [ ] Railway project created
- [ ] Data files uploaded or regenerated
- [ ] Environment variables configured (if needed)
- [ ] Deployment successful
- [ ] Health endpoint returns 200
- [ ] Statistics endpoint shows data counts
- [ ] Test searches return results
- [ ] Web interface accessible
- [ ] Custom domain configured (optional)

---

**Deployed Successfully?**

Share your Railway URL and start using the Patent Database API! 🎉