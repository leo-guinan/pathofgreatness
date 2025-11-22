"""Data models for The Greatness Path game."""
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Optional


class GameState(Enum):
    """Game states in the state machine."""
    WELCOME = "welcome"
    GREATNESS_MIRROR = "greatness_mirror"
    ORDER_REVEAL = "order_reveal"
    CHARACTER_CREATION = "character_creation"
    CHAPTER_BEFORE = "chapter_before"
    CHAPTER_AFTER = "chapter_after"
    COMPLETION = "completion"
    SALES_PAGE = "sales_page"


class Order(Enum):
    """The seven orders."""
    MYTHIC = "mythic"
    SPARTAN = "spartan"
    ATELIER = "atelier"
    ZEN = "zen"
    ATHLETE = "athlete"
    COMMANDER = "commander"
    FUTURIST = "futurist"


@dataclass
class CostEntry:
    """Cost tracking for a single API call."""
    state: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    model: str
    timestamp: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Character:
    """Player character."""
    name: str
    order: str
    archetype: str
    backstory: dict
    current_chapter: int = 1
    coherence_level: float = 1.0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        return Character(**data)


@dataclass
class ChapterProgress:
    """Progress through a chapter."""
    chapter: int
    before_narrative: str
    after_narrative: str
    transformation: str
    timestamp: str

    def to_dict(self):
        return asdict(self)


@dataclass
class TimelineEvent:
    """A moment in the player's journey."""
    chapter: int
    narrative: str
    transformation: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        return TimelineEvent(**data)


@dataclass
class SessionState:
    """Complete session state."""
    session_id: str
    state: str
    data: dict
    created_at: str
    updated_at: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        return SessionState(**data)


# State transition map
STATE_TRANSITIONS = {
    GameState.WELCOME: [GameState.GREATNESS_MIRROR],
    GameState.GREATNESS_MIRROR: [GameState.ORDER_REVEAL],
    GameState.ORDER_REVEAL: [GameState.CHARACTER_CREATION],
    GameState.CHARACTER_CREATION: [GameState.CHAPTER_BEFORE],
    GameState.CHAPTER_BEFORE: [GameState.CHAPTER_AFTER],
    GameState.CHAPTER_AFTER: [GameState.CHAPTER_BEFORE, GameState.COMPLETION],
    GameState.COMPLETION: [GameState.SALES_PAGE],
    GameState.SALES_PAGE: []  # Terminal state
}


# Model pricing (per 1k tokens)
MODEL_PRICING = {
    "anthropic/claude-3.5-sonnet": {
        "prompt": 0.003,
        "completion": 0.015
    },
    "anthropic/claude-3-haiku": {
        "prompt": 0.00025,
        "completion": 0.00125
    },
    "meta-llama/llama-3.1-8b-instruct": {
        "prompt": 0.00005,
        "completion": 0.00005
    },
    "meta-llama/llama-3.2-3b-instruct": {
        "prompt": 0.00002,
        "completion": 0.00002
    }
}


def calculate_cost(usage: dict, model: str) -> float:
    """Calculate cost based on token usage and model."""
    if model not in MODEL_PRICING:
        # Default to Claude Haiku pricing if unknown
        pricing = MODEL_PRICING["anthropic/claude-3-haiku"]
    else:
        pricing = MODEL_PRICING[model]

    prompt_cost = (usage["prompt_tokens"] / 1000) * pricing["prompt"]
    completion_cost = (usage["completion_tokens"] / 1000) * pricing["completion"]

    return prompt_cost + completion_cost
