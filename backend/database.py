"""
database.py
-----------
Thin database abstraction so the rest of the backend never has to care
whether it's talking to SQLite (quick local preview) or MySQL (the
engine named in the project proposal). Same idea as the original
prototype's Database class, just pulled into its own module.
"""

import os
import sqlite3

# config.py already loaded .env from BASE_DIR, so the DB_ENGINE /
# SQLITE_PATH env vars are available here without re-calling load_dotenv.
# This also means importing database.py on its own (e.g. in tests) works
# as long as config.py is imported first, which app.py does.


class Database:
    def __init__(self):
        self.engine = os.getenv("DB_ENGINE", "sqlite").lower()
        self.placeholder = "%s" if self.engine == "mysql" else "?"
        if self.engine == "mysql":
            import mysql.connector

            self.mysql = mysql.connector
            self.path = None
        else:
            self.mysql = None
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.path = os.getenv("SQLITE_PATH", os.path.join(base_dir, "portfolio_weirdos.db"))

    def connect(self):
        if self.engine == "mysql":
            return self.mysql.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
            )
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def fetchall(self, sql, params=()):
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True) if self.engine == "mysql" else connection.cursor()
            cursor.execute(self._sql(sql), params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def fetchone(self, sql, params=()):
        rows = self.fetchall(sql, params)
        return rows[0] if rows else None

    def execute(self, sql, params=()):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute(self._sql(sql), params)
            connection.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        finally:
            connection.close()

    def _sql(self, sql):
        # All SQL in this codebase uses ``?`` as the parameter placeholder.
        # When running against MySQL we swap ``?`` for ``%s``. A plain
        # str.replace is sufficient here because no SQL string in this
        # project embeds a literal ``?`` inside a quoted string literal.
        return sql.replace("?", self.placeholder)


db = Database()
