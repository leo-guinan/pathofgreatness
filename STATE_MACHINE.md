# State Machine Flow Diagram

## Complete State Transition Map

```
┌──────────────────────────────────────────────────────────────────┐
│                         THE GREATNESS PATH                        │
│                    Interactive State Machine                      │
└──────────────────────────────────────────────────────────────────┘

[START]
   │
   ▼
┌─────────────────┐
│   WELCOME       │  User sees: Title, description
│                 │  Action: "Begin your journey"
│  Cost: $0       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GREATNESS       │  User enters: Admired person
│   MIRROR        │  AI analyzes: Determines Order
│                 │
│  Cost: ~$0.01   │  Prompt: "Analyze [person]"
└────────┬────────┘  Model: mirror_analyzer (temp: 0.3)
         │            Response: {order, archetypes, explanation}
         ▼
┌─────────────────┐
│  ORDER_REVEAL   │  User sees: "You belong to Order of [X]"
│                 │  User selects: Archetype from list
│  Cost: $0       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CHARACTER      │  User enters: name, age, situation,
│  CREATION       │                struggle, greatness definition
│  Cost: $0       │  System creates: Character object
└────────┬────────┘  Saves to: SQLite characters table
         │
         ▼
┌─────────────────┐
│ CHAPTER_INTRO   │  AI generates: Chapter introduction narrative
│  (Chapter 1-8)  │  User sees: Beautiful narrative intro
│                 │
│  Cost: ~$0.005  │  Prompt: chapter_intro_prompt
└────────┬────────┘  Model: narrative_generator (temp: 0.8)
         │
         ▼
┌─────────────────┐
│ TRIAL_ATTEMPT   │  AI attempts: Trial for current chapter
│                 │  User sees: "Your character is working..."
│  Cost: ~$0.015  │
└────────┬────────┘  Prompt: trial_attemptor_prompt (temp: 0.8)
         │            Context: previous_attempts (if retry)
         ▼
┌─────────────────┐
│ TRIAL           │  AI evaluates: Submission against seal requirements
│ EVALUATION      │  System checks: All requirements present?
│                 │
│  Cost: ~$0.008  │  Prompt: trial_evaluator_prompt (temp: 0.1)
└────────┬────────┘  Response: {passed, requirements, missing}
         │
         ├─── [PASSED] ────────────────────┐
         │                                  │
         │ [FAILED]                         │
         ▼                                  ▼
┌─────────────────┐              ┌─────────────────┐
│ TRIAL_FEEDBACK  │              │ TRANSFORMATION  │  AI generates: Insight moment
│                 │              │                 │  User sees: "You realize..."
│  Cost: ~$0.006  │              │  Cost: ~$0.005  │
└────────┬────────┘              └────────┬────────┘
         │                                  │
         │                                  │
         └─── [RETRY] ───────┐              │
                              │              │
                         (Loop back          │
                      to TRIAL_ATTEMPT)      │
                                             ▼
                                    ┌─────────────────┐
                                    │ TIMELINE_EVENT  │  AI generates: Story moment
                                    │                 │  Saves to: timeline_events table
                                    │  Cost: ~$0.004  │
                                    └────────┬────────┘
                                             │
                                             │
                         ┌───────────────────┼───────────────────┐
                         │                   │                   │
                         │           [Chapter < 8]       [Chapter = 8]
                         │                   │                   │
                         │                   ▼                   ▼
                         │          ┌─────────────────┐  ┌─────────────────┐
                         │          │ CHAPTER_INTRO   │  │  COMPLETION     │
                         │          │ (Next Chapter)  │  │                 │
                         │          └────────┬────────┘  │  Cost: $0       │
                         │                   │           └─────────────────┘
                         │                   │                   │
                         └───────────────────┘                   │
                                                                 ▼
                                                              [END]

                                                    User sees: Full timeline
                                                               All transformations
                                                               Total cost

```

## State Details

### 1. WELCOME
- **UI**: Title screen
- **Action**: User clicks "Begin"
- **Transition**: → GREATNESS_MIRROR
- **Cost**: $0

### 2. GREATNESS_MIRROR
- **UI**: Input field for admired person
- **AI Call**: Analyze person → Determine Order
- **Transition**: → ORDER_REVEAL
- **Cost**: ~$0.01 (500 tokens)

### 3. ORDER_REVEAL
- **UI**: Show Order + Archetypes
- **Action**: User selects archetype
- **Transition**: → CHARACTER_CREATION
- **Cost**: $0

### 4. CHARACTER_CREATION
- **UI**: Form (name, age, 3 text questions)
- **Action**: Submit character
- **Transition**: → CHAPTER_INTRO (chapter=1)
- **Cost**: $0

### 5. CHAPTER_INTRO (×8)
- **UI**: Chapter title + narrative
- **AI Call**: Generate chapter introduction
- **Transition**: → TRIAL_ATTEMPT
- **Cost**: ~$0.005 (300 tokens)

### 6. TRIAL_ATTEMPT (×8+)
- **UI**: "Your character is working..."
- **AI Call**: Attempt trial based on instructions
- **Transition**: → TRIAL_EVALUATION
- **Cost**: ~$0.015 (1000 tokens)
- **Note**: May happen multiple times if trial fails

### 7. TRIAL_EVALUATION (×8+)
- **UI**: "Evaluating submission..."
- **AI Call**: Evaluate against seal requirements
- **Transition**:
  - If passed → TRANSFORMATION
  - If failed → TRIAL_FEEDBACK
- **Cost**: ~$0.008 (500 tokens)

### 8. TRIAL_FEEDBACK (×0-3 per chapter)
- **UI**: Show feedback, "Trying again..."
- **AI Call**: Generate constructive feedback
- **Transition**: → TRIAL_ATTEMPT (retry)
- **Cost**: ~$0.006 (400 tokens)
- **Note**: Only occurs on failed trials

### 9. TRANSFORMATION (×8)
- **UI**: Insight moment (highlighted)
- **AI Call**: Generate transformation narrative
- **Transition**: → TIMELINE_EVENT
- **Cost**: ~$0.005 (300 tokens)

### 10. TIMELINE_EVENT (×8)
- **UI**: "A moment added to your timeline"
- **AI Call**: Generate story moment
- **DB**: Save to timeline_events table
- **Transition**:
  - If chapter < 8 → CHAPTER_INTRO (next)
  - If chapter = 8 → COMPLETION
- **Cost**: ~$0.004 (250 tokens)

### 11. COMPLETION
- **UI**: Full timeline + cost summary
- **Action**: None (terminal state)
- **Cost**: $0

## Cost Breakdown by State

### Minimum Path (all trials pass first try)

| State            | Calls | Cost Each | Total    |
|------------------|-------|-----------|----------|
| Greatness Mirror | 1     | $0.010    | $0.010   |
| Chapter Intro    | 8     | $0.005    | $0.040   |
| Trial Attempt    | 8     | $0.015    | $0.120   |
| Trial Evaluation | 8     | $0.008    | $0.064   |
| Transformation   | 8     | $0.005    | $0.040   |
| Timeline Event   | 8     | $0.004    | $0.032   |
| **TOTAL**        | **41**| -         | **$0.306** |

### Realistic Path (2-3 retries across 8 chapters)

| State            | Calls | Cost Each | Total    |
|------------------|-------|-----------|----------|
| Greatness Mirror | 1     | $0.010    | $0.010   |
| Chapter Intro    | 8     | $0.005    | $0.040   |
| Trial Attempt    | 11    | $0.015    | $0.165   |
| Trial Evaluation | 11    | $0.008    | $0.088   |
| Trial Feedback   | 3     | $0.006    | $0.018   |
| Transformation   | 8     | $0.005    | $0.040   |
| Timeline Event   | 8     | $0.004    | $0.032   |
| **TOTAL**        | **50**| -         | **$0.393** |

*Note: Costs assume Claude 3 Haiku ($0.00025/$0.00125 per 1k tokens)*

## Auto-Progressing States

Some states auto-progress without user input:

1. **TRIAL_ATTEMPT** → Auto-triggers AI call, then → TRIAL_EVALUATION
2. **TRIAL_EVALUATION** → Auto-evaluates, then → TRANSFORMATION or TRIAL_FEEDBACK
3. **TRIAL_FEEDBACK** → Shows feedback, user clicks "Retry" → TRIAL_ATTEMPT

Frontend polls every 2 seconds during auto-progressing states.

## Database Operations by State

| State            | Read        | Write                 |
|------------------|-------------|-----------------------|
| WELCOME          | -           | Create session        |
| GREATNESS_MIRROR | -           | Update session        |
| ORDER_REVEAL     | -           | Update session        |
| CHARACTER_CREATION| -          | Create character      |
| CHAPTER_INTRO    | Character   | Update session        |
| TRIAL_ATTEMPT    | Character   | Update session        |
| TRIAL_EVALUATION | Character   | Update session        |
| TRIAL_FEEDBACK   | -           | Update session        |
| TRANSFORMATION   | Character   | Update session        |
| TIMELINE_EVENT   | Character   | Create timeline_event |
| COMPLETION       | Timeline    | -                     |

All states also write to `cost_log` table when AI is called.

## Error Handling

### State Validation
- Each state only allows specific transitions (checked in code)
- Invalid transitions return 400 error

### AI Failures
- Retry logic built-in (up to 3 attempts)
- JSON parsing errors caught and reported
- User sees error message, can restart from last valid state

### Database Errors
- SQLite ACID guarantees
- Foreign key constraints prevent orphaned data
- Session cleanup on delete removes all related data

## Testing the State Machine

```bash
# 1. Create session
curl -X POST http://localhost:8000/api/session
# Returns: {"session_id": "abc-123", "state": "welcome"}

# 2. Check current state
curl http://localhost:8000/api/session/abc-123
# Returns: Full state including ui_data

# 3. Advance through states
curl -X POST http://localhost:8000/api/transition \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "action": "start",
    "data": {}
  }'

# 4. Check costs at any time
curl http://localhost:8000/api/cost/abc-123
```

## State Machine Guarantees

1. **Deterministic**: Same inputs always produce same outputs
2. **Traceable**: Every transition logged in database
3. **Recoverable**: Can resume from any state after crash
4. **Measurable**: Every AI call tracked with precise cost
5. **Predictable**: Finite state machine with clear transitions

---

**Total States**: 11
**Average Journey**: 50 AI calls, ~$0.40 (with Haiku)
**Completion Time**: 10-15 minutes
