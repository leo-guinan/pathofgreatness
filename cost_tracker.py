"""Cost tracking for AI API calls."""
from datetime import datetime
from typing import Dict, List
from models import CostEntry, GameState
from database import Database


class CostTracker:
    """Track and report costs for AI API calls."""

    def __init__(self, db: Database):
        self.db = db

    def log_cost(
        self,
        session_id: str,
        state: GameState,
        usage: dict,
        cost: float,
        model: str
    ) -> CostEntry:
        """Log cost for an API call."""
        # Create cost entry
        entry = CostEntry(
            state=state.value,
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            cost_usd=cost,
            model=model,
            timestamp=datetime.utcnow().isoformat()
        )

        # Store in database
        self.db.insert_cost_log(
            session_id=session_id,
            state=state.value,
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            cost_usd=cost,
            model=model
        )

        return entry

    def get_session_cost(self, session_id: str) -> float:
        """Get total cost for a session."""
        return self.db.get_total_cost(session_id)

    def get_state_breakdown(self, session_id: str) -> Dict[str, float]:
        """Get cost breakdown by state."""
        return self.db.get_cost_by_state(session_id)

    def get_cost_log(self, session_id: str) -> List[CostEntry]:
        """Get full cost log for a session."""
        return self.db.get_cost_log(session_id)

    def get_cost_report(self, session_id: str) -> dict:
        """Get comprehensive cost report for a session."""
        total = self.get_session_cost(session_id)
        breakdown = self.get_state_breakdown(session_id)
        log = self.get_cost_log(session_id)

        # Calculate totals
        total_prompt_tokens = sum(entry.prompt_tokens for entry in log)
        total_completion_tokens = sum(entry.completion_tokens for entry in log)
        total_tokens = total_prompt_tokens + total_completion_tokens

        # Get model breakdown
        model_costs = {}
        for entry in log:
            if entry.model not in model_costs:
                model_costs[entry.model] = 0.0
            model_costs[entry.model] += entry.cost_usd

        return {
            "session_id": session_id,
            "total_cost_usd": total,
            "total_tokens": total_tokens,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "cost_by_state": breakdown,
            "cost_by_model": model_costs,
            "num_api_calls": len(log),
            "average_cost_per_call": total / len(log) if log else 0.0
        }

    def format_cost_report(self, session_id: str) -> str:
        """Format cost report as readable string."""
        report = self.get_cost_report(session_id)

        output = f"""
Cost Report for Session: {session_id}
{'=' * 60}

Total Cost: ${report['total_cost_usd']:.4f}
Total Tokens: {report['total_tokens']:,}
  - Prompt: {report['prompt_tokens']:,}
  - Completion: {report['completion_tokens']:,}

API Calls: {report['num_api_calls']}
Average Cost per Call: ${report['average_cost_per_call']:.4f}

Cost by State:
"""
        for state, cost in sorted(report['cost_by_state'].items(), key=lambda x: -x[1]):
            output += f"  {state:20s}: ${cost:.4f}\n"

        output += "\nCost by Model:\n"
        for model, cost in sorted(report['cost_by_model'].items(), key=lambda x: -x[1]):
            output += f"  {model:40s}: ${cost:.4f}\n"

        return output
