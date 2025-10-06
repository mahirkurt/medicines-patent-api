#!/bin/bash

# Railway Deployment Script for Patent Database API
# This script guides you through deploying to Railway

echo "========================================"
echo "Railway Deployment Guide"
echo "Patent Database API"
echo "========================================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo ""
    echo "Install Railway CLI:"
    echo "  npm install -g @railway/cli"
    echo ""
    echo "Or use Homebrew (macOS/Linux):"
    echo "  brew install railway"
    echo ""
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Check if logged in
echo "Checking Railway authentication..."
if railway whoami &> /dev/null; then
    RAILWAY_USER=$(railway whoami 2>&1 | grep "Logged in as" | cut -d' ' -f4-)
    echo "✅ Logged in as: $RAILWAY_USER"
else
    echo "❌ Not logged in to Railway"
    echo ""
    echo "Please login first:"
    echo "  railway login"
    echo ""
    exit 1
fi

echo ""
echo "========================================"
echo "Deployment Options"
echo "========================================"
echo ""
echo "Choose deployment method:"
echo ""
echo "1. Deploy from GitHub (Recommended)"
echo "   - Automatic deployments on git push"
echo "   - Easy rollbacks"
echo "   - Best for production"
echo ""
echo "2. Deploy from local files"
echo "   - Direct upload from this directory"
echo "   - Good for testing"
echo "   - Manual deployments only"
echo ""
echo "3. Manual setup instructions"
echo "   - Step-by-step guide"
echo "   - For custom configurations"
echo ""

read -p "Enter choice (1/2/3): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "========================================"
        echo "GitHub Deployment"
        echo "========================================"
        echo ""
        echo "📋 Steps to deploy from GitHub:"
        echo ""
        echo "1. Go to https://railway.app/new"
        echo ""
        echo "2. Click 'Deploy from GitHub repo'"
        echo ""
        echo "3. Select repository: mahirkurt/medicines-patent-api"
        echo ""
        echo "4. Railway will automatically:"
        echo "   - Detect Node.js project"
        echo "   - Install dependencies (npm install)"
        echo "   - Start server (npm start)"
        echo "   - Assign a public URL"
        echo ""
        echo "5. Important: Data files"
        echo "   Large files are excluded from git."
        echo "   After deployment, either:"
        echo "   a) Upload via Railway dashboard"
        echo "   b) Use Railway volumes"
        echo "   c) Regenerate with Python scripts"
        echo ""
        echo "6. Get your URL:"
        echo "   Settings -> Domains -> Generate Domain"
        echo ""
        echo "✅ That's it! Your API will be live."
        echo ""
        echo "Press Enter to open Railway dashboard..."
        read

        # Try to open Railway in browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "https://railway.app/new" &
        elif command -v open &> /dev/null; then
            open "https://railway.app/new" &
        elif command -v start &> /dev/null; then
            start "https://railway.app/new" &
        else
            echo "Open this URL in your browser:"
            echo "https://railway.app/new"
        fi
        ;;

    2)
        echo ""
        echo "========================================"
        echo "Local File Deployment"
        echo "========================================"
        echo ""
        echo "⚠️  Warning: This will deploy from local files"
        echo "   Not recommended for production use"
        echo ""
        read -p "Continue? (y/n): " CONFIRM

        if [ "$CONFIRM" != "y" ]; then
            echo "Deployment cancelled"
            exit 0
        fi

        echo ""
        echo "Initializing Railway project..."

        # Try to initialize
        railway init

        echo ""
        echo "Deploying to Railway..."
        railway up

        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "Get your URL:"
        railway domain
        ;;

    3)
        echo ""
        echo "========================================"
        echo "Manual Setup Instructions"
        echo "========================================"
        echo ""
        echo "Step 1: Create Railway Project"
        echo "-------------------------------"
        echo "  railway init"
        echo "  (Select workspace and create new project)"
        echo ""
        echo "Step 2: Link GitHub Repository (Optional)"
        echo "-----------------------------------------"
        echo "  Go to Railway dashboard"
        echo "  Settings -> Connect to GitHub"
        echo "  Select: mahirkurt/medicines-patent-api"
        echo ""
        echo "Step 3: Configure Environment"
        echo "------------------------------"
        echo "  railway variables set PORT=3005"
        echo "  (Optional: Add other env vars)"
        echo ""
        echo "Step 4: Deploy"
        echo "--------------"
        echo "  Option A (from GitHub):"
        echo "    Automatic on git push"
        echo ""
        echo "  Option B (from local):"
        echo "    railway up"
        echo ""
        echo "Step 5: Add Domain"
        echo "------------------"
        echo "  railway domain"
        echo "  Or go to Settings -> Domains in dashboard"
        echo ""
        echo "Step 6: Upload Data Files"
        echo "-------------------------"
        echo "  Use Railway dashboard or volumes"
        echo "  Upload to: /app/processed_data/"
        echo "  Required files:"
        echo "    - patents_processed.json"
        echo "    - drugs_processed.json"
        echo "    - relationships.json"
        echo ""
        echo "Step 7: Test Deployment"
        echo "-----------------------"
        echo "  curl https://your-app.railway.app/health"
        echo ""
        ;;

    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Quick Test Commands"
echo "========================================"
echo ""
echo "After deployment, test your API:"
echo ""
echo "# Get your Railway URL"
echo "export API_URL=\$(railway domain | grep https)"
echo ""
echo "# Health check"
echo "curl \$API_URL/health"
echo ""
echo "# Statistics"
echo "curl \$API_URL/api/statistics"
echo ""
echo "# Search"
echo "curl \"\$API_URL/api/patents/search?q=cancer&limit=5\""
echo ""
echo "========================================"
echo ""
echo "📚 Documentation:"
echo "   - README.md"
echo "   - DEPLOYMENT.md"
echo "   - GitHub: https://github.com/mahirkurt/medicines-patent-api"
echo ""
echo "🎉 Happy deploying!"
echo ""