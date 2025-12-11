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

## Next Steps

1. ✅ Databases created
2. ⏳ Deploy application to ECS/Fargate
3. ⏳ Setup GitHub Actions for CI/CD (BE-20)
4. ⏳ Configure domain and SSL