# Supabase Auth Setup (Option 2)

This guide wires **Supabase Auth** (sign up / sign in) to your **public.users** table. Passwords stay in **auth.users**; no `password` column in **public.users**.

---

## What Gets Set Up

1. **Trigger**: When someone signs up via Supabase Auth, a row is created in **public.users** with the same `id`, `email`, and `name` (from sign-up metadata).
2. **RLS**: Row Level Security so users can only read/update their own row in **public.users** and their own **conversations**. Your backend uses the **service role** key so it can still access all data.

---

## Step 1: Enable Email Auth in Supabase

1. In [Supabase Dashboard](https://app.supabase.com) → your project.
2. Go to **Authentication** → **Providers**.
3. Enable **Email** (and optionally **Email OTP** or others).
4. Under **Auth** → **Settings**, set **Site URL** and **Redirect URLs** if you use a frontend.

---

## Step 2: Run the Auth Sync SQL

1. In Supabase: **SQL Editor** → **New query**.
2. Open **`supabase_auth_sync.sql`** in this repo and copy its full contents.
3. Paste into the SQL Editor and click **Run**.
4. You should see “Success. No rows returned.”

This will:

- Create a trigger so each new **auth.users** row gets a matching **public.users** row (`id`, `email`, `name`).
- Enable RLS on **public.users** and **public.conversations**.
- Add policies so:
  - Signed-in users (anon key + JWT) can only read/update their own profile and conversations.
  - The backend (service role key) can read/update everything.

---

## Step 3: Use the Service Role Key in the Backend

For the backend to update conversations and users on behalf of any user, it must use the **service role** key, not the anon key.

1. In Supabase: **Settings** → **API**.
2. Copy **service_role** (under “Project API keys”). Keep it secret.
3. In your backend env (e.g. Render), set:
   ```bash
   SUPABASE_KEY=<paste service_role key here>
   ```
   (Same variable name; only the value changes from anon to service_role.)

**Important:** Use the service role key only in server-side env (e.g. Render). Never expose it in the frontend or in client-side code.

---

## Step 4: Update the Frontend

Yes — the frontend should be updated to use Supabase Auth and the **anon** key (never the service_role key in the frontend).

### Frontend checklist

| What | How |
|------|-----|
| **Supabase client** | Use the **anon (public)** key in the frontend env (e.g. `NEXT_PUBLIC_SUPABASE_ANON_KEY`). Never use the service_role key in the frontend. |
| **Sign up** | `supabase.auth.signUp({ email, password, options: { data: { full_name: '...' } } })`. The trigger creates the **public.users** row; no manual insert. |
| **Sign in** | `supabase.auth.signInWithPassword({ email, password })`. |
| **Session** | After sign-in, use `supabase.auth.getUser()` or `session.user.id` for the current user’s UUID. |
| **Create conversation** | When starting a new chat, create the row in **public.conversations** with `user_id: session.user.id` (and `messages: []`). Use the returned/conversation `id` as `conversation_id` when calling your backend `/chat`. |
| **Call backend** | Send `conversation_id` and `message` to `POST /chat`. The backend uses the service_role key to load that conversation and its `user_id`, so you don’t need to send the user id in the body. |
| **Protected routes** | Redirect to login if `supabase.auth.getSession()` is null. |

### Summary

- **Frontend**: anon key + Auth (signUp / signIn). Create conversations with `user_id = auth user id`. Call backend with `conversation_id` + `message`.
- **Backend**: service_role key. Fetches conversation (and thus `user_id`) from Supabase; no JWT or user id needed in the request body.

---

## Flow Summary

| Step | Where | What |
|------|--------|------|
| User signs up | Frontend → Supabase Auth | Row in **auth.users** (email, encrypted password). |
| Trigger runs | Supabase DB | Row in **public.users** (same `id`, email, name). |
| User signs in | Frontend → Supabase Auth | JWT with user `id`. |
| App calls backend | Frontend → Backend | Backend uses **service_role** to read/update **public.users** and **conversations**. |

---

## Troubleshooting

- **“Could not find the 'password' column of 'users'”**  
  You’re using Option 2: passwords live only in **auth.users**. Don’t add a `password` column to **public.users**. If the error is in the Supabase UI, refresh the page or reload the schema.

- **Backend can’t update conversations**  
  Ensure the backend env uses the **service_role** key for `SUPABASE_KEY`, not the anon key.

- **Existing public.users rows**  
  Rows created before Auth (e.g. from test data) have their own `id`s. New signups get synced automatically. To link old rows to Auth you’d need a one-off migration (e.g. match by email and set `id` to `auth.users.id`); for new users, the trigger is enough.
