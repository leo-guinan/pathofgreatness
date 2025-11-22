"""FastAPI backend for The Greatness Path game."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

from database import Database
from openrouter import OpenRouterClient
from cost_tracker import CostTracker
from state_machine_simple import GameStateMachine


# Ensure data directory exists
Path("data").mkdir(exist_ok=True)

# Initialize components
db = Database("data/game.db")
openrouter = OpenRouterClient()
cost_tracker = CostTracker(db)
game = GameStateMachine(db, openrouter, cost_tracker)

# FastAPI app
app = FastAPI(
    title="The Greatness Path",
    description="Interactive journey through 8 chapters of greatness",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Request/Response models
class CreateSessionResponse(BaseModel):
    session_id: str
    state: str


class TransitionRequest(BaseModel):
    session_id: str
    action: str
    data: Dict[str, Any]


class StateResponse(BaseModel):
    session_id: str
    state: str
    data: dict
    character: Optional[dict]
    total_cost: float
    ui_data: dict


class CostResponse(BaseModel):
    session_id: str
    total_cost_usd: float
    total_tokens: int
    cost_by_state: Dict[str, float]
    cost_by_model: Dict[str, float]
    num_api_calls: int


# Routes

@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")


@app.post("/api/session", response_model=CreateSessionResponse)
async def create_session():
    """Create a new game session."""
    session_id = game.create_session()
    return CreateSessionResponse(
        session_id=session_id,
        state="welcome"
    )


@app.get("/api/session/{session_id}", response_model=StateResponse)
async def get_session(session_id: str):
    """Get current session state."""
    state = game.get_current_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    return StateResponse(**state)


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    db.delete_session(session_id)
    return {"success": True}


@app.post("/api/transition")
async def transition(request: TransitionRequest):
    """Execute a state transition."""
    try:
        result = await game.transition(
            request.session_id,
            request.action,
            request.data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cost/{session_id}", response_model=CostResponse)
async def get_cost(session_id: str):
    """Get cost breakdown for session."""
    report = cost_tracker.get_cost_report(session_id)
    return CostResponse(**report)


@app.get("/api/timeline/{session_id}")
async def get_timeline(session_id: str):
    """Get timeline for session."""
    timeline = db.get_timeline(session_id)
    return {"timeline": [event.to_dict() for event in timeline]}


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
