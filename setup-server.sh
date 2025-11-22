#!/bin/bash

# Server Setup Script for The Path of Greatness
# Run this on your server at 178.156.207.21

set -e

echo "=== Setting up The Path of Greatness Server ==="

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y curl git

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed"
fi

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/greatness
cd /opt/greatness

# Set up environment file
echo "Setting up environment..."
if [ ! -f .env ]; then
    echo "OPENROUTER_API_KEY=your_api_key_here" > .env
    echo "⚠️  Please update .env with your actual OpenRouter API key!"
fi

# Create necessary directories
mkdir -p data
mkdir -p certbot/conf
mkdir -p certbot/www

# Set up firewall
echo "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
fi

# Set up Git for deployment
echo "Setting up Git repository..."
if [ ! -d .git ]; then
    git init
    git remote add origin https://github.com/yourusername/the-greatness-path.git
fi

echo ""
echo "=== Initial Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update /opt/greatness/.env with your OpenRouter API key"
echo "2. Ensure DNS for thepathofgreatness.com points to 178.156.207.21"
echo "3. Run ./init-ssl.sh to set up SSL certificates"
echo "4. Run ./deploy.sh to start the application"
