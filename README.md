# Portfolio for Weirdos — v2 (Backend / Frontend split)

The original prototype was a single `app.py` that mixed the HTTP server,
routing, database access, and HTML string-templating together. This
version separates it into two independent halves that talk over a JSON
REST API:

```
backend/    Python + Flask API server (no HTML at all)
frontend/   Static HTML/CSS/JS single-page app (no server-side code)
```

They can be run on different machines, different ports, or deployed
separately. During development they just need to know each other's URL.

## 1. Run the backend

```bash
cd backend
python3 -m pip install -r requirements.txt --break-system-packages   # if needed
python3 scripts/init_sqlite.py      # creates backend/portfolio_weirdos.db with seed data
python3 app.py
```

The API now runs at `http://127.0.0.1:5000`. Health check:
`curl http://127.0.0.1:5000/api/health`.

To point it at MySQL instead (matching the original proposal):

```bash
mysql -u root -p < database/mysql_schema.sql
DB_ENGINE=mysql DB_HOST=127.0.0.1 DB_PORT=3306 DB_USER=root DB_PASSWORD=yourpass DB_NAME=portfolio_weirdos python3 app.py
```

## 2. Run the frontend

The frontend is plain static files, so any static server works:

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://127.0.0.1:5500`. If your backend isn't on `127.0.0.1:5000`,
edit the `window.PFW_API_BASE` line at the top of `frontend/index.html`.

## Seed login

- Email: `sujit@example.com`
- Password: `password123`

## What changed vs. the original single-file app

| Concern | Original `app.py` | v2 |
|---|---|---|
| HTTP layer | Raw `http.server` | Flask |
| Response format | Hand-built HTML strings | JSON only — no HTML from the backend |
| Routing | `if/elif` chains in `do_GET`/`do_POST` | Flask blueprints (`routes/auth_routes.py`, `profile_routes.py`, `portfolio_routes.py`, `reflection_routes.py`) |
| UI | Rendered server-side | Rendered client-side by `frontend/js/*` from API responses |
| Auth | Cookie + in-memory session dict | Same idea, moved into `backend/auth.py` |
| Database | `Database` class inline in `app.py` | `backend/database.py`, unchanged logic (SQLite/MySQL dual engine preserved) |

## API summary

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/register` | Create account + draft profile |
| POST | `/api/login` / `/api/logout` | Session cookie auth |
| GET | `/api/me` | Current user |
| GET | `/api/profiles` | Directory of all public profiles |
| GET | `/api/profiles/<id>` | One profile |
| GET/PUT | `/api/profile/me` | Read/update your own profile |
| POST | `/api/profile/me/avatar` | Upload a profile picture to Cloudinary (multipart `avatar` field) |
| GET | `/api/dashboard` | Stats + recent profiles for the dashboard |
| GET | `/api/portfolio/user/<user_id>` | Read-only portfolio evidence for anyone |
| GET | `/api/portfolio/me` | Your own portfolio evidence (editable) |
| POST | `/api/portfolio/<section>` | Add a record (experiences/skills/identity_traits/habits) |
| DELETE | `/api/portfolio/<section>/<id>` | Remove your own record |
| GET/POST | `/api/reflections` | Personal journal entries |
| POST | `/api/feedback` | Usability testing form (Objective 4, no login required) |

## Why this structure for the dissertation

Splitting backend/frontend is easy to defend in a viva: the database
schema and the identity-vs-conventional data split (the actual research
question) live entirely in `backend/`, untouched by presentation
concerns. The frontend can be swapped for a different UI later without
touching the data model — which is a natural "future work" point for
your final report.
