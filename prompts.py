"""AI prompt templates based on the Prompt Library."""

# Order contexts for personalization
ORDER_CONTEXTS = {
    "mythic": "a Seer seeing visions",
    "spartan": "a Warrior building discipline",
    "atelier": "an Artisan refining craft",
    "zen": "a Sage finding clarity",
    "athlete": "a Champion performing",
    "commander": "a Strategist leading",
    "futurist": "a Navigator seeing patterns"
}

# Temperature settings for different prompt types
TEMPERATURES = {
    "trial_attemptor": 0.8,
    "trial_evaluator": 0.1,
    "feedback_provider": 0.7,
    "timeline_generator": 0.8,
    "mirror_analyzer": 0.3,
    "narrative_generator": 0.8
}


def get_greatness_mirror_prompt(admired_person: str) -> dict:
    """Prompt to analyze admired person and determine Order."""
    return {
        "system": """You are an expert at analyzing what people admire and mapping it to archetypes.
Based on who someone admires, you can determine their natural Order - their path to greatness.

The Seven Orders:
- MYTHIC: Seers who see futures others cannot (artists, visionaries, storytellers)
- SPARTAN: Warriors who build discipline and strength (athletes, military, disciplined practitioners)
- ATELIER: Artisans who refine craft to perfection (craftspeople, designers, makers)
- ZEN: Sages who find clarity through contemplation (philosophers, meditators, spiritual seekers)
- ATHLETE: Champions who perform at peak (competitors, performers, strivers)
- COMMANDER: Strategists who lead and organize (leaders, managers, organizers)
- FUTURIST: Navigators who see patterns and systems (technologists, scientists, futurists)

Respond with valid JSON only.""",

        "user": f"""Analyze this person: {admired_person}

Determine:
1. Which Order do they represent?
2. What specific archetype within that Order?
3. Why does someone who admires them belong to this Order?

Respond with ONLY valid JSON in this format:
{{
  "order": "mythic|spartan|atelier|zen|athlete|commander|futurist",
  "archetypes": ["Archetype 1", "Archetype 2", "Archetype 3"],
  "explanation": "Brief explanation of why this person represents this Order",
  "admired_person_traits": ["trait1", "trait2", "trait3"]
}}""",

        "temperature": TEMPERATURES["mirror_analyzer"]
    }


def get_chapter_before_prompt(character: dict, chapter_num: int,
                             chapter_theme: str, chapter_description: str) -> dict:
    """Prompt for AI to generate 'before' narrative showing current state."""
    order = character.get('order', 'mythic')
    order_context = ORDER_CONTEXTS.get(order, "a seeker")
    name = character.get('name', 'Seeker')
    situation = character.get('backstory', {}).get('situation', '')
    struggle = character.get('backstory', {}).get('struggle', '')

    return {
        "system": f"""You are a narrator for The Path of Greatness.
Write a "before" narrative that shows where {name} is now, before this chapter's transformation.
Show their current struggles, limitations, and where they need to grow.
Make it personal and specific to their journey.""",

        "user": f"""Character: {name}
Order: {order} ({order_context})
Current Situation: {situation}
Current Struggle: {struggle}
Chapter: {chapter_num} - {chapter_theme}
Theme Description: {chapter_description}

Write a "before" narrative (4-6 sentences) that:
1. Shows where {name} is right now in their journey
2. Highlights the gap between where they are and where they could be
3. Sets up the need for this chapter's transformation
4. Makes them feel the tension of their current state
5. Uses "you" language to make it immersive

Focus on showing their current limitations or struggles related to this chapter's theme.""",

        "temperature": TEMPERATURES["narrative_generator"]
    }


def get_chapter_after_prompt(character: dict, chapter_num: int,
                            chapter_theme: str, before_narrative: str) -> dict:
    """Prompt for AI to generate 'after' narrative showing transformation."""
    order = character.get('order', 'mythic')
    name = character.get('name', 'Seeker')

    return {
        "system": f"""You are a narrator for The Path of Greatness.
Write an "after" narrative that shows how {name} has transformed through this chapter.
Show the shift in their understanding, capabilities, or perspective.
Make it feel like genuine growth.""",

        "user": f"""Character: {name}
Order: {order}
Chapter: {chapter_num} - {chapter_theme}

Before State:
{before_narrative}

Write an "after" narrative (4-6 sentences) that:
1. Shows the transformation that has occurred
2. Contrasts clearly with the "before" state
3. Demonstrates new understanding, capability, or perspective
4. Feels earned and real, not superficial
5. Uses "you" language to make it immersive
6. Ends with a sense of ascension - they've climbed higher

Show them standing on a new rung of the ladder of greatness.""",

        "temperature": TEMPERATURES["narrative_generator"]
    }


def get_transformation_insight_prompt(character: dict, chapter_num: int,
                                     chapter_theme: str) -> dict:
    """Prompt for AI to generate the key insight/transformation moment."""
    name = character.get('name', 'Seeker')

    return {
        "system": """You are a guide helping someone realize deep insights.
Write the key insight or realization that emerges from this chapter.
This should be profound but accessible - a truth that changes how they see things.""",

        "user": f"""Character: {name}
Chapter: {chapter_num} - {chapter_theme}

Write the key insight (2-3 sentences) that {name} realizes in this chapter.
Format it as: "You realize..." or "You understand now that..."

Make it:
1. Specific to this chapter's theme
2. Personally transformative
3. A shift in perspective or understanding
4. Something they can carry forward

This is the wisdom they gain from climbing to this rung of greatness.""",

        "temperature": TEMPERATURES["narrative_generator"]
    }


def get_sales_page_prompt(character: dict, timeline: list, total_cost: float) -> dict:
    """Generate personalized sales page based on their journey."""
    name = character.get('name', 'Seeker')
    order = character.get('order', 'mythic')
    struggle = character.get('backstory', {}).get('struggle', 'limitation')
    greatness = character.get('backstory', {}).get('greatness', 'transformation')

    # Extract transformations from timeline
    transformations = [event.get('transformation', '') for event in timeline if event.get('transformation')]
    transformation_summary = '\n'.join([f"- {t}" for t in transformations[:3]])  # First 3

    return {
        "system": """You are a master copywriter creating a personalized sales page.
Your goal is near 100% conversion by making the offer irresistible and personal.
Use their actual journey, their struggles, their transformations to show proof.
Make them feel like this is THE moment to commit deeper.""",

        "user": f"""Create a personalized sales page for {name}.

THEIR JOURNEY DATA:
- Name: {name}
- Order: {order}
- Their struggle: {struggle}
- Their definition of greatness: {greatness}
- Cost of their transformation: ${total_cost:.4f}
- Transformations they experienced:
{transformation_summary}

BASE TEMPLATE TO PERSONALIZE:
{get_sales_template()}

YOUR TASK:
1. Keep the structure and power of the template
2. Personalize with {name}'s actual data
3. Reference their specific struggle and transformations
4. Use the cost they just saw (${total_cost:.4f}) to create contrast with $50
5. Make it feel like this sales page was written specifically for THEM
6. Keep the urgency and conviction
7. Use "you" language throughout

OUTPUT FORMAT:
Return a JSON object with these fields:
{{
    "headline": "Personalized headline",
    "hook": "Opening paragraphs that reference their journey",
    "transformation_proof": "What they just experienced",
    "offer_description": "What Chapter 1 gives them",
    "guarantee": "Why this will work for them specifically",
    "cta": "Clear call to action",
    "urgency": "Why they should act now"
}}

Make every word count. This should feel inevitable.""",

        "temperature": 0.8
    }


def get_sales_template() -> str:
    """Get the base sales template."""
    return """THE PATH OF GREATNESS
Do You Have What It Takes to Be Great?

For $[COST], I Generated an Entire Transformation.
Now imagine what I can do for you with $50.

You just saw it:
For less than [X] pennies, I turned [THEIR STRUGGLE] into [THEIR TRANSFORMATION].

That's what mastery looks like.
No fluff. No filler. No wasting your time or money.
Just transformation.

Now the only question left is:
Are YOU ready to walk your Path?

What You Get in Chapter 1: The $50 Coherence Breakthrough

Chapter 1 takes you from:
scattered → aligned
overwhelmed → in control
reactive → intentional

You get:
✔ The 24-Hour Coherence Challenge
✔ The Coherence Logbook
✔ Your First "Seal"
✔ The First Transformation

This chapter alone is worth $500.
But I'm giving it to you for $50.

Because I want you to win.

The Hard Truth: Most People Won't Do This

Not because it's expensive.
Not because it's hard.
But because stepping into greatness is terrifying.

You know this is your moment.

Your Path Begins Here.
Chapter 1 — $50

[Start Chapter 1 Now →]"""


