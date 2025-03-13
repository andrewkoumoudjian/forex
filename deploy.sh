#!/bin/bash

PROJECT_ID="$(gcloud config get-value project)"
IMAGE_NAME="forex-simulator"
SERVICE_NAME="forex-simulator"
REGION="us-central1"

echo "Building and deploying $SERVICE_NAME to Google Cloud Run..."

# Build the container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated

echo "Deployment complete. Your service will be available at:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'