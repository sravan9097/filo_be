# Environment Variables Setup Guide

## 📍 Where to Create the `.env` File

Create the `.env` file at the **project root level** (same directory as `main.py`, `config.py`, etc.)

```
ca_helper_be/
├── .env              ← Create here (project root)
├── main.py
├── config.py
├── models.py
├── services/
├── requirements.txt
└── README.md
```

**Full path:** `/Users/khk/Downloads/ca_helper_be/.env`

---

## 🔑 Required Environment Variables

You **must** provide these three variables:

### 1. Supabase Configuration

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

**How to get these:**
1. Go to your Supabase project dashboard: https://app.supabase.com
2. Navigate to **Settings** → **API**
3. Copy:
   - **Project URL** → Use for `SUPABASE_URL`
   - **anon/public key** → Use for `SUPABASE_KEY`

**Example:**
```bash
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzI5MCwiZXhwIjoxOTU0NTQzMjkwfQ.example
```

### 2. OpenAI Configuration

```bash
OPENAI_API_KEY=your_openai_api_key
```

**How to get this:**
1. Go to OpenAI API Keys: https://platform.openai.com/api-keys
2. Click **Create new secret key**
3. Copy the key (it starts with `sk-`)

**Example:**
```bash
OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890
```

---

## ⚙️ Optional Environment Variables

These have default values but can be customized:

### OpenAI Model Configuration

```bash
# Default: gpt-4o-mini (cheap model for conversation summarization)
SUMMARIZE_MODEL=gpt-4o-mini

# Default: gpt-4o (main model for GST reasoning)
MAIN_MODEL=gpt-4o
```

### CORS Configuration

```bash
# Default: ["*"] (allows all origins)
# For production, specify your frontend URL(s):
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
```

---

## 📝 Complete `.env` File Template

Create a file named `.env` in the project root with this content:

```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key

# Optional: Model Configuration
# SUMMARIZE_MODEL=gpt-4o-mini
# MAIN_MODEL=gpt-4o

# Optional: CORS Configuration
# CORS_ORIGINS=["*"]
```

---

## 🚀 Quick Setup Steps

1. **Navigate to project root:**
   ```bash
   cd /Users/khk/Downloads/ca_helper_be
   ```

2. **Create the `.env` file:**
   ```bash
   touch .env
   ```

3. **Edit the `.env` file** and add your credentials:
   ```bash
   # Use your preferred editor
   nano .env
   # or
   code .env
   # or
   vim .env
   ```

4. **Fill in the required variables** (see examples above)

5. **Verify the file exists:**
   ```bash
   ls -la .env
   ```

6. **Test the application:**
   ```bash
   python3 -m uvicorn main:app --reload
   ```

---

## ⚠️ Important Notes

- **Never commit `.env` to version control** - it's already in `.gitignore`
- **Keep your API keys secure** - don't share them publicly
- **The `.env` file must be in the project root** (same level as `main.py`)
- **No spaces around the `=` sign** in the `.env` file
- **No quotes needed** for simple string values (unless specified)

---

## 🔍 Troubleshooting

If you get errors about missing environment variables:

1. **Check file location:** Make sure `.env` is in the project root
2. **Check file name:** It must be exactly `.env` (with the dot)
3. **Check syntax:** No spaces around `=`, one variable per line
4. **Restart the server:** After creating/editing `.env`, restart uvicorn

