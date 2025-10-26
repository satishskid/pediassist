# PediAssist Deployment Guide

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
   docker run -d \
     -p 8000:8000 \
     -v pediassist_data:/app/data \
     -v pediassist_logs:/app/logs \
     --name pediassist \
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
