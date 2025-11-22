# Deployment Guide: The Path of Greatness

This guide covers deploying the application to your production server at `178.156.207.21` with SSL for `thepathofgreatness.com`.

## Prerequisites

- Server: Ubuntu/Debian at 178.156.207.21
- SSH access as root (already configured)
- Domain: thepathofgreatness.com
- DNS A record pointing to 178.156.207.21
- OpenRouter API key

## Initial Setup

### 1. DNS Configuration

Ensure your DNS records are set:

```
A     thepathofgreatness.com      178.156.207.21
A     www.thepathofgreatness.com  178.156.207.21
```

Wait for DNS propagation (check with `dig thepathofgreatness.com`)

### 2. Server Setup

SSH into your server:

```bash
ssh root@178.156.207.21
```

Clone the repository:

```bash
cd /opt
git clone https://github.com/yourusername/the-greatness-path.git greatness
cd greatness
```

Run the server setup script:

```bash
bash setup-server.sh
```

This will:
- Install Docker and Docker Compose
- Create necessary directories
- Set up firewall rules
- Create environment file template

### 3. Configure Environment

Edit the environment file:

```bash
nano /opt/greatness/.env
```

Add your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
```

Save and exit (Ctrl+X, Y, Enter)

### 4. Initialize SSL Certificates

**IMPORTANT**: Before running this, ensure DNS is propagated!

Edit `init-ssl.sh` to add your email:

```bash
nano init-ssl.sh
```

Change line 8:
```bash
EMAIL="your-email@example.com"
```

Run the SSL initialization:

```bash
bash init-ssl.sh
```

This will:
- Obtain Let's Encrypt SSL certificates
- Set up auto-renewal
- Configure TLS parameters

### 5. Deploy Application

Deploy the application:

```bash
bash deploy.sh
```

The application is now live at:
- https://thepathofgreatness.com
- https://www.thepathofgreatness.com

## GitHub Actions Setup

For automatic deployment on every push to GitHub:

### 1. Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add two secrets:

**SERVER_IP**
```
178.156.207.21
```

**SSH_PRIVATE_KEY**
```
-----BEGIN OPENSSH PRIVATE KEY-----
[Your SSH private key content]
-----END OPENSSH PRIVATE KEY-----
```

To get your SSH private key:
```bash
cat ~/.ssh/id_rsa
```

### 2. Initialize Git Repository on Server

On your server:

```bash
cd /opt/greatness
git init
git remote add origin https://github.com/yourusername/the-greatness-path.git
git branch -M main
git pull origin main
```

### 3. Test Automatic Deployment

Push a change to GitHub:

```bash
git add .
git commit -m "Test deployment"
git push origin main
```

GitHub Actions will automatically:
1. SSH into your server
2. Pull the latest code
3. Rebuild and restart containers
4. Run the application

Check deployment status at: `https://github.com/yourusername/the-greatness-path/actions`

## Manual Operations

### View Logs

```bash
cd /opt/greatness
docker-compose -f docker-compose.prod.yml logs -f
```

### Restart Application

```bash
cd /opt/greatness
docker-compose -f docker-compose.prod.yml restart
```

### Stop Application

```bash
cd /opt/greatness
docker-compose -f docker-compose.prod.yml down
```

### Rebuild and Restart

```bash
cd /opt/greatness
bash deploy.sh
```

### Check SSL Certificate Status

```bash
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates
```

### Renew SSL Certificate Manually

```bash
docker-compose -f docker-compose.prod.yml exec certbot certbot renew
```

## File Structure

```
/opt/greatness/
├── .env                          # Environment variables (API keys)
├── .git/                         # Git repository
├── .github/
│   └── workflows/
│       └── deploy.yml            # GitHub Actions workflow
├── certbot/
│   ├── conf/                     # SSL certificates
│   └── www/                      # ACME challenge files
├── data/                         # SQLite database
├── static/                       # Frontend assets
├── *.py                          # Python application files
├── Dockerfile                    # Docker build config
├── docker-compose.yml            # Local development
├── docker-compose.prod.yml       # Production deployment
├── nginx.conf                    # Nginx configuration
├── requirements.txt              # Python dependencies
├── setup-server.sh               # Server setup script
├── init-ssl.sh                   # SSL initialization script
└── deploy.sh                     # Deployment script
```

## Monitoring

### Check if application is running

```bash
curl -I https://thepathofgreatness.com
```

Expected response:
```
HTTP/2 200
server: nginx
...
```

### Check container status

```bash
docker-compose -f docker-compose.prod.yml ps
```

Should show:
- greatness-app (running)
- greatness-nginx (running)
- greatness-certbot (running)

### View resource usage

```bash
docker stats
```

## Troubleshooting

### SSL Certificate Failed

Check DNS propagation:
```bash
dig thepathofgreatness.com
```

Check ports are open:
```bash
netstat -tlnp | grep -E '80|443'
```

View certbot logs:
```bash
docker-compose -f docker-compose.prod.yml logs certbot
```

### Application Not Starting

Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs web
```

Verify environment variables:
```bash
cat .env
```

Rebuild containers:
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Database Issues

Database file location:
```bash
ls -la /opt/greatness/data/
```

Backup database:
```bash
cp /opt/greatness/data/game.db /opt/greatness/data/game.db.backup
```

### GitHub Actions Deployment Failed

Check GitHub Actions logs:
`https://github.com/yourusername/the-greatness-path/actions`

Test SSH connection:
```bash
ssh root@178.156.207.21 "cd /opt/greatness && pwd"
```

## Security Checklist

- [x] Firewall configured (ports 22, 80, 443)
- [x] SSL/TLS enabled with Let's Encrypt
- [x] Auto-renewal configured for SSL
- [x] Environment variables not committed to Git
- [x] SSH key-based authentication
- [x] Security headers configured in nginx
- [x] HTTPS redirect enabled

## Backup Strategy

### Backup Database

```bash
# On server
tar -czf backup-$(date +%Y%m%d).tar.gz /opt/greatness/data/

# Download to local machine
scp root@178.156.207.21:/opt/greatness/backup-*.tar.gz ./
```

### Restore Database

```bash
# Upload backup to server
scp backup-20250122.tar.gz root@178.156.207.21:/opt/greatness/

# On server
cd /opt/greatness
docker-compose -f docker-compose.prod.yml down
tar -xzf backup-20250122.tar.gz
docker-compose -f docker-compose.prod.yml up -d
```

## Updating the Application

### Option 1: Automatic (Recommended)

Just push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

GitHub Actions handles the rest.

### Option 2: Manual

SSH into server:

```bash
ssh root@178.156.207.21
cd /opt/greatness
bash deploy.sh
```

## Support

If you encounter issues:

1. Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verify DNS: `dig thepathofgreatness.com`
3. Check SSL: `docker-compose -f docker-compose.prod.yml exec certbot certbot certificates`
4. Review GitHub Actions: Check workflow runs in GitHub

## Cost Tracking

Monitor your OpenRouter API usage at:
https://openrouter.ai/usage

The application tracks costs internally in the SQLite database.

## Next Steps

After successful deployment:

1. Test the full user journey at https://thepathofgreatness.com
2. Monitor Fathom Analytics at https://app.usefathom.com
3. Monitor OpenRouter costs
4. Set up monitoring/alerting for downtime (optional)
5. Configure backups (recommended: daily cron job)

---

**Production URL**: https://thepathofgreatness.com
**Server IP**: 178.156.207.21
**Deploy Method**: Git push to main/master branch
**SSL**: Let's Encrypt (auto-renewing)
