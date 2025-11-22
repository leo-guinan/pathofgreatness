# Quick Start Guide

## Get Running in 5 Minutes

### 1. Prerequisites
- Docker installed
- OpenRouter API key ([sign up here](https://openrouter.ai/))

### 2. Setup
```bash
# Clone the repo
git clone <your-repo-url>
cd the-greatness-path

# Configure environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### 3. Run
```bash
docker-compose up --build
```

### 4. Play
Open your browser to: **http://localhost:8000**

---

## What You'll See

### Flow
1. **Welcome Screen** → Click "Begin your journey"
2. **Greatness Mirror** → Enter someone you admire (e.g., "Steve Jobs")
3. **Order Reveal** → See your Order and choose an archetype
4. **Character Creation** → Answer 5 quick questions about yourself
5. **8 Chapters** → Each chapter includes:
   - Narrative introduction
   - AI attempts trial (automatic)
   - Evaluation (automatic)
   - Transformation moment
   - Timeline event
6. **Completion** → View your full journey timeline

### Cost Tracking
Every AI call is measured and displayed:
- Top right corner shows total cost
- Final screen shows cost breakdown
- Expected: **$0.05-0.15** per complete journey (with Claude Haiku)

---

## Models & Costs

Edit `.env` to change model:

```bash
# Recommended (default)
OPENROUTER_MODEL=anthropic/claude-3-haiku

# Best quality
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Cheapest
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct
```

**Cost per session:**
- Claude 3.5 Sonnet: ~$0.50-1.00
- **Claude 3 Haiku: ~$0.05-0.15** ⭐ Recommended
- Llama 3.1 8B: ~$0.01-0.03
- Llama 3.2 3B: ~$0.005-0.01

---

## Deploy to Hetzner

### Automated Script
```bash
ssh root@your-server-ip
curl -sSL https://raw.githubusercontent.com/<your-repo>/main/deploy-hetzner.sh | bash -s <your-repo-url>
```

### Manual Steps
```bash
# On your Hetzner server
apt-get update && apt-get install -y docker.io docker-compose

git clone <your-repo-url>
cd the-greatness-path

cp .env.example .env
nano .env  # Add OPENROUTER_API_KEY

docker-compose up -d
```

Access at: **http://your-server-ip:8000**

---

## Troubleshooting

### App won't start
```bash
docker-compose logs
```
Check that:
- `.env` has `OPENROUTER_API_KEY`
- Port 8000 is available

### OpenRouter errors
- Verify API key at https://openrouter.ai/
- Check you have credits
- Try a different model

### Reset everything
```bash
docker-compose down
rm -rf data/
docker-compose up --build
```

---

## API Endpoints

```bash
# Create session
curl -X POST http://localhost:8000/api/session

# Get state
curl http://localhost:8000/api/session/{session_id}

# Get cost
curl http://localhost:8000/api/cost/{session_id}

# Get timeline
curl http://localhost:8000/api/timeline/{session_id}
```

---

## Next Steps

After testing locally:
1. Deploy to Hetzner (see above)
2. Set up domain + SSL (see README.md)
3. Share with users!

For full documentation, see [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
