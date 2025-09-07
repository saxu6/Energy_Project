# Deployment Guide - Energy Consumption Analyzer

## 🚀 Quick Deployment Options

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the system
python start_system.py

# Access at http://localhost:8000
```

### 2. Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build

# Or build manually
docker build -t energy-analyzer .
docker run -p 8000:8000 energy-analyzer
```

### 3. AWS ECS Deployment

#### Prerequisites
- AWS CLI configured
- Docker installed
- ECR repository created

#### Steps
```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name energy-analyzer

# 2. Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t energy-analyzer .
docker tag energy-analyzer:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/energy-analyzer:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/energy-analyzer:latest

# 3. Create ECS cluster and service
aws ecs create-cluster --cluster-name energy-analyzer-cluster
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster energy-analyzer-cluster --service-name energy-analyzer --task-definition energy-analyzer:1
```

### 4. Kubernetes Deployment

#### Prerequisites
- kubectl configured
- Kubernetes cluster running

#### Steps
```bash
# 1. Apply deployment
kubectl apply -f deployment.yaml

# 2. Check status
kubectl get pods
kubectl get services

# 3. Access the service
kubectl port-forward service/energy-analyzer-service 8000:80
```

## 🔧 Configuration

### Environment Variables
```bash
# Copy example file
cp env.example .env

# Edit configuration
nano .env
```

### Key Configuration Options
```bash
# Application
FLASK_ENV=production
PORT=8000
HOST=0.0.0.0

# ML Models
ANOMALY_CONTAMINATION=0.1
ANOMALY_CONFIDENCE_THRESHOLD=0.5

# AWS (for production)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET=energy-analyzer-data
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://localhost:8000/api/health
```

### Performance Monitoring
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# Monitor logs
docker logs energy-analyzer
kubectl logs deployment/energy-consumption-analyzer
```

### Alerting Setup
```bash
# Set up CloudWatch alarms (AWS)
aws cloudwatch put-metric-alarm \
  --alarm-name "EnergyAnalyzer-HighCPU" \
  --alarm-description "High CPU usage" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## 🔒 Security Configuration

### SSL/TLS Setup
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update Docker configuration
docker run -p 443:443 \
  -v $(pwd)/cert.pem:/app/cert.pem \
  -v $(pwd)/key.pem:/app/key.pem \
  energy-analyzer
```

### Network Security
```bash
# AWS Security Group
aws ec2 create-security-group \
  --group-name energy-analyzer-sg \
  --description "Security group for Energy Analyzer"

aws ec2 authorize-security-group-ingress \
  --group-name energy-analyzer-sg \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

## 📈 Scaling Configuration

### Auto Scaling (ECS)
```json
{
  "AutoScalingGroupName": "energy-analyzer-asg",
  "MinSize": 2,
  "MaxSize": 10,
  "DesiredCapacity": 3,
  "TargetTrackingConfigurations": [
    {
      "TargetValue": 70.0,
      "PredefinedMetricSpecification": {
        "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
      }
    }
  ]
}
```

### Load Balancer Setup
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name energy-analyzer-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678

# Create target group
aws elbv2 create-target-group \
  --name energy-analyzer-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345678 \
  --health-check-path /api/health
```

## 🗄️ Database Setup (Optional)

### PostgreSQL with RDS
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier energy-analyzer-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password your-password \
  --allocated-storage 20
```

### Redis for Caching
```bash
# Create ElastiCache cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id energy-analyzer-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Build and push Docker image
      run: |
        docker build -t energy-analyzer .
        docker tag energy-analyzer:latest ${{ secrets.ECR_REGISTRY }}/energy-analyzer:latest
        docker push ${{ secrets.ECR_REGISTRY }}/energy-analyzer:latest
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster energy-analyzer-cluster --service energy-analyzer --force-new-deployment
```

## 🧪 Testing Deployment

### Pre-deployment Tests
```bash
# Run validation tests
python final_validation.py

# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/available-data
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"bedType":"2","month":"January","day":1}'
```

### Post-deployment Verification
```bash
# Check application health
curl https://your-domain.com/api/health

# Test analysis functionality
curl -X POST https://your-domain.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"bedType":"2","month":"January","day":1}'

# Monitor performance
watch -n 5 'curl -s -w "%{time_total}\n" -o /dev/null https://your-domain.com/api/health'
```

## 🚨 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker logs energy-analyzer

# Check resource usage
docker stats energy-analyzer

# Verify environment variables
docker exec energy-analyzer env
```

#### High Response Times
```bash
# Check CPU and memory usage
docker stats energy-analyzer

# Monitor network
docker exec energy-analyzer netstat -tulpn

# Check application logs
docker logs energy-analyzer --tail 100
```

#### Database Connection Issues
```bash
# Test database connectivity
docker exec energy-analyzer python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:pass@host:5432/db')
print('Connected successfully')
"
```

### Performance Optimization

#### Memory Optimization
```bash
# Set memory limits
docker run -m 1g energy-analyzer

# Monitor memory usage
docker stats energy-analyzer
```

#### CPU Optimization
```bash
# Set CPU limits
docker run --cpus=2 energy-analyzer

# Monitor CPU usage
docker stats energy-analyzer
```

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify configuration settings
4. Contact the development team

---

**🎉 Your Energy Consumption Analyzer is now ready for production deployment!**
