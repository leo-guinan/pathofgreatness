# Fix for Blank Screen After Character Creation

## Problem
After submitting basic info (character creation), the page shows blank screen with all states set to `display: none`.

## Root Cause
When transitioning from `CHARACTER_CREATION` to `CHAPTER_BEFORE`, the "before" narrative wasn't being generated, so the `chapter_before` state had no content to show.

## Fix Applied

### 1. Generate Narrative During Transition
Modified `state_machine_simple.py` to generate the "before" narrative immediately when transitioning to `CHAPTER_BEFORE`:

```python
# When creating character, immediately generate first chapter's before narrative
elif current_state == GameState.CHARACTER_CREATION:
    result = await self._handle_character_creation(session_id, input_data)
    # Immediately generate the first chapter's before narrative
    before_result = await self._handle_chapter_before(session_id, {})
    result.update(before_result)
    next_state = GameState.CHAPTER_BEFORE
```

### 2. Added Loading State in UI
Added loading spinner in `chapter_before` view while narrative is being generated:

```html
<div x-show="!uiData.narrative" class="loading">
    <div class="spinner"></div>
    <p>Generating your narrative...</p>
</div>
```

### 3. Added Debug Logging
Added console.log statements in JavaScript to help diagnose issues:

```javascript
console.log('Current state:', this.state);
console.log('UI Data:', this.uiData);
console.log('Transition result:', result);
```

## Testing Steps

### Test in Browser

1. **Start the app**:
```bash
docker-compose up --build
```

2. **Open browser**: http://localhost:8000

3. **Open Developer Console** (F12 or Cmd+Option+I)

4. **Go through the flow**:
   - Welcome → Click "Begin Your Ascent"
   - Mirror → Enter "Steve Jobs" → Click "Reveal My Path"
   - Order Reveal → Select an archetype
   - Character Creation → Fill out 5 fields → Click "Start Climbing"

5. **Watch the console** for:
```
Advancing with action: create_character, data: {...}
Transition result: {...}
Current state: chapter_before
UI Data: {narrative: "...", ...}
Loading complete, current state: chapter_before
```

6. **You should see**:
   - Loading spinner while AI generates narrative (5-10 seconds)
   - Then Chapter 1 BEFORE page with blue narrative box
   - Progress bar showing 1/8
   - "Experience the Transformation" button

### Expected Behavior

**Character Creation → Chapter 1 BEFORE**:
- ✅ Loading spinner appears
- ✅ AI generates "before" narrative (~5-10 seconds with Claude Haiku)
- ✅ Page shows Chapter 1 BEFORE with narrative
- ✅ Blue themed narrative box
- ✅ Button enabled

**Chapter BEFORE → Chapter AFTER**:
- ✅ Click "Experience the Transformation"
- ✅ Loading spinner
- ✅ AI generates "after" narrative and transformation
- ✅ Page shows Chapter 1 AFTER with green narrative
- ✅ Gold transformation box

**Chapter AFTER → Next Chapter BEFORE**:
- ✅ Click "Continue Climbing"
- ✅ Loading spinner
- ✅ AI generates next chapter's "before" narrative
- ✅ Progress bar updates (2/8, 3/8, etc.)

### If Still Seeing Blank Screen

Check console for errors:

1. **State mismatch**:
   - Look for: "Current state: chapter_before"
   - If state is something else, that's the issue

2. **No narrative generated**:
   - Look for: "UI Data: {narrative: ''}"
   - If narrative is empty, AI generation failed

3. **API error**:
   - Look for: "Advance error: ..."
   - Shows backend error

4. **Loading stuck**:
   - Check if loading spinner never goes away
   - Backend might have crashed

### Check Backend Logs

```bash
docker-compose logs -f
```

Look for:
- OpenRouter API calls
- State transitions
- Any Python errors

### Common Issues

**Issue**: "OPENROUTER_API_KEY not set"
**Fix**: Check `.env` file has `OPENROUTER_API_KEY=your_key`

**Issue**: "429 Too Many Requests"
**Fix**: Wait a minute, or check OpenRouter credits

**Issue**: "Invalid JSON response"
**Fix**: AI might have returned non-JSON, check backend logs

**Issue**: Database locked
**Fix**: `rm data/game.db && docker-compose restart`

## Verification Checklist

- [ ] App starts without errors
- [ ] Welcome screen appears
- [ ] Greatness Mirror works (enter person, see Order)
- [ ] Order Reveal shows archetypes
- [ ] Character Creation form submits
- [ ] Loading spinner appears after submit
- [ ] Chapter 1 BEFORE page appears with narrative
- [ ] Can click through to AFTER page
- [ ] Can continue to Chapter 2
- [ ] Console shows no errors

## Quick Reset

If things get stuck:

```bash
# Stop everything
docker-compose down

# Clear database
rm -rf data/

# Rebuild and start
docker-compose up --build
```

## Summary

The fix ensures that:
1. Narratives are generated **during** state transitions, not after
2. UI shows loading state while AI is working
3. Console logging helps diagnose issues
4. Button is disabled until narrative is ready

The blank screen issue should now be resolved. The page will show a loading spinner while the AI generates content, then display the chapter page once ready.
