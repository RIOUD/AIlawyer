#!/bin/bash

# LawyerAgent Deployment Script
# Supports local, hybrid, and cloud deployment scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE=${1:-"local"}
ENVIRONMENT=${2:-"development"}
CONFIG_FILE="deployment_config.json"

# Logging
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3 first."
    fi
    
    log "Prerequisites check completed successfully"
}

# Load deployment configuration
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        log "Loading deployment configuration from $CONFIG_FILE"
        source <(jq -r 'to_entries | .[] | "export " + .key + "=\"" + .value + "\""' "$CONFIG_FILE")
    else
        warning "Configuration file $CONFIG_FILE not found, using defaults"
    fi
}

# Deploy local environment
deploy_local() {
    log "Deploying LawyerAgent in local mode..."
    
    # Build and start services
    docker-compose up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 30
    
    # Run health checks
    run_health_checks
    
    log "Local deployment completed successfully"
}

# Deploy hybrid environment
deploy_hybrid() {
    log "Deploying LawyerAgent in hybrid mode..."
    
    # Set hybrid-specific environment variables
    export DEPLOYMENT_MODE="hybrid"
    export CLOUD_ENABLED="true"
    export LOCAL_SECURITY="true"
    
    # Build and start services
    docker-compose -f docker-compose.yml -f docker-compose.hybrid.yml up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 45
    
    # Run health checks
    run_health_checks
    
    log "Hybrid deployment completed successfully"
}

# Deploy cloud environment
deploy_cloud() {
    log "Deploying LawyerAgent in cloud mode..."
    
    # Set cloud-specific environment variables
    export DEPLOYMENT_MODE="cloud"
    export CLOUD_ENABLED="true"
    export LOCAL_SECURITY="false"
    
    # Build and start services
    docker-compose -f docker-compose.yml -f docker-compose.cloud.yml up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 60
    
    # Run health checks
    run_health_checks
    
    log "Cloud deployment completed successfully"
}

# Run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Check main application
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log "✅ Main application is healthy"
    else
        error "❌ Main application health check failed"
    fi
    
    # Check Ollama
    if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        log "✅ Ollama service is healthy"
    else
        error "❌ Ollama service health check failed"
    fi
    
    # Check monitoring
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log "✅ Grafana monitoring is healthy"
    else
        warning "⚠️ Grafana monitoring not accessible"
    fi
    
    # Check Prometheus
    if curl -f http://localhost:9090 > /dev/null 2>&1; then
        log "✅ Prometheus monitoring is healthy"
    else
        warning "⚠️ Prometheus monitoring not accessible"
    fi
}

# Initialize system
initialize_system() {
    log "Initializing LawyerAgent system..."
    
    # Create necessary directories
    mkdir -p source_documents chroma_db security exports custom_templates logs
    
    # Set proper permissions
    chmod 755 source_documents chroma_db security exports custom_templates logs
    
    # Initialize database if needed
    if [ ! -f "legal_assistant.db" ]; then
        log "Initializing database..."
        python3 -c "from database import init_database; init_database()"
    fi
    
    log "System initialization completed"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring infrastructure..."
    
    # Create monitoring configuration
    mkdir -p monitoring/grafana/dashboards monitoring/grafana/datasources
    
    # Create Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'lawyeragent'
    static_configs:
      - targets: ['lawyeragent:5000']
    metrics_path: '/metrics'
    
  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
    metrics_path: '/api/metrics'
EOF
    
    log "Monitoring setup completed"
}

# Main deployment function
main() {
    log "Starting LawyerAgent deployment..."
    log "Deployment type: $DEPLOYMENT_TYPE"
    log "Environment: $ENVIRONMENT"
    
    # Check prerequisites
    check_prerequisites
    
    # Load configuration
    load_config
    
    # Initialize system
    initialize_system
    
    # Setup monitoring
    setup_monitoring
    
    # Deploy based on type
    case $DEPLOYMENT_TYPE in
        "local")
            deploy_local
            ;;
        "hybrid")
            deploy_hybrid
            ;;
        "cloud")
            deploy_cloud
            ;;
        "production")
            deploy_cloud
            ;;
        *)
            error "Invalid deployment type: $DEPLOYMENT_TYPE. Use: local, hybrid, cloud, or production"
            ;;
    esac
    
    # Display deployment information
    log "Deployment completed successfully!"
    log "Access points:"
    log "  - Main Application: http://localhost:5000"
    log "  - Grafana Dashboard: http://localhost:3000 (admin/admin)"
    log "  - Prometheus: http://localhost:9090"
    log "  - Ollama API: http://localhost:11434"
    
    log "Deployment log saved to: $LOG_FILE"
}

# Handle script arguments
case "${1:-}" in
    "stop")
        log "Stopping LawyerAgent services..."
        docker-compose down
        log "Services stopped"
        ;;
    "restart")
        log "Restarting LawyerAgent services..."
        docker-compose restart
        log "Services restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        log "Cleaning up LawyerAgent deployment..."
        docker-compose down -v
        docker system prune -f
        log "Cleanup completed"
        ;;
    *)
        main
        ;;
esac 