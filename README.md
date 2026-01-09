# GST CA Copilot Backend

A production-grade backend for GST (Goods and Services Tax) Chartered Accountant Copilot, built with FastAPI, Supabase, and OpenAI.

## Architecture

- **Stateless Backend**: The backend is completely stateless and fetches conversation history from Supabase on each request.
- **Single Endpoint**: `POST /chat` - handles all chat interactions
- **Frontend Integration**: Frontend stores all conversations in Supabase. Backend only processes messages and updates the database.

## Tech Stack

- **FastAPI**: Python web framework
- **Supabase**: PostgreSQL database for conversation storage
- **OpenAI API**: GPT models for GST law reasoning and conversation summarization

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/service key
- `OPENAI_API_KEY`: Your OpenAI API key

### 3. Set Up Supabase Database

Create a `conversations` table in your Supabase database:

```sql
CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  messages JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoint

### POST /chat

Main endpoint for chat interactions.

**Request Body:**
```json
{
  "chat_id": "unique-conversation-id",
  "message": "What is the GST rate for software services?"
}
```

**Response:**
```json
{
  "chat_id": "unique-conversation-id",
  "reply": "According to GST Act Section 2(102)...",
  "success": true,
  "error": null
}
```

## Flow

1. Frontend creates a conversation record in Supabase on first message
2. Every subsequent message calls `/chat` with `chat_id` + latest user message
3. Backend fetches existing `conversation.messages` from Supabase
4. Backend builds a CA-safe prompt with deterministic GST rules
5. Backend calls OpenAI API
6. Backend appends assistant response to `conversation.messages`
7. Backend updates Supabase and returns the reply

## Features

- ✅ Supabase DB client for conversation management
- ✅ Conversation summarization for long histories (gpt-4o-mini)
- ✅ Prompt builder with GST-specific rules
- ✅ OpenAI API integration with GPT-4
- ✅ Message append & save logic
- ✅ Comprehensive error handling
- ✅ CORS enabled for frontend integration

## Rules & Guidelines

The AI assistant follows these rules:
- Never hallucinates GST law
- Always mentions GST Act Section / Rule when answering legal questions
- Asks for missing info instead of assuming
- Keeps responses concise and professional

## Development

### Project Structure

```
.
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── models.py              # Pydantic models
├── services/
│   ├── supabase_service.py    # Supabase client
│   ├── openai_service.py      # OpenAI client & prompt builder
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## License

MIT

