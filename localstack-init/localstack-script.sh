#!/bin/bash

# Wait for LocalStack to be ready
sleep 10

# Create the S3 bucket
awslocal s3 mb s3://my-bucket

echo "Created S3 bucket: my-bucket"