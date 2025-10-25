#!/bin/bash

# LocalStack S3 bucket initialization script
# Based on chainlit-datalayer submodule: localstack-script.sh

echo "Initializing LocalStack S3 buckets..."

# Create the main bucket for Chainlit data storage
awslocal s3api \
    create-bucket --bucket my-bucket \
    --create-bucket-configuration LocationConstraint=eu-central-1 \
    --region eu-central-1

echo "Created bucket: my-bucket"

# Configure CORS for proper file handling
echo '{"CORSRules":[{"AllowedHeaders":["*"],"AllowedMethods":["GET","POST","PUT"],"AllowedOrigins":["*"],"ExposeHeaders":["ETag"]}]}' > /tmp/cors.json
awslocal s3api put-bucket-cors --bucket my-bucket --cors-configuration file:///tmp/cors.json

echo "Configured CORS for bucket: my-bucket"

# Verify bucket creation
awslocal s3 ls

echo "LocalStack S3 initialization complete!"