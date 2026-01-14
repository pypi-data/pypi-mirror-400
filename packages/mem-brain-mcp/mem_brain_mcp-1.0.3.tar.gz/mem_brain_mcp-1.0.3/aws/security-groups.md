# Security Groups Configuration

This document describes the security groups required for deploying Mem-Brain MCP Server on AWS ECS.

## Overview

Three security groups are needed:
1. **MCP Application Load Balancer (ALB) Security Group** - Allows inbound traffic from the internet
2. **MCP ECS Service Security Group** - Allows inbound traffic from the MCP ALB only
3. **API ALB Security Group** (existing) - Must allow inbound from MCP ECS service

## 1. MCP ALB Security Group

**Purpose**: Allow HTTP/HTTPS traffic from the internet to the MCP load balancer.

### Inbound Rules

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| HTTP | TCP | 80 | 0.0.0.0/0 | Allow HTTP from internet |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Allow HTTPS from internet |

### Outbound Rules

| Type | Protocol | Port Range | Destination | Description |
|------|----------|------------|-------------|-------------|
| All traffic | All | All | 0.0.0.0/0 | Allow all outbound traffic |

**Note**: For production, consider restricting the source to specific IP ranges or use AWS WAF.

## 2. MCP ECS Service Security Group

**Purpose**: Allow inbound traffic only from the MCP ALB security group, and outbound to the API ALB.

### Inbound Rules

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| Custom TCP | TCP | 8100 | MCP ALB Security Group ID | Allow traffic from MCP ALB |

### Outbound Rules

| Type | Protocol | Port Range | Destination | Description |
|------|----------|------------|-------------|-------------|
| HTTP | TCP | 80 | API ALB Security Group ID | Allow HTTP to API ALB |
| HTTPS | TCP | 443 | API ALB Security Group ID | Allow HTTPS to API ALB |

**Note**: The MCP server needs to reach the API ALB to proxy requests. Ensure the API ALB security group allows inbound from the MCP ECS security group.

## 3. API ALB Security Group (Update Required)

**Purpose**: Must allow inbound traffic from the MCP ECS service security group.

### Additional Inbound Rule Required

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| HTTP | TCP | 80 | MCP ECS Security Group ID | Allow HTTP from MCP ECS |
| HTTPS | TCP | 443 | MCP ECS Security Group ID | Allow HTTPS from MCP ECS |

## Creating Security Groups via AWS CLI

### 1. Create MCP ALB Security Group

```bash
VPC_ID="vpc-xxxxxxxxxxxxxxxxx"  # Replace with your VPC ID

MCP_ALB_SG_ID=$(aws ec2 create-security-group \
    --group-name membrain-mcp-alb-sg \
    --description "Security group for Mem-Brain MCP Application Load Balancer" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Add inbound HTTP rule
aws ec2 authorize-security-group-ingress \
    --group-id $MCP_ALB_SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Add inbound HTTPS rule
aws ec2 authorize-security-group-ingress \
    --group-id $MCP_ALB_SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

echo "MCP ALB Security Group ID: $MCP_ALB_SG_ID"
```

### 2. Create MCP ECS Service Security Group

```bash
MCP_ECS_SG_ID=$(aws ec2 create-security-group \
    --group-name membrain-mcp-ecs-sg \
    --description "Security group for Mem-Brain MCP ECS tasks" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Add inbound rule from MCP ALB
aws ec2 authorize-security-group-ingress \
    --group-id $MCP_ECS_SG_ID \
    --protocol tcp \
    --port 8100 \
    --source-group $MCP_ALB_SG_ID

# Add outbound rule for API ALB (replace API_ALB_SG_ID)
API_ALB_SG_ID="sg-xxxxxxxxxxxxxxxxx"  # Replace with API ALB security group ID

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

echo "MCP ECS Security Group ID: $MCP_ECS_SG_ID"
```

### 3. Update API ALB Security Group

```bash
# Allow inbound from MCP ECS service
API_ALB_SG_ID="sg-xxxxxxxxxxxxxxxxx"  # Replace with API ALB security group ID

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
```

## Security Best Practices

1. **Least Privilege**: Only allow necessary ports and protocols
2. **Security Group References**: Use security group IDs instead of CIDR blocks where possible
3. **Network Isolation**: Deploy ECS tasks in private subnets (though public IPs are enabled for simplicity)
4. **HTTPS**: Use HTTPS on the ALB with an SSL certificate (ACM)
5. **WAF**: Consider AWS WAF for additional protection
6. **VPC Flow Logs**: Enable VPC Flow Logs for monitoring
7. **Regular Audits**: Regularly review security group rules

## Troubleshooting

### MCP ECS tasks cannot reach API ALB
- Verify API ALB security group allows inbound from MCP ECS security group
- Check that MCP ECS security group has outbound rules to API ALB
- Verify subnet routing tables allow traffic
- Check that MCP ECS tasks can resolve the API ALB DNS name

### MCP ALB cannot reach MCP ECS tasks
- Verify MCP ECS security group allows inbound from MCP ALB security group
- Check that MCP ALB and MCP ECS tasks are in the same VPC
- Verify target group health checks are passing
- Check ECS task logs for errors

### Cannot access MCP server from internet
- Verify MCP ALB security group allows inbound HTTP/HTTPS
- Check MCP ALB listener configuration
- Verify DNS/Route53 configuration (if using custom domain)
- Check that target group has healthy targets

## Network Flow

```
Internet
  ↓ (HTTP/HTTPS)
MCP ALB (port 80/443)
  ↓ (port 8100)
MCP ECS Tasks
  ↓ (HTTP/HTTPS to API ALB)
API ALB
  ↓ (port 8000)
API ECS Tasks
  ↓ (PostgreSQL)
RDS Database
```

