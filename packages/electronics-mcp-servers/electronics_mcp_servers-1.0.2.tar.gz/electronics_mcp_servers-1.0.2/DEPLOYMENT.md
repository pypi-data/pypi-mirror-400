# 🚀 Deployment Guide

Comprehensive deployment instructions for Electronics MCP Servers in various environments.

---

## Table of Contents
- [Claude Desktop Integration](#claude-desktop-integration)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [HTTP Transport Setup](#http-transport-setup)
- [Security Configuration](#security-configuration)
- [Monitoring & Logging](#monitoring--logging)

---

## Claude Desktop Integration

### Step-by-Step Setup (Windows)

#### 1. Locate Configuration File
```powershell
# Open config directory
explorer $env:APPDATA\Claude
```

Look for `claude_desktop_config.json` in this folder.

#### 2. Edit Configuration
Add the following to your config file:

```json
{
  "mcpServers": {
    "resistor-decoder": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\projects\\python\\mcp-server",
        "run",
        "servers/resistor_decoder.py"
      ]
    },
    "capacitor-calc": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\projects\\python\\mcp-server",
        "run",
        "servers/capacitor_calculator.py"
      ]
    },
    "gpio-reference": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\projects\\python\\mcp-server",
        "run",
        "servers/gpio_reference.py"
      ]
    }
  }
}
```

**⚠️ Important:** Replace `D:\\projects\\python\\mcp-server` with your actual project path. Use double backslashes `\\` on Windows.

#### 3. Verify Configuration
```powershell
# Validate JSON syntax
python -m json.tool $env:APPDATA\Claude\claude_desktop_config.json
```

If valid, you'll see formatted JSON output. If errors, fix syntax issues.

#### 4. Restart Claude Desktop
1. **Quit Claude Desktop completely** (right-click system tray icon → Quit)
2. Relaunch Claude Desktop
3. Look for hammer icon 🔨 in the interface (indicates MCP tools available)

#### 5. Test Connection
Open a new conversation in Claude Desktop and try:

```
User: "What's the color code for a 10kΩ resistor?"
```

Claude should use the `encode_resistor_value` tool and respond with color bands.

---

### Step-by-Step Setup (macOS)

#### 1. Locate Configuration File
```bash
# Open config directory
open ~/Library/Application\ Support/Claude/
```

#### 2. Edit Configuration
Create or edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resistor-decoder": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/projects/mcp-server",
        "run",
        "servers/resistor_decoder.py"
      ]
    },
    "capacitor-calc": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/projects/mcp-server",
        "run",
        "servers/capacitor_calculator.py"
      ]
    },
    "gpio-reference": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/projects/mcp-server",
        "run",
        "servers/gpio_reference.py"
      ]
    }
  }
}
```

#### 3. Verify and Test
```bash
# Validate JSON
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop
killall "Claude Desktop"
open -a "Claude Desktop"
```

---

### Step-by-Step Setup (Linux)

#### 1. Configuration File Location
```bash
# Create config directory if it doesn't exist
mkdir -p ~/.config/Claude

# Edit configuration
nano ~/.config/Claude/claude_desktop_config.json
```

#### 2. Add Configuration
```json
{
  "mcpServers": {
    "resistor-decoder": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/yourname/projects/mcp-server",
        "run",
        "servers/resistor_decoder.py"
      ]
    },
    "capacitor-calc": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/yourname/projects/mcp-server",
        "run",
        "servers/capacitor_calculator.py"
      ]
    },
    "gpio-reference": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/yourname/projects/mcp-server",
        "run",
        "servers/gpio_reference.py"
      ]
    }
  }
}
```

#### 3. Restart Claude Desktop
```bash
# If using systemd
systemctl --user restart claude-desktop

# Or kill and relaunch manually
pkill -f "claude"
claude-desktop &
```

---

## Docker Deployment

### Single Container

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY servers/ ./servers/
COPY tests/ ./tests/

# Install dependencies
RUN uv sync --no-dev

# Expose port for HTTP transport (optional)
EXPOSE 8000

# Default command (can be overridden)
CMD ["uv", "run", "servers/gpio_reference.py"]
```

**Build and Run:**
```bash
# Build image
docker build -t electronics-mcp:latest .

# Run specific server (stdio transport)
docker run -i electronics-mcp uv run servers/resistor_decoder.py

# Run with HTTP transport
docker run -p 8000:8000 electronics-mcp uv run servers/gpio_reference.py --transport http --port 8000
```

---

### Docker Compose (All Servers)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  resistor-decoder:
    build: .
    container_name: mcp-resistor
    command: uv run servers/resistor_decoder.py --transport http --port 8001
    ports:
      - "8001:8001"
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  capacitor-calc:
    build: .
    container_name: mcp-capacitor
    command: uv run servers/capacitor_calculator.py --transport http --port 8002
    ports:
      - "8002:8002"
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  gpio-reference:
    build: .
    container_name: mcp-gpio
    command: uv run servers/gpio_reference.py --transport http --port 8003
    ports:
      - "8003:8003"
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: NGINX reverse proxy
  nginx:
    image: nginx:alpine
    container_name: mcp-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - resistor-decoder
      - capacitor-calc
      - gpio-reference
    restart: unless-stopped
```

**nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream resistor {
        server resistor-decoder:8001;
    }

    upstream capacitor {
        server capacitor-calc:8002;
    }

    upstream gpio {
        server gpio-reference:8003;
    }

    server {
        listen 80;
        server_name localhost;

        location /resistor/ {
            proxy_pass http://resistor/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /capacitor/ {
            proxy_pass http://capacitor/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /gpio/ {
            proxy_pass http://gpio/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

**Deploy with Docker Compose:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Update and restart
docker-compose build
docker-compose up -d
```

---

## Cloud Deployment

### AWS Lambda (Serverless)

**serverless.yml:**
```yaml
service: electronics-mcp

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 256
  timeout: 30
  environment:
    STAGE: ${opt:stage, 'dev'}

functions:
  resistorDecoder:
    handler: servers/resistor_decoder.lambda_handler
    events:
      - http:
          path: /resistor/{proxy+}
          method: ANY
          cors: true

  capacitorCalc:
    handler: servers/capacitor_calculator.lambda_handler
    events:
      - http:
          path: /capacitor/{proxy+}
          method: ANY
          cors: true

  gpioReference:
    handler: servers/gpio_reference.lambda_handler
    events:
      - http:
          path: /gpio/{proxy+}
          method: ANY
          cors: true

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    layer: true
```

**Lambda handler wrapper:**
```python
# Add to each server file
def lambda_handler(event, context):
    import json
    from mcp.server.fastmcp import FastMCP
    
    # Initialize MCP server
    mcp = FastMCP("Server Name")
    
    # Extract tool name and parameters from event
    body = json.loads(event.get('body', '{}'))
    tool_name = body.get('tool')
    params = body.get('params', {})
    
    # Call appropriate tool function
    result = globals()[tool_name](**params)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'result': result}),
        'headers': {'Content-Type': 'application/json'}
    }
```

**Deploy:**
```bash
# Install Serverless Framework
npm install -g serverless

# Deploy to AWS
serverless deploy --stage prod

# Test function
serverless invoke -f resistorDecoder --data '{"tool": "encode_resistor_value", "params": {"resistance": 10000}}'
```

---

### Google Cloud Run

**Dockerfile (optimized for Cloud Run):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy files
COPY . .

# Install dependencies
RUN uv sync --no-dev

# Use HTTP transport for Cloud Run
ENV PORT=8080
CMD ["uv", "run", "servers/gpio_reference.py", "--transport", "http", "--port", "8080"]
```

**Deploy:**
```bash
# Build and push image
gcloud builds submit --tag gcr.io/your-project/mcp-gpio

# Deploy to Cloud Run
gcloud run deploy mcp-gpio \
  --image gcr.io/your-project/mcp-gpio \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 60s

# Get service URL
gcloud run services describe mcp-gpio --format='value(status.url)'
```

---

### Azure Container Instances

**Deploy with Azure CLI:**
```bash
# Create resource group
az group create --name mcp-servers --location eastus

# Create container instance
az container create \
  --resource-group mcp-servers \
  --name mcp-gpio \
  --image electronics-mcp:latest \
  --registry-login-server yourregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label mcp-gpio \
  --ports 8000 \
  --environment-variables LOG_LEVEL=INFO \
  --command-line "uv run servers/gpio_reference.py --transport http --port 8000"

# Get FQDN
az container show --resource-group mcp-servers --name mcp-gpio --query ipAddress.fqdn
```

---

## HTTP Transport Setup

### Basic HTTP Server

**Start server:**
```bash
# GPIO Reference on port 8003
uv run fastmcp run servers/gpio_reference.py --transport http --port 8003 --host 0.0.0.0

# Resistor Decoder on port 8001
uv run fastmcp run servers/resistor_decoder.py --transport http --port 8001 --host 0.0.0.0

# Capacitor Calc on port 8002
uv run fastmcp run servers/capacitor_calculator.py --transport http --port 8002 --host 0.0.0.0
```

**Claude Desktop HTTP configuration:**
```json
{
  "mcpServers": {
    "gpio-reference-http": {
      "url": "http://localhost:8003/mcp"
    },
    "resistor-decoder-http": {
      "url": "http://localhost:8001/mcp"
    },
    "capacitor-calc-http": {
      "url": "http://localhost:8002/mcp"
    }
  }
}
```

---

### HTTPS with TLS

**Generate self-signed certificate (development):**
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/CN=localhost"
```

**Start with TLS:**
```bash
uv run fastmcp run servers/gpio_reference.py \
  --transport http \
  --port 8003 \
  --ssl-certfile cert.pem \
  --ssl-keyfile key.pem
```

**Production TLS (Let's Encrypt with Certbot):**
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d mcp.yourdomain.com

# Configure server with real cert
uv run fastmcp run servers/gpio_reference.py \
  --transport http \
  --port 8003 \
  --ssl-certfile /etc/letsencrypt/live/mcp.yourdomain.com/fullchain.pem \
  --ssl-keyfile /etc/letsencrypt/live/mcp.yourdomain.com/privkey.pem
```

---

## Security Configuration

### Authentication

**Token-based auth:**
```python
# Add to server initialization
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP(
    "GPIO Reference",
    auth_token=os.getenv("MCP_AUTH_TOKEN", "your-secret-token")
)
```

**Client configuration:**
```json
{
  "mcpServers": {
    "gpio-reference": {
      "url": "https://mcp.yourdomain.com:8003/mcp",
      "headers": {
        "Authorization": "Bearer your-secret-token"
      }
    }
  }
}
```

---

### Rate Limiting

**Add rate limiter:**
```python
from functools import wraps
from collections import defaultdict
import time

# Simple in-memory rate limiter
rate_limit_storage = defaultdict(list)

def rate_limit(max_calls=10, time_window=60):
    """Limit function calls to max_calls per time_window seconds."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_id = "global"  # Use IP or API key in production
            now = time.time()
            
            # Clean old entries
            rate_limit_storage[client_id] = [
                t for t in rate_limit_storage[client_id]
                if t > now - time_window
            ]
            
            # Check limit
            if len(rate_limit_storage[client_id]) >= max_calls:
                raise Exception(
                    f"Rate limit exceeded: {max_calls} calls per {time_window}s"
                )
            
            # Record this call
            rate_limit_storage[client_id].append(now)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Apply to tools
@mcp.tool()
@rate_limit(max_calls=100, time_window=60)
def get_pin_info(board: str, pin_number: int) -> str:
    # ... existing code ...
```

---

### CORS Configuration

**For web-based clients:**
```python
from fastapi.middleware.cors import CORSMiddleware

mcp.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Monitoring & Logging

### Structured Logging

**Add logging to servers:**
```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/mcp/gpio_reference.log')
    ]
)

logger = logging.getLogger(__name__)

# Add to tool functions
@mcp.tool()
def get_pin_info(board: str, pin_number: int) -> str:
    logger.info(f"get_pin_info called: board={board}, pin={pin_number}")
    try:
        result = _get_pin_info_impl(board, pin_number)
        logger.info(f"get_pin_info success: board={board}, pin={pin_number}")
        return result
    except Exception as e:
        logger.error(f"get_pin_info error: board={board}, pin={pin_number}, error={str(e)}")
        raise
```

---

### Prometheus Metrics

**Add metrics endpoint:**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
tool_calls = Counter('mcp_tool_calls_total', 'Total tool invocations', ['tool_name', 'status'])
tool_duration = Histogram('mcp_tool_duration_seconds', 'Tool execution time', ['tool_name'])

# Instrument tools
@mcp.tool()
def get_pin_info(board: str, pin_number: int) -> str:
    with tool_duration.labels(tool_name='get_pin_info').time():
        try:
            result = _get_pin_info_impl(board, pin_number)
            tool_calls.labels(tool_name='get_pin_info', status='success').inc()
            return result
        except Exception as e:
            tool_calls.labels(tool_name='get_pin_info', status='error').inc()
            raise

# Add metrics endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**Scrape config (prometheus.yml):**
```yaml
scrape_configs:
  - job_name: 'mcp-servers'
    static_configs:
      - targets: ['localhost:8001', 'localhost:8002', 'localhost:8003']
```

---

### Health Checks

**Add health endpoint:**
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "server": "GPIO Reference",
        "version": "0.4.0",
        "uptime": time.time() - start_time
    }

@app.get("/ready")
def readiness_check():
    # Check dependencies (e.g., database, cache)
    try:
        # Verify PIN_DATABASE loaded
        assert len(PIN_DATABASE) > 0
        return {"status": "ready"}
    except:
        return {"status": "not ready"}, 503
```

---

## Performance Optimization

### Connection Pooling (HTTP Clients)

```python
import aiohttp

async def main():
    # Create session with connection pooling
    connector = aiohttp.TCPConnector(
        limit=100,              # Total connection limit
        limit_per_host=30,      # Per-host limit
        ttl_dns_cache=300,      # DNS cache TTL
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Make requests
        async with session.post('http://localhost:8003/mcp/get_pin_info', 
                                json={'board': 'ESP32', 'pin_number': 0}) as resp:
            result = await resp.json()
```

---

### Caching

**Add LRU cache for frequently accessed data:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_pin_info_cached(board: str, pin_number: int) -> str:
    """Cached version of get_pin_info."""
    return get_pin_info(board, pin_number)
```

---

## Troubleshooting Deployment

### Check Server Logs
```bash
# Docker
docker logs mcp-gpio

# Systemd
journalctl -u mcp-gpio -f

# Direct
tail -f /var/log/mcp/gpio_reference.log
```

### Test Connectivity
```bash
# Stdio transport
echo '{"method": "tools/list"}' | uv run python servers/gpio_reference.py

# HTTP transport
curl -X POST http://localhost:8003/mcp/get_pin_info \
  -H "Content-Type: application/json" \
  -d '{"board": "ESP32", "pin_number": 0}'
```

### Performance Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Load test
ab -n 1000 -c 10 -T 'application/json' \
  -p request.json \
  http://localhost:8003/mcp/get_pin_info
```

---

**For complete usage examples, see [EXAMPLES.md](EXAMPLES.md)**
**For project documentation, see [README.md](README.md)**
