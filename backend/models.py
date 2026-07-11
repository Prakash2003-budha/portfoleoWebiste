from database import db


class UserModel:
    @classmethod
    def exists_by_email(cls, email):
        return db.fetchone("SELECT id FROM users WHERE lower(email) = lower(?)", (email,))

    @classmethod
    def find_by_email(cls, email):
        return db.fetchone("SELECT * FROM users WHERE lower(email) = lower(?)", (email,))

    @classmethod
    def get_by_id(cls, user_id):
        return db.fetchone("SELECT id, email, full_name, role FROM users WHERE id = ?", (user_id,))

    @classmethod
    def create(cls, full_name, email, password_hash):
        return db.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            (full_name, email, password_hash),
        )


class ProfileModel:
    @classmethod
    def list_public(cls):
        rows = db.fetchall(
            """SELECT profiles.*, users.full_name
               FROM profiles JOIN users ON users.id = profiles.user_id
               ORDER BY profiles.id DESC"""
        )
        return rows

    @classmethod
    def get_by_id(cls, profile_id):
        return db.fetchone(
            """SELECT profiles.*, users.full_name, users.email
               FROM profiles JOIN users ON users.id = profiles.user_id
               WHERE profiles.id = ?""",
            (profile_id,),
        )

    @classmethod
    def get_by_user_id(cls, user_id):
        return db.fetchone("SELECT * FROM profiles WHERE user_id = ?", (user_id,))

    @classmethod
    def upsert_for_user(cls, user_id, display_name, headline, location, bio):
        existing = cls.get_by_user_id(user_id)
        if existing:
            db.execute(
                "UPDATE profiles SET display_name = ?, headline = ?, location = ?, bio = ? WHERE user_id = ?",
                (display_name, headline, location, bio, user_id),
            )
            return existing["id"]

        return db.execute(
            "INSERT INTO profiles (user_id, display_name, headline, location, bio) VALUES (?, ?, ?, ?, ?)",
            (user_id, display_name, headline, location, bio),
        )

    @classmethod
    def count_all(cls):
        return db.fetchone("SELECT COUNT(*) AS total FROM profiles")["total"]

    @classmethod
    def list_recent(cls, limit=6):
        return db.fetchall(
            """SELECT profiles.*, users.full_name
               FROM profiles JOIN users ON users.id = profiles.user_id
               ORDER BY profiles.id DESC LIMIT ?""",
            (limit,),
        )


class ReflectionModel:
    @classmethod
    def list_for_user(cls, user_id):
        return db.fetchall(
            "SELECT * FROM reflections WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )

    @classmethod
    def count_for_user(cls, user_id):
        return db.fetchone(
            "SELECT COUNT(*) AS total FROM reflections WHERE user_id = ?",
            (user_id,),
        )["total"]

    @classmethod
    def create(cls, user_id, title, body, mood):
        return db.execute(
            "INSERT INTO reflections (user_id, title, body, mood) VALUES (?, ?, ?, ?)",
            (user_id, title, body, mood),
        )


class PortfolioModel:
    @classmethod
    def list_section(cls, table, user_id):
        return db.fetchall(f"SELECT * FROM {table} WHERE user_id = ? ORDER BY id DESC", (user_id,))

    @classmethod
    def add_item(cls, table, user_id, columns, values):
        placeholders = ", ".join(["?"] * (len(columns) + 1))
        column_list = ", ".join(["user_id"] + columns)
        return db.execute(
            f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})",
            tuple([user_id] + values),
        )

    @classmethod
    def get_owner_id(cls, table, item_id):
        return db.fetchone(f"SELECT user_id FROM {table} WHERE id = ?", (item_id,))

    @classmethod
    def delete_item(cls, table, item_id):
        return db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))

    @classmethod
    def owner_profile(cls, user_id):
        return db.fetchone(
            """SELECT profiles.*, users.full_name FROM profiles
               JOIN users ON users.id = profiles.user_id WHERE profiles.user_id = ?""",
            (user_id,),
        )


class FeedbackModel:
    @classmethod
    def create(cls, visitor_name, clarity_rating, identity_rating, comments):
        return db.execute(
            """INSERT INTO usability_feedback
               (visitor_name, clarity_rating, identity_rating, comments) VALUES (?, ?, ?, ?)""",
            (visitor_name, clarity_rating, identity_rating, comments),
        )
