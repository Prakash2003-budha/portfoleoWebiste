import argparse
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
SQLITE_PATH = os.getenv("SQLITE_PATH") or "portfolio_weirdos.db"

if DB_ENGINE != "sqlite":
    raise SystemExit("This reset helper only works for sqlite databases.")

DB_PATH = Path(SQLITE_PATH) if Path(SQLITE_PATH).is_absolute() else BASE_DIR / SQLITE_PATH


def list_users():
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found at {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT id, full_name, email, activated FROM users ORDER BY id").fetchall()
    if not rows:
        print("No users found.")
        return
    print("Registered users:")
    for row in rows:
        status = "activated" if row["activated"] else "pending"
        print(f"- {row['email']} ({row['full_name']}) [{status}]")


def delete_user(email):
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found at {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (email,))
        row = cur.fetchone()
        if not row:
            raise SystemExit(f"No user found with email: {email}")
        user_id = row[0]
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    print(f"Deleted user {email} from {DB_PATH}")


def reset_database():
    from init_sqlite import init_sqlite_db

    print(f"Resetting database at {DB_PATH}")
    init_sqlite_db(path=str(DB_PATH))


def main():
    parser = argparse.ArgumentParser(description="Reset or remove a user from the local SQLite database.")
    parser.add_argument("--list", action="store_true", help="List all registered users.")
    parser.add_argument("--email", help="Delete a user by email address.")
    parser.add_argument("--reset", action="store_true", help="Reset the database to the seeded sample state.")

    args = parser.parse_args()

    if args.list:
        list_users()
        return

    if args.email:
        delete_user(args.email)
        return

    if args.reset:
        reset_database()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
