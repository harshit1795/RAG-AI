#!/bin/bash

# RAG Architecture Streamlit App - GCP Deployment Script
# This script deploys the application to Google Cloud Platform

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="rag-architecture-app"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}RAG Architecture - GCP Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if project ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}GCP_PROJECT_ID not set. Attempting to get current project...${NC}"
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: No GCP project selected${NC}"
        echo "Please set GCP_PROJECT_ID environment variable or run:"
        echo "  gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

echo -e "${GREEN}Project ID:${NC} $PROJECT_ID"
echo -e "${GREEN}Region:${NC} $REGION"
echo -e "${GREEN}Service Name:${NC} $SERVICE_NAME"
echo ""

# Confirm deployment
read -p "$(echo -e ${YELLOW}Do you want to proceed with deployment? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}Step 1: Enabling required APIs...${NC}"
gcloud services enable \
    appengine.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    --project=$PROJECT_ID

echo ""
echo -e "${GREEN}Step 2: Building Docker image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME --project=$PROJECT_ID

echo ""
echo -e "${GREEN}Step 3: Deploying to App Engine...${NC}"
gcloud app deploy app.yaml \
    --project=$PROJECT_ID \
    --quiet

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Your application is now live at:${NC}"
gcloud app browse --project=$PROJECT_ID --no-launch-browser

echo ""
echo -e "${YELLOW}Note: The first deployment may take 10-15 minutes.${NC}"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo "  View logs:    gcloud app logs tail -s default"
echo "  Open in browser: gcloud app browse"
echo "  Stop app:     gcloud app versions stop [VERSION]"
echo ""
