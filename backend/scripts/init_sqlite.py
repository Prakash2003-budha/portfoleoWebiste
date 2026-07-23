import sqlite3


PASSWORD_HASH = "pbkdf2_sha256$706f7274666f6c696f5f666f725f77656972646f735f73656564$4db137a9bb3348fbb99b899a5f04bba2ef379757c8c817076d903ff45dd2c6a8"


schema = """
DROP TABLE IF EXISTS usability_feedback;
DROP TABLE IF EXISTS reflections;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS habits;
DROP TABLE IF EXISTS identity_traits;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS experiences;
DROP TABLE IF EXISTS profiles;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  activated INTEGER NOT NULL DEFAULT 0,
  activation_token TEXT,
  role TEXT NOT NULL DEFAULT 'student',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  display_name TEXT NOT NULL,
  headline TEXT NOT NULL,
  location TEXT,
  bio TEXT,
  avatar_url TEXT,
  avatar_public_id TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE experiences (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  organization TEXT NOT NULL,
  description TEXT,
  start_date TEXT,
  end_date TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  confidence_level INTEGER NOT NULL CHECK (confidence_level BETWEEN 1 AND 5),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE identity_traits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  trait_name TEXT NOT NULL,
  trait_type TEXT NOT NULL,
  description TEXT,
  visibility TEXT NOT NULL DEFAULT 'public',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE habits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  frequency TEXT,
  identity_link TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL DEFAULT 'Untitled post',
  canvas_json TEXT NOT NULL,
  thumbnail TEXT NOT NULL,
  width INTEGER NOT NULL DEFAULT 1080,
  height INTEGER NOT NULL DEFAULT 1080,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE reflections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  mood TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE usability_feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  visitor_name TEXT DEFAULT 'Anonymous',
  clarity_rating INTEGER NOT NULL CHECK (clarity_rating BETWEEN 1 AND 5),
  identity_rating INTEGER NOT NULL CHECK (identity_rating BETWEEN 1 AND 5),
  comments TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS canvas_layouts;
CREATE TABLE canvas_layouts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  canvas_width INTEGER NOT NULL DEFAULT 1000,
  canvas_height INTEGER NOT NULL DEFAULT 1300,
  background_color TEXT NOT NULL DEFAULT '#ffffff',
  elements TEXT NOT NULL DEFAULT '[]',
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


import os


def init_sqlite_db(path=None, seed=True):
    """(Re)create the sqlite schema at `path` (defaults to SQLITE_PATH env
    var, falling back to backend/portfolio_weirdos.db). Set seed=False to
    get an empty-but-schema-correct database, e.g. for tests."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if path is None:
        path = os.getenv("SQLITE_PATH") or os.path.join(base_dir, "portfolio_weirdos.db")

    connection = sqlite3.connect(path)
    connection.executescript(schema)

    if not seed:
        connection.commit()
        connection.close()
        print(f"Created empty schema at {path}")
        return

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (id, full_name, email, password_hash, activated, role) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "Sujit Khadgi", "sujit@example.com", PASSWORD_HASH, 1, "student"),
    )
    cursor.execute(
        "INSERT INTO profiles (user_id, display_name, headline, location, bio) VALUES (?, ?, ?, ?, ?)",
        (
            1,
            "Sujit Khadgi",
            "Computing student building a relational portfolio for full-person identity",
            "Birmingham / Kathmandu",
            "A portfolio that includes the formal evidence of skill and the more human details: habits, contradictions, creative energy, strengths, weaknesses, and reflections.",
        ),
    )
    cursor.execute(
        "INSERT INTO experiences (user_id, title, organization, description, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)",
        (
            1,
            "Project Developer",
            "Portfolio for Weirdos",
            "Designed a prototype portfolio system that combines professional records with structured identity attributes.",
            "2025-12-01",
            None,
        ),
    )
    cursor.executemany(
        "INSERT INTO skills (user_id, name, category, confidence_level) VALUES (?, ?, ?, ?)",
        [
            (1, "Relational database design", "Technical", 4),
            (1, "Human-centred design", "Design", 4),
            (1, "Prototype development", "Technical", 4),
            (1, "Reflective writing", "Identity", 5),
        ],
    )
    cursor.executemany(
        "INSERT INTO identity_traits (user_id, trait_name, trait_type, description, visibility) VALUES (?, ?, ?, ?, ?)",
        [
            (1, "Creative outsider thinking", "strength", "Looks for unusual angles instead of only repeating standard portfolio formats.", "public"),
            (1, "Overthinking useful details", "weakness", "Can spend too long polishing ideas, but it often reveals better design questions.", "public"),
            (1, "Playful seriousness", "personality", "Takes meaningful work seriously without making the whole experience lifeless.", "public"),
        ],
    )
    cursor.executemany(
        "INSERT INTO habits (user_id, name, frequency, identity_link) VALUES (?, ?, ?, ?)",
        [
            (1, "Collecting odd project ideas", "Weekly", "Keeps the portfolio connected to curiosity and non-traditional learning."),
            (1, "Writing reflection notes", "After milestones", "Turns personal development into structured evidence."),
        ],
    )
    import json as _json

    _sample_canvas = _json.dumps({
        "version": "5.3.0",
        "background": "#1b6f5c",
        "objects": [
            {"type": "textbox", "left": 90, "top": 320, "width": 900, "text": "Sujit is\nstill becoming.",
             "fontFamily": "Inter", "fontSize": 96, "fontWeight": 800, "fill": "#f7f3ea"},
            {"type": "textbox", "left": 90, "top": 640, "width": 700, "text": "Welcome to my wall — made in the Studio, not a form.",
             "fontFamily": "Inter", "fontSize": 32, "fill": "#d7f5e9"},
        ],
    })
    _sample_thumb = (
        "data:image/svg+xml;base64,"
        + __import__("base64").b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080">'
            b'<rect width="1080" height="1080" fill="#1b6f5c"/>'
            b'<text x="80" y="420" font-family="sans-serif" font-size="96" font-weight="800" fill="#f7f3ea">Sujit is</text>'
            b'<text x="80" y="520" font-family="sans-serif" font-size="96" font-weight="800" fill="#f7f3ea">still becoming.</text>'
            b'<text x="80" y="620" font-family="sans-serif" font-size="32" fill="#d7f5e9">Welcome to my wall - made in the Studio, not a form.</text>'
            b'</svg>'
        ).decode()
    )
    cursor.execute(
        "INSERT INTO posts (user_id, title, canvas_json, thumbnail, width, height) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "Still becoming", _sample_canvas, _sample_thumb, 1080, 1080),
    )
    cursor.execute(
        "INSERT INTO reflections (user_id, title, body, mood) VALUES (?, ?, ?, ?)",
        (1, "Why this portfolio exists", "Traditional portfolios show achievement, but they often miss the person behind the achievement. This prototype stores both.", "Focused"),
    )
    cursor.execute(
        "INSERT INTO usability_feedback (visitor_name, clarity_rating, identity_rating, comments) VALUES (?, ?, ?, ?)",
        ("Sample tester", 5, 5, "The portfolio makes the identity traits visible without losing structure."),
    )
    connection.commit()
    connection.close()
    print(f"Created schema at {path} with seed login sujit@example.com / password123")


if __name__ == "__main__":
    init_sqlite_db()
