#!/bin/bash
# GCP Cloud Storage Bucket Setup Script
# Creates and configures the QEW camera images bucket

set -e

BUCKET_NAME="qew-camera-images"
PROJECT_ID="${1:-YOUR_PROJECT_ID}"  # Pass project ID as argument
REGION="us-central1"

echo "=========================================="
echo "GCP Storage Bucket Setup for QEW Cameras"
echo "=========================================="
echo ""
echo "Bucket: gs://${BUCKET_NAME}"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found"
    echo "Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if gsutil is installed
if ! command -v gsutil &> /dev/null; then
    echo "❌ Error: gsutil not found"
    echo "Please install Google Cloud SDK"
    exit 1
fi

# Authenticate if needed
echo "Step 1: Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "Please authenticate with your Google Cloud account:"
    gcloud auth login
fi

# Set project
echo ""
echo "Step 2: Setting project..."
if [ "$PROJECT_ID" == "YOUR_PROJECT_ID" ]; then
    echo "❌ Error: Please provide your GCP project ID"
    echo "Usage: ./setup-gcp-bucket.sh YOUR_PROJECT_ID"
    exit 1
fi

gcloud config set project "${PROJECT_ID}"

# Create bucket
echo ""
echo "Step 3: Creating storage bucket..."
if gsutil ls -b "gs://${BUCKET_NAME}" &> /dev/null; then
    echo "✅ Bucket already exists: gs://${BUCKET_NAME}"
else
    gsutil mb -p "${PROJECT_ID}" -c STANDARD -l "${REGION}" "gs://${BUCKET_NAME}/"
    echo "✅ Created bucket: gs://${BUCKET_NAME}"
fi

# Create CORS configuration
echo ""
echo "Step 4: Configuring CORS for browser uploads..."
cat > /tmp/cors-config.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE", "HEAD"],
    "responseHeader": ["Content-Type", "Content-Length", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set /tmp/cors-config.json "gs://${BUCKET_NAME}"
rm /tmp/cors-config.json
echo "✅ CORS configured"

# Set bucket to public read (for viewing uploaded images)
echo ""
echo "Step 5: Setting bucket permissions (public read)..."
gsutil iam ch allUsers:objectViewer "gs://${BUCKET_NAME}"
echo "✅ Public read access enabled"

# Create directory structure
echo ""
echo "Step 6: Creating directory structure..."
echo "Creating placeholder for collections/"
echo "placeholder" | gsutil cp - "gs://${BUCKET_NAME}/collections/.gitkeep"
echo "Creating placeholder for metadata/"
echo "placeholder" | gsutil cp - "gs://${BUCKET_NAME}/metadata/.gitkeep"
echo "✅ Directory structure created"

# Display bucket info
echo ""
echo "=========================================="
echo "✅ GCP Storage Bucket Setup Complete!"
echo "=========================================="
echo ""
echo "Bucket URL: gs://${BUCKET_NAME}"
echo "Public URL: https://storage.googleapis.com/${BUCKET_NAME}"
echo "Region: ${REGION}"
echo ""
echo "Next Steps:"
echo "1. Update .env file:"
echo "   VITE_GCP_STORAGE_BUCKET=${BUCKET_NAME}"
echo "   VITE_GCP_PROJECT_ID=${PROJECT_ID}"
echo "   VITE_GEMINI_API_KEY=<your-api-key>"
echo ""
echo "2. Uncomment VITE_GEMINI_API_KEY in .env to enable GCP upload"
echo ""
echo "3. Run 'npm run dev' and click 'START COLLECTION'"
echo ""
echo "To verify bucket:"
echo "  gsutil ls -r gs://${BUCKET_NAME}"
echo ""
