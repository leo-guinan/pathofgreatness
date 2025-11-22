# The Path of Greatness - Simplified

An interactive journey through 8 transformations. Watch yourself climb the ladder of greatness, one step at a time.

## What This Does

This is a **narrative-driven transformation experience** where:

1. You enter someone you admire → AI determines your "Order" (path to greatness)
2. You create your character → Answer 5 quick questions
3. You experience 8 chapters → Each showing:
   - **BEFORE**: Where you are now (your limitations, struggles)
   - **AFTER**: Where you've climbed to (your transformation)
4. You see your complete story → Timeline of all 8 transformations

**No trials, no tests, no loops** - just pure narrative transformation.

## Simplified State Machine

```
WELCOME
   ↓
GREATNESS_MIRROR (AI determines Order)
   ↓
ORDER_REVEAL
   ↓
CHARACTER_CREATION
   ↓
CHAPTER 1 BEFORE → CHAPTER 1 AFTER
   ↓
CHAPTER 2 BEFORE → CHAPTER 2 AFTER
   ↓
...
   ↓
CHAPTER 8 BEFORE → CHAPTER 8 AFTER
   ↓
COMPLETION (full timeline)
```

**Total states**: 7 (down from 11)
**AI calls per journey**: ~20 (down from ~50)
**Cost per journey**: ~$0.03-0.08 with Claude Haiku

## The Experience

### Before Each Chapter
Shows you where you are now:
- Your current limitations
- What you haven't yet learned
- The gap between who you are and who you could be
- Blue-themed narrative box

### After Each Chapter
Shows you transformed:
- What you've learned
- How you've changed
- The new rung you're standing on
- Green-themed narrative box
- Gold-highlighted transformation insight

### Visual Design
- **Dark theme** with gold accents
- **Progress bar** showing chapter progress
- **"BEFORE" and "AFTER" labels** clearly marked
- **Ladder metaphor** - each chapter is a rung higher

## Quick Start

```bash
# 1. Setup
cp .env.example .env
# Add your OPENROUTER_API_KEY

# 2. Run
docker-compose up --build

# 3. Play
http://localhost:8000
```

## Cost Breakdown

### AI Calls Per Journey

| Call Type | Count | Cost Each (Haiku) | Total |
|-----------|-------|-------------------|-------|
| Mirror (Order detection) | 1 | $0.002 | $0.002 |
| Chapter BEFORE narratives | 8 | $0.003 | $0.024 |
| Chapter AFTER narratives | 8 | $0.003 | $0.024 |
| Transformation insights | 8 | $0.002 | $0.016 |
| **TOTAL** | **25** | - | **$0.066** |

### Model Comparison (per journey)

- **Claude 3 Haiku** (recommended): $0.03-0.08
- **Claude 3.5 Sonnet**: $0.30-0.80
- **Llama 3.1 8B**: $0.005-0.02
- **Llama 3.2 3B**: $0.002-0.01

## What Changed from Original Design

### Removed
- ❌ Trial attempt system (AI doing exercises)
- ❌ Trial evaluation system
- ❌ Feedback loops (retry logic)
- ❌ Complex state transitions
- ❌ Multiple attempts per chapter
- ❌ "Trial" concept entirely

### Simplified To
- ✅ Simple before/after narratives
- ✅ Direct transformation experience
- ✅ Clean visual progression
- ✅ Focus on storytelling, not simulation
- ✅ Half the cost
- ✅ Half the AI calls

## User Journey

### Step 1: Mirror (30 seconds)
```
"Who do you admire?"
→ Enter: "Marcus Aurelius"
→ AI: "You walk the Path of Zen (Sage)"
```

### Step 2: Choose Archetype (10 seconds)
```
Choose from: Philosopher, Meditator, Spiritual Seeker
→ Select: "Philosopher"
```

### Step 3: Create Character (1 minute)
```
- Name: Alex
- Age: 32
- Situation: "Feeling scattered across too many projects"
- Struggle: "Can't focus on what matters"
- Greatness: "Living with clarity and purpose"
```

### Step 4: 8 Chapters (10-15 minutes)

**Chapter 1: Coherence - BEFORE**
> You wake each morning to a dozen notifications, each pulling you in a different direction. Your projects multiply faster than you complete them. You tell yourself you're productive, but you feel scattered. The gap between your intentions and your actions grows wider each day. You haven't felt truly focused in months...

[Click: "Experience the Transformation"]

**Chapter 1: Coherence - AFTER**
> You've learned to see through the noise. Now, before taking on anything new, you pause and ask: "Does this align with what truly matters?" Your projects are fewer, but each one moves forward with clarity. You recognize scattered energy for what it is - a choice, not a condition. You've climbed to a place where coherence isn't an accident, it's a practice...

**TRANSFORMATION**
> You realize: Coherence isn't about doing more with focus. It's about choosing less, with intention.

[Continues for 7 more chapters...]

### Step 5: Completion (2 minutes)
View full timeline of all 8 transformations. See how far you've climbed.

## File Structure

```
the-greatness-path/
├── Core Backend (4 files)
│   ├── main.py                 # FastAPI app
│   ├── state_machine_simple.py # Simplified state machine
│   ├── models.py              # Data models
│   ├── database.py            # SQLite
│   ├── openrouter.py          # AI client
│   ├── prompts.py             # Narrative prompts
│   └── cost_tracker.py        # Cost logging
│
├── Frontend (3 files)
│   └── static/
│       ├── index.html         # UI
│       ├── css/style.css      # Dark theme
│       └── js/app.js          # Alpine.js
│
├── Deployment (3 files)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
└── Documentation
    ├── README_SIMPLE.md       # This file
    └── .env.example
```

## API Endpoints

```bash
# Create session
POST /api/session

# Get current state
GET /api/session/{session_id}

# Advance state
POST /api/transition
{
  "session_id": "...",
  "action": "transform",
  "data": {}
}

# Get cost breakdown
GET /api/cost/{session_id}

# Get timeline
GET /api/timeline/{session_id}
```

## State Transitions

```python
# Welcome → Mirror
POST /api/transition {"action": "start", "data": {}}

# Mirror → Order Reveal
POST /api/transition {"action": "submit", "data": {"admired_person": "..."}}

# Order Reveal → Character Creation
POST /api/transition {"action": "select_archetype", "data": {"archetype": "..."}}

# Character Creation → Chapter 1 Before
POST /api/transition {"action": "create_character", "data": {...}}

# Chapter Before → Chapter After
POST /api/transition {"action": "transform", "data": {}}

# Chapter After → Next Chapter Before (or Completion if chapter 8)
POST /api/transition {"action": "continue", "data": {}}
```

## Development

### Local Testing
```bash
docker-compose up --build
# Access: http://localhost:8000
```

### View Database
```bash
sqlite3 data/game.db
.tables
SELECT * FROM sessions;
SELECT * FROM cost_log;
```

### Monitor Costs
```bash
curl http://localhost:8000/api/cost/{session_id} | jq
```

## Deploy to Hetzner

```bash
# Automated
./deploy-hetzner.sh https://github.com/your/repo

# Manual
ssh root@your-server
apt-get install -y docker.io docker-compose
git clone https://github.com/your/repo
cd repo
cp .env.example .env
nano .env  # Add API key
docker-compose up -d
```

## Configuration

### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your_key_here

# Optional
OPENROUTER_MODEL=anthropic/claude-3-haiku  # default
PORT=8000  # default
```

### Chapter Themes

1. **Coherence** - Aligning actions with vision
2. **Vision** - Seeing the future you want
3. **Discipline** - Daily practice of excellence
4. **Craft** - Mastery through refinement
5. **Performance** - Showing up when it matters
6. **Leadership** - Elevating others as you rise
7. **Innovation** - Creating new paths
8. **Legacy** - What endures after you're gone

## Design Principles

### Why "Before/After" Instead of Trials?

1. **Focus on transformation, not simulation** - Users don't need to watch AI do exercises
2. **Clearer narrative arc** - Before shows struggle, After shows growth
3. **More efficient** - Half the AI calls, half the cost
4. **Better UX** - No waiting for trial loops, direct to insight
5. **Ladder metaphor** - Each chapter is literally a rung they climb

### Visual Language

- **Dark background** - Focus on content
- **Gold accents** - Sense of value, achievement
- **Blue (before)** - Current state, calm reflection
- **Green (after)** - Growth, transformation, ascension
- **Progress bar** - Visual sense of climbing
- **Clear "BEFORE/AFTER" labels** - No confusion about where they are

## Monitoring

### Check Costs
```bash
# Per session
curl http://localhost:8000/api/cost/{session_id}

# In database
sqlite3 data/game.db "SELECT SUM(cost_usd) FROM cost_log WHERE session_id='...';"
```

### View Timeline
```bash
curl http://localhost:8000/api/timeline/{session_id}
```

### Check Sessions
```bash
sqlite3 data/game.db "SELECT session_id, state, updated_at FROM sessions ORDER BY updated_at DESC LIMIT 10;"
```

## Troubleshooting

### App won't start
- Check `.env` has `OPENROUTER_API_KEY`
- Verify port 8000 is free: `lsof -i :8000`
- Check Docker logs: `docker-compose logs`

### Costs too high
- Change model to Llama: `OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct`
- Check cost log: `curl http://localhost:8000/api/cost/{session_id}`

### Narratives not generating
- Check OpenRouter API key is valid
- Check OpenRouter dashboard for credits
- View API logs in Docker: `docker-compose logs -f`

### Database errors
- Reset: `rm data/game.db && docker-compose restart`
- Check permissions: `ls -la data/`

## Future Enhancements

- [ ] Visual ladder graphic showing progress
- [ ] Animated transitions between before/after
- [ ] Export timeline as PDF or image
- [ ] Social sharing of completed journey
- [ ] Multiple characters per user
- [ ] Save/resume functionality
- [ ] Analytics dashboard

## License

MIT

## Credits

Built with FastAPI, Alpine.js, OpenRouter, and SQLite.
Based on "The Path of Greatness" framework.
