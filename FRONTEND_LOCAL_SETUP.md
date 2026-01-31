# Frontend Configuration for Local Backend Testing

## Backend Status
✅ **Local backend is running at:** `http://localhost:8000`

## Available Endpoints
- `GET http://localhost:8000/` - Health check
- `POST http://localhost:8000/api/chat` - Send chat message
- `GET http://localhost:8000/api/chats?user_id={uuid}` - List user's conversations
- `GET http://localhost:8000/api/chats/{conversation_id}` - Fetch specific conversation

---

## Frontend Configuration Changes

### Option 1: Environment Variable (Recommended)

In your **frontend** project, update the `.env` or `.env.local` file:

```bash
# For local testing - comment out production URL
# NEXT_PUBLIC_API_URL=https://filo-jgum.onrender.com
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase config (keep these the same)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Then in your API calls, use:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Example: Send chat message
const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    conversation_id: conversationId,
    message: userMessage
  })
});
```

---

### Option 2: Direct Code Change (Quick Test)

If you just want to test quickly without env vars, find where your frontend makes API calls and change:

**From:**
```javascript
const API_URL = 'https://filo-jgum.onrender.com';
```

**To:**
```javascript
const API_URL = 'http://localhost:8000';
```

---

## Example API Calls

### 1. List Conversations
```javascript
const userId = '5cc32b12-12cc-4ec1-84dd-f1ed5621bcfd'; // Your user ID from Supabase Auth
const response = await fetch(`http://localhost:8000/api/chats?user_id=${userId}`);
const { conversations, count } = await response.json();
console.log(`Found ${count} conversations:`, conversations);
```

### 2. Fetch a Conversation
```javascript
const conversationId = '7aaefde3-5c16-400a-a518-9ff8649d384f';
const response = await fetch(`http://localhost:8000/api/chats/${conversationId}`);
const conversation = await response.json();
console.log('Conversation:', conversation);
```

### 3. Send a Message
```javascript
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    conversation_id: conversationId,
    message: 'What is the GST rate for software services?'
  })
});
const { reply, success } = await response.json();
console.log('Assistant reply:', reply);
```

---

## Testing Checklist

1. ✅ Update frontend to use `http://localhost:8000`
2. ✅ Restart your frontend dev server (e.g. `npm run dev`)
3. ✅ Sign in to the frontend (if you have auth)
4. ✅ Try creating a new conversation
5. ✅ Try sending a message
6. ✅ Check browser console (F12) for any errors
7. ✅ Verify messages save to Supabase

---

## CORS Note

The backend already has CORS enabled with `allow_origins=["*"]`, so your frontend can call `localhost:8000` without CORS issues.

---

## Switch Back to Production

When you're done testing locally:

1. **Stop the local backend:** Press `Ctrl+C` in the terminal running uvicorn
2. **Update frontend env:**
   ```bash
   NEXT_PUBLIC_API_URL=https://filo-jgum.onrender.com
   ```
3. **Restart frontend dev server**

---

## Troubleshooting

### "Failed to fetch" error
- Make sure the backend is running: `curl http://localhost:8000/`
- Check that you're using `http://localhost:8000` (not `https://`)

### "Conversation not found" error
- Create a new conversation first (frontend should insert a row in `conversations` table)
- Or use an existing conversation_id from your test data

### CORS error
- Already configured; shouldn't happen. But if it does, check that `CORS_ORIGINS` in backend `.env` includes `["*"]`

---

## Your Test Data

You have **5 conversations** in Supabase for user `5cc32b12-12cc-4ec1-84dd-f1ed5621bcfd`:
- `7aaefde3-5c16-400a-a518-9ff8649d384f`
- `f8a6df93-a1ea-49ec-9109-ba21216880be`
- `62696362-521d-4cea-9bd3-83e7a8aad982`
- `7feac7ed-f39a-4abc-b68e-f431118a9a1b`
- `317feb16-c501-426b-aae4-77a5c9d1a41c`

All are currently empty (no messages). Test by sending a message to one of them!
