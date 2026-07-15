#!/bin/bash

# RAG Architecture - Cloud Run Deployment Script
# Cloud Run is cheaper than App Engine for low-traffic apps

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="rag-architecture-app"
MEMORY="2Gi"
CPU="1"
MIN_INSTANCES="0"
MAX_INSTANCES="3"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}RAG Architecture - Cloud Run Deployment${NC}"
echo -e "${GREEN}(Lower cost alternative to App Engine)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not installed${NC}"
    exit 1
fi

# Get project ID
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: No GCP project set${NC}"
        echo "Run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

echo -e "${GREEN}Project:${NC} $PROJECT_ID"
echo -e "${GREEN}Region:${NC} $REGION"
echo -e "${GREEN}Service:${NC} $SERVICE_NAME"
echo -e "${GREEN}Memory:${NC} $MEMORY"
echo -e "${GREEN}CPU:${NC} $CPU"
echo ""

read -p "$(echo -e ${YELLOW}Deploy to Cloud Run? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}Step 1: Enabling APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    --project=$PROJECT_ID

echo ""
echo -e "${GREEN}Step 2: Building container...${NC}"
gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --project=$PROJECT_ID

echo ""
echo -e "${GREEN}Step 3: Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory $MEMORY \
    --cpu $CPU \
    --min-instances $MIN_INSTANCES \
    --max-instances $MAX_INSTANCES \
    --port 8080 \
    --project=$PROJECT_ID

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --project=$PROJECT_ID \
    --format 'value(status.url)')

echo -e "${GREEN}Your app is live at:${NC}"
echo "$SERVICE_URL"
echo ""

echo -e "${GREEN}Cost Estimate:${NC}"
echo "  • First 2M requests/month: FREE"
echo "  • Instance time: \$0.00001800/sec (\$1.30/hour)"
echo "  • With min_instances=0: Only pay when used!"
echo ""

echo -e "${GREEN}Useful commands:${NC}"
echo "  View logs:    gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo "  Update:       ./deploy-cloudrun.sh"
echo "  Delete:       gcloud run services delete $SERVICE_NAME --region=$REGION"
echo ""
