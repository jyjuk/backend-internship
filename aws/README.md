# AWS Infrastructure Setup

## Resources Created

### RDS PostgreSQL
- **Instance ID**: backend-internship-db
- **Engine**: PostgreSQL 15.15
- **Instance Class**: db.t3.micro (Free Tier)
- **Storage**: 20 GB gp2
- **Region**: eu-central-1
- **Security Group**: sg-029cc442ba3f50e50

### ElastiCache Redis
- **Cluster ID**: backend-internship-redis
- **Engine**: Redis 7.1.0
- **Node Type**: cache.t3.micro (Free Tier)
- **Region**: eu-central-1
- **Security Group**: sg-053a56ea83e03f75d

## Connection Details

Connection details are stored in `aws/aws-resources.txt` (not committed to git).

### RDS Connection Test
```bash
psql -h backend-internship-db.cvu0ss0asvz3.eu-central-1.rds.amazonaws.com -U postgres -d internship_db
```

### Redis Connection Test
```bash
redis-cli -h backend-internship-redis.ljzqoe.0001.euc1.cache.amazonaws.com -p 6379
```

## Security

⚠️ **IMPORTANT**: 
- Security groups currently allow access from `0.0.0.0/0` (anywhere)
- For production, restrict to specific IPs or VPC only
- Never commit credentials to git

## Cost Monitoring

Both services are within AWS Free Tier:
- RDS: 750 hours/month of db.t3.micro
- ElastiCache: 750 hours/month of cache.t3.micro

Monitor usage in AWS Console: Billing Dashboard


## ECS Deployment

### Resources
- **ECR Repository**: 809641219603.dkr.ecr.eu-central-1.amazonaws.com/backend-internship
- **ECS Cluster**: backend-cluster
- **ECS Service**: backend-service
- **Task Definition**: backend-task:1

### Application Access
- **Public IP**: Check ECS Console for current IP
- **API URL**: http://<PUBLIC_IP>:8000
- **API Docs**: http://<PUBLIC_IP>:8000/docs

### Manual Deployment Commands

**Build and Push Docker Image:**
```bash
# Login to ECR
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 809641219603.dkr.ecr.eu-central-1.amazonaws.com

# Build
docker build -f Dockerfile.production -t backend-internship:latest .

# Tag
docker tag backend-internship:latest 809641219603.dkr.ecr.eu-central-1.amazonaws.com/backend-internship:latest

# Push
docker push 809641219603.dkr.ecr.eu-central-1.amazonaws.com/backend-internship:latest
```

**Force New Deployment:**
```bash
aws ecs update-service --cluster backend-cluster --service backend-service --force-new-deployment --region eu-central-1
```

**Get Task Public IP:**
```bash
# List tasks
aws ecs list-tasks --cluster backend-cluster --service-name backend-service --region eu-central-1

# Get task details
aws ecs describe-tasks --cluster backend-cluster --tasks <TASK_ARN> --region eu-central-1

# Get public IP from ENI
aws ec2 describe-network-interfaces --network-interface-ids <ENI_ID> --region eu-central-1 --query "NetworkInterfaces[0].Association.PublicIp" --output text
```

## GitHub Actions CI/CD

Automated deployment configured in `.github/workflows/deploy.yml`

**Trigger**: Push to `develop` branch

**Process**:
1. Build Docker image
2. Push to ECR
3. Update ECS task definition
4. Deploy to ECS service

## Cost Monitoring

**Current Monthly Costs** (estimated):
- RDS PostgreSQL: ~$0 (Free Tier 750h)
- ElastiCache Redis: ~$0 (Free Tier 750h)
- ECS Fargate: ~$0 (Free Tier 750h)
- ECR Storage: ~$0 (Free Tier 10GB)
- Data Transfer: Minimal

**Total**: Within AWS Free Tier limits