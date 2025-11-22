# Retry Logic & Error Handling

## Changes Made

### 1. Retry Logic in OpenRouter Client (`openrouter.py`)

**Added automatic retry with exponential backoff:**

```python
max_retries = 3  # Will try 3 times before failing
```

**Retry schedule:**
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds
- Attempt 4: Wait 4 seconds (if needed)

**Retryable errors:**
- `httpx.RemoteProtocolError` - Peer closed connection
- `httpx.ReadTimeout` - Request timed out
- `httpx.ConnectError` - Connection failed
- `httpx.ReadError` - Read error (like chunked read failure)
- `ConnectionError` - General connection errors

**Non-retryable errors:**
- HTTP 500 errors (server errors, not network)
- Invalid JSON responses
- Authentication errors

**Timeout increased:**
- Changed from 60s to 90s to allow slower responses

### 2. User-Friendly Error Messages (`app.js`)

**Before:**
```
Failed to advance: peer closed connection without sending complete message body (incomplete chunked read)
```

**After:**
```
Network connection interrupted. Please try again.
```

**Error mapping:**
- Network errors → "Network connection interrupted. Please try again."
- 500 errors → "Server error. The AI service may be temporarily unavailable. Please try again in a moment."
- Timeouts → "Request timed out. Please try again."

**Auto-dismiss:**
- Errors automatically disappear after 5 seconds
- User can still interact with Retry button before dismissal

### 3. Retry Button (`index.html` + `style.css`)

**Added retry button to error display:**
- Click to clear error and refresh state
- Styled to match the theme
- User can quickly retry without reloading page

## How It Works

### Network Failure Scenario

1. **User clicks button** → API call to OpenRouter
2. **Connection drops mid-response** → `RemoteProtocolError`
3. **Automatic retry #1** → Wait 1 second, try again
4. **Still fails** → Wait 2 seconds, try again
5. **Success!** → Continue normally

OR

5. **All retries exhausted** → Show user-friendly error with Retry button

### User Experience

**Without retry logic:**
```
Click button → Network error → Blank screen → User confused → Refresh page → Start over
```

**With retry logic:**
```
Click button → Network hiccup → Auto-retry (1s) → Success → User never notices
```

OR if all retries fail:
```
Click button → Network fails 3 times → Friendly error message + Retry button → Click Retry → Continue from where they were
```

## Configuration

### Change retry count

In `openrouter.py`:
```python
async def chat_completion(
    self,
    messages: list,
    temperature: float = 0.7,
    model: Optional[str] = None,
    max_tokens: int = 2000,
    max_retries: int = 3  # Change this number
)
```

### Change backoff timing

In `openrouter.py`:
```python
wait_time = (2 ** attempt) * 1  # Current: 1s, 2s, 4s
wait_time = (2 ** attempt) * 2  # Slower: 2s, 4s, 8s
wait_time = attempt + 1         # Linear: 1s, 2s, 3s
```

### Change timeout

In `openrouter.py`:
```python
async with httpx.AsyncClient(timeout=90.0) as client:  # Current: 90 seconds
async with httpx.AsyncClient(timeout=120.0) as client: # Increase to 2 minutes
```

## Testing Retry Logic

### Simulate network failure

1. **Start app**: `docker-compose up --build`
2. **Go through flow** until you need an AI call
3. **Kill network temporarily**:
   ```bash
   # On Mac/Linux
   sudo ifconfig en0 down
   sleep 3
   sudo ifconfig en0 up
   ```
4. **Observe**: Should see retry messages in logs
5. **Result**: Should recover automatically

### Check logs

```bash
docker-compose logs -f
```

Look for:
```
API call failed (attempt 1/3): RemoteProtocolError
Retrying in 1s...
API call failed (attempt 2/3): RemoteProtocolError
Retrying in 2s...
[Success on attempt 3]
```

## Edge Cases Handled

### 1. Transient Network Issues
**Problem**: WiFi hiccup, router restart, etc.
**Solution**: Automatic retry with backoff

### 2. OpenRouter Service Hiccup
**Problem**: OpenRouter briefly unavailable
**Solution**: Retry with longer waits gives service time to recover

### 3. Incomplete Chunked Responses
**Problem**: Response starts but connection drops mid-stream
**Solution**: Retry from scratch

### 4. User on Slow Connection
**Problem**: 60s timeout too short
**Solution**: Increased to 90s

### 5. Complete Service Outage
**Problem**: OpenRouter down for extended period
**Solution**: Fail gracefully with clear message and Retry button

## Monitoring

### Check retry frequency

```bash
# Count retries in logs
docker-compose logs | grep "Retrying in"

# Check failed attempts
docker-compose logs | grep "failed after"
```

### Alert thresholds

If you see:
- **< 1% retry rate**: Normal, occasional network hiccups
- **1-5% retry rate**: Acceptable, monitor for patterns
- **> 5% retry rate**: Investigate network or OpenRouter issues
- **Any "failed after 3 attempts"**: Immediate attention needed

## Cost Impact

**Retries DO NOT increase cost** because:
- Failed requests don't complete → No tokens used → No charge
- Only successful completions are billed
- Retry logic is free (just time delay)

**Example:**
- Attempt 1: Fails at 50% response → $0.00
- Attempt 2: Fails at 75% response → $0.00
- Attempt 3: Completes successfully → $0.01 (normal charge)
- **Total cost: $0.01** (same as without retry)

## Benefits

✅ **Better UX**: Users don't see transient errors
✅ **Higher completion rate**: More journeys finish successfully
✅ **Resilience**: App handles network issues gracefully
✅ **Clear feedback**: When it does fail, user knows what to do
✅ **No extra cost**: Failed requests aren't charged
✅ **Debugging**: Retry logs help diagnose issues

## Summary

- **3 automatic retries** with exponential backoff (1s, 2s, 4s)
- **90 second timeout** (increased from 60s)
- **User-friendly error messages** instead of technical jargon
- **Retry button** for manual retry without page reload
- **Auto-dismiss errors** after 5 seconds
- **Zero cost** for failed attempts

Network issues are now handled gracefully with minimal user disruption!
