# The Path of Greatness - Web Game

An interactive web-based journey through the 8 chapters of greatness, powered by AI and managed through a predictable state machine.

## Features

- **State Machine-Driven**: Predictable game flow through 11 distinct states
- **AI-Powered**: Uses OpenRouter for narrative generation and trial management
- **Cost Tracking**: Every AI call is measured and logged
- **Minimal Dependencies**: Only FastAPI, Uvicorn, and HTTPX
- **Docker-Ready**: Deploy as a container to Hetzner or any Docker host
- **SQLite Storage**: Lightweight, file-based database
- **Responsive UI**: Clean, minimal frontend with Alpine.js (15kb)

## Architecture

### State Machine

The game follows a strict state machine with these states:

```
WELCOME → GREATNESS_MIRROR → ORDER_REVEAL → CHARACTER_CREATION →
CHAPTER_INTRO → TRIAL_ATTEMPT → TRIAL_EVALUATION →
[TRIAL_FEEDBACK → TRIAL_ATTEMPT] (loop until pass) →
TRANSFORMATION → TIMELINE_EVENT →
[CHAPTER_INTRO (next chapter) OR COMPLETION]
```

### Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Alpine.js + Vanilla JS
- **Database**: SQLite
- **AI**: OpenRouter API
- **Container**: Docker Alpine Linux

### Cost Tracking

Every state transition that uses AI is tracked with:
- Prompt tokens
- Completion tokens
- Cost in USD
- Model used
- Timestamp

View costs via `/api/cost/{session_id}` endpoint.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenRouter API key ([get one here](https://openrouter.ai/))

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo>
cd the-greatness-path
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

3. **Run with Docker Compose**
```bash
docker-compose up --build
```

4. **Access the app**
```
http://localhost:8000
```

### Run Without Docker

1. **Install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set environment variables**
```bash
export OPENROUTER_API_KEY=your_key_here
```

3. **Run the app**
```bash
python main.py
```

## Deployment to Hetzner

### Option 1: Docker Compose (Recommended)

1. **Create a Hetzner Cloud server**
   - Choose CX11 or larger
   - Select Ubuntu 22.04
   - Add your SSH key

2. **SSH into server**
```bash
ssh root@your-server-ip
```

3. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

4. **Clone your repository**
```bash
git clone <your-repo>
cd the-greatness-path
```

5. **Set up environment**
```bash
cp .env.example .env
nano .env  # Add your OPENROUTER_API_KEY
```

6. **Run the application**
```bash
docker-compose up -d
```

7. **Check status**
```bash
docker-compose ps
docker-compose logs -f
```

8. **Access your app**
```
http://your-server-ip:8000
```

### Option 2: Manual Deployment Script

Save this as `deploy-hetzner.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying The Greatness Path to Hetzner"

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt-get install -y docker-compose

# Clone repository (replace with your repo)
git clone <your-repo> /app/greatness-path
cd /app/greatness-path

# Set up environment
cp .env.example .env
echo "⚠️  Please edit .env and add your OPENROUTER_API_KEY"
read -p "Press enter when ready..."

# Build and run
docker-compose up -d

# Show logs
docker-compose logs -f
```

Run it:
```bash
chmod +x deploy-hetzner.sh
./deploy-hetzner.sh
```

### Setting Up HTTPS (Optional but Recommended)

1. **Install Nginx**
```bash
apt-get install -y nginx certbot python3-certbot-nginx
```

2. **Configure Nginx**
```bash
cat > /etc/nginx/sites-available/greatness-path <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/greatness-path /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

3. **Get SSL Certificate**
```bash
certbot --nginx -d your-domain.com
```

## API Documentation

### Session Management

- `POST /api/session` - Create new session
  - Returns: `{session_id, state}`

- `GET /api/session/{session_id}` - Get current state
  - Returns: `{session_id, state, data, character, total_cost, ui_data}`

- `DELETE /api/session/{session_id}` - Delete session

### State Transitions

- `POST /api/transition` - Advance state
  - Body: `{session_id, action, data}`
  - Returns: `{success, next_state, data}`

### Cost Tracking

- `GET /api/cost/{session_id}` - Get cost breakdown
  - Returns: `{total_cost_usd, cost_by_state, cost_by_model, ...}`

### Timeline

- `GET /api/timeline/{session_id}` - Get journey timeline
  - Returns: `{timeline: [{chapter, narrative, transformation}]}`

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY` (required) - Your OpenRouter API key
- `OPENROUTER_MODEL` (optional) - Model to use (default: `anthropic/claude-3-haiku`)
- `PORT` (optional) - Port to run on (default: `8000`)

### Model Options

Recommended models by cost/quality trade-off:

**Best Quality** (highest cost)
- `anthropic/claude-3.5-sonnet` - Best narrative quality
  - ~$0.003/1k prompt tokens, ~$0.015/1k completion tokens

**Recommended** (balanced)
- `anthropic/claude-3-haiku` - Good quality, low cost
  - ~$0.00025/1k prompt tokens, ~$0.00125/1k completion tokens

**Budget** (lowest cost)
- `meta-llama/llama-3.1-8b-instruct` - Decent quality, very low cost
  - ~$0.00005/1k tokens
- `meta-llama/llama-3.2-3b-instruct` - Basic quality, minimal cost
  - ~$0.00002/1k tokens

### Expected Costs

For a complete 8-chapter journey:

- **Claude 3.5 Sonnet**: ~$0.50-1.00 per session
- **Claude 3 Haiku**: ~$0.05-0.15 per session (recommended)
- **Llama 3.1 8B**: ~$0.01-0.03 per session
- **Llama 3.2 3B**: ~$0.005-0.01 per session

## File Structure

```
the-greatness-path/
├── main.py                 # FastAPI app entry point
├── state_machine.py        # Core game state machine
├── models.py              # Data models & enums
├── database.py            # SQLite operations
├── openrouter.py          # OpenRouter API client
├── prompts.py             # AI prompt templates
├── cost_tracker.py        # Cost measurement
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose config
├── .env.example          # Environment template
├── ARCHITECTURE.md       # Detailed architecture docs
├── README.md             # This file
├── data/                 # SQLite database (created at runtime)
│   └── game.db
└── static/               # Frontend files
    ├── index.html
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Development

### Running Tests

```bash
# TODO: Add tests
pytest
```

### Database Management

The SQLite database is stored in `data/game.db`.

**View database**:
```bash
sqlite3 data/game.db
.tables
.schema sessions
SELECT * FROM sessions;
```

**Reset database**:
```bash
rm data/game.db
# Restart the app to recreate
```

### Monitoring Costs

```bash
# View cost for a session
curl http://localhost:8000/api/cost/{session_id}

# Or check the database
sqlite3 data/game.db "SELECT * FROM cost_log;"
```

## Troubleshooting

### App won't start
- Check Docker logs: `docker-compose logs`
- Verify `.env` file has `OPENROUTER_API_KEY`
- Check port 8000 isn't already in use

### AI calls failing
- Verify OpenRouter API key is valid
- Check OpenRouter dashboard for quota/credits
- Try a different model in `.env`

### Database errors
- Delete `data/game.db` and restart
- Check file permissions on `data/` directory

### Cost tracking not working
- Check `cost_log` table in database
- Verify API responses include `usage` field

## Contributing

This is a minimal MVP. Future improvements:

- [ ] Add automated tests
- [ ] Implement caching for common narratives
- [ ] Add user authentication
- [ ] Support multiple concurrent games
- [ ] Export timeline as PDF/image
- [ ] Social sharing features
- [ ] Progressive Web App (PWA)
- [ ] Analytics dashboard

## License

MIT

## Credits

Based on "The Path of Greatness" framework.
Built with FastAPI, Alpine.js, and OpenRouter.
