# Supabase Project Setup & Connection Guide

Follow these steps to create a Supabase project and connect this backend to it.

---

## Step 1: Create a Supabase Project

1. Go to **[https://app.supabase.com](https://app.supabase.com)** and sign in (or create an account).
2. Click **"New Project"**.
3. Fill in:
   - **Name**: e.g. `filo-be` or `gst-copilot`
   - **Database Password**: Choose a strong password and **save it** (you need it for direct DB access).
   - **Region**: Pick the region closest to your users.
4. Click **"Create new project"** and wait for the project to be ready (1–2 minutes).

---

## Step 2: Get Your API Keys

1. In the project dashboard, go to **Settings** (gear icon in the sidebar) → **API**.
2. Copy these two values:
   - **Project URL** → use for `SUPABASE_URL`
   - **Project API keys** → **anon public** key → use for `SUPABASE_KEY`  
     (Use the **anon** key, not the **service_role** key, for the backend.)

---

## Step 3: Add Keys to This Project

1. Open the **`.env`** file in the project root (same folder as `main.py`).
2. Set (or update) these lines with your values:

```bash
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxx...
```

Replace with your actual **Project URL** and **anon public** key.  
No quotes needed. No spaces around `=`.

3. Save the file.

---

## Step 4: Create Database Tables in Supabase

The backend expects **two tables**: `users` and `conversations`.

1. In the Supabase dashboard, open **SQL Editor**.
2. Click **"New query"**.
3. Paste and run the SQL from **`supabase_schema.sql`** (in this repo).

Or paste this schema:

```sql
-- Users (for CA context: business type, state, GSTIN, etc.)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT,
  email TEXT UNIQUE,
  name TEXT,
  gstin TEXT,
  state TEXT,
  business_type TEXT,
  turnover NUMERIC,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations (chat history per user)
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  messages JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Optional: index for faster lookups
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
```

4. Click **"Run"**. You should see “Success. No rows returned.”

---

## Step 5: (Optional) Add Test Data

To test the API with sample data:

1. In **SQL Editor**, open **`test_data.sql`** from this repo (or copy its contents).
2. Run it.  
   This inserts one test user and one test conversation.  
   For real use, your frontend will create users and conversations.

---

## Step 6: Verify the Connection

1. Restart the backend (if it’s running):
   ```bash
   uvicorn main:app --reload
   ```
2. Open **http://localhost:8000** — you should see `{"status":"healthy"}`.
3. Open **http://localhost:8000/docs** and try **POST /chat** with a `conversation_id` that exists in `conversations` (e.g. from `test_data.sql`).

---

## Summary Checklist

| Step | Action |
|------|--------|
| 1 | Create project at [app.supabase.com](https://app.supabase.com) |
| 2 | Copy **Project URL** and **anon public** key from Settings → API |
| 3 | Put `SUPABASE_URL` and `SUPABASE_KEY` in `.env` |
| 4 | Run the schema SQL in Supabase SQL Editor to create `users` and `conversations` |
| 5 | (Optional) Run `test_data.sql` for test data |
| 6 | Restart backend and test `/` and `/chat` |

---

## Notes

- **anon key**: Safe to use in the backend; respect Row Level Security (RLS) if you enable it.
- **service_role key**: Bypasses RLS; use only in trusted server code, never in the frontend.
- Keep **`.env`** out of version control (it’s in `.gitignore`). Never commit real keys.

If you share your **Project URL** and **anon key** (you can redact part of the key if you prefer), we can double-check that the backend is configured correctly.
