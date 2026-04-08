# Nurva AI Backend API Documentation

## Overview

The chatbot has been completely refactored to use a **Django backend API** instead of client-side JavaScript logic. All agent responses, session management, and payment verification now happen on the server.

## Architecture

```
ChatbotUI (HTML/JS)
    ↓
API Endpoints
    ↓
Django Views & Logic
    ↓
Agent Logic & Database
    ↓
(Optional) External AI APIs (Claude, OpenAI)
```

## API Endpoints

### 1. Send Message & Get Response
**POST** `/api/chat/`

Send a message to an agent and receive an AI-generated response.

**Request:**
```json
{
  "message": "Help me organize my tasks",
  "agent": "flow",
  "session_id": "session_1234567890",
  "is_paid": false
}
```

**Response (Success):**
```json
{
  "success": true,
  "session_id": "session_1234567890",
  "response": "I can help you organize your tasks...",
  "message_count": 1,
  "trial_limit": 3
}
```

**Response (Trial Exceeded):**
```json
{
  "error": "Free trial limit reached",
  "message_count": 3,
  "limit": 3
}
```

**Status Codes:**
- `200 OK` - Message sent successfully
- `400 Bad Request` - Invalid request data
- `429 Too Many Requests` - Trial limit reached
- `500 Internal Server Error` - Server error

### 2. Get Session Information
**GET** `/api/session/?session_id=<session_id>`

Retrieve all messages and metadata for a chat session.

**Response:**
```json
{
  "session_id": "session_1234567890",
  "agent": "flow",
  "message_count": 5,
  "is_paid": false,
  "messages": [
    {
      "role": "user",
      "content": "Help me organize my tasks",
      "agent_key": "flow",
      "created_at": "2024-04-04T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "I can help you organize your tasks...",
      "agent_key": "flow",
      "created_at": "2024-04-04T12:00:01Z"
    }
  ]
}
```

### 3. Unlock Session (Payment Verification)
**POST** `/api/unlock/`

Verify password and unlock unlimited access for a session.

**Request:**
```json
{
  "session_id": "session_1234567890",
  "password": "nurva2024"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Session unlocked successfully"
}
```

**Response (Failure):**
```json
{
  "error": "Invalid password"
}
```

**Status Codes:**
- `200 OK` - Session unlocked
- `400 Bad Request` - Missing required fields
- `401 Unauthorized` - Invalid password
- `404 Not Found` - Session not found

## Database Models

### Agent
Represents an AI agent (Flow, Staff, SEO, Strategist)

**Fields:**
- `key` (CharField) - Unique identifier ('flow', 'staff', 'seo', 'strat')
- `name` (CharField) - Display name (e.g., "Nurva Flow")
- `role` (CharField) - Agent's specialty (e.g., "PA & Planning")
- `description` (TextField) - Long description
- `avatar_color` (CharField) - Hex color code for avatar
- `system_prompt` (TextField) - Claude/OpenAI system prompt
- `emoji` (CharField) - Agent emoji
- `created_at` (DateTimeField) - Creation timestamp

### ChatSession
Represents a user's chat session

**Fields:**
- `session_id` (CharField) - Unique session identifier
- `agent` (ForeignKey) - Agent being used
- `is_paid` (BooleanField) - Whether user has paid
- `message_count` (IntegerField) - Number of messages sent
- `created_at` (DateTimeField) - Session creation time
- `updated_at` (DateTimeField) - Last message time

### ChatMessage
Individual messages in a conversation

**Fields:**
- `session` (ForeignKey) - Parent session
- `role` (CharField) - 'user' or 'assistant'
- `content` (TextField) - Message text
- `agent_key` (CharField) - Which agent responded
- `created_at` (DateTimeField) - Message timestamp

## Configuration

### Environment Variables (.env)

```env
# Chat Settings
CHAT_PASSWORD=nurva2024              # Password to unlock unlimited access
OWNER_CODE=NURVA-OWNER-2024          # Owner bypass code

# Optional: AI API Keys
ANTHROPIC_API_KEY=your-key           # For Claude integration
OPENAI_API_KEY=your-key              # For ChatGPT integration
```

### Free Trial Settings

Located in `chat/views.py` (ChatAPIView.post method):
```python
FREE_TRIAL_LIMIT = 3  # Messages allowed before payment
```

To change: Edit the value in the code and restart server.

## Frontend Implementation

The chatbot HTML (`chat/templates/chat/chatbot.html`) uses vanilla JavaScript to:

1. **Build UI locally** - Agent tabs, messages, sidebar
2. **Send messages to API** - Via `fetch()` POST to `/api/chat/`
3. **Handle responses** - Display AI messages and manage state
4. **Track sessions** - Store `session_id` in localStorage
5. **Manage trial** - Count messages, show upgrade overlay

### JavaScript Functions

```javascript
// Core functions
sendMessage()           // Send user message to API
appendMessage()         // Add message to DOM
switchAgent()          // Change active agent
showWelcome()          // Display welcome message

// Payment functions
unlockAccess()         // Verify password and unlock
showUnlockForm()       // Show password input
updateTrialBanner()    // Update remaining message count

// Utilities
handleKeyDown()        // Enter key to send
autoResize()          // Auto-expand textarea
getCookie()           // Get CSRF token
escapeHtml()          // Security: prevent XSS
```

## Integration with AI APIs

### Option 1: Anthropic Claude API

Install:
```bash
pip install anthropic
```

In `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

In `chat/agent_logic.py`, uncomment and use:
```python
response = integrate_with_claude_api(agent_key, user_message, system_prompt)
```

### Option 2: OpenAI ChatGPT API

Install:
```bash
pip install openai
```

In `.env`:
```env
OPENAI_API_KEY=sk-...
```

In `chat/agent_logic.py`, uncomment and use:
```python
response = integrate_with_openai_api(user_message, system_prompt)
```

### Option 3: Custom AI Provider

Edit `get_agent_response()` in `chat/agent_logic.py`:
```python
def get_agent_response(agent_key: str, user_message: str, conversation_history=None) -> str:
    # Your custom logic here
    # Return AI-generated response
    return response
```

## Development Workflow

### 1. Start Development Server
```bash
cd /Users/sami/Desktop/Nurva\ AI/nurva_project
source venv/bin/activate
python manage.py runserver
```

Visit: http://localhost:8000/chatbot/

### 2. Make Changes

**Edit Agent Responses:**
- File: `chat/agent_logic.py`
- Functions: `demo_flow_response()`, `demo_staff_response()`, etc.

**Edit API Behavior:**
- File: `chat/views.py`
- View: `ChatAPIView.post()`

**Edit Frontend UI:**
- File: `chat/templates/chat/chatbot.html`
- JavaScript section at bottom

**Edit Models:**
- File: `chat/models.py`
- Then run: `python manage.py makemigrations && python manage.py migrate`

### 3. Test API Endpoints

Using curl:
```bash
# Send message
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "agent": "flow",
    "session_id": "test_session"
  }'

# Get session
curl http://localhost:8000/api/session/?session_id=test_session

# Unlock
curl -X POST http://localhost:8000/api/unlock/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "password": "nurva2024"
  }'
```

## Trial System

### How It Works

1. **Browser Storage** - `localStorage.setItem('nurva_trial_count', count)`
2. **API Tracking** - `ChatSession.message_count` in database
3. **Limit Check** - `if count >= 3` in `ChatAPIView.post()`
4. **Reset Option** - `Clear trial on new chat` button in sidebar

### Testing Trial Limit

1. Open chatbot
2. Send 3 messages
3. On 4th message, see upgrade overlay with payment options
4. Click "Already a member?" → Enter password: `nurva2024`
5. ✅ Unlimited access granted

### Resetting Trial

In browser DevTools console:
```javascript
localStorage.removeItem('nurva_trial_count');
localStorage.removeItem('nurva_is_paid');
location.reload();
```

## Admin Panel

Create superuser:
```bash
python manage.py createsuperuser
```

Access: http://localhost:8000/admin/

**View/Manage:**
- Agents - View & edit all 4 AI agents
- Chat Sessions - See all user sessions
- Chat Messages - View conversation history

## Common Issues

### "CSRF token missing"
The API endpoints have `@csrf_exempt` decorator. If you remove it, ensure frontend sends CSRF token from cookies.

### "Agent not found"
Make sure agents are initialized:
```bash
python setup_db.py
```

### Trial always shows 3 messages
Clear localStorage:
```javascript
localStorage.clear()
```

### API returns "Invalid JSON"
Check request headers:
```json
{"Content-Type": "application/json"}
```

### Password unlock doesn't work
Check `.env` file:
```env
CHAT_PASSWORD=nurva2024
OWNER_CODE=NURVA-OWNER-2024
```

## Next Steps

1. **Connect Real AI API** - Replace demo responses with Claude/OpenAI
2. **Add Image Generation** - Implement Pollinations.ai integration
3. **User Authentication** - Add Django login/registration
4. **Payment Processing** - Integrate Stripe or Paddle
5. **Conversation History** - Load previous chats from database
6. **Multi-platform** - Add mobile/desktop app

## Support & Debugging

### Enable Debug Logging
In `chat/views.py`:
```python
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Message: {user_message}")
```

### Check Database
```bash
python manage.py shell
>>> from chat.models import ChatSession, ChatMessage
>>> ChatSession.objects.all().count()
>>> ChatMessage.objects.all()[:10]
```

### View Server Logs
Server output shows all API calls and errors.

## File Structure

```
chat/
├── models.py              # Agent, ChatSession, ChatMessage
├── views.py               # ChatAPIView, API endpoints
├── urls.py                # /api/chat/, /api/session/
├── agent_logic.py         # AI response generation
├── migrations/
│   ├── 0001_initial.py   # Create tables
│   └── __init__.py
├── templates/
│   └── chat/
│       ├── home.html      # Home page
│       ├── chatbot.html   # Chat UI with API calls
│       └── chatbot_old.html # Backup of original
├── admin.py              # Admin interface
├── apps.py               # App configuration
├── tests.py              # Unit tests
└── migrations/

nurva_config/
├── settings.py           # Django settings
├── urls.py               # Main URL routing
├── asgi.py              # ASGI config
└── wsgi.py              # WSGI config

Root/
├── manage.py             # Django command tool
├── setup_db.py           # Initialize agents
├── requirements.txt      # Dependencies
├── .env                  # Environment variables
└── README.md            # Documentation
```

---

**Questions?** Check the inline code comments or read the official Django documentation.
