"""SQLite database operations."""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from models import SessionState, CostEntry, Character, TimelineEvent


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str = "data/game.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Cost log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                state TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                model TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Characters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                session_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                order_type TEXT NOT NULL,
                archetype TEXT NOT NULL,
                backstory JSON NOT NULL,
                current_chapter INTEGER DEFAULT 1,
                coherence_level REAL DEFAULT 1.0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Timeline events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                chapter INTEGER NOT NULL,
                narrative TEXT NOT NULL,
                transformation TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        conn.commit()
        conn.close()

    def _get_conn(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Session operations
    def create_session(self, session_id: str, state: str, data: dict) -> SessionState:
        """Create a new session."""
        conn = self._get_conn()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO sessions (session_id, state, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, state, json.dumps(data), now, now)
        )

        conn.commit()
        conn.close()

        return SessionState(
            session_id=session_id,
            state=state,
            data=data,
            created_at=now,
            updated_at=now
        )

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session by ID."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return SessionState(
            session_id=row['session_id'],
            state=row['state'],
            data=json.loads(row['data']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def update_session(self, session_id: str, state: str, data: dict):
        """Update session state."""
        conn = self._get_conn()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()
        cursor.execute(
            "UPDATE sessions SET state = ?, data = ?, updated_at = ? WHERE session_id = ?",
            (state, json.dumps(data), now, session_id)
        )

        conn.commit()
        conn.close()

    def delete_session(self, session_id: str):
        """Delete a session and all related data."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM timeline_events WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM characters WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM cost_log WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

        conn.commit()
        conn.close()

    # Cost tracking operations
    def insert_cost_log(self, session_id: str, state: str, prompt_tokens: int,
                       completion_tokens: int, cost_usd: float, model: str):
        """Log cost for an API call."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO cost_log (session_id, state, prompt_tokens, completion_tokens, cost_usd, model)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, state, prompt_tokens, completion_tokens, cost_usd, model)
        )

        conn.commit()
        conn.close()

    def get_total_cost(self, session_id: str) -> float:
        """Get total cost for a session."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT SUM(cost_usd) as total FROM cost_log WHERE session_id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()

        return row['total'] or 0.0

    def get_cost_by_state(self, session_id: str) -> Dict[str, float]:
        """Get cost breakdown by state."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT state, SUM(cost_usd) as total FROM cost_log WHERE session_id = ? GROUP BY state",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return {row['state']: row['total'] for row in rows}

    def get_cost_log(self, session_id: str) -> List[CostEntry]:
        """Get full cost log for a session."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM cost_log WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            CostEntry(
                state=row['state'],
                prompt_tokens=row['prompt_tokens'],
                completion_tokens=row['completion_tokens'],
                cost_usd=row['cost_usd'],
                model=row['model'],
                timestamp=row['timestamp']
            )
            for row in rows
        ]

    # Character operations
    def save_character(self, session_id: str, character: Character):
        """Save or update character."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT OR REPLACE INTO characters
               (session_id, name, order_type, archetype, backstory, current_chapter, coherence_level)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, character.name, character.order, character.archetype,
             json.dumps(character.backstory), character.current_chapter, character.coherence_level)
        )

        conn.commit()
        conn.close()

    def get_character(self, session_id: str) -> Optional[Character]:
        """Get character for session."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM characters WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Character(
            name=row['name'],
            order=row['order_type'],
            archetype=row['archetype'],
            backstory=json.loads(row['backstory']),
            current_chapter=row['current_chapter'],
            coherence_level=row['coherence_level']
        )

    # Timeline operations
    def add_timeline_event(self, session_id: str, event: TimelineEvent):
        """Add timeline event."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO timeline_events (session_id, chapter, narrative, transformation)
               VALUES (?, ?, ?, ?)""",
            (session_id, event.chapter, event.narrative, event.transformation)
        )

        conn.commit()
        conn.close()

    def get_timeline(self, session_id: str) -> List[TimelineEvent]:
        """Get full timeline for session."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM timeline_events WHERE session_id = ? ORDER BY chapter",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            TimelineEvent(
                chapter=row['chapter'],
                narrative=row['narrative'],
                transformation=row['transformation'],
                timestamp=row['timestamp']
            )
            for row in rows
        ]
