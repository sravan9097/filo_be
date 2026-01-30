-- ============================================
-- Supabase schema for Filo / GST CA Copilot
-- ============================================
-- Run this in Supabase: SQL Editor → New query → Paste → Run

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

-- Index for faster lookups by user
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
