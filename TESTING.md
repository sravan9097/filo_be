# Testing the GST CA Copilot Backend

## Quick Test Guide

### 1. Set Up Test Data in Supabase

Run the SQL queries from `test_data.sql` in your Supabase SQL Editor:

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the queries from `test_data.sql`
4. Click **Run** to execute

This will create:
- `test-chat-001`: Conversation with existing message history
- `test-chat-002`: Empty conversation (for testing first message)
- `test-chat-003`: Conversation with multiple exchanges

### 2. Test the API

#### Option A: Using Swagger UI (Recommended)

1. Start the server:
   ```bash
   python3 -m uvicorn main:app --reload
   ```

2. Open http://localhost:8000/docs

3. Click on `POST /chat` endpoint

4. Click **Try it out**

5. Use this test request:
   ```json
   {
     "chat_id": "test-chat-001",
     "message": "What documents do I need for GST registration?"
   }
   ```

6. Click **Execute**

#### Option B: Using cURL

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test-chat-001",
    "message": "What documents do I need for GST registration?"
  }'
```

#### Option C: Using Python

```python
import requests

url = "http://localhost:8000/chat"
payload = {
    "chat_id": "test-chat-001",
    "message": "What documents do I need for GST registration?"
}

response = requests.post(url, json=payload)
print(response.json())
```

### 3. Test Scenarios

#### Scenario 1: Continue Existing Conversation
```json
{
  "chat_id": "test-chat-001",
  "message": "Can you provide more details about the documentation required?"
}
```
**Expected**: Backend fetches existing messages and continues the conversation.

#### Scenario 2: New Conversation
```json
{
  "chat_id": "new-chat-123",
  "message": "What is the GST rate for restaurant services?"
}
```
**Expected**: Backend creates a new conversation in Supabase.

#### Scenario 3: Empty Conversation
```json
{
  "chat_id": "test-chat-002",
  "message": "I need help with GST filing"
}
```
**Expected**: Backend starts fresh conversation with empty history.

### 4. Verify in Supabase

After making API calls, check Supabase:

1. Go to **Table Editor** → `conversations`
2. Find your `chat_id`
3. Verify that:
   - New messages are appended
   - `updated_at` timestamp is updated
   - Messages array contains both user and assistant messages

### 5. Sample Test Requests

#### Test 1: Basic GST Query
```json
{
  "chat_id": "test-basic-001",
  "message": "What is GST?"
}
```

#### Test 2: Section-Specific Query
```json
{
  "chat_id": "test-section-001",
  "message": "Explain Section 16 of the CGST Act regarding input tax credit"
}
```

#### Test 3: Calculation Query
```json
{
  "chat_id": "test-calc-001",
  "message": "How do I calculate GST on an invoice of ₹10,000 with 18% GST rate?"
}
```

#### Test 4: Missing Information Query
```json
{
  "chat_id": "test-missing-001",
  "message": "What is the GST rate for my business?"
}
```
**Expected**: AI should ask for more details about the business type.

### 6. Expected Response Format

```json
{
  "chat_id": "test-chat-001",
  "reply": "According to GST Act Section 16...",
  "success": true,
  "error": null
}
```

### 7. Error Testing

#### Test Empty Message
```json
{
  "chat_id": "test-error-001",
  "message": ""
}
```
**Expected**: 400 Bad Request with error message

#### Test Invalid Chat ID Format
```json
{
  "chat_id": "",
  "message": "Test message"
}
```
**Expected**: Should still work (creates new conversation with empty ID)

### 8. Monitoring

Check server logs for:
- Conversation summarization (for long histories)
- OpenAI API calls
- Supabase operations
- Any errors

### 9. Clean Up

To remove test data:
```sql
DELETE FROM conversations WHERE id LIKE 'test-%';
```

## Troubleshooting

1. **"Invalid API key" error**: Check your `.env.local` file has correct Supabase anon key (not publishable key)

2. **"Conversation not found"**: This is normal for new chat_ids - backend will create it

3. **OpenAI errors**: Verify your `OPENAI_API_KEY` is valid and has credits

4. **Database errors**: Ensure the `conversations` table exists in Supabase

