# PediAssist Deployment Guide

## Quick Start Options

### 🐳 Docker Deployment (Recommended)

#### Local Development:
```bash
# Clone your repository
git clone <your-repo-url>
cd pediassist

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8000/simple
```

#### Production with Docker:
```bash
# Build production image
docker build -t pediassist:latest .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=postgresql://user:pass@host:5432/pediassist \
  -e LICENSE_KEY=your-license-key \
  --name pediassist \
  pediassist:latest
```

### ☁️ Cloud Deployment Options

#### 1. Render (Free Tier Available)
1. Fork this repository to your GitHub
2. Sign up at [render.com](https://render.com)
3. Click "New Web Service"
4. Connect your GitHub repository
5. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m pediassist.web_app`
   - Environment: Add your environment variables
6. Deploy!

#### 2. Railway (Developer Friendly)
1. Fork repository to GitHub
2. Sign up at [railway.app](https://railway.app)
3. Connect GitHub repository
4. Railway automatically detects Python app
5. Add environment variables
6. Deploy with one click

#### 3. DigitalOcean App Platform
1. Create DigitalOcean account
2. Create new App Platform app
3. Connect GitHub repository
4. Configure:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python -m pediassist.web_app`
5. Add database (PostgreSQL recommended)
6. Deploy

## Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Required
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here

# Optional - Database (defaults to SQLite)
DATABASE_URL=sqlite:///./data/pediassist.db
# For PostgreSQL: postgresql://user:password@host:5432/pediassist

# Optional - License
LICENSE_KEY=your-license-key

# Optional - LLM Configuration
LLM_PROVIDER=ollama  # or openai, anthropic, etc.
MODEL=llama2
API_KEY=your-api-key-if-required

# Optional - Security
CORS_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com"]
```

## Production Considerations

### Security
- Change default secret keys
- Use HTTPS in production
- Configure proper CORS settings
- Set up rate limiting
- Use environment-specific configurations

### Database
- Use PostgreSQL for production
- Set up regular backups
- Configure connection pooling
- Monitor database performance

### Monitoring
- Set up application monitoring (e.g., Sentry)
- Configure log aggregation
- Set up health checks
- Monitor resource usage

### Scaling
- Use container orchestration (Kubernetes) for high availability
- Configure auto-scaling rules
- Set up load balancing
- Use CDN for static assets

## API Endpoints

Once deployed, these endpoints will be available:

- `GET /` - System status
- `POST /api/diagnose` - Generate diagnosis
- `POST /api/treatment` - Generate treatment plan
- `POST /api/communicate` - Generate patient communication
- `GET /api/usage` - Usage statistics
- `GET /simple` - Web interface

## Testing Your Deployment

```bash
# Test system status
curl https://your-domain.com/

# Test diagnosis API
curl -X POST https://your-domain.com/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"age": 5, "chief_complaint": "cough and fever"}'

# Test web interface
open https://your-domain.com/simple
```

## Troubleshooting

### Common Issues:
1. **Port already in use**: Change port in docker-compose.yml or use different port
2. **Database connection failed**: Check DATABASE_URL format and credentials
3. **License validation failed**: Verify LICENSE_KEY is correct
4. **Memory issues**: Increase Docker memory limits or use external database

### Getting Help:
- Check application logs: `docker logs pediassist`
- Enable debug mode: Set `ENVIRONMENT=development`
- Review error responses from API endpoints

## Next Steps

1. Choose your deployment platform
2. Set up monitoring and alerts
3. Configure automated backups
4. Set up CI/CD pipeline
5. Monitor usage and performance
6. Scale as needed