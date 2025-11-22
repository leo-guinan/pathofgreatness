# Quick Deployment Reference

## First Time Setup (One-time only)

### 1. DNS Setup
Point DNS A records to `178.156.207.21`:
- thepathofgreatness.com
- www.thepathofgreatness.com

### 2. Server Setup
```bash
ssh root@178.156.207.21
cd /opt
git clone https://github.com/yourusername/the-greatness-path.git greatness
cd greatness
bash setup-server.sh
```

### 3. Add API Key
```bash
nano .env
# Add: OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
```

### 4. Initialize SSL
```bash
nano init-ssl.sh
# Change EMAIL to your email
bash init-ssl.sh
```

### 5. Deploy
```bash
bash deploy.sh
```

### 6. Setup GitHub Auto-Deploy

Add secrets to GitHub repo (Settings → Secrets):
- `SERVER_IP`: 178.156.207.21
- `SSH_PRIVATE_KEY`: (your SSH private key)

Initialize Git on server:
```bash
cd /opt/greatness
git init
git remote add origin https://github.com/yourusername/the-greatness-path.git
git branch -M main
git pull origin main
```

Done! Now every push to `main` auto-deploys.

## Regular Operations

### Deploy Changes (Manual)
```bash
ssh root@178.156.207.21
cd /opt/greatness
bash deploy.sh
```

### Deploy Changes (Automatic)
```bash
git push origin main
```

### View Logs
```bash
ssh root@178.156.207.21
cd /opt/greatness
docker-compose -f docker-compose.prod.yml logs -f
```

### Restart Application
```bash
ssh root@178.156.207.21
cd /opt/greatness
docker-compose -f docker-compose.prod.yml restart
```

### Check SSL Status
```bash
ssh root@178.156.207.21
cd /opt/greatness
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates
```

## URLs

- **Production**: https://thepathofgreatness.com
- **Server IP**: 178.156.207.21
- **GitHub Actions**: https://github.com/yourusername/the-greatness-path/actions
- **Fathom Analytics**: https://app.usefathom.com

## Files Created

- `nginx.conf` - Nginx reverse proxy with SSL
- `docker-compose.prod.yml` - Production Docker setup
- `setup-server.sh` - Initial server configuration
- `init-ssl.sh` - SSL certificate setup
- `deploy.sh` - Deployment script
- `.github/workflows/deploy.yml` - Auto-deploy on push
- `DEPLOYMENT.md` - Full deployment guide
- `QUICK_DEPLOY.md` - This file

## Emergency Commands

### Stop Everything
```bash
docker-compose -f docker-compose.prod.yml down
```

### Rebuild from Scratch
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Backup Database
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz /opt/greatness/data/
```
