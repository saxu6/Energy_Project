# Energy Consumption Anomaly Detection System - Architecture

## 🎯 **System Vision**

### **Problem Statement**
Detect abnormal electricity usage spikes in hostel rooms (2-bed, 4-bed, 6-bed) by analyzing energy consumption patterns, considering occupancy, climate factors, and seasonal variations to enable proactive facility management.

### **User Personas**
1. **Admin**: System configuration, user management, global analytics
2. **Facility Manager**: Real-time monitoring, alert management, cost optimization
3. **Warden**: Room-level insights, occupancy correlation, maintenance alerts

### **Key Performance Indicators (KPIs)**
- **Anomaly Detection**: Precision > 85%, Recall > 80%, F1-Score > 82%
- **Mean Time to Alert (MTTA)**: < 60 seconds from data ingestion
- **False Positive Rate**: < 15% of total alerts
- **System Availability**: 99.9% uptime
- **Cost Savings**: 15-25% reduction in energy waste

### **Service Level Objectives (SLOs)**
- **Latency**: P95 API response time < 200ms
- **Throughput**: 1000+ readings/second processing capacity
- **Accuracy**: Model drift detection with 7-day retraining cycles
- **Reliability**: 99.9% data processing success rate

## 🏗️ **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Ingestion     │    │     Storage     │
│                 │    │                 │    │                 │
│ • Smart Meters  │───▶│ • API Gateway   │───▶│ • PostgreSQL    │
│ • Weather APIs  │    │ • Lambda        │    │ • Redis Cache   │
│ • Occupancy     │    │ • Kinesis       │    │ • S3 Parquet    │
│ • Manual Input  │    │ • EventBridge   │    │ • MLflow        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Processing    │    │   ML Pipeline   │    │     Analytics   │
│                 │    │                 │    │                 │
│ • Feature Eng.  │◀───│ • Deep Learning │───▶│ • Real-time     │
│ • Data Quality  │    │ • Ensemble      │    │ • Historical    │
│ • Aggregation   │    │ • AutoML        │    │ • Predictive    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │   Notifications │    │   Integration   │
│                 │    │                 │    │                 │
│ • React/Next.js │◀───│ • WebSocket     │───▶│ • Email/SMS     │
│ • Mobile App    │    │ • SNS/SQS       │    │ • Slack/Teams   │
│ • Dashboard     │    │ • Push Notif.   │    │ • Webhooks      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ **Technology Stack**

### **Backend & APIs**
- **Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL 15+ (RDS)
- **Cache**: Redis 7+ (ElastiCache)
- **Message Queue**: Apache Kafka / AWS Kinesis
- **ML Platform**: MLflow + SageMaker (optional)

### **Frontend & UI**
- **Framework**: Next.js 14+ (React 18)
- **Styling**: Tailwind CSS + Shadcn/ui
- **Charts**: Recharts + D3.js
- **State Management**: Zustand / Redux Toolkit
- **Real-time**: Socket.io / WebSocket

### **Infrastructure & DevOps**
- **Cloud**: AWS (ECS Fargate, RDS, S3, CloudFront)
- **IaC**: Terraform / AWS CDK
- **CI/CD**: GitHub Actions
- **Monitoring**: CloudWatch + Prometheus + Grafana
- **Security**: IAM, KMS, WAF, Secrets Manager

### **Machine Learning**
- **Deep Learning**: PyTorch / TensorFlow
- **AutoML**: AutoGluon / Optuna
- **Feature Store**: Feast / Tecton
- **Model Serving**: TorchServe / TensorFlow Serving

## 📊 **Data Architecture**

### **Database Schema (PostgreSQL)**
```sql
-- Core entities
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    hostel VARCHAR(50) NOT NULL,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    bed_type INTEGER CHECK (bed_type IN (2, 4, 6)),
    floor INTEGER,
    building VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE meters (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id),
    serial_number VARCHAR(50) UNIQUE NOT NULL,
    meter_type VARCHAR(30),
    installation_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    meter_id INTEGER REFERENCES meters(id),
    timestamp TIMESTAMP NOT NULL,
    kwh DECIMAL(10,4) NOT NULL,
    voltage DECIMAL(6,2),
    current DECIMAL(6,2),
    power_factor DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE weather (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    temperature_c DECIMAL(4,1),
    humidity_percent DECIMAL(4,1),
    rainfall_mm DECIMAL(6,2),
    wind_speed_kmh DECIMAL(5,2),
    pressure_hpa DECIMAL(6,1),
    location VARCHAR(50)
);

CREATE TABLE occupancy (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id),
    timestamp TIMESTAMP NOT NULL,
    count INTEGER CHECK (count >= 0),
    source VARCHAR(20) -- 'manual', 'sensor', 'inference'
);

CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id),
    timestamp TIMESTAMP NOT NULL,
    reading_id INTEGER REFERENCES readings(id),
    anomaly_score DECIMAL(5,4),
    confidence DECIMAL(5,4),
    anomaly_type VARCHAR(30), -- 'high_consumption', 'low_consumption', 'unusual_pattern'
    model_version VARCHAR(20),
    features JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id),
    anomaly_id INTEGER REFERENCES anomalies(id),
    alert_type VARCHAR(30),
    severity VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    message TEXT,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INTEGER,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('admin', 'manager', 'warden', 'viewer')),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_readings_timestamp ON readings(timestamp);
CREATE INDEX idx_readings_meter_id ON readings(meter_id);
CREATE INDEX idx_anomalies_room_timestamp ON anomalies(room_id, timestamp);
CREATE INDEX idx_anomalies_score ON anomalies(anomaly_score DESC);
CREATE INDEX idx_weather_timestamp ON weather(timestamp);
```

### **Data Lake Schema (S3 Parquet)**
```
s3://energy-data-lake/
├── raw/
│   ├── readings/dt=YYYY-MM-DD/
│   ├── weather/dt=YYYY-MM-DD/
│   └── occupancy/dt=YYYY-MM-DD/
├── processed/
│   ├── features/dt=YYYY-MM-DD/
│   ├── anomalies/dt=YYYY-MM-DD/
│   └── aggregations/dt=YYYY-MM-DD/
└── ml/
    ├── models/
    ├── experiments/
    └── predictions/
```

## 🔄 **Data Flow Architecture**

### **Real-time Pipeline**
```
Smart Meters → API Gateway → Lambda → Kinesis → ECS Stream Processor → PostgreSQL
     ↓              ↓           ↓         ↓              ↓              ↓
Weather API → EventBridge → Lambda → Kinesis → ECS Stream Processor → PostgreSQL
     ↓              ↓           ↓         ↓              ↓              ↓
Occupancy → API Gateway → Lambda → Kinesis → ECS Stream Processor → PostgreSQL
```

### **Batch Pipeline**
```
S3 Raw Data → Glue ETL → S3 Processed → EMR/ECS → Feature Engineering → MLflow
     ↓           ↓           ↓           ↓           ↓              ↓
PostgreSQL → DMS → S3 → Glue → S3 → EMR/ECS → Model Training → MLflow
```

### **ML Pipeline**
```
Feature Store → Model Training → Model Validation → Model Registry → Model Serving
     ↓              ↓                ↓                ↓              ↓
S3 Features → SageMaker → A/B Testing → MLflow → ECS/TorchServe → API Gateway
```

## 🔐 **Security Architecture**

### **Network Security**
- **VPC**: Public/Private subnets with NAT Gateway
- **Security Groups**: Least privilege access
- **WAF**: Rate limiting, DDoS protection
- **VPN**: Site-to-site for on-premise integration

### **Data Security**
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **KMS**: Key management for sensitive data
- **IAM**: Role-based access control
- **Secrets Manager**: Credential management

### **Application Security**
- **Authentication**: JWT with refresh tokens
- **Authorization**: RBAC with fine-grained permissions
- **Input Validation**: Schema validation, SQL injection prevention
- **Audit Logging**: CloudTrail, application logs

## 📈 **Scalability Architecture**

### **Horizontal Scaling**
- **ECS Fargate**: Auto-scaling based on CPU/memory
- **RDS**: Read replicas, connection pooling
- **Redis**: Cluster mode for high availability
- **S3**: Global distribution with CloudFront

### **Performance Optimization**
- **Caching**: Redis for hot data, CloudFront for static assets
- **Database**: Query optimization, indexing strategy
- **API**: Response compression, pagination
- **ML**: Model quantization, batch inference

## 🚀 **Deployment Architecture**

### **Environment Strategy**
```
Development → Staging → Production
     ↓           ↓          ↓
Local Docker → ECS Dev → ECS Prod
     ↓           ↓          ↓
SQLite → RDS Dev → RDS Prod
```

### **Blue-Green Deployment**
```
Version A (Blue) ← Load Balancer → Version B (Green)
     ↓                                    ↓
ECS Service A ← Health Checks → ECS Service B
     ↓                                    ↓
RDS Primary A ← Read Replicas → RDS Primary B
```

## 📊 **Monitoring & Observability**

### **Metrics & Alarms**
- **Application**: Request rate, error rate, latency
- **Infrastructure**: CPU, memory, disk, network
- **Business**: Anomaly detection rate, alert accuracy
- **ML**: Model performance, data drift, prediction latency

### **Logging Strategy**
- **Structured Logging**: JSON format with correlation IDs
- **Centralized**: CloudWatch Logs with retention policies
- **Search**: Elasticsearch for log analysis
- **Alerting**: PagerDuty integration for critical issues

## 💰 **Cost Optimization**

### **Resource Optimization**
- **Compute**: Spot instances for batch processing
- **Storage**: S3 lifecycle policies (Standard → IA → Glacier)
- **Database**: RDS auto-pause for non-production
- **CDN**: CloudFront for global content delivery

### **Monitoring & Governance**
- **Cost Allocation**: Tags for resource tracking
- **Budgets**: Monthly spending limits with alerts
- **Right-sizing**: Regular resource optimization reviews
- **Reserved Instances**: Long-term commitment discounts
