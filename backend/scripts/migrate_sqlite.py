import sqlite3
import os
from pathlib import Path


def migrate_sqlite_db():
    base_dir = Path(__file__).resolve().parent.parent
    db_path = Path(os.getenv("SQLITE_PATH", str(base_dir / "portfolio_weirdos.db")))

    print(f"Migrating SQLite database at {db_path}")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(users);")
    columns = [row[1] for row in cursor.fetchall()]

    if "activated" not in columns:
        print("Adding activated column to users table")
        cursor.execute("ALTER TABLE users ADD COLUMN activated INTEGER NOT NULL DEFAULT 0")
        cursor.execute("UPDATE users SET activated = 1")

    if "activation_token" not in columns:
        print("Adding activation_token column to users table")
        cursor.execute("ALTER TABLE users ADD COLUMN activation_token TEXT")

    cursor.execute("PRAGMA table_info(profiles);")
    profile_columns = [row[1] for row in cursor.fetchall()]

    if "avatar_url" not in profile_columns:
        print("Adding avatar_url column to profiles table")
        cursor.execute("ALTER TABLE profiles ADD COLUMN avatar_url TEXT")

    if "avatar_public_id" not in profile_columns:
        print("Adding avatar_public_id column to profiles table")
        cursor.execute("ALTER TABLE profiles ADD COLUMN avatar_public_id TEXT")

    cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name='posts';"""
    )
    if not cursor.fetchone():
        print("Creating posts table (visual Canva-style posts)")
        cursor.execute(
            """
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
            )
            """
        )

    cursor.execute("DROP TABLE IF EXISTS education")
    cursor.execute("DROP TABLE IF EXISTS achievements")

    connection.commit()
    connection.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate_sqlite_db()