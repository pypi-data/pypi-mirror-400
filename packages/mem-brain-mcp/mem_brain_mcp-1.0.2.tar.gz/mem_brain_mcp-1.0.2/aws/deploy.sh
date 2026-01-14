#!/bin/bash

# Deployment script for Mem-Brain MCP Server to AWS ECS
# Usage: ./deploy.sh [REGION] [ECR_REPO_NAME] [CLUSTER_NAME] [SERVICE_NAME]
# Example: ./deploy.sh ap-south-1 membrain-mcp membrain-cluster membrain-mcp

set -e

REGION=${1:-$(aws configure get region)}
ECR_REPO_NAME=${2:-"membrain-mcp"}
CLUSTER_NAME=${3:-"membrain-cluster"}
SERVICE_NAME=${4:-"membrain-mcp"}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

if [ -z "$REGION" ]; then
    echo "Error: AWS region not found. Please provide it as first argument or configure AWS CLI."
    exit 1
fi

if [ -z "$ACCOUNT_ID" ]; then
    echo "Error: AWS account ID not found. Please configure AWS CLI."
    exit 1
fi

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}"
IMAGE_TAG=${IMAGE_TAG:-"latest"}
FULL_IMAGE_URI="${ECR_URI}:${IMAGE_TAG}"

echo "=========================================="
echo "Deploying Mem-Brain MCP Server to ECS"
echo "=========================================="
echo "Region: $REGION"
echo "Account ID: $ACCOUNT_ID"
echo "ECR Repository: $ECR_REPO_NAME"
echo "ECR URI: $ECR_URI"
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "Image Tag: $IMAGE_TAG"
echo "=========================================="
echo ""

# Step 1: Check if ECR repository exists, create if not
echo "Step 1: Checking ECR repository..."
if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$REGION" &>/dev/null; then
    echo "ECR repository does not exist. Creating..."
    aws ecr create-repository \
        --repository-name "$ECR_REPO_NAME" \
        --region "$REGION" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256 \
        --no-cli-pager
    echo "ECR repository created."
else
    echo "ECR repository exists."
fi
echo ""

# Step 2: Login to ECR
echo "Step 2: Logging in to ECR..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ECR_URI"
echo ""

# Step 3: Build Docker image with buildx for linux/amd64
echo "Step 3: Building Docker image for linux/amd64..."
cd "$(dirname "$0")/.."
docker buildx build --platform linux/amd64 -f docker/Dockerfile -t "$ECR_REPO_NAME:$IMAGE_TAG" --load .
docker tag "$ECR_REPO_NAME:$IMAGE_TAG" "$FULL_IMAGE_URI"
echo "Docker image built and tagged."
echo ""

# Step 4: Push image to ECR
echo "Step 4: Pushing image to ECR..."
docker push "$FULL_IMAGE_URI"
echo "Image pushed to ECR."
echo ""

# Step 5: Update task definition with new image
echo "Step 5: Updating ECS task definition..."
TASK_DEF_FILE="aws/ecs-task-definition.json"

# Create a temporary task definition with updated image URI
TEMP_TASK_DEF=$(mktemp)
sed "s|638331727768.dkr.ecr.ap-south-1.amazonaws.com/membrain-mcp:latest|${FULL_IMAGE_URI}|g" "$TASK_DEF_FILE" | \
sed "s|638331727768|${ACCOUNT_ID}|g" | \
sed "s|ap-south-1|${REGION}|g" > "$TEMP_TASK_DEF"

# Register new task definition revision
TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json "file://${TEMP_TASK_DEF}" \
    --region "$REGION" \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "New task definition registered: $TASK_DEF_ARN"
rm "$TEMP_TASK_DEF"
echo ""

# Step 6: Update ECS service
echo "Step 6: Updating ECS service..."
aws ecs update-service \
    --cluster "$CLUSTER_NAME" \
    --service "$SERVICE_NAME" \
    --task-definition "$TASK_DEF_ARN" \
    --force-new-deployment \
    --region "$REGION" \
    --no-cli-pager

echo "Service update initiated."
echo ""

# Step 7: Wait for service to stabilize
echo "Step 7: Waiting for service to stabilize..."
echo "This may take a few minutes..."
aws ecs wait services-stable \
    --cluster "$CLUSTER_NAME" \
    --services "$SERVICE_NAME" \
    --region "$REGION"

echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Service details:"
aws ecs describe-services \
    --cluster "$CLUSTER_NAME" \
    --services "$SERVICE_NAME" \
    --region "$REGION" \
    --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount,TaskDefinition:taskDefinition}' \
    --output table

echo ""
echo "To view logs:"
echo "  aws logs tail /ecs/membrain-mcp --follow --region $REGION"

