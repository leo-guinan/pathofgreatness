# The Greatness Path - Web Game Architecture

## Overview
Minimal web-based version of The Path of Greatness game, deployable as a Docker container.

## Tech Stack (Minimal Dependencies)
- **Backend**: FastAPI (only core, no extras)
- **Frontend**: Alpine.js (15kb) or Vanilla JS
- **Database**: SQLite (built-in Python)
- **AI**: OpenRouter API (HTTP requests only)
- **WSGI**: Uvicorn
- **Container**: Docker Alpine Linux

## State Machine

### States
```python
class GameState(Enum):
    WELCOME = "welcome"
    GREATNESS_MIRROR = "greatness_mirror"
    ORDER_REVEAL = "order_reveal"
    CHARACTER_CREATION = "character_creation"
    CHAPTER_INTRO = "chapter_intro"
    TRIAL_ATTEMPT = "trial_attempt"
    TRIAL_EVALUATION = "trial_evaluation"
    TRIAL_FEEDBACK = "trial_feedback"
    TRANSFORMATION = "transformation"
    TIMELINE_EVENT = "timeline_event"
    COMPLETION = "completion"
```

### State Transitions
```
WELCOME -> GREATNESS_MIRROR (user starts)
GREATNESS_MIRROR -> ORDER_REVEAL (submit admired person)
ORDER_REVEAL -> CHARACTER_CREATION (select archetype)
CHARACTER_CREATION -> CHAPTER_INTRO (start journey, chapter=1)
CHAPTER_INTRO -> TRIAL_ATTEMPT (begin trial)
TRIAL_ATTEMPT -> TRIAL_EVALUATION (submission ready)
TRIAL_EVALUATION -> TRIAL_FEEDBACK (if failed)
TRIAL_EVALUATION -> TRANSFORMATION (if passed)
TRIAL_FEEDBACK -> TRIAL_ATTEMPT (retry)
TRANSFORMATION -> TIMELINE_EVENT (save moment)
TIMELINE_EVENT -> CHAPTER_INTRO (next chapter) OR COMPLETION (if chapter=8)
```

### State Data Model
```python
@dataclass
class SessionState:
    session_id: str
    state: GameState
    data: dict  # State-specific data
    cost_log: list[CostEntry]
    created_at: datetime
    updated_at: datetime
```

### Cost Tracking
```python
@dataclass
class CostEntry:
    state: GameState
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    model: str
    timestamp: datetime
```

## Data Models

### Character
```python
@dataclass
class Character:
    name: str
    order: str  # mythic, spartan, atelier, zen, athlete, commander, futurist
    archetype: str
    backstory: dict
    current_chapter: int
    coherence_level: float
```

### TrialAttempt
```python
@dataclass
class TrialAttempt:
    chapter: int
    attempt_number: int
    submission: str
    evaluation: dict
    passed: bool
    feedback: str
    cost: CostEntry
```

### Timeline
```python
@dataclass
class TimelineEvent:
    chapter: int
    narrative: str
    transformation: str
    timestamp: datetime
```

## API Design

### REST Endpoints

#### Session Management
- `POST /api/session` - Create new session
- `GET /api/session/{session_id}` - Get session state
- `DELETE /api/session/{session_id}` - Delete session

#### State Transitions
- `POST /api/state/advance` - Advance to next state with data
- `GET /api/state/current` - Get current state and UI data

#### Game Actions
- `POST /api/mirror` - Analyze admired person -> Order
- `POST /api/character` - Create character
- `POST /api/trial/attempt` - AI attempts trial
- `POST /api/trial/evaluate` - Evaluate submission
- `GET /api/timeline` - Get full timeline

#### Cost Tracking
- `GET /api/cost/{session_id}` - Get cost breakdown
- `GET /api/cost/total` - Get total cost for session

### WebSocket (Optional for Real-time Updates)
- `/ws/{session_id}` - Real-time state updates

## Database Schema (SQLite)

### sessions
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    state TEXT NOT NULL,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### cost_log
```sql
CREATE TABLE cost_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    state TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    model TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### characters
```sql
CREATE TABLE characters (
    session_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    order_type TEXT NOT NULL,
    archetype TEXT NOT NULL,
    backstory JSON NOT NULL,
    current_chapter INTEGER DEFAULT 1,
    coherence_level REAL DEFAULT 1.0,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### timeline_events
```sql
CREATE TABLE timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    narrative TEXT NOT NULL,
    transformation TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

## OpenRouter Integration

### Configuration
```python
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"  # or cheaper model
```

### Cost Calculation
```python
# OpenRouter returns usage in response
{
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 200,
        "total_tokens": 300
    }
}

# Calculate cost based on model pricing
# Store in cost_log table
```

### Prompt Templates
Use the AI Prompt Library JSON for all prompts:
- trial_attemptor
- trial_evaluator
- feedback_provider
- timeline_generator

## Frontend Structure

### Minimal HTML/JS App
```
/static
  /css
    style.css (minimal, <5kb)
  /js
    alpine.min.js (15kb CDN)
    app.js (main application logic)
  index.html
```

### State-Driven UI
Each state renders a specific view:
```javascript
const stateViews = {
    welcome: () => renderWelcome(),
    greatness_mirror: () => renderMirror(),
    order_reveal: () => renderOrder(),
    // ... etc
}
```

### Real-time Updates
- Poll `/api/state/current` every 2s when AI is working
- Show loading indicators
- Update UI based on state changes

## Docker Setup

### Dockerfile
```dockerfile
FROM python:3.11-alpine

WORKDIR /app

# Minimal dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./data:/app/data
```

### Requirements.txt (Minimal)
```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.1  # For OpenRouter API calls
```

## File Structure
```
the-greatness-path/
├── main.py                 # FastAPI app entry point
├── state_machine.py        # State machine logic
├── models.py              # Data models
├── database.py            # SQLite operations
├── openrouter.py          # OpenRouter client
├── prompts.py             # AI prompt templates
├── cost_tracker.py        # Cost measurement
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── data/                  # SQLite DB storage
│   └── game.db
└── static/                # Frontend
    ├── index.html
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Cost Tracking Implementation

### Cost Tracker Class
```python
class CostTracker:
    def __init__(self, db):
        self.db = db

    def log_cost(self, session_id: str, state: GameState,
                 usage: dict, model: str):
        # Calculate cost based on model pricing
        cost = self._calculate_cost(usage, model)

        # Store in database
        self.db.insert_cost_log(
            session_id=session_id,
            state=state.value,
            prompt_tokens=usage['prompt_tokens'],
            completion_tokens=usage['completion_tokens'],
            cost_usd=cost,
            model=model
        )

        return cost

    def get_session_cost(self, session_id: str) -> float:
        return self.db.get_total_cost(session_id)

    def get_state_breakdown(self, session_id: str) -> dict:
        return self.db.get_cost_by_state(session_id)
```

### Model Pricing (Configurable)
```python
MODEL_PRICING = {
    "anthropic/claude-3.5-sonnet": {
        "prompt": 0.003,  # per 1k tokens
        "completion": 0.015
    },
    "meta-llama/llama-3.1-8b-instruct": {
        "prompt": 0.0001,
        "completion": 0.0001
    }
}
```

## State Machine Implementation

### Core State Machine
```python
class GameStateMachine:
    def __init__(self, db, openrouter, cost_tracker):
        self.db = db
        self.openrouter = openrouter
        self.cost_tracker = cost_tracker

    async def transition(self, session_id: str,
                        action: str, data: dict) -> dict:
        # Get current state
        session = self.db.get_session(session_id)
        current_state = GameState(session['state'])

        # Execute state-specific logic
        handler = self._get_handler(current_state)
        result = await handler(session_id, data)

        # Update state
        next_state = self._next_state(current_state, result)
        self.db.update_session(session_id, next_state, result)

        return result

    def _get_handler(self, state: GameState):
        handlers = {
            GameState.GREATNESS_MIRROR: self._handle_mirror,
            GameState.TRIAL_ATTEMPT: self._handle_trial_attempt,
            # ... etc
        }
        return handlers[state]

    async def _handle_mirror(self, session_id: str, data: dict):
        # Call OpenRouter to analyze admired person
        response = await self.openrouter.analyze_person(
            person=data['admired_person']
        )

        # Track cost
        self.cost_tracker.log_cost(
            session_id,
            GameState.GREATNESS_MIRROR,
            response['usage'],
            response['model']
        )

        return {
            'order': response['order'],
            'archetypes': response['archetypes'],
            'explanation': response['explanation']
        }
```

## Deployment to Hetzner

### Steps
1. Create Hetzner Cloud instance (CX11 or larger)
2. Install Docker
3. Clone repo
4. Set environment variables
5. Run `docker-compose up -d`

### Environment Variables
```bash
OPENROUTER_API_KEY=your_key_here
DATABASE_PATH=/app/data/game.db
PORT=8000
```

## Performance Considerations

### Caching
- Cache common narratives (same order/chapter combos)
- Cache order analysis for popular people
- Store in SQLite cache table

### Optimization
- Use smallest viable model for each task
- Batch database operations
- Minimize frontend JS bundle
- Use HTTP/2 for static assets

## Security
- Rate limiting per session
- Input validation on all endpoints
- Sanitize user inputs before LLM calls
- CORS configuration for production
- HTTPS only in production

## Monitoring
- Log all API calls
- Track error rates
- Monitor cost per session
- Alert on high costs
