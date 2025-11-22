#!/bin/bash

# Server Cleanup Script
# Safely stops existing services to prepare for deployment

set -e

echo "=== Cleaning Up Server for Fresh Deployment ==="
echo ""

# Stop system nginx if running
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "Stopping system nginx service..."
    sudo systemctl stop nginx
    sudo systemctl disable nginx
    echo "✓ System nginx stopped and disabled"
fi

# Stop system apache if running
if systemctl is-active --quiet apache2 2>/dev/null; then
    echo "Stopping system apache2 service..."
    sudo systemctl stop apache2
    sudo systemctl disable apache2
    echo "✓ System apache2 stopped and disabled"
fi

# Stop any running Docker containers
if docker ps -q | grep -q .; then
    echo "Stopping running Docker containers..."
    docker stop $(docker ps -q)
    echo "✓ All Docker containers stopped"
fi

# Optional: Remove stopped containers
read -p "Remove all stopped Docker containers? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker container prune -f
    echo "✓ Stopped containers removed"
fi

# Optional: Remove unused Docker images
read -p "Remove unused Docker images? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker image prune -a -f
    echo "✓ Unused images removed"
fi

# Check ports are now free
echo ""
echo "Checking if ports are now free..."
if sudo lsof -i :80 > /dev/null 2>&1; then
    echo "⚠️  Port 80 still in use:"
    sudo lsof -i :80
else
    echo "✓ Port 80 is free"
fi

if sudo lsof -i :443 > /dev/null 2>&1; then
    echo "⚠️  Port 443 still in use:"
    sudo lsof -i :443
else
    echo "✓ Port 443 is free"
fi

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Server is ready for deployment!"
echo "Next steps:"
echo "  1. Configure .env file with API key"
echo "  2. Run: bash init-ssl.sh (if SSL not set up yet)"
echo "  3. Run: bash deploy.sh"
