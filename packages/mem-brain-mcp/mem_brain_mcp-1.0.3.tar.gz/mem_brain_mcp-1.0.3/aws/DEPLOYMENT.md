# AWS ECS Deployment Guide for Mem-Brain MCP Server

This guide walks you through deploying Mem-Brain MCP Server to AWS ECS (Fargate) with an Application Load Balancer.

## Prerequisites

- AWS CLI installed and configured (`aws configure`)
- Docker installed and running
- Docker Buildx installed (for multi-platform builds)
- AWS account with appropriate permissions:
  - ECS (create clusters, services, task definitions)
  - ECR (create repositories, push images)
  - EC2 (create security groups, VPC configuration)
  - ELB (create load balancers, target groups)
  - IAM (create roles for ECS tasks)
- **Mem-Brain API already deployed** and accessible via ALB
- Same VPC and subnets as the API deployment

## Architecture Overview

```
Internet → MCP ALB → ECS Fargate Service (MCP Server) → API ALB → API ECS Service → RDS PostgreSQL
                ↓
            CloudWatch Logs
```

## Step-by-Step Deployment

### Step 1: Set Up Security Groups

See [security-groups.md](./security-groups.md) for detailed instructions.

**Quick Summary:**
1. Create MCP ALB security group (allow HTTP/HTTPS from internet)
2. Create MCP ECS security group (allow port 8100 from MCP ALB, allow outbound to API ALB)
3. Update API ALB security group (allow inbound from MCP ECS security group)

```bash
# Set variables
VPC_ID="vpc-xxxxxxxxxxxxxxxxx"  # Replace with your VPC ID
API_ALB_SG_ID="sg-xxxxxxxxxxxxxxxxx"  # Replace with API ALB security group ID

# Create MCP ALB security group
MCP_ALB_SG_ID=$(aws ec2 create-security-group \
    --group-name membrain-mcp-alb-sg \
    --description "Security group for Mem-Brain MCP ALB" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow HTTP/HTTPS from internet
aws ec2 authorize-security-group-ingress \
    --group-id $MCP_ALB_SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $MCP_ALB_SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Create MCP ECS service security group
MCP_ECS_SG_ID=$(aws ec2 create-security-group \
    --group-name membrain-mcp-ecs-sg \
    --description "Security group for Mem-Brain MCP ECS tasks" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow traffic from MCP ALB
aws ec2 authorize-security-group-ingress \
    --group-id $MCP_ECS_SG_ID \
    --protocol tcp \
    --port 8100 \
    --source-group $MCP_ALB_SG_ID

# Allow outbound to API ALB
aws ec2 authorize-security-group-egress \
    --group-id $MCP_ECS_SG_ID \
    --protocol tcp \
    --port 80 \
    --source-group $API_ALB_SG_ID

aws ec2 authorize-security-group-egress \
    --group-id $MCP_ECS_SG_ID \
    --protocol tcp \
    --port 443 \
    --source-group $API_ALB_SG_ID

# Update API ALB security group to allow inbound from MCP ECS
aws ec2 authorize-security-group-ingress \
    --group-id $API_ALB_SG_ID \
    --protocol tcp \
    --port 80 \
    --source-group $MCP_ECS_SG_ID

aws ec2 authorize-security-group-ingress \
    --group-id $API_ALB_SG_ID \
    --protocol tcp \
    --port 443 \
    --source-group $MCP_ECS_SG_ID

echo "MCP ALB Security Group: $MCP_ALB_SG_ID"
echo "MCP ECS Security Group: $MCP_ECS_SG_ID"
```

### Step 2: Create CloudWatch Log Group

```bash
REGION="ap-south-1"  # Replace with your region

aws logs create-log-group \
    --log-group-name /ecs/membrain-mcp \
    --region $REGION
```

### Step 3: Create Application Load Balancer

```bash
# Set variables
VPC_ID="vpc-xxxxxxxxxxxxxxxxx"  # Replace with your VPC ID
PUBLIC_SUBNET_1="subnet-xxxxxxxxxxxxxxxxx"  # Replace with your public subnet IDs
PUBLIC_SUBNET_2="subnet-xxxxxxxxxxxxxxxxx"

# Create ALB
MCP_ALB_ARN=$(aws elbv2 create-load-balancer \
    --name membrain-mcp-alb \
    --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
    --security-groups $MCP_ALB_SG_ID \
    --scheme internet-facing \
    --type application \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)

# Create target group
MCP_TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
    --name membrain-mcp-tg \
    --protocol HTTP \
    --port 8100 \
    --vpc-id $VPC_ID \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --target-type ip \
    --matcher HttpCode=200 \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

# Create listener (HTTP)
aws elbv2 create-listener \
    --load-balancer-arn $MCP_ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$MCP_TARGET_GROUP_ARN

# Get ALB DNS name
MCP_ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $MCP_ALB_ARN \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

echo "MCP ALB ARN: $MCP_ALB_ARN"
echo "MCP Target Group ARN: $MCP_TARGET_GROUP_ARN"
echo "MCP ALB DNS: $MCP_ALB_DNS"
```

### Step 4: Update ECS Service Configuration

Update `aws/ecs-service-config.json` with your actual values:

```bash
# Set variables
VPC_ID="vpc-xxxxxxxxxxxxxxxxx"
PUBLIC_SUBNET_1="subnet-xxxxxxxxxxxxxxxxx"
PUBLIC_SUBNET_2="subnet-xxxxxxxxxxxxxxxxx"
MCP_ECS_SG_ID="sg-xxxxxxxxxxxxxxxxx"
MCP_TARGET_GROUP_ARN="arn:aws:elasticloadbalancing:REGION:ACCOUNT_ID:targetgroup/membrain-mcp-tg/xxxxxxxxxxxxxxxx"

# Update the JSON file (or edit manually)
cd aws
sed -i.bak "s|sg-xxxxxxxxxxxxxxxxx|$MCP_ECS_SG_ID|g" ecs-service-config.json
sed -i.bak "s|subnet-xxxxxxxxxxxxxxxxx|$PUBLIC_SUBNET_1|g" ecs-service-config.json
sed -i.bak "s|subnet-xxxxxxxxxxxxxxxxx|$PUBLIC_SUBNET_2|g" ecs-service-config.json
sed -i.bak "s|arn:aws:elasticloadbalancing:REGION:ACCOUNT_ID:targetgroup/membrain-mcp-tg/xxxxxxxxxxxxxxxx|$MCP_TARGET_GROUP_ARN|g" ecs-service-config.json
```

### Step 5: Update Task Definition

Update `aws/ecs-task-definition.json` with your API ALB DNS name:

```bash
# Set API ALB DNS (from your API deployment)
API_ALB_DNS="membrain-api-alb-1094729422.ap-south-1.elb.amazonaws.com"

# Update task definition
cd aws
sed -i.bak "s|http://membrain-api-alb-1094729422.ap-south-1.elb.amazonaws.com|http://$API_ALB_DNS|g" ecs-task-definition.json
```

### Step 6: Deploy Using Deployment Script

The easiest way to deploy is using the provided script:

```bash
cd mem-brain-mcp/aws
./deploy.sh [REGION] [ECR_REPO_NAME] [CLUSTER_NAME] [SERVICE_NAME]
```

**Example:**
```bash
cd mem-brain-mcp/aws
./deploy.sh ap-south-1 membrain-mcp membrain-cluster membrain-mcp
```

The script will:
1. Create ECR repository if it doesn't exist
2. Build Docker image for linux/amd64
3. Push image to ECR
4. Register new task definition
5. Create or update ECS service
6. Wait for deployment to stabilize

### Step 7: Manual Deployment (Alternative)

If you prefer manual deployment:

#### 7.1 Build and Push Docker Image

```bash
cd mem-brain-mcp

# Login to ECR
REGION="ap-south-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/membrain-mcp"

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

# Create ECR repository if it doesn't exist
aws ecr create-repository \
    --repository-name membrain-mcp \
    --region $REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 || true

# Build image for linux/amd64
docker buildx build --platform linux/amd64 -f docker/Dockerfile -t membrain-mcp:latest --load .

# Tag and push
docker tag membrain-mcp:latest ${ECR_URI}:latest
docker push ${ECR_URI}:latest
```

#### 7.2 Register Task Definition

```bash
cd aws
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="ap-south-1"

# Update image URI in task definition
sed "s|638331727768.dkr.ecr.ap-south-1.amazonaws.com/membrain-mcp:latest|${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/membrain-mcp:latest|g" ecs-task-definition.json | \
sed "s|638331727768|${ACCOUNT_ID}|g" | \
sed "s|ap-south-1|${REGION}|g" > /tmp/mcp-task-def.json

# Register task definition
TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/mcp-task-def.json \
    --region $REGION \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "Task Definition ARN: $TASK_DEF_ARN"
```

#### 7.3 Create ECS Service

```bash
CLUSTER_NAME="membrain-cluster"
SERVICE_NAME="membrain-mcp"

# Update service config with actual values
sed "s|sg-xxxxxxxxxxxxxxxxx|$MCP_ECS_SG_ID|g" ecs-service-config.json | \
sed "s|subnet-xxxxxxxxxxxxxxxxx|$PUBLIC_SUBNET_1|g" | \
sed "s|subnet-xxxxxxxxxxxxxxxxx|$PUBLIC_SUBNET_2|g" | \
sed "s|arn:aws:elasticloadbalancing:REGION:ACCOUNT_ID:targetgroup/membrain-mcp-tg/xxxxxxxxxxxxxxxx|$MCP_TARGET_GROUP_ARN|g" > /tmp/mcp-service-config.json

# Create service
aws ecs create-service \
    --cli-input-json file:///tmp/mcp-service-config.json \
    --cluster $CLUSTER_NAME \
    --region $REGION

# Wait for service to stabilize
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION
```

### Step 8: Verify Deployment

```bash
# Get ALB DNS
MCP_ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names membrain-mcp-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

# Test health endpoint
curl http://$MCP_ALB_DNS/health

# Check service status
aws ecs describe-services \
    --cluster membrain-cluster \
    --services membrain-mcp \
    --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}' \
    --output table

# View logs
aws logs tail /ecs/membrain-mcp --follow --region $REGION
```

## Configuration

### Environment Variables

The MCP server requires the following environment variables (set in the task definition):

- `API_BASE_URL`: URL of the deployed Mem-Brain API ALB (e.g., `http://membrain-api-alb-1094729422.ap-south-1.elb.amazonaws.com`)
- `MCP_SERVER_HOST`: Server host (default: `0.0.0.0`)
- `MCP_SERVER_PORT`: Server port (default: `8100`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

**Note**: `MEMBRAIN_API_KEY` is optional in the server configuration. Per-user JWT tokens are configured in MCP clients (Cursor, Claude Desktop, etc.) via request headers.

## Updating the Deployment

To update the MCP server after making code changes:

```bash
cd mem-brain-mcp/aws
./deploy.sh ap-south-1 membrain-mcp membrain-cluster membrain-mcp
```

Or manually:

```bash
# Build and push new image
# ... (same as Step 7.1)

# Register new task definition revision
# ... (same as Step 7.2)

# Update service
aws ecs update-service \
    --cluster membrain-cluster \
    --service membrain-mcp \
    --task-definition membrain-mcp \
    --force-new-deployment \
    --region ap-south-1
```

## Troubleshooting

### Service fails to start

1. **Check CloudWatch Logs:**
   ```bash
   aws logs tail /ecs/membrain-mcp --follow --region ap-south-1
   ```

2. **Check task status:**
   ```bash
   aws ecs describe-tasks \
       --cluster membrain-cluster \
       --tasks $(aws ecs list-tasks --cluster membrain-cluster --service-name membrain-mcp --query 'taskArns[0]' --output text) \
       --query 'tasks[0].{LastStatus:lastStatus,StoppedReason:stoppedReason,Containers:containers[0].{Name:name,LastStatus:lastStatus,Reason:reason}}' \
       --output json
   ```

3. **Common issues:**
   - **Image pull errors**: Check ECR repository exists and IAM role has permissions
   - **Health check failures**: Verify `/health` endpoint is accessible
   - **Cannot reach API**: Check security groups allow MCP ECS → API ALB traffic
   - **Port conflicts**: Ensure port 8100 is correctly configured

### MCP server cannot reach API

1. **Verify security groups:**
   ```bash
   # Check MCP ECS security group has outbound rule to API ALB
   aws ec2 describe-security-groups \
       --group-ids $MCP_ECS_SG_ID \
       --query 'SecurityGroups[0].IpPermissionsEgress'
   
   # Check API ALB security group allows inbound from MCP ECS
   aws ec2 describe-security-groups \
       --group-ids $API_ALB_SG_ID \
       --query 'SecurityGroups[0].IpPermissions'
   ```

2. **Test connectivity from ECS task:**
   ```bash
   # Get task ID
   TASK_ID=$(aws ecs list-tasks --cluster membrain-cluster --service-name membrain-mcp --query 'taskArns[0]' --output text | cut -d/ -f3)
   
   # Execute command in container
   aws ecs execute-command \
       --cluster membrain-cluster \
       --task $TASK_ID \
       --container membrain-mcp \
       --command "curl -v http://membrain-api-alb-1094729422.ap-south-1.elb.amazonaws.com/health" \
       --interactive
   ```

### Health checks failing

1. **Check health endpoint:**
   ```bash
   curl http://$MCP_ALB_DNS/health
   ```

2. **Check target group health:**
   ```bash
   aws elbv2 describe-target-health \
       --target-group-arn $MCP_TARGET_GROUP_ARN \
       --query 'TargetHealthDescriptions[*].{Target:Target.Id,Health:TargetHealth.State,Reason:TargetHealth.Reason}'
   ```

## Cleanup

To remove the deployment:

```bash
# Delete ECS service
aws ecs update-service \
    --cluster membrain-cluster \
    --service membrain-mcp \
    --desired-count 0 \
    --region ap-south-1

aws ecs delete-service \
    --cluster membrain-cluster \
    --service membrain-mcp \
    --region ap-south-1

# Delete ALB and target group
aws elbv2 delete-load-balancer --load-balancer-arn $MCP_ALB_ARN
aws elbv2 delete-target-group --target-group-arn $MCP_TARGET_GROUP_ARN

# Delete security groups (after removing rules)
aws ec2 delete-security-group --group-id $MCP_ECS_SG_ID
aws ec2 delete-security-group --group-id $MCP_ALB_SG_ID

# Delete CloudWatch log group
aws logs delete-log-group --log-group-name /ecs/membrain-mcp --region ap-south-1

# Delete ECR repository (optional)
aws ecr delete-repository --repository-name membrain-mcp --force --region ap-south-1
```

## Next Steps

After deployment:

1. **Update MCP client configuration** to use the deployed ALB DNS:
   ```json
   {
     "mcpServers": {
       "mem-brain": {
         "url": "http://membrain-mcp-alb-xxxxxxxxx.ap-south-1.elb.amazonaws.com/mcp",
         "headers": {
           "Authorization": "Bearer YOUR_JWT_TOKEN"
         }
       }
     }
   }
   ```

2. **Test the connection** from your MCP client (Cursor, Claude Desktop, etc.)

3. **Monitor logs** for any issues:
   ```bash
   aws logs tail /ecs/membrain-mcp --follow --region ap-south-1
   ```

