# Demo Flask Application - Complete CI/CD Pipeline

A comprehensive demonstration of modern DevSecOps practices using Jenkins CI/CD pipeline with security scanning, code quality analysis, and automated deployment.

![CI/CD Pipeline](https://img.shields.io/badge/CI/CD-Jenkins-blue)
![Security](https://img.shields.io/badge/Security-Trivy%20%7C%20Gitleaks-red)
![Quality](https://img.shields.io/badge/Quality-SonarQube-green)
![Container](https://img.shields.io/badge/Container-Docker-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project demonstrates a complete CI/CD pipeline for a Python Flask web application with PostgreSQL database. The pipeline incorporates industry best practices including:

- **Security Scanning**: Trivy for container vulnerabilities, Gitleaks for secrets detection
- **Code Quality**: SonarQube analysis with quality gates
- **Dependency Management**: Dependency-Track for SBOM and vulnerability tracking
- **Automated Testing**: Comprehensive unit test suite with coverage reporting
- **Containerization**: Multi-stage Docker builds with security best practices
- **Infrastructure as Code**: Docker Compose for local development and production deployment
- **Rollback Capabilities**: Automated rollback to previous versions

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitLab CE     │    │    Jenkins      │    │    Harbor       │
│                 │    │   CI/CD Server  │    │   Registry      │
│ • Source Code   │◄──►│ • Build & Test  │◄──►│ • Docker Images │
│ • Webhooks      │    │ • Security Scan │    │ • Image Storage │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  SonarQube      │    │ Dependency-Track │    │   Production    │
│ Code Quality    │    │   SBOM & Vulns   │    │   Environment   │
│ • Static Analysis│    │ • Vulnerability │    │ • Docker Swarm  │
│ • Quality Gates │    │ • License Check │    │ • Load Balancer │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Features

### 🔧 Core Application
- **RESTful API**: Complete CRUD operations for user management
- **PostgreSQL Database**: Robust data persistence with connection pooling
- **Input Validation**: Comprehensive validation with custom error handling
- **Logging**: Structured logging with configurable levels
- **Health Checks**: Application and database health monitoring

### 🛡️ Security & Quality
- **Container Security**: Trivy vulnerability scanning
- **Secrets Detection**: Gitleaks for hardcoded secrets
- **Code Quality**: SonarQube static analysis
- **Dependency Tracking**: SBOM generation and vulnerability management
- **Security Headers**: Production-ready security configurations

### 🚀 DevOps & CI/CD
- **Automated Pipeline**: 16-stage Jenkins pipeline
- **Multi-stage Builds**: Optimized Docker images
- **Blue-Green Deployment**: Zero-downtime deployments
- **Rollback Support**: Automated rollback to previous versions
- **Infrastructure as Code**: Complete Docker Compose setup

### 📊 Monitoring & Observability
- **Health Endpoints**: Application and infrastructure monitoring
- **Log Aggregation**: Centralized logging strategy
- **Performance Metrics**: Response times and error rates
- **Container Metrics**: Resource usage monitoring

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum
- **Storage**: 50GB free space

### Required Tools
- **Docker**: 24.0+ CE
- **Docker Compose**: 2.20.0+
- **Git**: 2.30+
- **Python**: 3.11+

### External Services
- **Jenkins**: 2.387+ LTS with required plugins
- **GitLab**: 15.0+ CE/EE
- **Harbor**: 2.8+ registry
- **SonarQube**: 9.9+ LTS
- **Dependency-Track**: 4.8+
- **PostgreSQL**: 15.x

See [tools_requirements.md](tools_requirements.md) for detailed installation instructions.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone http://your-gitlab-server:8082/devops/demo-flask-app.git
cd demo-flask-app
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Local Development
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View application logs
docker-compose logs -f app

# Access the application
curl http://localhost:5000/
```

### 4. Run Tests
```bash
# Run unit tests
docker-compose exec app python -m pytest tests/ -v

# Run with coverage
docker-compose exec app python -m pytest tests/ --cov=src --cov-report=html
```

### 5. Access Points
- **Application**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/users
- **Health Check**: http://localhost:5000/
- **Nginx Proxy**: http://localhost

## 💻 Development Setup

### Local Development Environment

1. **Python Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt
pip install -r src/requirements-dev.txt
```

2. **Database Setup**
```bash
# Start PostgreSQL
docker run -d \
  --name postgres-dev \
  -e POSTGRES_DB=demo_app \
  -e POSTGRES_USER=demo_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:15-alpine

# Run database migrations
python scripts/database_migration.py
```

3. **Run Application**
```bash
# Set environment variables
export FLASK_ENV=development
export DB_HOST=localhost
export DB_PASSWORD=secure_password

# Start application
cd src
python app.py
```

### IDE Setup

#### VS Code
```json
{
  "python.pythonPath": "venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm
- Set Python interpreter to `venv/bin/python`
- Enable pytest as test runner
- Configure run/debug configurations for Flask app

## 🔄 CI/CD Pipeline

The Jenkins pipeline consists of 16 comprehensive stages:

### Pipeline Stages
1. **Environment Setup** - Initialize build environment
2. **Source Code Checkout** - Pull latest code from GitLab
3. **Environment Configuration** - Set up credentials and variables
4. **Build Preparation** - Install dependencies and prepare build
5. **Unit Testing** - Run pytest with coverage (80% minimum)
6. **Code Quality Analysis** - SonarQube static analysis
7. **Security Scan - Secrets** - Gitleaks secrets detection
8. **Docker Image Build** - Multi-stage container build
9. **Container Security Scan** - Trivy vulnerability scanning
10. **Dependency Scan** - Dependency-Track SBOM analysis
11. **Registry Push** - Push image to Harbor registry
12. **Pre-Deployment Approval** - Manual approval gate
13. **Application Deployment** - Docker Compose deployment
14. **Database Migration Approval** - Schema change approval
15. **Database Migration** - Run migration scripts
16. **Post-Deployment Verification** - Health checks and validation

### Pipeline Configuration

See [JenkinsSetup.md](JenkinsSetup.md) for complete Jenkins configuration instructions.

### Pipeline Parameters
- `ROLLBACK_TAG`: Previous build tag for rollback
- `BRANCH_NAME`: Git branch to build (develop/main/staging)
- `SKIP_TESTS`: Skip unit tests (not recommended)
- `SKIP_SECURITY_SCANS`: Skip security scans (not recommended)

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### Health Check
```http
GET /
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-19T10:30:00.000Z",
  "version": "1.0.0",
  "database": "connected"
}
```

#### Get Users
```http
GET /api/users
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30,
      "created_at": "2025-01-19T10:00:00",
      "updated_at": "2025-01-19T10:00:00"
    }
  ],
  "count": 1
}
```

#### Create User
```http
POST /api/users
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "age": 25
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "age": 25,
    "created_at": "2025-01-19T10:30:00",
    "updated_at": "2025-01-19T10:30:00"
  },
  "message": "User created successfully"
}
```

See [docs/API.md](docs/API.md) for complete API documentation.

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_app.py::TestHealthCheck::test_health_check_success -v
```

### Test Coverage
- **Minimum Coverage**: 80%
- **Coverage Report**: `htmlcov/index.html`
- **Test Framework**: pytest
- **Mocking**: unittest.mock

### Integration Tests
```bash
# Test with real database
pytest tests/ -m integration --tb=short

# Test API endpoints
pytest tests/test_api.py -v
```

### Performance Tests
```bash
# Load testing
ab -n 1000 -c 10 http://localhost:5000/

# Memory profiling
python -m memory_profiler src/app.py
```

## 🚢 Deployment

### Production Deployment

1. **Environment Setup**
```bash
# Production environment variables
cp .env.example .env.production
# Edit .env.production with production values
```

2. **Build and Deploy**
```bash
# Build production images
docker-compose -f docker-compose.yml build

# Deploy to production
docker-compose -f docker-compose.yml up -d

# Run health checks
./scripts/health_check.sh
```

### Rollback Procedure

```bash
# Rollback to previous version
./scripts/rollback.sh build-123

# Verify rollback
./scripts/health_check.sh
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment procedures.

## 🔒 Security

### Security Features
- **Container Scanning**: Trivy vulnerability assessment
- **Secrets Detection**: Gitleaks automated scanning
- **Dependency Auditing**: OWASP Dependency-Check integration
- **Code Security**: SonarQube security rules
- **Input Validation**: Comprehensive input sanitization
- **HTTPS Enforcement**: SSL/TLS configuration

### Security Best Practices
- Non-root container execution
- Minimal base images
- Regular security updates
- Secrets management
- Network segmentation
- Access control

### Compliance
- **OWASP Top 10**: Addressed through multiple security layers
- **Container Security**: CIS Docker benchmarks
- **Code Security**: CWE/SANS Top 25 coverage

## 📊 Monitoring

### Application Metrics
- **Health Endpoints**: `/health`, `/metrics`
- **Response Times**: Application Performance Monitoring
- **Error Rates**: Exception tracking and alerting
- **Resource Usage**: CPU, memory, disk monitoring

### Infrastructure Monitoring
- **Container Metrics**: Docker stats and Prometheus
- **Database Metrics**: PostgreSQL monitoring
- **Registry Metrics**: Harbor usage statistics
- **CI/CD Metrics**: Jenkins build statistics

### Logging
- **Application Logs**: Structured JSON logging
- **Container Logs**: Docker logging drivers
- **Audit Logs**: User actions and system events
- **Security Logs**: Authentication and authorization events

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker-compose logs app

# Check environment variables
docker-compose exec app env

# Test database connection
docker-compose exec app python -c "import psycopg2; print('DB OK')"
```

#### Pipeline Failures
```bash
# Check Jenkins logs
sudo tail -f /var/log/jenkins/jenkins.log

# Validate pipeline syntax
# Jenkins UI → Pipeline Syntax → Declarative Directive Generator

# Check agent connectivity
ssh jenkins-agent "docker --version"
```

#### Database Connection Issues
```bash
# Test database connectivity
docker-compose exec postgres pg_isready -U demo_user -d demo_app

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v postgres
docker-compose up -d postgres
```

#### Container Issues
```bash
# Check container status
docker-compose ps

# Inspect container
docker-compose exec app sh

# Check resource usage
docker stats
```

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
export LOG_LEVEL=DEBUG

# Run with debug mode
docker-compose up --scale app=1
```

### Support Resources
- **Jenkins Documentation**: https://www.jenkins.io/doc/
- **Docker Documentation**: https://docs.docker.com/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- **PEP 8**: Python style guide compliance
- **Type Hints**: Use type annotations
- **Documentation**: Docstrings for all functions
- **Testing**: 80%+ test coverage
- **Security**: No hardcoded secrets

### Commit Convention
```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scopes: app, api, db, docker, jenkins, docs
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Jenkins Community** for the excellent CI/CD platform
- **Docker Community** for containerization technology
- **OWASP** for security best practices
- **Linux Community** for the robust operating system

## 📞 Contact

**Project Maintainer**: DevOps Team
**Email**: devops@company.com
**GitLab**: http://your-gitlab-server:8082/devops/demo-flask-app

---

**Happy Coding! 🚀**

*This project demonstrates enterprise-grade CI/CD practices and can be used as a template for production applications.*