"""
Docker setup and deployment scripts for PediAssist
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class DockerManager:
    """Manages Docker setup and deployment for PediAssist"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.docker_dir = self.project_root / "docker"
        self.configs_dir = self.docker_dir / "configs"
        self.scripts_dir = self.docker_dir / "scripts"
        
    def create_docker_files(self):
        """Create Docker configuration files"""
        self._create_dockerfile()
        self._create_docker_compose()
        self._create_nginx_config()
        self._create_environment_files()
        self._create_deployment_scripts()
        
    def _create_dockerfile(self):
        """Create main Dockerfile"""
        dockerfile_content = '''# PediAssist Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    git \\
    sqlite3 \\
    nginx \\
    supervisor \\
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config /app/cache \\
    && chown -R appuser:appuser /app

# Copy configuration files
COPY docker/configs/nginx.conf /etc/nginx/nginx.conf
COPY docker/configs/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create startup script
COPY docker/scripts/start.sh /start.sh
RUN chmod +x /start.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["/start.sh"]
'''
        
        dockerfile_path = self.project_root / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
        logger.info("Created Dockerfile", path=str(dockerfile_path))
    
    def _create_docker_compose(self):
        """Create docker-compose configuration"""
        compose_content = '''version: '3.8'

services:
  # Main PediAssist application
  pediassist:
    build: .
    container_name: pediassist-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PEDIASIST_ENV=production
      - PEDIASIST_DB_PATH=/app/data/pediassist.db
      - PEDIASIST_LOG_LEVEL=INFO
      - PEDIASIST_ENCRYPTION_KEY=${PEDIASIST_ENCRYPTION_KEY}
      - PEDIASIST_JWT_SECRET=${PEDIASIST_JWT_SECRET}
      - PEDIASIST_LICENSE_KEY=${PEDIASIST_LICENSE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
    volumes:
      - pediassist_data:/app/data
      - pediassist_logs:/app/logs
      - pediassist_cache:/app/cache
    depends_on:
      - redis
      - postgres
    networks:
      - pediassist_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis for caching and session management
  redis:
    image: redis:7-alpine
    container_name: pediassist-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - pediassist_network
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # PostgreSQL for production database
  postgres:
    image: postgres:15-alpine
    container_name: pediassist-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=pediassist
      - POSTGRES_USER=pediassist
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - pediassist_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pediassist -d pediassist"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: pediassist-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/configs/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/configs/ssl:/etc/nginx/ssl
      - nginx_logs:/var/log/nginx
    depends_on:
      - pediassist
    networks:
      - pediassist_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: pediassist-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./docker/configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - pediassist_network

  # Grafana for monitoring dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: pediassist-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/configs/grafana:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - pediassist_network

volumes:
  pediassist_data:
  pediassist_logs:
  pediassist_cache:
  redis_data:
  postgres_data:
  nginx_logs:
  prometheus_data:
  grafana_data:

networks:
  pediassist_network:
    driver: bridge
'''
        
        compose_path = self.project_root / "docker-compose.yml"
        compose_path.write_text(compose_content)
        logger.info("Created docker-compose.yml", path=str(compose_path))
    
    def _create_nginx_config(self):
        """Create Nginx configuration"""
        nginx_config = '''user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Upstream configuration
    upstream pediassist {
        server pediassist:8000;
    }
    
    # HTTP server
    server {
        listen 80;
        server_name _;
        
        # Redirect to HTTPS in production
        # return 301 https://$server_name$request_uri;
        
        location / {
            proxy_pass http://pediassist;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://pediassist/health;
        }
        
        # API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://pediassist;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Auth endpoints rate limiting
        location /auth/ {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://pediassist;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Static files
        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # HTTPS server (uncomment and configure for production)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    #     ssl_prefer_server_ciphers off;
    #     
    #     location / {
    #         proxy_pass http://pediassist;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #         proxy_set_header X-Forwarded-Proto $scheme;
    #     }
    # }
}
'''
        
        # Create configs directory
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        
        nginx_path = self.configs_dir / "nginx.conf"
        nginx_path.write_text(nginx_config)
        logger.info("Created nginx.conf", path=str(nginx_path))
    
    def _create_environment_files(self):
        """Create environment configuration files"""
        # Production environment file
        env_production = '''# PediAssist Production Environment Configuration
PEDIASIST_ENV=production
PEDIASIST_LOG_LEVEL=INFO
PEDIASIST_DB_PATH=/app/data/pediassist.db

# Security Keys (Generate secure keys for production)
PEDIASIST_ENCRYPTION_KEY=your-secure-encryption-key-here
PEDIASIST_JWT_SECRET=your-secure-jwt-secret-here
PEDIASIST_LICENSE_KEY=your-license-key-here

# Database Configuration
POSTGRES_PASSWORD=your-secure-postgres-password-here

# LLM Provider API Keys (BYOK Model)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint-here
GOOGLE_API_KEY=your-google-api-key-here
OLLAMA_BASE_URL=http://localhost:11434

# Monitoring
GRAFANA_PASSWORD=your-secure-grafana-password-here

# Rate Limiting
PEDIASIST_API_RATE_LIMIT=100
PEDIASIST_MAX_LOGIN_ATTEMPTS=5
PEDIASIST_SESSION_TIMEOUT=60
'''
        
        # Development environment file
        env_development = '''# PediAssist Development Environment Configuration
PEDIASIST_ENV=development
PEDIASIST_LOG_LEVEL=DEBUG
PEDIASIST_DB_PATH=./data/pediassist.db

# Security Keys (Use simple keys for development only)
PEDIASIST_ENCRYPTION_KEY=dev-encryption-key
PEDIASIST_JWT_SECRET=dev-jwt-secret
PEDIASIST_LICENSE_KEY=PA-BASIC-0000-0000-0000-0000

# Database Configuration (SQLite for development)
POSTGRES_PASSWORD=dev-postgres-password

# LLM Provider API Keys (Optional for development)
# OPENAI_API_KEY=your-openai-api-key-here
# ANTHROPIC_API_KEY=your-anthropic-api-key-here
# AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
# GOOGLE_API_KEY=your-google-api-key-here
OLLAMA_BASE_URL=http://localhost:11434

# Monitoring
GRAFANA_PASSWORD=dev-grafana-password

# Rate Limiting
PEDIASIST_API_RATE_LIMIT=1000
PEDIASIST_MAX_LOGIN_ATTEMPTS=10
PEDIASIST_SESSION_TIMEOUT=120
'''
        
        env_prod_path = self.project_root / ".env.production"
        env_dev_path = self.project_root / ".env.development"
        
        env_prod_path.write_text(env_production)
        env_dev_path.write_text(env_development)
        
        logger.info("Created environment files", paths=[str(env_prod_path), str(env_dev_path)])
    
    def _create_deployment_scripts(self):
        """Create deployment and management scripts"""
        # Start script
        start_script = '''#!/bin/bash
# PediAssist Start Script

set -e

echo "Starting PediAssist..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f .env.development ]; then
    export $(cat .env.development | grep -v '^#' | xargs)
fi

# Create necessary directories
mkdir -p data logs cache

# Start services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check health
echo "Checking service health..."
docker-compose ps

echo "PediAssist is starting up!"
echo "Application will be available at: http://localhost:8000"
echo "Grafana dashboard: http://localhost:3000"
echo "Prometheus metrics: http://localhost:9090"
echo ""
echo "Use 'docker-compose logs -f pediassist' to view application logs"
echo "Use 'docker-compose down' to stop all services"
'''
        
        # Stop script
        stop_script = '''#!/bin/bash
# PediAssist Stop Script

echo "Stopping PediAssist..."
docker-compose down

echo "PediAssist stopped successfully!"
'''
        
        # Update script
        update_script = '''#!/bin/bash
# PediAssist Update Script

echo "Updating PediAssist..."

# Pull latest code
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "PediAssist updated successfully!"
'''
        
        # Backup script
        backup_script = '''#!/bin/bash
# PediAssist Backup Script

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in $BACKUP_DIR..."

# Backup database
echo "Backing up database..."
docker-compose exec postgres pg_dump -U pediassist pediassist > "$BACKUP_DIR/database.sql"

# Backup application data
echo "Backing up application data..."
docker run --rm -v pediassist_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/data.tar.gz -C /data .

# Backup configuration
echo "Backing up configuration..."
cp -r docker "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"
cp Dockerfile "$BACKUP_DIR/"

# Backup environment files
cp .env.* "$BACKUP_DIR/" 2>/dev/null || true

echo "Backup completed successfully!"
echo "Backup location: $BACKUP_DIR"
'''
        
        # Create scripts directory
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Write scripts
        scripts = {
            "start.sh": start_script,
            "stop.sh": stop_script,
            "update.sh": update_script,
            "backup.sh": backup_script
        }
        
        for script_name, content in scripts.items():
            script_path = self.scripts_dir / script_name
            script_path.write_text(content)
            script_path.chmod(0o755)  # Make executable
            logger.info("Created script", script=script_name, path=str(script_path))
    
    def create_monitoring_config(self):
        """Create monitoring configuration files"""
        # Prometheus configuration
        prometheus_config = '''global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'pediassist'
    static_configs:
      - targets: ['pediassist:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
'''
        
        # Grafana dashboard configuration
        grafana_dashboard = '''{
  "dashboard": {
    "id": null,
    "title": "PediAssist Monitoring",
    "tags": ["pediassist"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Application Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(pediassist_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(pediassist_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(pediassist_errors_total[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pediassist_db_connections_active",
            "legendFormat": "Active connections"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}'''
        
        # Create configs directory
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        
        # Write monitoring configs
        prometheus_path = self.configs_dir / "prometheus.yml"
        grafana_dashboard_path = self.configs_dir / "grafana-dashboard.json"
        
        prometheus_path.write_text(prometheus_config)
        grafana_dashboard_path.write_text(grafana_dashboard)
        
        logger.info("Created monitoring configurations", 
                   prometheus=str(prometheus_path),
                   grafana_dashboard=str(grafana_dashboard_path))
    
    def create_ssl_certificates(self):
        """Create SSL certificates for HTTPS"""
        ssl_dir = self.configs_dir / "ssl"
        ssl_dir.mkdir(exist_ok=True)
        
        # Generate self-signed certificate for development
        ssl_script = '''#!/bin/bash
# Generate SSL certificates for development

CERT_DIR="docker/configs/ssl"
mkdir -p "$CERT_DIR"

echo "Generating SSL certificates..."

# Generate private key
openssl genrsa -out "$CERT_DIR/key.pem" 2048

# Generate certificate signing request
openssl req -new -key "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.csr" -subj "/C=US/ST=State/L=City/O=PediAssist/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in "$CERT_DIR/cert.csr" -signkey "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem"

# Clean up
rm "$CERT_DIR/cert.csr"

echo "SSL certificates generated successfully!"
echo "Certificate: $CERT_DIR/cert.pem"
echo "Private key: $CERT_DIR/key.pem"
echo ""
echo "WARNING: These are self-signed certificates for development only!"
echo "For production, use proper SSL certificates from a Certificate Authority."
'''
        
        ssl_script_path = self.scripts_dir / "generate-ssl.sh"
        ssl_script_path.write_text(ssl_script)
        ssl_script_path.chmod(0o755)
        
        logger.info("Created SSL generation script", path=str(ssl_script_path))
    
    def create_kubernetes_manifests(self):
        """Create Kubernetes deployment manifests"""
        k8s_dir = self.docker_dir / "kubernetes"
        k8s_dir.mkdir(parents=True, exist_ok=True)
        
        # Deployment manifest
        deployment_manifest = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: pediassist
  namespace: pediassist
  labels:
    app: pediassist
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pediassist
  template:
    metadata:
      labels:
        app: pediassist
    spec:
      containers:
      - name: pediassist
        image: pediassist:latest
        ports:
        - containerPort: 8000
        env:
        - name: PEDIASIST_ENV
          value: "production"
        - name: PEDIASIST_DB_PATH
          value: "/app/data/pediassist.db"
        - name: PEDIASIST_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: pediassist-secrets
              key: encryption-key
        - name: PEDIASIST_JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: pediassist-secrets
              key: jwt-secret
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: logs-volume
          mountPath: /app/logs
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
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
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: pediassist-data
      - name: logs-volume
        persistentVolumeClaim:
          claimName: pediassist-logs
---
apiVersion: v1
kind: Service
metadata:
  name: pediassist-service
  namespace: pediassist
spec:
  selector:
    app: pediassist
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
'''
        
        deployment_path = k8s_dir / "deployment.yaml"
        deployment_path.write_text(deployment_manifest)
        
        logger.info("Created Kubernetes deployment manifest", path=str(deployment_path))
    
    def setup_complete_deployment(self):
        """Set up complete deployment infrastructure"""
        logger.info("Setting up complete deployment infrastructure...")
        
        # Create all Docker files
        self.create_docker_files()
        
        # Create monitoring configuration
        self.create_monitoring_config()
        
        # Create SSL certificates
        self.create_ssl_certificates()
        
        # Create Kubernetes manifests
        self.create_kubernetes_manifests()
        
        # Create deployment documentation
        self.create_deployment_docs()
        
        logger.info("Complete deployment infrastructure created successfully!")
    
    def create_deployment_docs(self):
        """Create deployment documentation"""
        docs_content = '''# PediAssist Deployment Guide

## Quick Start

### Using Docker Compose (Recommended)

1. **Set up environment variables:**
   ```bash
   cp .env.development .env
   # Edit .env with your API keys and configuration
   ```

2. **Start the application:**
   ```bash
   ./docker/scripts/start.sh
   ```

3. **Access the application:**
   - Application: http://localhost:8000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

### Manual Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t pediassist:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \\
     -p 8000:8000 \\
     -v pediassist_data:/app/data \\
     -v pediassist_logs:/app/logs \\
     --name pediassist \\
     pediassist:latest
   ```

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- SSL certificates (for HTTPS)
- API keys for LLM providers (BYOK model)
- Valid PediAssist license

### Security Configuration

1. **Generate secure keys:**
   ```bash
   openssl rand -base64 32 > encryption_key.txt
   openssl rand -base64 32 > jwt_secret.txt
   ```

2. **Set up SSL certificates:**
   ```bash
   ./docker/scripts/generate-ssl.sh
   # For production, replace with proper certificates
   ```

### Monitoring Setup

The deployment includes comprehensive monitoring:

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Health checks**: Application health monitoring

### Scaling

For high availability:

1. **Database scaling:** Use managed PostgreSQL
2. **Application scaling:** Increase replica count
3. **Load balancing:** Use managed load balancers

### Backup and Recovery

1. **Create backup:**
   ```bash
   ./docker/scripts/backup.sh
   ```

2. **Restore from backup:**
   ```bash
   # Restore database
   docker-compose exec -T postgres psql -U pediassist pediassist < backup.sql
   
   # Restore application data
   docker run --rm -v pediassist_data:/data -v ./backup:/backup alpine tar xzf /backup/data.tar.gz -C /data
   ```

## Troubleshooting

### Common Issues

1. **Container won't start:**
   - Check Docker logs: `docker-compose logs pediassist`
   - Verify environment variables
   - Check port availability

2. **Database connection issues:**
   - Ensure PostgreSQL is running
   - Check database credentials
   - Verify network connectivity

3. **LLM provider errors:**
   - Verify API keys in environment
   - Check provider rate limits
   - Review provider documentation

### Performance Tuning

1. **Database optimization:**
   - Use connection pooling
   - Optimize queries
   - Consider read replicas

2. **Application optimization:**
   - Enable caching
   - Optimize LLM calls
   - Use CDN for static assets

3. **Resource allocation:**
   - Adjust container resource limits
   - Monitor resource usage
   - Scale horizontally as needed

## Support

For deployment support:
- Check application logs: `docker-compose logs`
- Monitor metrics in Grafana
- Review security audit logs
- Contact support with license issues
'''
        
        docs_path = self.docker_dir / "README.md"
        docs_path.write_text(docs_content)
        
        logger.info("Created deployment documentation", path=str(docs_path))

# Global Docker manager instance
docker_manager = DockerManager()

def setup_deployment():
    """Set up complete deployment infrastructure"""
    docker_manager.setup_complete_deployment()

def create_docker_files():
    """Create Docker configuration files"""
    docker_manager.create_docker_files()

def create_monitoring_config():
    """Create monitoring configuration"""
    docker_manager.create_monitoring_config()