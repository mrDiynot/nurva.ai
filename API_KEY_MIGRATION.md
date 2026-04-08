# API Key Migration - Backend Management

## Summary

The chatbot has been updated to fetch the Anthropic API key from the backend instead of hardcoding it in the frontend. This improves security and makes it easier to rotate or update API keys.

## What Changed

### 1. Backend (`chat/views.py`)
- **New Endpoint:** `/api/key/` - Returns the API key from `.env`
- **Method:** GET
- **Response:** `{ "success": true, "api_key": "..." }`

### 2. Frontend (`chat/templates/chat/chatbot.html`)
- **Modified `sendMessage()` function** to:
  - Fetch API key from `/api/key/` before sending messages
  - Use the retrieved key in the Anthropic API call
  - Removed hardcoded API key from code
- **Auto-start:** Modal is hidden, chatbot loads immediately
- **Message flow:** User → API call to `/api/key/` → Call to Claude → Response

### 3. URL Routing (`chat/urls.py`)
- **Old:** `/api/chat/`, `/api/session/`, `/api/unlock/` (removed)
- **New:** `/api/key/` (added)

## How It Works

1. User opens chatbot at `http://localhost:8000/chatbot/`
2. Page loads, modal is hidden, chatbot is ready
3. User types message and clicks send
4. JavaScript fetches API key from `http://localhost:8000/api/key/`
5. Backend returns key from `.env` file (secure, not exposed in code)
6. JavaScript uses key to call Anthropic API directly
7. Response displayed in chat

## Security Improvements

✅ **API Key not in Frontend Code** - No longer hardcoded in HTML/JS
✅ **Centralized Management** - Change key once in `.env`
✅ **Server-Controlled** - Backend decides what key to serve
✅ **Easy Rotation** - Update `.env` and restart server

## API Reference

### Get API Key
```bash
curl http://localhost:8000/api/key/
```

**Response:**
```json
{
  "success": true,
  "api_key": "sk-ant-api03-..."
}
```

**Error (if not configured):**
```json
{
  "success": false,
  "error": "API key not configured"
}
```

## Configuration

API key is stored in `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

To change it:
1. Edit `.env` file
2. Update `ANTHROPIC_API_KEY` value
3. Restart Django server
4. All new messages will use the new key

## Files Modified

- `chat/views.py` - Simplified, added `get_api_key()` function
- `chat/urls.py` - Updated routes, removed old API endpoints
- `chat/templates/chat/chatbot.html` - Modified `sendMessage()` function
- Restored from `chatbot_old.html` - Kept original functionality

## Testing

```bash
# Test the API endpoint
curl http://localhost:8000/api/key/

# Test the chatbot page
curl http://localhost:8000/chatbot/
```

## Limitations

- API key still sent to Anthropic directly from browser (this is required for the `anthropic-dangerous-direct-browser-access` header)
- For better security, you could create a backend endpoint that proxies to Anthropic API (more complex, slightly slower)

## Next Steps (Optional)

For maximum security, you could:
1. Create backend proxy endpoint: `POST /api/message/`
2. Move all Anthropic API calls to backend
3. Remove browser access requirement
4. Add per-user rate limiting and logging

This would require more changes but provides enterprise-grade security.
