-- ============================================
-- Simple Test Data - 1 User + 1 Conversation
-- ============================================
-- Run this in your Supabase SQL Editor
-- (Assumes tables already exist)

-- Insert 1 user
INSERT INTO users (phone, email, name, gstin, state, business_type, turnover)
VALUES (
  '+91-9876543210',
  'test@example.com',
  'Test User',
  '27ABCDE1234F1Z5',
  'Maharashtra',
  'Manufacturing',
  5000000
)
ON CONFLICT DO NOTHING;

-- Insert 1 conversation for that user
-- (Replace the user_id with the actual UUID from the users table after running the above)
INSERT INTO conversations (user_id, messages)
SELECT 
  id,
  '[
    {
      "role": "user",
      "content": "What is the GST rate for software services?"
    },
    {
      "role": "assistant",
      "content": "According to GST Act Section 2(102), software services are classified as services. The GST rate for software services is typically 18% under the GST regime."
    }
  ]'::jsonb
FROM users
WHERE email = 'test@example.com'
LIMIT 1;
