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

### Railway

1. Connect GitHub repository
2. Set environment variables (if needed)
3. Deploy automatically

### Local

```bash
npm install
npm start
```

Server runs on port 3005.

## Data Sources

- **Cortellis** - Patent and drug data
- **Google Patents** - Additional patent information via SerpAPI

## License

MIT