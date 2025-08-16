# LawyerAgent Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Options](#deployment-options)
4. [Local Deployment](#local-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Hybrid Deployment](#hybrid-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [Production Deployment](#production-deployment)
9. [Monitoring Setup](#monitoring-setup)
10. [User Testing Setup](#user-testing-setup)
11. [Troubleshooting](#troubleshooting)
12. [Security Considerations](#security-considerations)

## Overview

This guide provides comprehensive instructions for deploying the LawyerAgent system in various environments. The system supports multiple deployment modes to accommodate different security requirements and infrastructure constraints.

### System Architecture

LawyerAgent consists of the following core components:

- **Main Application**: Flask-based web interface and RAG system
- **Ollama LLM**: Local language model for offline inference
- **ChromaDB**: Vector database for document embeddings
- **Security Manager**: Encryption, audit logging, and access control
- **Monitoring System**: Real-time system health and performance monitoring
- **User Feedback System**: Structured feedback collection and analytics

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores (8+ recommended)
- RAM: 8GB (16GB+ recommended)
- Storage: 50GB available space
- OS: Linux, macOS, or Windows with WSL2

**Recommended Requirements:**
- CPU: 8+ cores
- RAM: 32GB+
- Storage: 100GB+ SSD
- GPU: NVIDIA GPU with 8GB+ VRAM (optional, for faster inference)

### Software Dependencies

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Docker & Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Ollama**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull required model
   ollama pull mixtral
   ```

4. **Git**
   ```bash
   git --version
   ```

## Deployment Options

### 1. Local Deployment
- **Use Case**: Development, testing, single-user scenarios
- **Security**: Complete offline operation
- **Pros**: Simple setup, no external dependencies
- **Cons**: Limited scalability, manual updates

### 2. Docker Deployment
- **Use Case**: Consistent environments, easy deployment
- **Security**: Containerized isolation
- **Pros**: Reproducible, portable, easy scaling
- **Cons**: Additional resource overhead

### 3. Hybrid Deployment
- **Use Case**: Sensitive data local, non-sensitive data cloud
- **Security**: Selective data residency
- **Pros**: Balance of security and collaboration
- **Cons**: Complex configuration, network dependencies

### 4. Cloud Deployment
- **Use Case**: Enterprise deployment, multi-user access
- **Security**: Cloud security with encryption
- **Pros**: High availability, easy scaling
- **Cons**: Internet dependency, potential data exposure

## Local Deployment

### Quick Start (Recommended for Testing)

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Lawyeragent
   ```

2. **Run Automated Setup**
   ```bash
   python setup.py
   ```

3. **Process Sample Documents**
   ```bash
   python ingest.py
   ```

4. **Start the Application**
   ```bash
   python app.py
   ```

5. **Access the System**
   - Web Interface: http://localhost:5000
   - CLI Interface: Available in terminal

### Manual Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Ollama Installation**
   ```bash
   ollama serve
   # In another terminal
   ollama pull mixtral
   ```

3. **Create Required Directories**
   ```bash
   mkdir -p source_documents chroma_db security exports custom_templates
   ```

4. **Initialize the System**
   ```bash
   python -c "from database import init_database; init_database()"
   ```

5. **Add Legal Documents**
   ```bash
   # Copy your legal PDF files to source_documents/
   cp /path/to/your/documents/*.pdf source_documents/
   ```

6. **Process Documents**
   ```bash
   python ingest.py
   ```

7. **Start the Application**
   ```bash
   python app.py
   ```

## Docker Deployment

### Single Container Deployment

1. **Build the Image**
   ```bash
   docker build -t lawyeragent .
   ```

2. **Run the Container**
   ```bash
   docker run -d \
     --name lawyeragent \
     -p 5000:5000 \
     -p 11434:11434 \
     -v $(pwd)/source_documents:/app/source_documents \
     -v $(pwd)/chroma_db:/app/chroma_db \
     -v $(pwd)/security:/app/security \
     -v $(pwd)/exports:/app/exports \
     lawyeragent
   ```

3. **Verify Deployment**
   ```bash
   docker logs lawyeragent
   curl http://localhost:5000/health
   ```

### Multi-Service Deployment

1. **Start All Services**
   ```bash
   docker-compose up -d
   ```

2. **Check Service Status**
   ```bash
   docker-compose ps
   ```

3. **View Logs**
   ```bash
   docker-compose logs -f
   ```

4. **Access Services**
   - Main Application: http://localhost:5000
   - Grafana Dashboard: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090

### Production Docker Deployment

1. **Create Production Configuration**
   ```bash
   cp docker-compose.yml docker-compose.prod.yml
   ```

2. **Update Environment Variables**
   ```yaml
   # docker-compose.prod.yml
   environment:
     - SECURITY_ENABLED=true
     - ENABLE_AUDIT_LOGGING=true
     - LOG_LEVEL=INFO
     - OLLAMA_HOST=0.0.0.0
   ```

3. **Deploy with Production Settings**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Hybrid Deployment

### Overview

Hybrid deployment allows sensitive legal documents to remain local while enabling cloud-based collaboration for non-sensitive data.

### Configuration

1. **Create Hybrid Configuration**
   ```bash
   cp docker-compose.yml docker-compose.hybrid.yml
   ```

2. **Configure Data Classification**
   ```python
   # hybrid_config.json
   {
     "deployment_mode": "hybrid",
     "local_components": {
       "sensitive_documents": true,
       "encryption_keys": true,
       "audit_logs": true
     },
     "cloud_components": {
       "collaboration": true,
       "analytics": true,
       "backup": true
     },
     "sync_settings": {
       "encryption": "end_to_end",
       "frequency": "real_time",
       "conflict_resolution": "local_wins"
     }
   }
   ```

3. **Deploy Hybrid System**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.hybrid.yml up -d
   ```

### Security Considerations

- All sensitive data remains encrypted locally
- Cloud sync uses end-to-end encryption
- Audit trails are maintained for all operations
- Access controls prevent unauthorized data exposure

## Cloud Deployment

### AWS Deployment

1. **Create EC2 Instance**
   ```bash
   # Launch Ubuntu 22.04 LTS instance
   # Minimum: t3.large (2 vCPU, 8GB RAM)
   # Recommended: t3.xlarge (4 vCPU, 16GB RAM)
   ```

2. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd Lawyeragent
   
   # Deploy with cloud configuration
   docker-compose -f docker-compose.yml -f docker-compose.cloud.yml up -d
   ```

4. **Configure Security Groups**
   - Allow HTTP (80) and HTTPS (443)
   - Allow SSH (22) for management
   - Restrict access to specific IP ranges

### Azure Deployment

1. **Create Azure Container Instance**
   ```bash
   # Create resource group
   az group create --name lawyeragent-rg --location westeurope
   
   # Deploy container
   az container create \
     --resource-group lawyeragent-rg \
     --name lawyeragent \
     --image lawyeragent:latest \
     --ports 5000 11434 \
     --dns-name-label lawyeragent \
     --cpu 2 \
     --memory 8
   ```

2. **Configure Networking**
   ```bash
   # Create virtual network
   az network vnet create \
     --resource-group lawyeragent-rg \
     --name lawyeragent-vnet \
     --subnet-name default
   ```

### Google Cloud Deployment

1. **Create GKE Cluster**
   ```bash
   # Create cluster
   gcloud container clusters create lawyeragent-cluster \
     --zone us-central1-a \
     --num-nodes 3 \
     --machine-type e2-standard-4
   ```

2. **Deploy Application**
   ```bash
   # Apply Kubernetes manifests
   kubectl apply -f k8s/
   ```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] SSL certificates obtained
- [ ] Firewall rules configured
- [ ] User access controls defined

### Production Configuration

1. **Environment Variables**
   ```bash
   # .env.production
   SECURITY_ENABLED=true
   ENABLE_AUDIT_LOGGING=true
   LOG_LEVEL=INFO
   OLLAMA_HOST=0.0.0.0
   OLLAMA_ORIGINS=*
   DATABASE_URL=postgresql://user:pass@host:5432/lawyeragent
   REDIS_URL=redis://host:6379
   ```

2. **SSL Configuration**
   ```nginx
   # nginx.conf
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://lawyeragent:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Deploy Production Stack**
   ```bash
   # Deploy with production configuration
   docker-compose -f docker-compose.yml \
     -f docker-compose.prod.yml \
     -f docker-compose.monitoring.yml \
     up -d
   ```

### Backup Strategy

1. **Database Backups**
   ```bash
   # Create backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   docker exec lawyeragent-postgres pg_dump -U lawyeragent > backup_$DATE.sql
   ```

2. **Document Backups**
   ```bash
   # Backup source documents
   tar -czf documents_backup_$DATE.tar.gz source_documents/
   ```

3. **Configuration Backups**
   ```bash
   # Backup configuration files
   tar -czf config_backup_$DATE.tar.gz config/ security/ custom_templates/
   ```

## Monitoring Setup

### Grafana Dashboard

1. **Access Grafana**
   - URL: http://localhost:3000
   - Username: admin
   - Password: admin (change in production)

2. **Import Dashboards**
   - System Health Dashboard
   - Performance Metrics Dashboard
   - User Activity Dashboard
   - Security Alerts Dashboard

3. **Configure Alerts**
   ```yaml
   # grafana/alerts.yml
   alerts:
     - name: "High CPU Usage"
       condition: "cpu_usage > 80"
       duration: "5m"
       severity: "warning"
   ```

### Prometheus Configuration

1. **Configure Targets**
   ```yaml
   # prometheus.yml
   scrape_configs:
     - job_name: 'lawyeragent'
       static_configs:
         - targets: ['lawyeragent:5000']
       metrics_path: '/metrics'
   ```

2. **Set Up Recording Rules**
   ```yaml
   # recording_rules.yml
   groups:
     - name: lawyeragent
       rules:
         - record: response_time_avg
           expr: avg(response_time_seconds)
   ```

### Alert Management

1. **Configure Alert Channels**
   ```yaml
   # alertmanager.yml
   route:
     group_by: ['alertname']
     group_wait: 10s
     group_interval: 10s
     repeat_interval: 1h
     receiver: 'web.hook'
   receivers:
     - name: 'web.hook'
       webhook_configs:
         - url: 'http://127.0.0.1:5001/'
   ```

## User Testing Setup

### Initialize Testing Framework

1. **Set Up Feedback System**
   ```bash
   python user_feedback_system.py --init
   ```

2. **Configure Test Scenarios**
   ```bash
   python user_testing_scenarios.py --setup
   ```

3. **Start Monitoring**
   ```bash
   python monitoring/production_monitor.py --start
   ```

### User Testing Process

1. **Create Test Users**
   ```python
   from user_feedback_system import UserFeedbackSystem, UserType
   
   feedback_system = UserFeedbackSystem()
   
   # Create test user profiles
   solo_lawyer = feedback_system.create_user_profile(
       UserType.SOLO_LAWYER,
       experience_years=8,
       practice_areas=["family_law"],
       jurisdiction="vlaams"
   )
   ```

2. **Run Test Scenarios**
   ```python
   from user_testing_scenarios import UserTestingFramework
   
   framework = UserTestingFramework(feedback_system)
   results = framework.run_test_suite(UserType.SOLO_LAWYER)
   ```

3. **Collect Feedback**
   ```python
   # Submit feedback
   feedback_id = feedback_system.submit_feedback(
       user_id=solo_lawyer,
       category="usability",
       sentiment="positive",
       title="Easy to use interface",
       description="The interface is intuitive and responsive."
   )
   ```

### Analytics and Reporting

1. **Generate Test Reports**
   ```bash
   python user_testing_scenarios.py --report
   ```

2. **View Feedback Analytics**
   ```python
   analytics = feedback_system.get_feedback_analytics()
   print(json.dumps(analytics, indent=2))
   ```

## Troubleshooting

### Common Issues

1. **Ollama Connection Issues**
   ```bash
   # Check Ollama status
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   sudo systemctl restart ollama
   ```

2. **ChromaDB Issues**
   ```bash
   # Check ChromaDB directory
   ls -la chroma_db/
   
   # Recreate vector store
   rm -rf chroma_db/
   python ingest.py
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Increase swap space
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

4. **Docker Issues**
   ```bash
   # Check container status
   docker ps -a
   
   # View container logs
   docker logs lawyeragent
   
   # Restart containers
   docker-compose restart
   ```

### Performance Optimization

1. **System Tuning**
   ```bash
   # Increase file descriptors
   echo "* soft nofile 65536" >> /etc/security/limits.conf
   echo "* hard nofile 65536" >> /etc/security/limits.conf
   ```

2. **Database Optimization**
   ```sql
   -- Optimize SQLite database
   VACUUM;
   ANALYZE;
   ```

3. **Memory Optimization**
   ```bash
   # Configure Ollama memory usage
   export OLLAMA_HOST=0.0.0.0
   export OLLAMA_ORIGINS=*
   ```

## Security Considerations

### Data Protection

1. **Encryption at Rest**
   - All sensitive documents are encrypted using AES-256-GCM
   - Encryption keys are stored securely
   - Regular key rotation is recommended

2. **Access Control**
   - Implement role-based access control
   - Use strong authentication mechanisms
   - Regular access reviews

3. **Audit Logging**
   - All system activities are logged
   - Logs are tamper-evident
   - Regular log analysis

### Network Security

1. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

2. **SSL/TLS Configuration**
   - Use strong cipher suites
   - Regular certificate renewal
   - HSTS implementation

3. **VPN Access**
   - Implement VPN for remote access
   - Use certificate-based authentication
   - Regular VPN audits

### Compliance

1. **GDPR Compliance**
   - Data minimization
   - Right to be forgotten
   - Data portability
   - Privacy by design

2. **Belgian Privacy Law**
   - Local data residency
   - Orde van Vlaamse Balies compliance
   - Client confidentiality

3. **Regular Audits**
   - Security assessments
   - Compliance reviews
   - Penetration testing

## Support and Maintenance

### Regular Maintenance

1. **System Updates**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade
   
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   ```

2. **Database Maintenance**
   ```bash
   # Backup and optimize
   python -c "from database import backup_database; backup_database()"
   ```

3. **Log Rotation**
   ```bash
   # Configure logrotate
   sudo logrotate /etc/logrotate.d/lawyeragent
   ```

### Support Resources

- **Documentation**: README.md, API documentation
- **Issues**: GitHub issues tracker
- **Community**: User forums and discussions
- **Professional Support**: Available for enterprise deployments

### Emergency Procedures

1. **System Recovery**
   ```bash
   # Restore from backup
   python -c "from database import restore_database; restore_database('backup_file.sql')"
   ```

2. **Incident Response**
   - Document the incident
   - Contain the threat
   - Eradicate the cause
   - Recover systems
   - Lessons learned

---

This deployment guide provides comprehensive instructions for deploying LawyerAgent in various environments. For additional support or questions, please refer to the project documentation or contact the development team. 