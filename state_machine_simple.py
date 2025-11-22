"""Simplified game state machine - Before/After chapter structure."""
import uuid
from typing import Dict, Optional
from models import GameState, Character, ChapterProgress, TimelineEvent
from database import Database
from openrouter import OpenRouterClient
from cost_tracker import CostTracker
import prompts


# Chapter themes (8 chapters from the book)
CHAPTER_THEMES = {
    1: {
        "title": "Coherence",
        "description": "The foundation - aligning your actions with your vision"
    },
    2: {
        "title": "Vision",
        "description": "Seeing the future you want to create"
    },
    3: {
        "title": "Discipline",
        "description": "The daily practice that builds greatness"
    },
    4: {
        "title": "Craft",
        "description": "Mastery through deliberate refinement"
    },
    5: {
        "title": "Performance",
        "description": "Showing up when it matters most"
    },
    6: {
        "title": "Leadership",
        "description": "Elevating others as you rise"
    },
    7: {
        "title": "Innovation",
        "description": "Creating new paths where none existed"
    },
    8: {
        "title": "Legacy",
        "description": "What endures after you're gone"
    }
}


class GameStateMachine:
    """Manages simplified game state transitions."""

    def __init__(self, db: Database, openrouter: OpenRouterClient, cost_tracker: CostTracker):
        self.db = db
        self.openrouter = openrouter
        self.cost_tracker = cost_tracker

    def create_session(self) -> str:
        """Create a new game session."""
        session_id = str(uuid.uuid4())
        self.db.create_session(
            session_id=session_id,
            state=GameState.WELCOME.value,
            data={"current_chapter": 1}
        )
        return session_id

    def get_current_state(self, session_id: str) -> Optional[Dict]:
        """Get current session state and UI data."""
        session = self.db.get_session(session_id)
        if not session:
            return None

        state = GameState(session.state)
        character = self.db.get_character(session_id)
        character_data = character.to_dict() if character else None
        total_cost = self.cost_tracker.get_session_cost(session_id)

        return {
            "session_id": session_id,
            "state": state.value,
            "data": session.data,
            "character": character_data,
            "total_cost": total_cost,
            "ui_data": self._get_ui_data_for_state(state, session.data, character_data)
        }

    def _get_ui_data_for_state(self, state: GameState, data: dict, character: Optional[dict]) -> dict:
        """Get UI-specific data for current state."""
        if state == GameState.WELCOME:
            return {
                "title": "The Path of Greatness",
                "subtitle": "An Interactive Journey Through 8 Transformations",
                "description": "Watch yourself climb the ladder of greatness, one transformation at a time.",
                "action": "Begin Your Ascent"
            }

        elif state == GameState.GREATNESS_MIRROR:
            return {
                "title": "The Greatness Mirror",
                "description": "Who do you admire most? This person reveals your natural path to greatness.",
                "prompt": "Enter the name of someone you admire:",
                "action": "Reveal My Path"
            }

        elif state == GameState.ORDER_REVEAL:
            return {
                "title": f"You Walk the Path of {data.get('order', '').title()}",
                "description": data.get('explanation', ''),
                "archetypes": data.get('archetypes', []),
                "action": "Choose Your Archetype"
            }

        elif state == GameState.CHARACTER_CREATION:
            return {
                "title": "Your Journey Begins",
                "description": "Tell us about yourself to personalize your transformation.",
                "fields": [
                    {"name": "name", "label": "Your name", "type": "text"},
                    {"name": "age", "label": "Your age", "type": "number"},
                    {"name": "situation", "label": "Where are you now? (one sentence)", "type": "text"},
                    {"name": "struggle", "label": "What holds you back? (one sentence)", "type": "text"},
                    {"name": "greatness", "label": "What does greatness mean to you? (one sentence)", "type": "text"}
                ],
                "action": "Start Climbing"
            }

        elif state == GameState.CHAPTER_BEFORE:
            chapter = data.get('current_chapter', 1)
            theme = CHAPTER_THEMES.get(chapter, {})
            return {
                "title": f"Chapter {chapter}: {theme.get('title', '')}",
                "subtitle": "BEFORE",
                "description": theme.get('description', ''),
                "narrative": data.get('before_narrative', ''),
                "chapter": chapter,
                "total_chapters": 8,
                "action": "Experience the Transformation"
            }

        elif state == GameState.CHAPTER_AFTER:
            chapter = data.get('current_chapter', 1)
            theme = CHAPTER_THEMES.get(chapter, {})
            return {
                "title": f"Chapter {chapter}: {theme.get('title', '')}",
                "subtitle": "AFTER",
                "description": "You have ascended",
                "narrative": data.get('after_narrative', ''),
                "transformation": data.get('transformation_insight', ''),
                "chapter": chapter,
                "total_chapters": 8,
                "action": "Continue Climbing" if chapter < 8 else "Complete Your Journey"
            }

        elif state == GameState.COMPLETION:
            timeline = self.db.get_timeline(data.get('session_id', session_id if 'session_id' in dir() else ''))
            return {
                "title": "You Have Completed The Path",
                "subtitle": "8 Transformations, One Journey",
                "description": "Look back at how far you've climbed.",
                "timeline": [event.to_dict() for event in timeline],
                "total_cost": data.get('total_cost', 0.0),
                "action": "See What's Next"
            }

        elif state == GameState.SALES_PAGE:
            sales_data = data.get('sales_page', {})
            return {
                "headline": sales_data.get('headline', ''),
                "hook": sales_data.get('hook', ''),
                "transformation_proof": sales_data.get('transformation_proof', ''),
                "offer_description": sales_data.get('offer_description', ''),
                "guarantee": sales_data.get('guarantee', ''),
                "cta": sales_data.get('cta', ''),
                "urgency": sales_data.get('urgency', ''),
                "total_cost": data.get('total_cost', 0.0),
                "character_name": character.get('name', 'Seeker') if character else 'Seeker'
            }

        return {}

    async def transition(self, session_id: str, action: str, input_data: dict) -> dict:
        """Execute a state transition."""
        session = self.db.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        current_state = GameState(session.state)

        # Route to appropriate handler
        if current_state == GameState.WELCOME:
            next_state = GameState.GREATNESS_MIRROR
            result = {"ready": True}

        elif current_state == GameState.GREATNESS_MIRROR:
            result = await self._handle_greatness_mirror(session_id, input_data)
            next_state = GameState.ORDER_REVEAL

        elif current_state == GameState.ORDER_REVEAL:
            result = {"selected_archetype": input_data.get('archetype', '')}
            next_state = GameState.CHARACTER_CREATION

        elif current_state == GameState.CHARACTER_CREATION:
            result = await self._handle_character_creation(session_id, input_data)
            # Immediately generate the first chapter's before narrative
            before_result = await self._handle_chapter_before(session_id, {})
            result.update(before_result)
            next_state = GameState.CHAPTER_BEFORE

        elif current_state == GameState.CHAPTER_BEFORE:
            # User clicked to see the transformation
            result = await self._handle_chapter_after(session_id, input_data)
            next_state = GameState.CHAPTER_AFTER

        elif current_state == GameState.CHAPTER_AFTER:
            # User clicked to continue to next chapter
            character = self.db.get_character(session_id)

            if character and character.current_chapter >= 8:
                next_state = GameState.COMPLETION
                result = {"completed": True}
            else:
                # Move to next chapter
                if character:
                    character.current_chapter += 1
                    self.db.save_character(session_id, character)

                # Generate the next chapter's before narrative
                result = await self._handle_chapter_before(session_id, {})
                next_state = GameState.CHAPTER_BEFORE

        elif current_state == GameState.COMPLETION:
            # Generate personalized sales page
            result = await self._handle_sales_page_generation(session_id, input_data)
            next_state = GameState.SALES_PAGE

        elif current_state == GameState.SALES_PAGE:
            result = {"viewed": True}
            next_state = GameState.SALES_PAGE  # Terminal state

        else:
            raise ValueError(f"Unknown state: {current_state}")

        # Update session
        merged_data = {**session.data, **result}
        print(f"DEBUG: Updating session to state={next_state.value}")
        print(f"DEBUG: Merged data keys: {list(merged_data.keys())}")
        if 'after_narrative' in merged_data:
            print(f"DEBUG: after_narrative exists, length={len(merged_data.get('after_narrative', ''))}")
        if 'transformation_insight' in merged_data:
            print(f"DEBUG: transformation_insight exists, length={len(merged_data.get('transformation_insight', ''))}")

        self.db.update_session(session_id, next_state.value, merged_data)

        return {
            "success": True,
            "next_state": next_state.value,
            "data": result
        }

    async def _handle_greatness_mirror(self, session_id: str, data: dict) -> dict:
        """Handle Greatness Mirror analysis."""
        admired_person = data.get('admired_person', '')
        if not admired_person:
            raise ValueError("admired_person is required")

        prompt_data = prompts.get_greatness_mirror_prompt(admired_person)
        response = await self.openrouter.analyze_person(admired_person, prompt_data)

        self.cost_tracker.log_cost(
            session_id,
            GameState.GREATNESS_MIRROR,
            response['usage'],
            response['cost'],
            response['model']
        )

        return {
            'admired_person': admired_person,
            'order': response['order'],
            'archetypes': response['archetypes'],
            'explanation': response['explanation'],
            'traits': response['traits']
        }

    async def _handle_character_creation(self, session_id: str, data: dict) -> dict:
        """Handle character creation."""
        session = self.db.get_session(session_id)

        character = Character(
            name=data.get('name', 'Seeker'),
            order=session.data.get('order', 'mythic'),
            archetype=session.data.get('selected_archetype', 'Seeker'),
            backstory={
                'age': data.get('age', 30),
                'situation': data.get('situation', ''),
                'struggle': data.get('struggle', ''),
                'greatness': data.get('greatness', ''),
                'admired_person': session.data.get('admired_person', '')
            },
            current_chapter=1,
            coherence_level=1.0
        )

        self.db.save_character(session_id, character)

        return {
            'character_created': True,
            'current_chapter': 1
        }

    async def _handle_chapter_before(self, session_id: str, data: dict) -> dict:
        """Generate 'before' narrative for current chapter."""
        character = self.db.get_character(session_id)
        if not character:
            raise ValueError("Character not found")

        chapter_num = character.current_chapter
        theme = CHAPTER_THEMES.get(chapter_num, {})

        # Generate "before" narrative
        prompt_data = prompts.get_chapter_before_prompt(
            character.to_dict(),
            chapter_num,
            theme.get('title', ''),
            theme.get('description', '')
        )

        response = await self.openrouter.generate_narrative(prompt_data, max_tokens=500)

        self.cost_tracker.log_cost(
            session_id,
            GameState.CHAPTER_BEFORE,
            response['usage'],
            response['cost'],
            response['model']
        )

        return {
            'current_chapter': chapter_num,
            'before_narrative': response['narrative']
        }

    async def _handle_chapter_after(self, session_id: str, data: dict) -> dict:
        """Generate 'after' narrative and transformation for current chapter."""
        session = self.db.get_session(session_id)
        character = self.db.get_character(session_id)
        if not character:
            raise ValueError("Character not found")

        chapter_num = character.current_chapter
        theme = CHAPTER_THEMES.get(chapter_num, {})
        before_narrative = session.data.get('before_narrative', '')

        # Generate "after" narrative
        after_prompt = prompts.get_chapter_after_prompt(
            character.to_dict(),
            chapter_num,
            theme.get('title', ''),
            before_narrative
        )

        after_response = await self.openrouter.generate_narrative(after_prompt, max_tokens=500)

        print(f"DEBUG: After narrative generated: {after_response['narrative'][:100]}...")

        self.cost_tracker.log_cost(
            session_id,
            GameState.CHAPTER_AFTER,
            after_response['usage'],
            after_response['cost'],
            after_response['model']
        )

        # Generate transformation insight
        insight_prompt = prompts.get_transformation_insight_prompt(
            character.to_dict(),
            chapter_num,
            theme.get('title', '')
        )

        insight_response = await self.openrouter.generate_narrative(insight_prompt, max_tokens=300)

        print(f"DEBUG: Transformation insight generated: {insight_response['narrative'][:100]}...")

        self.cost_tracker.log_cost(
            session_id,
            GameState.CHAPTER_AFTER,
            insight_response['usage'],
            insight_response['cost'],
            insight_response['model']
        )

        # Save to timeline
        event = TimelineEvent(
            chapter=chapter_num,
            narrative=after_response['narrative'],
            transformation=insight_response['narrative']
        )

        self.db.add_timeline_event(session_id, event)

        return {
            'after_narrative': after_response['narrative'],
            'transformation_insight': insight_response['narrative'],
            'current_chapter': chapter_num,
            'session_id': session_id
        }

    async def _handle_sales_page_generation(self, session_id: str, data: dict) -> dict:
        """Generate personalized sales page."""
        character = self.db.get_character(session_id)
        if not character:
            raise ValueError("Character not found")

        # Get timeline
        timeline = self.db.get_timeline(session_id)
        timeline_data = [event.to_dict() for event in timeline]

        # Get total cost
        total_cost = self.cost_tracker.get_session_cost(session_id)

        # Generate sales page
        prompt_data = prompts.get_sales_page_prompt(
            character.to_dict(),
            timeline_data,
            total_cost
        )

        response = await self.openrouter.generate_narrative(prompt_data, max_tokens=2000)

        print(f"DEBUG: Sales page generated, length={len(response['narrative'])}")

        # Track cost
        self.cost_tracker.log_cost(
            session_id,
            GameState.SALES_PAGE,
            response['usage'],
            response['cost'],
            response['model']
        )

        # Parse JSON response
        try:
            import json
            sales_content = response['narrative'].strip()
            if sales_content.startswith("```json"):
                sales_content = sales_content[7:]
            if sales_content.startswith("```"):
                sales_content = sales_content[3:]
            if sales_content.endswith("```"):
                sales_content = sales_content[:-3]
            sales_content = sales_content.strip()

            sales_page = json.loads(sales_content)
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse sales page JSON: {e}")
            # Fallback to basic template
            sales_page = {
                "headline": "THE PATH OF GREATNESS",
                "hook": f"For ${total_cost:.4f}, you just experienced 8 transformations. Now imagine what $50 can do.",
                "transformation_proof": "You climbed the ladder. You felt the shifts. You know this works.",
                "offer_description": "Chapter 1: The $50 Coherence Breakthrough - The foundation that makes everything else possible.",
                "guarantee": "If you do Chapter 1 properly, you cannot stay the same person.",
                "cta": "Start Chapter 1 Now",
                "urgency": "This is the only time greatness costs $50. Everything after gets more expensive."
            }

        return {
            'sales_page': sales_page,
            'total_cost': total_cost,
            'session_id': session_id
        }
