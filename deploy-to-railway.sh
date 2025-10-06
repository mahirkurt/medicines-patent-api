#!/bin/bash

# Automated Railway Deployment Script
# Patent Database API

set -e  # Exit on error

echo "=========================================="
echo "🚀 Railway Deployment Automation"
echo "Patent Database API"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI not found${NC}"
    echo ""
    echo "Install Railway CLI:"
    echo "  npm install -g @railway/cli"
    echo ""
    exit 1
fi

if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Railway${NC}"
    echo ""
    echo "Login to Railway:"
    echo "  railway login"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Display deployment info
echo "=========================================="
echo "📊 Deployment Information"
echo "=========================================="
echo ""
echo "Repository: mahirkurt/medicines-patent-api"
echo "Branch: master"
echo "Service: Patent Database API"
echo ""

# Get current status
RAILWAY_USER=$(railway whoami 2>&1 | grep "Logged in as" | cut -d' ' -f4- || echo "Unknown")
echo "Railway User: $RAILWAY_USER"
echo ""

# Deployment options
echo "=========================================="
echo "🎯 Deployment Method"
echo "=========================================="
echo ""
echo "This will deploy the Patent Database API to Railway"
echo "using the GitHub repository."
echo ""

read -p "Continue with deployment? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "=========================================="
echo "🔧 Deployment Steps"
echo "=========================================="
echo ""

# Step 1: Open Railway dashboard for GitHub deployment
echo -e "${BLUE}Step 1: Opening Railway Dashboard${NC}"
echo "Please follow these steps in your browser:"
echo ""
echo "1. Click 'New Project'"
echo "2. Select 'Deploy from GitHub repo'"
echo "3. Choose: mahirkurt/medicines-patent-api"
echo "4. Wait for build to complete"
echo "5. Generate domain in Settings → Networking"
echo ""

# Try to open browser
if command -v xdg-open &> /dev/null; then
    xdg-open "https://railway.app/new" &
elif command -v open &> /dev/null; then
    open "https://railway.app/new" &
elif command -v start &> /dev/null; then
    start "https://railway.app/new" &
else
    echo "Open this URL: https://railway.app/new"
fi

echo ""
read -p "Press Enter when deployment is complete..."

echo ""
echo -e "${BLUE}Step 2: Testing Deployment${NC}"
echo ""

read -p "Enter your Railway URL (e.g., https://your-app.railway.app): " RAILWAY_URL

if [ -z "$RAILWAY_URL" ]; then
    echo -e "${YELLOW}No URL provided. Skipping tests.${NC}"
else
    echo ""
    echo "Testing $RAILWAY_URL..."
    echo ""

    # Test health endpoint
    echo -n "Health check... "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/health")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "${GREEN}✓ PASS${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP $HTTP_CODE${NC}"
    fi

    # Test statistics
    echo -n "Statistics... "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/api/statistics")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "${GREEN}✓ PASS${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP $HTTP_CODE${NC}"
    fi

    # Test search
    echo -n "Patent search... "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/api/patents/search?q=cancer&limit=5")

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "${GREEN}✓ PASS${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP $HTTP_CODE${NC}"
    fi

    echo ""
    echo -e "${GREEN}Basic tests complete!${NC}"
    echo ""
    echo "Run full test suite:"
    echo "  bash test-api.sh $RAILWAY_URL"
fi

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""

if [ -n "$RAILWAY_URL" ]; then
    echo "🌐 API URL: $RAILWAY_URL"
    echo ""
    echo "Quick links:"
    echo "  API Docs:    $RAILWAY_URL/"
    echo "  Health:      $RAILWAY_URL/health"
    echo "  Statistics:  $RAILWAY_URL/api/statistics"
    echo "  Web UI:      Open $RAILWAY_URL in browser"
fi

echo ""
echo "📚 Documentation:"
echo "  - README.md"
echo "  - DEPLOYMENT.md"
echo "  - RAILWAY_SETUP.md"
echo "  - DEPLOYMENT_SUMMARY.md"
echo ""
echo "🎉 Your Patent Database API is live!"
echo ""