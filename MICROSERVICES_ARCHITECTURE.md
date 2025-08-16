# Legal Assistant AI Platform - Microservices Architecture

## Overview

The Legal Assistant AI Platform has been refactored from a monolithic architecture to a microservices-based architecture. This document provides a comprehensive overview of the new architecture, its components, and how they interact.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Layer                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Web UI    │  │   Mobile    │  │   API       │            │
│  │             │  │   App       │  │   Clients   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Nginx Reverse Proxy                        │    │
│  │  • Load Balancing                                       │    │
│  │  • Rate Limiting                                        │    │
│  │  • SSL Termination                                      │    │
│  │  • Security Headers                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Microservices Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Security  │  │  Document   │  │   Query     │            │
│  │   Service   │  │ Processing  │  │ Processing  │            │
│  │   (8001)    │  │  Service    │  │  Service    │            │
│  │             │  │   (8002)    │  │   (8003)    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                 │                 │                  │
│         └─────────────────┼─────────────────┘                  │
│                           │                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Web Interface Service                      │    │
│  │                    (8000)                               │    │
│  │  • API Gateway                                         │    │
│  │  • User Interface                                      │    │
│  │  • Service Orchestration                               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ PostgreSQL  │  │    Redis    │  │   Ollama    │            │
│  │  Database   │  │    Cache    │  │     LLM     │            │
│  │   (5432)    │  │   (6379)    │  │   (11434)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Layer                             │
│  ┌─────────────┐  ┌─────────────┐                              │
│  │ Prometheus  │  │   Grafana   │                              │
│  │  (9090)     │  │   (3000)    │                              │
│  └─────────────┘  └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

## Service Descriptions

### 1. Security Service (Port 8001)

**Purpose**: Handles all authentication, authorization, and security operations.

**Key Features**:
- User authentication and session management
- JWT token generation and validation
- Password hashing and verification
- Role-based access control (RBAC)
- Audit logging
- Brute force protection
- Account lockout mechanisms

**API Endpoints**:
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `POST /auth/change-password` - Password change
- `GET /auth/me` - Get current user info
- `GET /users` - List users (admin only)
- `GET /audit/log` - Get audit log (admin only)

**Dependencies**:
- PostgreSQL (users, sessions, audit_events tables)
- Redis (session caching, rate limiting)

### 2. Document Processing Service (Port 8002)

**Purpose**: Handles document ingestion, processing, and storage.

**Key Features**:
- Document upload and validation
- Text extraction from various formats (PDF, DOCX, TXT)
- Document metadata extraction
- Vector embedding generation
- Document storage and indexing
- Processing status tracking
- Background job processing

**API Endpoints**:
- `POST /documents/upload` - Upload document
- `GET /documents/{id}/status` - Get processing status
- `GET /documents/{id}` - Get document details
- `GET /documents` - List documents
- `DELETE /documents/{id}` - Delete document
- `GET /statistics` - Get processing statistics

**Dependencies**:
- PostgreSQL (documents table)
- ChromaDB (vector storage)
- Ollama (LLM for processing)
- Redis (job queue)

### 3. Query Processing Service (Port 8003)

**Purpose**: Handles natural language queries and RAG operations.

**Key Features**:
- Natural language query processing
- Vector similarity search
- RAG (Retrieval-Augmented Generation)
- Query history and caching
- Response generation with sources
- Query analytics and statistics

**API Endpoints**:
- `POST /query` - Process query
- `GET /queries/history` - Get query history
- `GET /queries/statistics` - Get query statistics
- `GET /queries/search` - Search query history

**Dependencies**:
- PostgreSQL (queries table)
- ChromaDB (vector search)
- Ollama (LLM for generation)
- Redis (query caching)

### 4. Web Interface Service (Port 8000)

**Purpose**: Provides the user interface and API gateway functionality.

**Key Features**:
- Modern web interface
- API gateway and routing
- Service orchestration
- User session management
- Real-time updates
- Responsive design

**API Endpoints**:
- `GET /` - Main application page
- `POST /api/auth/login` - Login proxy
- `POST /api/query` - Query proxy
- `POST /api/documents/upload` - Upload proxy

**Dependencies**:
- All other microservices
- Redis (session storage)

## Shared Components

### Shared Library (`shared/`)

**Purpose**: Common utilities, models, and configurations used across all services.

**Components**:
- **Models** (`shared/models.py`): Data structures and enums
- **Configuration** (`shared/config.py`): Configuration management
- **Utilities** (`shared/utils.py`): Common utility functions

**Key Features**:
- Standardized data models
- Configuration validation
- Security utilities
- Logging setup
- Input validation and sanitization

## Infrastructure Components

### PostgreSQL Database

**Purpose**: Primary data store for all services.

**Tables**:
- `users` - User accounts and authentication
- `sessions` - User sessions and tokens
- `documents` - Document metadata and status
- `queries` - Query history and results
- `audit_events` - Security audit logs

**Features**:
- ACID compliance
- JSONB support for flexible data
- Full-text search capabilities
- Automatic indexing
- Backup and recovery

### Redis Cache

**Purpose**: High-performance caching and session storage.

**Use Cases**:
- Session caching
- Rate limiting
- Job queues
- Query result caching
- Temporary data storage

### Ollama LLM

**Purpose**: Local large language model for AI operations.

**Features**:
- Offline operation
- Multiple model support
- Custom model training
- REST API interface

## Security Architecture

### Authentication Flow

1. **Login Request**: Client sends credentials to Security Service
2. **Validation**: Security Service validates credentials against database
3. **Token Generation**: JWT token generated with user claims
4. **Session Creation**: Session stored in database and Redis
5. **Response**: Token returned to client

### Authorization Flow

1. **Request**: Client includes JWT token in request header
2. **Token Validation**: Service validates token with Security Service
3. **Permission Check**: Service checks user permissions for requested action
4. **Access Control**: Request allowed/denied based on permissions

### Security Features

- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: bcrypt with high cost factor
- **Rate Limiting**: Per-endpoint and per-user limits
- **Input Validation**: Comprehensive sanitization
- **Audit Logging**: All security events logged
- **CORS Protection**: Cross-origin request control
- **Security Headers**: XSS, CSRF, and other protections

## Deployment Architecture

### Docker Compose Setup

The platform uses Docker Compose for orchestration with the following services:

```yaml
services:
  security-service:           # Port 8001
  document-processing-service: # Port 8002
  query-processing-service:    # Port 8003
  web-interface-service:      # Port 8000
  postgres:                   # Port 5432
  redis:                      # Port 6379
  ollama:                     # Port 11434
  nginx:                      # Port 80/443
  prometheus:                 # Port 9090
  grafana:                    # Port 3000
```

### Network Architecture

- **Bridge Network**: All services communicate via Docker bridge network
- **Port Binding**: Services bound to localhost for security
- **Service Discovery**: Services discover each other by container name
- **Load Balancing**: Nginx provides load balancing and routing

## Monitoring and Observability

### Prometheus

**Purpose**: Metrics collection and storage.

**Metrics Collected**:
- Service health and availability
- Request rates and latencies
- Error rates and types
- Resource utilization
- Custom business metrics

### Grafana

**Purpose**: Metrics visualization and alerting.

**Dashboards**:
- Service overview dashboard
- Performance metrics
- Error tracking
- User activity
- System resources

## Development Workflow

### Local Development

1. **Setup Environment**: Run `python setup_security.py`
2. **Start Services**: Run `./deploy-microservices.sh`
3. **Access Services**: Use provided URLs and credentials
4. **Monitor**: Access Prometheus and Grafana dashboards

### Service Development

1. **Create Service**: Add new service to `services/` directory
2. **Add Dockerfile**: Create service-specific Dockerfile
3. **Update Compose**: Add service to `docker-compose.microservices.yml`
4. **Update Nginx**: Add routing rules to `nginx/nginx.conf`
5. **Test**: Use health check endpoints for validation

## Benefits of Microservices Architecture

### Scalability
- **Horizontal Scaling**: Each service can be scaled independently
- **Resource Optimization**: Services use only required resources
- **Load Distribution**: Traffic distributed across multiple instances

### Maintainability
- **Separation of Concerns**: Each service has a single responsibility
- **Independent Development**: Teams can work on different services
- **Technology Diversity**: Different services can use different technologies

### Reliability
- **Fault Isolation**: Service failures don't affect entire system
- **Graceful Degradation**: System continues operating with partial failures
- **Easy Rollbacks**: Individual services can be rolled back

### Security
- **Isolated Security Contexts**: Each service has its own security boundary
- **Defense in Depth**: Multiple layers of security controls
- **Audit Trail**: Comprehensive logging across all services

## Migration from Monolithic Architecture

### Completed Changes

1. **Service Separation**: Monolithic app split into 4 microservices
2. **Database Schema**: PostgreSQL schema created for all services
3. **API Gateway**: Nginx reverse proxy implemented
4. **Containerization**: All services containerized with Docker
5. **Monitoring**: Prometheus and Grafana monitoring stack
6. **Security**: Enhanced security with isolated contexts

### Benefits Achieved

- **Improved Performance**: Services can be optimized independently
- **Better Security**: Isolated security contexts and enhanced controls
- **Easier Maintenance**: Smaller, focused codebases
- **Enhanced Monitoring**: Comprehensive observability
- **Scalability**: Independent scaling of services

## Next Steps

### Short Term (Next 2 Weeks)
1. **Service Integration**: Complete integration between services
2. **Database Migration**: Migrate existing data to new schema
3. **Testing**: Comprehensive testing of all services
4. **Documentation**: Complete API documentation

### Medium Term (Next Month)
1. **Performance Optimization**: Optimize service performance
2. **Advanced Monitoring**: Implement custom metrics and alerts
3. **Security Hardening**: Additional security measures
4. **CI/CD Pipeline**: Automated deployment pipeline

### Long Term (Next Quarter)
1. **Kubernetes Migration**: Move to Kubernetes for production
2. **Service Mesh**: Implement Istio for advanced networking
3. **Multi-Region**: Deploy across multiple regions
4. **Advanced Features**: Implement advanced AI features

## Conclusion

The microservices architecture provides a robust, scalable, and maintainable foundation for the Legal Assistant AI Platform. The separation of concerns, enhanced security, and improved monitoring capabilities position the platform for future growth and development.

The architecture maintains the core functionality of the original monolithic application while providing significant improvements in scalability, security, and maintainability. The modular design allows for independent development and deployment of services, enabling faster iteration and better resource utilization. 