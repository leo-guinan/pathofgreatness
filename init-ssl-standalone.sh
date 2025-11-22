#!/bin/bash

# Standalone SSL Certificate Setup Script
# This version uses certbot standalone mode (no nginx needed)

set -e

DOMAIN="thepathofgreatness.com"
EMAIL="your-email@example.com"  # Change this to your email

echo "=== Initializing SSL Certificates for $DOMAIN (Standalone Mode) ==="
echo ""

# Check if port 80 is available
if sudo lsof -i :80 > /dev/null 2>&1; then
    echo "⚠️  Error: Port 80 is in use!"
    echo ""
    echo "Port 80 must be free for certificate acquisition."
    echo "Run this first:"
    echo "  bash diagnose-server.sh     # See what's using port 80"
    echo "  bash cleanup-server.sh      # Stop services using port 80"
    echo ""
    exit 1
fi

# Create directories if they don't exist
mkdir -p certbot/conf
mkdir -p certbot/www

# Download recommended TLS parameters
if [ ! -f "certbot/conf/options-ssl-nginx.conf" ]; then
    echo "Downloading recommended TLS parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > certbot/conf/options-ssl-nginx.conf
fi

if [ ! -f "certbot/conf/ssl-dhparams.pem" ]; then
    echo "Downloading recommended DH parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > certbot/conf/ssl-dhparams.pem
fi

# Obtain certificate using standalone mode
echo "Obtaining SSL certificate from Let's Encrypt..."
echo "This will bind to port 80 temporarily..."
echo ""

docker run --rm \
    -p 80:80 \
    -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    certbot/certbot certonly \
    --standalone \
    --preferred-challenges http \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo ""
echo "=== SSL Certificate Setup Complete ==="
echo ""
echo "Certificates are now available in certbot/conf/live/$DOMAIN/"
echo ""
echo "Certificate details:"
ls -la certbot/conf/live/$DOMAIN/ || echo "Certificate directory not found - check for errors above"
echo ""
echo "Next step: Run deployment"
echo "  bash deploy.sh"
