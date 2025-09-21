# Google Cloud Setup for Legal Cat

This document provides step-by-step instructions for setting up Google Cloud services required by the Legal Cat application.

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed
- Project with Vertex AI API enabled

## 1. Create a Google Cloud Project

```bash
# Create a new project (or use an existing one)
gcloud projects create your-project-id --name="Legal Cat"

# Set the project as your default
gcloud config set project your-project-id
```

## 2. Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable other required services
gcloud services enable storage.googleapis.com
gcloud services enable compute.googleapis.com
```

## 3. Create a Service Account

```bash
# Create service account
gcloud iam service-accounts create legal-cat-service \
    --description="Service account for Legal Cat application" \
    --display-name="Legal Cat Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-cat-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-cat-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download service account key
gcloud iam service-accounts keys create ~/legal-cat-service-account.json \
    --iam-account=legal-cat-service@your-project-id.iam.gserviceaccount.com
```

## 4. Set Up Environment Variables

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```bash
# Required Google Cloud settings
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/legal-cat-service-account.json

# Optional: Legacy Google AI API key (for fallback)
GOOGLE_API_KEY=your-google-ai-api-key
```

## 5. Test Authentication

```bash
# Test authentication
gcloud auth application-default print-access-token

# Test Vertex AI access
gcloud ai models list --region=us-central1
```

## 6. Development Setup

```bash
# Install dependencies
uv sync

# Run the application
uv run uvicorn app.main:app --reload
```

## 7. Alternative Authentication Methods

### Using Application Default Credentials (ADC)

For development, you can use gcloud authentication:
```bash
gcloud auth application-default login
```

### Using Workload Identity (for GKE)

If deploying to Google Kubernetes Engine:
```bash
# Create Kubernetes service account
kubectl create serviceaccount legal-cat-ksa

# Bind to Google service account
gcloud iam service-accounts add-iam-policy-binding \
    legal-cat-service@your-project-id.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:your-project-id.svc.id.goog[default/legal-cat-ksa]"

# Annotate Kubernetes service account
kubectl annotate serviceaccount legal-cat-ksa \
    iam.gke.io/gcp-service-account=legal-cat-service@your-project-id.iam.gserviceaccount.com
```

## 8. Environment-Specific Configurations

### Development
- Use service account key file
- Enable debug logging
- Use local ChromaDB storage

### Staging
- Use Workload Identity or ADC
- Moderate logging
- Use Cloud Storage for document storage

### Production
- Use Workload Identity
- Minimal logging
- Use Cloud Storage with proper IAM
- Enable monitoring and alerting

## 9. Security Best Practices

1. **Principle of Least Privilege**: Only grant necessary IAM roles
2. **Key Rotation**: Regularly rotate service account keys
3. **Environment Separation**: Use different projects for dev/staging/prod
4. **Secret Management**: Use Google Secret Manager for sensitive values
5. **Audit Logging**: Enable Cloud Audit Logs

## 10. Troubleshooting

### Common Issues

**Authentication Errors**:
```bash
# Check current authentication
gcloud auth list

# Re-authenticate if needed
gcloud auth application-default login
```

**API Not Enabled**:
```bash
# List enabled APIs
gcloud services list --enabled

# Enable missing APIs
gcloud services enable aiplatform.googleapis.com
```

**Permission Denied**:
```bash
# Check IAM bindings
gcloud projects get-iam-policy your-project-id

# Verify service account permissions
gcloud iam service-accounts get-iam-policy \
    legal-cat-service@your-project-id.iam.gserviceaccount.com
```

### Logging and Monitoring

Enable Cloud Logging for the application:
```python
import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()
```

## 11. Cost Optimization

- Use appropriate machine types for Vertex AI
- Enable auto-scaling for workloads
- Monitor API usage and set quotas
- Use preemptible instances where possible
- Implement request caching

## 12. Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)
- [IAM Best Practices](https://cloud.google.com/iam/docs/using-iam-securely)
- [Cost Optimization Guide](https://cloud.google.com/vertex-ai/docs/general/pricing)