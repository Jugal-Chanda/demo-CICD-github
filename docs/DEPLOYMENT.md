# Deployment Documentation

Complete deployment guide for the Demo Flask Application.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring Setup](#monitoring-setup)
- [Security Configuration](#security-configuration)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)

## Overview

This document provides comprehensive deployment instructions for the Demo Flask Application across different environments and platforms.

### Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Reverse Proxy  │    │   Application   │
│     (Nginx)     │────│     (Nginx)      │────│    (Flask)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │  (PostgreSQL)   │
                    └─────────────────┘
```

### Supported Platforms
- **Docker & Docker Compose**: Development and small-scale production
- **Kubernetes**: Large-scale production deployments
- **AWS ECS/Fargate**: Cloud-native deployments
- **Azure Container Instances**: Quick cloud deployments
- **Google Cloud Run**: Serverless deployments

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 1 core
- **RAM**: 512 MB
- **Storage**: 5 GB
- **Network**: 100 Mbps

#### Recommended Requirements
- **CPU**: 2+ cores
- **RAM**: 2 GB
- **Storage**: 20 GB SSD
- **Network**: 1 Gbps

### Software Dependencies

#### Required Software
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git 2.30+
- Python 3.11+ (for local development)

#### Optional Software
- Kubernetes 1.24+
- Helm 3.0+
- Terraform 1.0+
- Ansible 2.10+

### Network Requirements

#### Inbound Ports
- **80**: HTTP traffic
- **443**: HTTPS traffic
- **22**: SSH access (administration)

#### Outbound Ports
- **5432**: PostgreSQL database
- **6379**: Redis (if used)
- **25/587**: SMTP (email notifications)

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/demo-flask-app.git
cd demo-flask-app
```

### 2. Environment Configuration

Create environment-specific configuration files:

```bash
# Copy environment template
cp .env.example .env

# Edit configuration for your environment
nano .env
```

#### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-super-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@db:5432/demo_db
DB_HOST=db
DB_PORT=5432
DB_NAME=demo_db
DB_USER=demo_user
DB_PASSWORD=secure_password

# Application Configuration
APP_NAME=Demo Flask App
APP_VERSION=1.0.0
API_PREFIX=/api

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
BCRYPT_ROUNDS=12

# External Services
REDIS_URL=redis://redis:6379/0
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
PROMETHEUS_METRICS=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 3. SSL Certificate Setup

#### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

#### Using Self-Signed Certificate

```bash
# Generate private key
openssl genrsa -out server.key 2048

# Generate certificate signing request
openssl req -new -key server.key -out server.csr

# Generate self-signed certificate
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

# Move certificates to nginx directory
sudo mv server.crt /etc/ssl/certs/
sudo mv server.key /etc/ssl/private/
```

## Deployment Options

### Option 1: Docker Compose (Recommended for Small Deployments)

#### Quick Start

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Scale application
docker-compose up -d --scale app=3
```

#### Production Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Update application
docker-compose pull && docker-compose up -d

# Backup database
docker-compose exec db pg_dump -U demo_user demo_db > backup.sql
```

### Option 2: Docker Swarm

#### Initialize Swarm

```bash
# Initialize Docker Swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.swarm.yml demo-app

# Check services
docker service ls

# Scale services
docker service scale demo-app_app=5
```

### Option 3: Manual Deployment

#### Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
```

#### Setup Application

```bash
# Create application directory
sudo mkdir -p /opt/demo-app
sudo chown $USER:$USER /opt/demo-app

# Clone repository
git clone https://github.com/your-org/demo-flask-app.git /opt/demo-app
cd /opt/demo-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python scripts/database_migration.py

# Start application
gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app
```

## Docker Deployment

### Docker Compose Configuration

#### docker-compose.yml (Base Configuration)

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
    environment:
      - FLASK_ENV=production
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=demo_db
      - POSTGRES_USER=demo_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Production Overrides (docker-compose.prod.yml)

```yaml
version: '3.8'

services:
  app:
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s

  db:
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups

  nginx:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
```

### Multi-Stage Docker Build

#### Dockerfile

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copy installed dependencies
COPY --from=builder /root/.local /home/app/.local
ENV PATH=/home/app/.local/bin:$PATH

# Copy application code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "wsgi:app"]
```

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Install Helm
curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz -o helm.tar.gz
tar -zxvf helm.tar.gz && sudo mv linux-amd64/helm /usr/local/bin/
```

### Deploy to Kubernetes

#### 1. Create Namespace

```bash
kubectl create namespace demo-app
```

#### 2. Create ConfigMaps and Secrets

```bash
# Create configmap
kubectl create configmap demo-app-config \
  --from-literal=flask_env=production \
  --from-literal=log_level=INFO \
  --namespace=demo-app

# Create secret
kubectl create secret generic demo-app-secret \
  --from-literal=secret_key=your-secret-key \
  --from-literal=db_password=secure-db-password \
  --namespace=demo-app
```

#### 3. Deploy PostgreSQL

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: demo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: "demo_db"
        - name: POSTGRES_USER
          value: "demo_user"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: demo-app-secret
              key: db_password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: demo-app
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

#### 4. Deploy Application

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: demo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      containers:
      - name: demo-app
        image: your-registry/demo-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: FLASK_ENV
          valueFrom:
            configMapKeyRef:
              name: demo-app-config
              key: flask_env
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: demo-app-secret
              key: secret_key
        - name: DATABASE_URL
          value: "postgresql://demo_user:$(DB_PASSWORD)@postgres:5432/demo_db"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: demo-app
  namespace: demo-app
spec:
  selector:
    app: demo-app
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### 5. Deploy Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-app-ingress
  namespace: demo-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - your-domain.com
    secretName: demo-app-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: demo-app
            port:
              number: 8000
```

#### 6. Deploy Using Helm

```bash
# Add Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace demo-app \
  --set postgresqlDatabase=demo_db \
  --set postgresqlUsername=demo_user

# Deploy application
helm install demo-app ./helm/demo-app
```

## CI/CD Pipeline

### Jenkins Pipeline Integration

The application includes a comprehensive Jenkins pipeline (`Jenkinsfile`) with the following stages:

1. **Checkout**: Code checkout from Git
2. **Setup**: Environment preparation
3. **Security Scan**: Gitleaks for secrets detection
4. **Code Quality**: SonarQube analysis
5. **Build**: Docker image building
6. **Security Scan**: Trivy container scanning
7. **Dependency Check**: OWASP dependency analysis
8. **Test**: Unit and integration tests
9. **Deploy**: Automated deployment
10. **Post-Deploy Tests**: Health checks and validation

#### Jenkins Setup

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'your-registry/demo-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/your-org/demo-flask-app.git'
            }
        }

        stage('Security Scan') {
            steps {
                sh 'gitleaks detect --verbose --redact --config .gitleaks.toml'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker-compose down
                    docker-compose up -d
                '''
            }
        }
    }

    post {
        always {
            sh 'docker-compose logs'
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
```

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python -m pytest tests/ -v

    - name: Build and push Docker image
      run: |
        docker build -t your-registry/demo-app:${{ github.sha }} .
        docker push your-registry/demo-app:${{ github.sha }}

    - name: Deploy to production
      run: |
        ssh user@your-server << EOF
          cd /opt/demo-app
          docker-compose pull
          docker-compose up -d
          docker-compose logs -f app
        EOF
```

## Monitoring Setup

### Application Monitoring

#### Prometheus Metrics

The application exposes Prometheus metrics at `/metrics`:

```python
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Custom metrics
REQUEST_COUNT = metrics.counter(
    'request_count', 'Request count',
    labels={'method': lambda: request.method, 'endpoint': lambda: request.path}
)
```

#### Grafana Dashboards

Import the provided Grafana dashboard (`monitoring/grafana-dashboard.json`) for comprehensive monitoring.

### Infrastructure Monitoring

#### Docker Container Monitoring

```bash
# Monitor container resources
docker stats

# Container logs
docker-compose logs -f --tail=100 app

# Health checks
docker-compose ps
```

#### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop sysstat -y

# Monitor system resources
htop

# Disk usage
df -h

# Network monitoring
sudo apt install nload -y
nload
```

## Security Configuration

### SSL/TLS Configuration

#### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### Database Security

```sql
-- Create application user with limited privileges
CREATE USER demo_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE demo_db TO demo_user;
GRANT USAGE ON SCHEMA public TO demo_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO demo_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO demo_user;

-- Enable row-level security if needed
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
```

### Container Security

```dockerfile
# Use non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Minimize attack surface
RUN apt-get update && apt-get install -y --no-install-recommends \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*

# Use specific package versions
FROM python:3.11.4-slim
```

## Backup and Recovery

### Database Backup

#### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/demo_db_${DATE}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U demo_user -h localhost demo_db > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

#### Schedule Backups

```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /opt/demo-app/scripts/backup.sh
```

### Application Backup

```bash
# Backup application data
tar -czf app_backup_$(date +%Y%m%d).tar.gz \
    --exclude='logs/*' \
    --exclude='*.log' \
    /opt/demo-app/
```

### Recovery Procedures

#### Database Recovery

```bash
# Stop application
docker-compose down

# Restore database
gunzip demo_db_20250119_020000.sql.gz
docker-compose exec -T db psql -U demo_user -d demo_db < demo_db_20250119_020000.sql

# Start application
docker-compose up -d
```

#### Application Rollback

```bash
# Rollback to previous version
docker tag your-registry/demo-app:v1.0.0 your-registry/demo-app:latest
docker-compose pull
docker-compose up -d

# Verify rollback
curl -f http://localhost/health
```

## Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check logs
docker-compose logs app

# Check environment variables
docker-compose exec app env

# Test database connection
docker-compose exec app python -c "import psycopg2; psycopg2.connect(os.environ['DATABASE_URL'])"
```

#### Database Connection Issues

```bash
# Check database status
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection manually
docker-compose exec db psql -U demo_user -d demo_db -c "SELECT version();"
```

#### High Memory Usage

```bash
# Check container memory usage
docker stats

# Check application memory usage
docker-compose exec app ps aux --sort=-%mem | head -10

# Adjust Gunicorn workers
# In docker-compose.yml
environment:
  - GUNICORN_WORKERS=2
```

#### Slow Response Times

```bash
# Check application logs for slow queries
docker-compose logs app | grep "slow"

# Enable SQL query logging
environment:
  - SQLALCHEMY_ECHO=true

# Profile application performance
docker-compose exec app python -m cProfile -s time app.py
```

### Health Checks

#### Application Health Check

```bash
# Manual health check
curl -f http://localhost/health

# Check all services
docker-compose ps

# Check nginx status
curl -I http://localhost/
```

#### Automated Health Monitoring

```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost/health"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $STATUS -ne 200 ]; then
    echo "Application is unhealthy (Status: $STATUS)"
    # Send alert (email, Slack, etc.)
    exit 1
else
    echo "Application is healthy"
fi
```

## Performance Tuning

### Application Performance

#### Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
```

#### Database Optimization

```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### Infrastructure Performance

#### Docker Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

#### Nginx Optimization

```nginx
worker_processes auto;
worker_connections 1024;

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### Caching Strategies

#### Redis Caching

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL')
})

@app.route('/api/users')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_users():
    return jsonify(get_all_users())
```

#### Database Query Caching

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

# Enable query result caching
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

## Scaling Strategies

### Horizontal Scaling

```bash
# Scale application instances
docker-compose up -d --scale app=5

# Load balancer configuration
upstream app_backend {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
    }
}
```

### Database Scaling

#### Read Replicas

```yaml
services:
  db_master:
    # Master database configuration

  db_replica:
    image: postgres:15-alpine
    environment:
      - POSTGRES_MASTER_HOST=db_master
      - POSTGRES_MASTER_PORT=5432
    depends_on:
      - db_master
```

#### Connection Pooling

```python
from psycopg2.pool import ThreadedConnectionPool

pool = ThreadedConnectionPool(
    minconn=2,
    maxconn=20,
    host=os.environ['DB_HOST'],
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD']
)
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Log Rotation

```bash
# Configure logrotate
cat > /etc/logrotate.d/demo-app << EOF
/opt/demo-app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 app app
    postrotate
        docker-compose restart app
    endscript
}
EOF
```

#### Dependency Updates

```bash
# Update Python dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose pull

# Update system packages
sudo apt update && sudo apt upgrade -y
```

#### Database Maintenance

```sql
-- Vacuum and analyze tables
VACUUM ANALYZE users;

-- Reindex tables
REINDEX TABLE users;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Support and Resources

### Documentation Links
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Community Resources
- [Flask Community Forum](https://discuss.python.org/c/flask/)
- [Docker Community](https://forums.docker.com/)
- [PostgreSQL Mailing Lists](https://www.postgresql.org/list/)

### Professional Support
- **Email**: support@your-domain.com
- **Documentation**: https://docs.your-domain.com
- **Status Page**: https://status.your-domain.com

---

*Last updated: January 19, 2025*
*Version: 1.0.0*