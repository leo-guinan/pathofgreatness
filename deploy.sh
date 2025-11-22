#!/bin/bash

# Deployment Script for The Path of Greatness
# Can be run manually or triggered by GitHub Actions

set -e

echo "=== Deploying The Path of Greatness ==="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Pull latest changes if in git repo
if [ -d .git ]; then
    echo "Pulling latest changes from Git..."
    git pull origin main || git pull origin master || echo "No git updates available"
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Build and start new containers
echo "Building and starting containers..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Check if containers are running
echo "Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# Show logs
echo ""
echo "=== Recent logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Application is now running at:"
echo "  https://thepathofgreatness.com"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To restart:"
echo "  docker-compose -f docker-compose.prod.yml restart"
