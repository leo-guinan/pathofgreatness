#!/bin/bash

# SSL Certificate Setup Script
# This script obtains Let's Encrypt SSL certificates for thepathofgreatness.com

set -e

DOMAIN="thepathofgreatness.com"
EMAIL="your-email@example.com"  # Change this to your email

echo "=== Initializing SSL Certificates for $DOMAIN ==="

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

# Create temporary nginx config for certificate acquisition
echo "Creating temporary nginx configuration..."
cat > nginx-temp.conf << 'EOF'
server {
    listen 80;
    server_name thepathofgreatness.com www.thepathofgreatness.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Acquiring SSL certificate...';
        add_header Content-Type text/plain;
    }
}
EOF

# Start nginx temporarily for certificate acquisition
echo "Starting nginx for certificate acquisition..."
docker run --rm -d \
    --name temp-nginx \
    -p 80:80 \
    -v "$(pwd)/nginx-temp.conf:/etc/nginx/conf.d/default.conf" \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    nginx:alpine

# Wait for nginx to start
sleep 3

# Obtain certificate
echo "Obtaining SSL certificate from Let's Encrypt..."
docker run --rm \
    -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Stop temporary nginx
echo "Stopping temporary nginx..."
docker stop temp-nginx || true

# Clean up
rm nginx-temp.conf

echo ""
echo "=== SSL Certificate Setup Complete ==="
echo ""
echo "Certificates are now available in certbot/conf/live/$DOMAIN/"
echo "You can now run ./deploy.sh to start the application with SSL"
