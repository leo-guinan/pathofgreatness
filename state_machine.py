"""Core game state machine."""
import uuid
from typing import Dict, Optional
from models import GameState, Character, TrialAttempt, TimelineEvent, STATE_TRANSITIONS
from database import Database
from openrouter import OpenRouterClient
from cost_tracker import CostTracker
import prompts


# Chapter themes (8 chapters from the book)
CHAPTER_THEMES = {
    1: {"title": "Coherence", "description": "The foundation of all greatness"},
    2: {"title": "Vision", "description": "Seeing what others cannot"},
    3: {"title": "Discipline", "description": "The daily practice of excellence"},
    4: {"title": "Craft", "description": "Mastery through iteration"},
    5: {"title": "Performance", "description": "Showing up when it matters"},
    6: {"title": "Leadership", "description": "Guiding others to greatness"},
    7: {"title": "Innovation", "description": "Creating the future"},
    8: {"title": "Legacy", "description": "What you leave behind"}
}

# Simplified trial instructions (for MVP)
TRIAL_INSTRUCTIONS = {
    1: "Reflect on a moment today when you felt most coherent and focused. What were you doing? What made it different from when you feel scattered?",
    2: "Describe a vision you have for your future that excites you. What would achieving it require? What's the first step?",
    3: "What's one practice you commit to doing daily for the next week? Why this practice? How will you ensure you do it?",
    4: "Choose one skill you want to improve. What specific action can you take tomorrow to practice it? How will you measure improvement?",
    5: "When do you perform at your best? Describe the conditions. How can you create these conditions more often?",
    6: "Think of someone you want to help succeed. What's one action you can take this week to support their growth?",
    7: "What's one problem you see that others don't? How might you solve it differently?",
    8: "What do you want to be remembered for? What actions align with this legacy?"
}

# Seal requirements (what must be in the submission)
SEAL_REQUIREMENTS = {
    1: "A specific moment described, what you were doing, and what made it coherent",
    2: "A clear vision, what it requires, and a first step",
    3: "A daily practice, why you chose it, and how you'll ensure consistency",
    4: "A specific skill, an action for tomorrow, and how you'll measure progress",
    5: "Conditions for peak performance and how to create them more often",
    6: "A specific person and one action to support them this week",
    7: "A problem others don't see and a different approach to solving it",
    8: "What you want to be remembered for and actions that align with it"
}


class GameStateMachine:
    """Manages game state transitions and AI interactions."""

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
            data={}
        )
        return session_id

    def get_current_state(self, session_id: str) -> Optional[Dict]:
        """Get current session state and UI data."""
        session = self.db.get_session(session_id)
        if not session:
            return None

        state = GameState(session.state)

        # Get character if exists
        character = self.db.get_character(session_id)
        character_data = character.to_dict() if character else None

        # Get cost info
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
                "title": "Welcome to The Path of Greatness",
                "description": "An interactive journey through the 8 chapters of greatness",
                "action": "Begin your journey"
            }

        elif state == GameState.GREATNESS_MIRROR:
            return {
                "title": "The Greatness Mirror",
                "description": "Who do you admire most? This person reveals your Order - your path to greatness.",
                "prompt": "Enter the name of someone you admire:",
                "action": "Reveal my Order"
            }

        elif state == GameState.ORDER_REVEAL:
            return {
                "title": f"You belong to The Order of {data.get('order', '').title()}",
                "description": data.get('explanation', ''),
                "archetypes": data.get('archetypes', []),
                "action": "Choose your archetype"
            }

        elif state == GameState.CHARACTER_CREATION:
            return {
                "title": "Create Your Character",
                "description": "Tell us about yourself to personalize your journey",
                "fields": [
                    {"name": "name", "label": "Your name", "type": "text"},
                    {"name": "age", "label": "Your age", "type": "number"},
                    {"name": "situation", "label": "Current life situation (one sentence)", "type": "text"},
                    {"name": "struggle", "label": "Biggest struggle right now (one sentence)", "type": "text"},
                    {"name": "greatness", "label": "What greatness means to you (one sentence)", "type": "text"}
                ],
                "action": "Begin the journey"
            }

        elif state == GameState.CHAPTER_INTRO:
            chapter = data.get('current_chapter', 1)
            theme = CHAPTER_THEMES.get(chapter, {})
            return {
                "title": f"Chapter {chapter}: {theme.get('title', '')}",
                "description": theme.get('description', ''),
                "narrative": data.get('chapter_intro', ''),
                "action": "Begin trial"
            }

        elif state == GameState.TRIAL_ATTEMPT:
            return {
                "title": "Trial in Progress",
                "description": "Your character is attempting the trial...",
                "status": "in_progress",
                "attempt_number": data.get('attempt_number', 1)
            }

        elif state == GameState.TRIAL_EVALUATION:
            return {
                "title": "Evaluating Submission",
                "description": "Assessing your character's work...",
                "status": "evaluating"
            }

        elif state == GameState.TRIAL_FEEDBACK:
            return {
                "title": "Feedback",
                "description": "Your character received guidance",
                "feedback": data.get('feedback', ''),
                "attempt_number": data.get('attempt_number', 1),
                "action": "Try again"
            }

        elif state == GameState.TRANSFORMATION:
            chapter = data.get('current_chapter', 1)
            return {
                "title": "Transformation",
                "description": f"You completed Chapter {chapter}",
                "transformation": data.get('transformation', ''),
                "action": "Continue"
            }

        elif state == GameState.TIMELINE_EVENT:
            return {
                "title": "Your Journey",
                "description": "A moment added to your timeline",
                "event": data.get('timeline_event', ''),
                "action": "Continue"
            }

        elif state == GameState.COMPLETION:
            timeline = self.db.get_timeline(data.get('session_id', ''))
            return {
                "title": "Journey Complete",
                "description": "You have walked The Path of Greatness",
                "timeline": [event.to_dict() for event in timeline],
                "transformations": data.get('transformations', []),
                "action": "View full timeline"
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
            result = await self._handle_order_reveal(session_id, input_data)
            next_state = GameState.CHARACTER_CREATION

        elif current_state == GameState.CHARACTER_CREATION:
            result = await self._handle_character_creation(session_id, input_data)
            next_state = GameState.CHAPTER_INTRO

        elif current_state == GameState.CHAPTER_INTRO:
            result = await self._handle_chapter_intro(session_id, input_data)
            next_state = GameState.TRIAL_ATTEMPT

        elif current_state == GameState.TRIAL_ATTEMPT:
            result = await self._handle_trial_attempt(session_id, input_data)
            next_state = GameState.TRIAL_EVALUATION

        elif current_state == GameState.TRIAL_EVALUATION:
            result = await self._handle_trial_evaluation(session_id, input_data)
            # Next state depends on evaluation
            if result.get('passed'):
                next_state = GameState.TRANSFORMATION
            else:
                next_state = GameState.TRIAL_FEEDBACK

        elif current_state == GameState.TRIAL_FEEDBACK:
            result = {"feedback_shown": True}
            next_state = GameState.TRIAL_ATTEMPT

        elif current_state == GameState.TRANSFORMATION:
            result = await self._handle_transformation(session_id, input_data)
            next_state = GameState.TIMELINE_EVENT

        elif current_state == GameState.TIMELINE_EVENT:
            result = await self._handle_timeline_event(session_id, input_data)
            # Check if more chapters
            character = self.db.get_character(session_id)
            if character and character.current_chapter >= 8:
                next_state = GameState.COMPLETION
            else:
                # Advance to next chapter
                if character:
                    character.current_chapter += 1
                    self.db.save_character(session_id, character)
                next_state = GameState.CHAPTER_INTRO

        elif current_state == GameState.COMPLETION:
            result = {"completed": True}
            next_state = GameState.COMPLETION  # Terminal state

        else:
            raise ValueError(f"Unknown state: {current_state}")

        # Update session
        merged_data = {**session.data, **result}
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

        # Get prompts
        prompt_data = prompts.get_greatness_mirror_prompt(admired_person)

        # Call AI
        response = await self.openrouter.analyze_person(admired_person, prompt_data)

        # Track cost
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

    async def _handle_order_reveal(self, session_id: str, data: dict) -> dict:
        """Handle archetype selection."""
        archetype = data.get('archetype', '')
        if not archetype:
            raise ValueError("archetype is required")

        return {'selected_archetype': archetype}

    async def _handle_character_creation(self, session_id: str, data: dict) -> dict:
        """Handle character creation."""
        session = self.db.get_session(session_id)

        # Create character
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

        # Save character
        self.db.save_character(session_id, character)

        return {
            'character_created': True,
            'current_chapter': 1
        }

    async def _handle_chapter_intro(self, session_id: str, data: dict) -> dict:
        """Generate chapter introduction narrative."""
        character = self.db.get_character(session_id)
        if not character:
            raise ValueError("Character not found")

        chapter_num = character.current_chapter
        theme = CHAPTER_THEMES.get(chapter_num, {})

        # Generate intro narrative
        prompt_data = prompts.get_chapter_intro_prompt(
            character.to_dict(),
            chapter_num,
            theme.get('title', '')
        )

        response = await self.openrouter.generate_narrative(prompt_data)

        # Track cost
        self.cost_tracker.log_cost(
            session_id,
            GameState.CHAPTER_INTRO,
            response['usage'],
            response['cost'],
            response['model']
        )

        return {
            'current_chapter': chapter_num,
            'chapter_intro': response['narrative'],
            'attempt_number': 1,
            'previous_attempts': []
        }

    async def _handle_trial_attempt(self, session_id: str, data: dict) -> dict:
        """AI attempts the trial."""
        session = self.db.get_session(session_id)
        character = self.db.get_character(session_id)

        chapter = character.current_chapter
        attempt_number = session.data.get('attempt_number', 1)
        previous_attempts = session.data.get('previous_attempts', [])

        # Get trial instructions
        trial_instructions = TRIAL_INSTRUCTIONS.get(chapter, "Reflect on your journey so far.")
        seal_requirements = SEAL_REQUIREMENTS.get(chapter, "A thoughtful reflection")

        # Get prompt
        prompt_data = prompts.get_trial_attemptor_prompt(
            trial_instructions,
            seal_requirements,
            previous_attempts,
            character.order
        )

        # AI attempts trial
        response = await self.openrouter.attempt_trial(prompt_data)

        # Track cost
        self.cost_tracker.log_cost(
            session_id,
            GameState.TRIAL_ATTEMPT,
            response['usage'],
            response['cost'],
            response['model']
        )

        return {
            'submission': response['submission'],
            'trial_instructions': trial_instructions,
            'seal_requirements': seal_requirements
        }

    async def _handle_trial_evaluation(self, session_id: str, data: dict) -> dict:
        """Evaluate trial submission."""
        session = self.db.get_session(session_id)
        character = self.db.get_character(session_id)

        submission = session.data.get('submission', '')
        trial_instructions = session.data.get('trial_instructions', '')
        seal_requirements = session.data.get('seal_requirements', '')

        # Simple requirements check (for MVP)
        requirements_json = [{"requirement_number": 1, "text": seal_requirements}]

        # Get prompt
        prompt_data = prompts.get_trial_evaluator_prompt(
            trial_instructions,
            seal_requirements,
            submission,
            requirements_json
        )

        # Evaluate
        response = await self.openrouter.evaluate_trial(prompt_data)

        # Track cost
        self.cost_tracker.log_cost(
            session_id,
            GameState.TRIAL_EVALUATION,
            response['usage'],
            response['cost'],
            response['model']
        )

        evaluation = response['evaluation']
        passed = evaluation.get('passed', False)

        result = {
            'evaluation': evaluation,
            'passed': passed
        }

        # If failed, generate feedback
        if not passed:
            attempt_number = session.data.get('attempt_number', 1)

            feedback_prompt = prompts.get_feedback_provider_prompt(
                trial_instructions,
                submission,
                evaluation,
                attempt_number,
                "needs_revision"
            )

            feedback_response = await self.openrouter.provide_feedback(feedback_prompt)

            # Track cost
            self.cost_tracker.log_cost(
                session_id,
                GameState.TRIAL_EVALUATION,
                feedback_response['usage'],
                feedback_response['cost'],
                feedback_response['model']
            )

            result['feedback'] = feedback_response['feedback']

            # Store attempt
            previous_attempts = session.data.get('previous_attempts', [])
            previous_attempts.append({
                'submission': submission,
                'evaluation': evaluation,
                'feedback': feedback_response['feedback']
            })

            result['previous_attempts'] = previous_attempts
            result['attempt_number'] = attempt_number + 1

        return result

    async def _handle_transformation(self, session_id: str, data: dict) -> dict:
        """Generate transformation moment."""
        character = self.db.get_character(session_id)
        chapter_num = character.current_chapter
        theme = CHAPTER_THEMES.get(chapter_num, {})

        # Generate transformation
        prompt_data = prompts.get_transformation_prompt(
            character.to_dict(),
            chapter_num,
            theme.get('title', ''),
            {'status': 'passed'}
        )

        response = await self.openrouter.generate_narrative(prompt_data, max_tokens=300)

        # Track cost
        self.cost_tracker.log_cost(
            session_id,
            GameState.TRANSFORMATION,
            response['usage'],
            response['cost'],
            response['model']
        )

        return {
            'transformation': response['narrative']
        }

    async def _handle_timeline_event(self, session_id: str, data: dict) -> dict:
        """Generate and save timeline event."""
        session = self.db.get_session(session_id)
        character = self.db.get_character(session_id)
        chapter_num = character.current_chapter

        # Generate timeline narrative
        prompt_data = prompts.get_timeline_generator_prompt(
            character.to_dict(),
            chapter_num,
            {'status': 'passed'}
        )

        response = await self.openrouter.generate_narrative(prompt_data, max_tokens=200)

        # Track cost
        self.cost_tracker.log_cost(
            session_id,
            GameState.TIMELINE_EVENT,
            response['usage'],
            response['cost'],
            response['model']
        )

        # Save to timeline
        event = TimelineEvent(
            chapter=chapter_num,
            narrative=response['narrative'],
            transformation=session.data.get('transformation', '')
        )

        self.db.add_timeline_event(session_id, event)

        return {
            'timeline_event': response['narrative'],
            'session_id': session_id
        }
