# Schoolhouse frontend (React)

A small React (Vite) app wired to your FastAPI backend:

- `/login` — sign in
- `/signup` — register as student, teacher, or parent
- `/chat` — chat with the agent, streamed token-by-token from `POST /chat/stream/{role}`
- `/profile` — shows the profile for whichever role is logged in (`/students/profile`, `/teachers/profile`, `/parents/profile`)

## Run it

```bash
cd react-frontend
npm install
npm run dev
```

By default it talks to `http://localhost:8080`. To point at a different backend, create `.env`:

```
VITE_API_BASE=http://localhost:8080
```

## Assumptions made about the backend

1. **Login response shape.** `AuthContext.jsx` assumes `POST /auth/login` returns
   `{ access_token, token_type, role, user_id }`. If your `TokenResponse` schema uses
   different field names, update `loginWithResponse` in `src/context/AuthContext.jsx`.
2. **Bearer auth.** Every authenticated request sends `Authorization: Bearer <access_token>`.
   This assumes `require_role` reads the token from that header.
3. **Registration fields.** The signup form sends the fields your `StudentRegister` /
   `TeacherRegister` / `ParentRegister` schemas use in the snippets you shared
   (`name`, `email`, `password`, plus `class_name`/`roll_number`, `subject`, or
   `phone`/`student_id`). Adjust `src/pages/Signup.jsx` if your actual schemas differ.

## Two things worth fixing in the backend before this will fully work

- In `app.py`, both `history()` and `chat_stream()` write
  `current_user = Depends(require_role(role))` **inside the function body**. `Depends(...)`
  only resolves when it's a parameter default — written this way, `current_user` is just the
  `Depends` wrapper object, not the decoded user, and `current_user["user_id"]` will raise.
  It needs to be a parameter, e.g. `async def chat_stream(request: Request, role: str, current_user=Depends(require_role(role))):`
  (and `require_role(role)` itself can't depend on a path param that way in FastAPI — you'd
  typically pass `role` as a query/body value and check it against the token's claimed role
  inside the dependency instead).
- The `/chat/history/{role}` route is missing its leading slash (`"chat/history/{role}"` →
  `"/chat/history/{role}"`), and `get_chat_history(user_id, thread_id)` is called with only
  `user_id` for `build_thread_id`, which expects `(user_id, role)`.

The frontend is written to work once those are fixed — it already sends the Bearer token and
calls the routes with a leading slash.
