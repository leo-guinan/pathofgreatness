#!/bin/bash
# Deployment script for Hetzner Cloud
set -e

echo "🚀 Deploying The Greatness Path to Hetzner"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Update system
echo -e "${GREEN}📦 Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install Docker
echo -e "${GREEN}🐳 Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo -e "${GREEN}📦 Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose
else
    echo "Docker Compose already installed"
fi

# Create app directory
APP_DIR="/app/greatness-path"
echo -e "${GREEN}📁 Creating app directory: ${APP_DIR}${NC}"
mkdir -p ${APP_DIR}

# Check if git repo is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}⚠️  No git repository provided${NC}"
    echo "Usage: ./deploy-hetzner.sh <git-repo-url>"
    echo "Skipping git clone..."
else
    echo -e "${GREEN}📥 Cloning repository...${NC}"
    if [ -d "${APP_DIR}/.git" ]; then
        cd ${APP_DIR}
        git pull
    else
        git clone $1 ${APP_DIR}
        cd ${APP_DIR}
    fi
fi

# Set up environment
echo -e "${GREEN}⚙️  Setting up environment...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Created .env from .env.example${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your OPENROUTER_API_KEY${NC}"
        echo ""
        read -p "Press enter when you've added your API key..."
    else
        echo -e "${RED}❌ No .env.example found!${NC}"
        exit 1
    fi
else
    echo ".env already exists"
fi

# Create data directory
mkdir -p data

# Build and run
echo -e "${GREEN}🏗️  Building Docker image...${NC}"
docker-compose build

echo -e "${GREEN}🚀 Starting application...${NC}"
docker-compose up -d

# Wait for health check
echo -e "${GREEN}⏳ Waiting for application to be healthy...${NC}"
sleep 10

# Check if running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Application is running!${NC}"
    echo ""
    echo "Access your app at:"
    echo "  http://$(hostname -I | awk '{print $1}'):8000"
    echo ""
    echo "Useful commands:"
    echo "  docker-compose logs -f     # View logs"
    echo "  docker-compose ps          # Check status"
    echo "  docker-compose restart     # Restart app"
    echo "  docker-compose down        # Stop app"
    echo ""
else
    echo -e "${RED}❌ Application failed to start${NC}"
    echo "Check logs:"
    docker-compose logs
    exit 1
fi

# Optional: Set up Nginx + SSL
echo ""
read -p "Do you want to set up Nginx + SSL? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}📦 Installing Nginx...${NC}"
    apt-get install -y nginx certbot python3-certbot-nginx

    read -p "Enter your domain name: " DOMAIN

    echo -e "${GREEN}⚙️  Configuring Nginx...${NC}"
    cat > /etc/nginx/sites-available/greatness-path <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    ln -sf /etc/nginx/sites-available/greatness-path /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    nginx -t
    systemctl reload nginx

    echo -e "${GREEN}🔒 Getting SSL certificate...${NC}"
    certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --register-unsafely-without-email

    echo -e "${GREEN}✅ SSL configured!${NC}"
    echo "Access your app at: https://${DOMAIN}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
