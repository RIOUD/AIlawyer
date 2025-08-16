# Legal Assistant AI Platform - Microservices Quick Start Guide

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Python** (version 3.11 or higher)
- **Git** (for cloning the repository)

## Quick Start (5 Minutes)

### Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Lawyeragent

# Setup security configuration
python setup_security.py
```

### Step 2: Deploy Microservices

```bash
# Make deployment script executable
chmod +x deploy-microservices.sh

# Deploy all services
./deploy-microservices.sh
```

### Step 3: Access the Platform

Once deployment is complete, you can access:

- **Main Application**: http://localhost:8000
- **Security Service**: http://localhost:8001
- **Document Processing**: http://localhost:8002
- **Query Processing**: http://localhost:8003
- **Monitoring**: http://localhost:9090 (Prometheus)
- **Dashboard**: http://localhost:3000 (Grafana)

### Step 4: Login

Use the default credentials:
- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

## Service Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Web Interface (8000)                 │
│  • Main application interface                           │
│  • API gateway functionality                            │
└─────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────┐
│  Security (8001) │ Document (8002) │ Query (8003)      │
│  • Auth/Login    │ • File Upload   │ • AI Queries      │
│  • User Mgmt     │ • Processing    │ • RAG Operations  │
│  • Audit Logs    │ • Vector Store  │ • History         │
└─────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL │ Redis │ Ollama │ Prometheus │ Grafana    │
│  • Database │ • Cache│ • LLM  │ • Metrics  │ • Dashboard│
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 🔐 Security Service
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Admin and user roles with different permissions
- **Audit Logging**: Comprehensive security event tracking
- **Brute Force Protection**: Account lockout mechanisms

### 📄 Document Processing Service
- **Multi-Format Support**: PDF, DOCX, TXT file processing
- **Vector Embeddings**: AI-powered document indexing
- **Background Processing**: Asynchronous document handling
- **Status Tracking**: Real-time processing status updates

### ❓ Query Processing Service
- **Natural Language**: Human-like query understanding
- **RAG Operations**: Retrieval-Augmented Generation
- **Source Attribution**: Links to original documents
- **Query History**: Searchable query logs

### 🌐 Web Interface Service
- **Modern UI**: Clean, responsive web interface
- **API Gateway**: Centralized request routing
- **Service Orchestration**: Coordinates between services
- **Real-time Updates**: Live status and progress updates

## API Endpoints

### Authentication
```bash
# Login
POST http://localhost:8001/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Get current user
GET http://localhost:8001/auth/me
Authorization: Bearer <token>
```

### Document Operations
```bash
# Upload document
POST http://localhost:8002/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

# Get document status
GET http://localhost:8002/documents/{id}/status
Authorization: Bearer <token>
```

### Query Operations
```bash
# Process query
POST http://localhost:8003/query
Authorization: Bearer <token>
{
  "question": "What are the requirements for employment contracts?",
  "session_id": "web_session_123"
}

# Get query history
GET http://localhost:8003/queries/history
Authorization: Bearer <token>
```

## Monitoring and Health Checks

### Service Health
Each service provides a health check endpoint:
```bash
curl http://localhost:8000/health  # Web Interface
curl http://localhost:8001/health  # Security
curl http://localhost:8002/health  # Document Processing
curl http://localhost:8003/health  # Query Processing
```

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Purpose**: Metrics collection and storage
- **Features**: Service health, performance, error rates

### Grafana Dashboards
- **URL**: http://localhost:3000
- **Credentials**: `admin` / `admin`
- **Purpose**: Metrics visualization and alerting

## Development Workflow

### Adding a New Service

1. **Create Service Directory**:
```bash
mkdir -p services/new_service
touch services/new_service/__init__.py
touch services/new_service/app.py
```

2. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY shared/ ./shared/
COPY services/new_service/ ./services/new_service/
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8004
CMD ["python", "services/new_service/app.py"]
```

3. **Update Docker Compose**:
```yaml
new-service:
  build:
    context: .
    dockerfile: services/new_service/Dockerfile
  ports:
    - "127.0.0.1:8004:8004"
  environment:
    - NEW_SERVICE_HOST=0.0.0.0
    - NEW_SERVICE_PORT=8004
```

4. **Update Nginx Configuration**:
```nginx
location /api/new-service/ {
    proxy_pass http://new-service:8004/;
    # ... other settings
}
```

### Local Development

For local development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export JWT_SECRET="your-jwt-secret"
export MASTER_PASSWORD="your-master-password"

# Run services individually
python services/security/app.py
python services/document_processing/app.py
python services/query_processing/app.py
python services/web_interface/app.py
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

2. **Docker Permission Issues**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

3. **Service Not Starting**:
```bash
# Check logs
docker-compose -f docker-compose.microservices.yml logs <service-name>

# Restart service
docker-compose -f docker-compose.microservices.yml restart <service-name>
```

4. **Database Connection Issues**:
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.microservices.yml ps postgres

# Restart database
docker-compose -f docker-compose.microservices.yml restart postgres
```

### Health Check Commands

```bash
# Check all services
./health-check.sh

# Check specific service
curl -f http://localhost:8001/health

# Check database
docker exec legal-assistant-postgres pg_isready -U postgres

# Check Redis
docker exec legal-assistant-redis redis-cli ping
```

## Security Best Practices

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique secrets for each environment
- Rotate secrets regularly

### Network Security
- Services are bound to localhost by default
- Use VPN for remote access
- Implement proper firewall rules

### Access Control
- Use strong passwords
- Implement role-based access
- Monitor audit logs regularly

## Performance Optimization

### Scaling Services
```bash
# Scale specific service
docker-compose -f docker-compose.microservices.yml up -d --scale query-processing-service=3

# Scale all services
docker-compose -f docker-compose.microservices.yml up -d --scale security-service=2 --scale document-processing-service=2 --scale query-processing-service=3
```

### Resource Limits
```yaml
services:
  query-processing-service:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker exec legal-assistant-postgres pg_dump -U postgres legal_assistant > backup.sql

# Restore backup
docker exec -i legal-assistant-postgres psql -U postgres legal_assistant < backup.sql
```

### Configuration Backup
```bash
# Backup configuration
tar -czf config-backup.tar.gz .env nginx/ monitoring/

# Restore configuration
tar -xzf config-backup.tar.gz
```

## Support and Resources

### Documentation
- [Microservices Architecture](MICROSERVICES_ARCHITECTURE.md)
- [Security Guide](SECURITY_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)

### Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Service Logs**: `docker-compose logs -f`

### Community
- GitHub Issues: Report bugs and feature requests
- Documentation: Keep updated with latest changes
- Security: Report security vulnerabilities privately

## Next Steps

1. **Explore the Interface**: Try uploading documents and asking questions
2. **Review Monitoring**: Check Prometheus and Grafana dashboards
3. **Customize Configuration**: Modify environment variables for your needs
4. **Scale for Production**: Implement proper production deployment
5. **Add Features**: Extend services with additional functionality

---

**Need Help?** Check the troubleshooting section above or create an issue in the repository. 