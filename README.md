# Patent Database API

Comprehensive patent and drug intelligence system integrating Cortellis and Google Patents data.

## Features

- **77,767 Patents** - Comprehensive pharmaceutical patent database
- **13,023 Drugs** - Detailed drug pipeline information
- **33,650 Relationships** - Drug-patent connections
- **RESTful API** - Full-featured REST endpoints
- **Analysis Tools** - Patent landscape, competitive analysis, expiry timelines
- **Web Interface** - Interactive search and exploration

## API Endpoints

### Patents
- `GET /api/patents/search` - Search patents
- `GET /api/patents/:id` - Patent details
- `GET /api/patents/drug/:drugName` - Patents by drug
- `GET /api/patents/company/:company` - Patents by company

### Drugs
- `GET /api/drugs/search` - Search drugs
- `GET /api/drugs/:id` - Drug details
- `GET /api/drugs/indication/:indication` - Drugs by indication
- `GET /api/drugs/phase/:phase` - Drugs by development phase

### Analysis
- `GET /api/analysis/patent-landscape` - Patent landscape analysis
- `GET /api/analysis/drug-pipeline` - Drug pipeline analysis
- `GET /api/analysis/competitive/:company` - Competitive analysis
- `GET /api/analysis/expiry-timeline` - Patent expiry timeline

## Deployment

### Railway (Recommended)

**Deploy from GitHub:**
1. Go to [Railway](https://railway.app)
2. Create new project from GitHub repo: `mahirkurt/medicines-patent-api`
3. Railway will auto-detect Node.js and deploy
4. Service will be available at Railway-provided URL

**Important Notes:**
- Large data files (*.xlsx, processed_data/patents_processed.json) are excluded from git
- Upload these files manually to Railway or regenerate using Python scripts
- Server runs on port 3005 (Railway will auto-assign PORT env variable)

### Local Development

```bash
# Install dependencies
npm install

# Start server
npm start
```

Server runs on http://localhost:3005

### Test the API

```bash
# Health check
curl http://localhost:3005/health

# Search patents
curl "http://localhost:3005/api/patents/search?q=cancer&limit=5"

# Search drugs
curl "http://localhost:3005/api/drugs/search?q=aspirin"
```

## Data Sources

- **Cortellis** - Patent and drug data
- **Google Patents** - Additional patent information via SerpAPI

## License

MIT