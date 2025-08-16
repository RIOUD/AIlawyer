#!/bin/bash

# Legal Assistant AI Platform - Microservices Deployment Script
# This script deploys the complete microservices architecture

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to check environment file
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f env.template ]; then
            cp env.template .env
            print_warning "Please edit .env file with your secure values before continuing."
            print_warning "Run: python setup_security.py to configure security settings."
            exit 1
        else
            print_error "env.template not found. Cannot create .env file."
            exit 1
        fi
    fi
    
    # Check for required environment variables
    source .env
    
    required_vars=("SECRET_KEY" "MASTER_PASSWORD" "JWT_SECRET" "ADMIN_PASSWORD")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        print_warning "Please run: python setup_security.py to configure security settings."
        exit 1
    fi
    
    print_success "Environment configuration check passed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p vector_store
    mkdir -p source_documents
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    print_success "Directories created"
}

# Function to build and start services
deploy_services() {
    print_status "Building and starting microservices..."
    
    # Stop any existing containers
    docker-compose -f docker-compose.microservices.yml down --remove-orphans
    
    # Build images
    print_status "Building Docker images..."
    docker-compose -f docker-compose.microservices.yml build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f docker-compose.microservices.yml up -d
    
    print_success "Services deployment completed"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    services=(
        "security-service:8001"
        "document-processing-service:8002"
        "query-processing-service:8003"
        "web-interface-service:8000"
        "postgres:5432"
        "redis:6379"
    )
    
    for service in "${services[@]}"; do
        host=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        print_status "Waiting for $host:$port..."
        
        timeout=60
        while ! nc -z $host $port 2>/dev/null; do
            if [ $timeout -le 0 ]; then
                print_error "Timeout waiting for $host:$port"
                exit 1
            fi
            sleep 1
            timeout=$((timeout - 1))
        done
        
        print_success "$host:$port is ready"
    done
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    services=(
        "http://localhost:8001/health"
        "http://localhost:8002/health"
        "http://localhost:8003/health"
        "http://localhost:8000/health"
    )
    
    for url in "${services[@]}"; do
        print_status "Checking $url..."
        
        if curl -f -s "$url" > /dev/null; then
            print_success "$url is healthy"
        else
            print_error "$url is not responding"
            return 1
        fi
    done
    
    print_success "All services are healthy"
}

# Function to display deployment information
show_deployment_info() {
    print_success "Deployment completed successfully!"
    echo
    echo "=== Service URLs ==="
    echo "Web Interface:     http://localhost:8000"
    echo "Security Service:  http://localhost:8001"
    echo "Document Service:  http://localhost:8002"
    echo "Query Service:     http://localhost:8003"
    echo
    echo "=== Monitoring ==="
    echo "Prometheus:        http://localhost:9090"
    echo "Grafana:           http://localhost:3000 (admin/admin)"
    echo
    echo "=== Database ==="
    echo "PostgreSQL:        localhost:5432"
    echo "Redis:             localhost:6379"
    echo
    echo "=== Default Credentials ==="
    echo "Admin:  admin/admin123"
    echo "User:   user/user123"
    echo
    echo "=== Useful Commands ==="
    echo "View logs:         docker-compose -f docker-compose.microservices.yml logs -f"
    echo "Stop services:     docker-compose -f docker-compose.microservices.yml down"
    echo "Restart services:  docker-compose -f docker-compose.microservices.yml restart"
}

# Main deployment function
main() {
    echo "=========================================="
    echo "Legal Assistant AI Platform - Deployment"
    echo "=========================================="
    echo
    
    check_prerequisites
    check_environment
    create_directories
    deploy_services
    wait_for_services
    check_health
    show_deployment_info
}

# Run main function
main "$@" 