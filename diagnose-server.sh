#!/bin/bash

# Server Diagnostic Script
# Run this to check what's using ports 80/443

echo "=== Server Diagnostic Report ==="
echo ""

echo "--- Processes using port 80 ---"
sudo lsof -i :80 || netstat -tlnp | grep :80
echo ""

echo "--- Processes using port 443 ---"
sudo lsof -i :443 || netstat -tlnp | grep :443
echo ""

echo "--- Running Docker containers ---"
docker ps -a
echo ""

echo "--- Docker networks ---"
docker network ls
echo ""

echo "--- Systemd web servers ---"
systemctl list-units --type=service --state=running | grep -E "nginx|apache|httpd"
echo ""

echo "--- All listening ports ---"
sudo netstat -tlnp | grep LISTEN
echo ""

echo "=== Recommendations ==="
echo ""

# Check if nginx is running as system service
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "⚠️  System nginx service is running"
    echo "   Stop it with: sudo systemctl stop nginx"
    echo "   Disable it with: sudo systemctl disable nginx"
    echo ""
fi

if systemctl is-active --quiet apache2 2>/dev/null; then
    echo "⚠️  System apache2 service is running"
    echo "   Stop it with: sudo systemctl stop apache2"
    echo "   Disable it with: sudo systemctl disable apache2"
    echo ""
fi

# Check for docker containers
if docker ps -q | grep -q .; then
    echo "⚠️  Docker containers are running"
    echo "   List them with: docker ps"
    echo "   Stop all with: docker stop \$(docker ps -q)"
    echo ""
fi

echo "To clean up and prepare for fresh deployment:"
echo "  bash cleanup-server.sh"
