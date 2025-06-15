# Deployment Guide

## Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 2. Install Dependencies
```bash
# Using pip
pip install -e .

# Or using Make
make install
```

### 3. Run the System
```bash
# Complete system
make run

# Web interface only
make web

# Using Docker
docker-compose up -d
```

## Required API Keys

### OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Add to `.env` as `OPENAI_API_KEY=your_key_here`

### SerpAPI Key
1. Visit https://serpapi.com/dashboard
2. Copy your API key
3. Add to `.env` as `SERPAPI_API_KEY=your_key_here`

### LinkedIn Access Token (Optional)
1. Create LinkedIn App at https://www.linkedin.com/developers/
2. Generate access token with posting permissions
3. Add to `.env` as `LINKEDIN_ACCESS_TOKEN=your_token_here`

## Local Development

```bash
# Setup development environment
make setup

# Run tests
make test

# View logs
make logs

# Clean temporary files
make clean
```

## Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Scale if needed
docker-compose up -d --scale multi-agent-content-system=2
```

## Production Deployment

### Server Requirements
- Python 3.11+
- 512MB+ RAM
- 1GB+ disk space
- Internet connectivity for API calls

### Environment Variables
```bash
export FLASK_ENV=production
export PORT=5000
export LOG_LEVEL=INFO
```

### Process Management
Use systemd, supervisor, or PM2 to manage the process:

```bash
# Example systemd service
sudo systemctl enable multi-agent-content
sudo systemctl start multi-agent-content
```

### Health Monitoring
- Health check endpoint: `/api/status`
- Logs location: `logs/system.log`
- Metrics available at dashboard

## Troubleshooting

### Common Issues

**API Key Errors**
- Verify keys in `.env` file
- Check API quotas and billing
- Test with minimal requests

**Port Conflicts**
- Change PORT in `.env`
- Kill existing processes on port 5000

**Permission Errors**
- Ensure write access to `logs/` and `data/` directories
- Check file permissions for `.env`

**Import Errors**
- Reinstall dependencies: `pip install -e .`
- Check Python version compatibility

### Support Commands
```bash
# Check system status
curl http://localhost:5000/api/status

# Test API connectivity
python -c "from utils.config import get_config; get_config().validate()"

# View recent logs
tail -f logs/system.log
```