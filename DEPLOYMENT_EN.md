# Deployment Guide - PDF Tools

This guide walks you through deploying PDF Tools on various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Secrets Configuration](#secrets-configuration)
- [Deploy on Replit](#deploy-on-replit)
- [Deploy on Heroku](#deploy-on-heroku)
- [Deploy on VPS (DigitalOcean, AWS, etc.)](#deploy-on-vps)
- [Deploy with Docker](#deploy-with-docker)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.11 or higher
- OpenRouter account (optional, for AI analysis)
- Git (to clone the project)

## Secrets Configuration

### Required Secrets

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | ✅ Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key | ⚠️ Optional* |
| `ADMIN_SECRET` | Secret for Git updates | ✅ Yes (production) |

*If `OPENROUTER_API_KEY` is not configured, intelligent analysis will be disabled but all other features will continue to work normally.

### Generate a SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Get an OpenRouter Key

1. Create an account on [https://openrouter.ai](https://openrouter.ai)
2. Go to **Settings** > **API Keys**
3. Click **Create Key**
4. Copy the generated key
5. Add credits if necessary (free model available)

### Generate an ADMIN_SECRET

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Deploy on Replit

### Step 1: Import the Project

1. Go to [Replit](https://replit.com)
2. Click **+ Create Repl**
3. Select **Import from GitHub**
4. Paste the repository URL
5. Click **Import from GitHub**

### Step 2: Configure Secrets

1. In your Repl, click the **🔒 Secrets** icon (Tools > Secrets)
2. Add the following secrets:
   ```
   SECRET_KEY = <your-secret-key>
   OPENROUTER_API_KEY = <your-openrouter-key>
   ADMIN_SECRET = <your-admin-secret>
   ```

### Step 3: Verify Configuration

The project is already configured with:
- ✅ `pyproject.toml` with all dependencies
- ✅ Workflow configured for Gunicorn
- ✅ Automatic deployment configuration

### Step 4: Launch the Application

1. Click **Run**
2. The application will be accessible on port 5000
3. Replit will automatically generate a public URL

### Step 5: Publish (Optional)

1. Click **Deploy** in the top right
2. Choose **Autoscale** for a web application
3. Follow instructions to get a custom domain

---

## Deploy on Heroku

### Step 1: Prerequisites

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login
```

### Step 2: Create the Application

```bash
# Create a new app
heroku create pdf-tools-app

# Add Python buildpack
heroku buildpacks:add heroku/python
```

### Step 3: Configure Environment Variables

```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set ADMIN_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set OPENROUTER_API_KEY=<your-key>
```

### Step 4: Create a Procfile

```bash
echo "web: gunicorn --bind 0.0.0.0:\$PORT main:app" > Procfile
```

### Step 5: Deploy

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Step 6: Open the Application

```bash
heroku open
```

---

## Deploy on VPS

### Step 1: Prepare the Server

```bash
# SSH connection
ssh user@your-server-ip

# Update the system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y
```

### Step 2: Clone the Project

```bash
cd /var/www
sudo git clone <your-repo> pdf-tools
cd pdf-tools
```

### Step 3: Create a Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Create a .env file
sudo nano .env
```

Add:
```
SECRET_KEY=<your-secret-key>
ADMIN_SECRET=<your-admin-secret>
OPENROUTER_API_KEY=<your-key>
```

### Step 5: Configure Gunicorn with Systemd

```bash
sudo nano /etc/systemd/system/pdf-tools.service
```

Add:
```ini
[Unit]
Description=PDF Tools Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/pdf-tools
Environment="PATH=/var/www/pdf-tools/venv/bin"
EnvironmentFile=/var/www/pdf-tools/.env
ExecStart=/var/www/pdf-tools/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 main:app

[Install]
WantedBy=multi-user.target
```

### Step 6: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/pdf-tools
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For unlimited uploads
        client_max_body_size 0;
        proxy_request_buffering off;
    }
}
```

### Step 7: Activate and Start

```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/pdf-tools /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start the service
sudo systemctl start pdf-tools
sudo systemctl enable pdf-tools
sudo systemctl status pdf-tools
```

### Step 8: Configure SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Deploy with Docker

### Step 1: Create a Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary folders
RUN mkdir -p instance/uploads tmp

# Expose port
EXPOSE 5000

# Default environment variables
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

# Launch Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "600", "main:app"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_SECRET=${ADMIN_SECRET}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./instance:/app/instance
      - ./tmp:/app/tmp
    restart: unless-stopped
```

### Step 3: Create .env

```bash
SECRET_KEY=<your-secret-key>
ADMIN_SECRET=<your-admin-secret>
OPENROUTER_API_KEY=<your-key>
```

### Step 4: Launch

```bash
docker-compose up -d
```

---

## Environment Variables

### Main Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECRET_KEY` | String | - | Flask secret key (required) |
| `OPENROUTER_API_KEY` | String | - | OpenRouter API key (optional) |
| `ADMIN_SECRET` | String | - | Secret for Git updates (required in production) |

### Optional Variables (Advanced)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FLASK_ENV` | String | production | Flask environment |
| `FLASK_DEBUG` | Boolean | False | Flask debug mode |
| `MAX_WORKERS` | Integer | 10 | Number of workers for parallel download |

---

## Updating the Application

### Via Web Interface (Recommended)

The application has an automatic update feature via the web interface:

1. **Configure ADMIN_SECRET** (required):
   ```bash
   # Generate a secure secret
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Add to your environment variables
   export ADMIN_SECRET="your_generated_secret"
   ```

2. **Use the web interface**:
   - Click the **"Git Update"** button in the navigation
   - Enter the admin secret (ADMIN_SECRET)
   - Confirm the operation
   - The server will automatically execute `git pull`
   - Restart the application if necessary

3. **Security**:
   - ✅ Access protected by admin secret
   - ✅ Logs of all access attempts
   - ✅ Returns 403 for unauthorized access
   - ✅ Ideal for quick production updates

### On VPS (Manual Method)

```bash
cd /var/www/pdf-tools
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart pdf-tools
```

### On Heroku

```bash
git push heroku main
```

### On Docker

```bash
docker-compose down
git pull origin main
docker-compose up -d --build
```

### On Replit

```bash
# Option 1: Web Interface (Recommended)
# Use the "Git Update" button in the navigation

# Option 2: Shell
git pull origin main
# The application will restart automatically
```

---

## Troubleshooting

### Issue: Intelligent analysis doesn't work

**Solution:**
1. Verify that `OPENROUTER_API_KEY` is configured
2. Check credits on your OpenRouter account
3. Check logs: `gunicorn --log-level debug main:app`

### Issue: Upload fails for large files

**Solution:**
1. For Nginx, add `client_max_body_size 0;`
2. Check available disk space
3. MAX_CONTENT_LENGTH limit has been removed from code

### Issue: Slow bulk download

**Solution:**
1. Increase number of workers: modify `max_workers` in `pdf_downloader.py`
2. Check server bandwidth
3. Use a geographically closer server

### Issue: 502 Bad Gateway Error

**Solution:**
1. Verify Gunicorn is running: `systemctl status pdf-tools`
2. Increase Nginx timeout:
   ```nginx
   proxy_read_timeout 600;
   proxy_connect_timeout 600;
   proxy_send_timeout 600;
   ```

### Issue: Insufficient memory

**Solution:**
1. Reduce number of Gunicorn workers
2. Increase server RAM
3. Use Redis/Celery for long tasks (future implementation)

---

## Logs and Monitoring

### View Production Logs

**Systemd (VPS):**
```bash
sudo journalctl -u pdf-tools -f
```

**Docker:**
```bash
docker-compose logs -f web
```

**Heroku:**
```bash
heroku logs --tail
```

---

## Performance and Optimization

### Production Recommendations

1. **Server:** Minimum 2 CPU, 4GB RAM
2. **Gunicorn Workers:** `(2 × CPU) + 1`
3. **Timeout:** 600 seconds minimum
4. **Storage:** SSD recommended
5. **CDN:** For static files (optional)

### Optimal Gunicorn Configuration

```bash
gunicorn \
  --workers 4 \
  --timeout 600 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --bind 0.0.0.0:5000 \
  --reuse-port \
  main:app
```

---

## Security

### Security Checklist

- ✅ Unique and complex SECRET_KEY
- ✅ ADMIN_SECRET configured for Git updates
- ✅ HTTPS enabled (SSL/TLS)
- ✅ Firewall configured
- ✅ Regular updates
- ✅ Logs enabled
- ✅ Regular backups
- ✅ Rate limiting (implement if necessary)

---

## Support

For questions or issues:
- Check the [main documentation](README.md)
- Open an issue on GitHub
- Check the [CHANGELOG](CHANGELOG.md)

---

**Successful deployment!** 🚀 Your PDF Tools platform is now in production.
