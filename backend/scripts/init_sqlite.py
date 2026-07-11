import sqlite3


PASSWORD_HASH = "pbkdf2_sha256$706f7274666f6c696f5f666f725f77656972646f735f73656564$4db137a9bb3348fbb99b899a5f04bba2ef379757c8c817076d903ff45dd2c6a8"


schema = """
DROP TABLE IF EXISTS usability_feedback;
DROP TABLE IF EXISTS reflections;
DROP TABLE IF EXISTS habits;
DROP TABLE IF EXISTS identity_traits;
DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS experiences;
DROP TABLE IF EXISTS education;
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
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE education (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  institution TEXT NOT NULL,
  qualification TEXT NOT NULL,
  start_year INTEGER,
  end_year INTEGER,
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

CREATE TABLE achievements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  achieved_on TEXT,
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
"""


import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
connection = sqlite3.connect(os.path.join(BASE_DIR, "portfolio_weirdos.db"))
connection.executescript(schema)
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
cursor.executemany(
    "INSERT INTO education (user_id, institution, qualification, start_year, end_year) VALUES (?, ?, ?, ?, ?)",
    [
        (1, "Birmingham City University", "CMP6200 Individual Honours Project", 2025, 2026),
        (1, "School of Computing and Digital Technology", "Undergraduate Computing pathway", 2024, 2026),
    ],
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
cursor.execute(
    "INSERT INTO achievements (user_id, title, description, achieved_on) VALUES (?, ?, ?, ?)",
    (
        1,
        "Project interim report completed",
        "Defined the problem, aims, objectives, scope, methodology, risks, and ethics for Portfolio for Weirdos.",
        "2026-03-06",
    ),
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
print("Created portfolio_weirdos.db with seed login sujit@example.com / password123")
