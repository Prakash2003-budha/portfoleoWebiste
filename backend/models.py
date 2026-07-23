from database import db

PORTFOLIO_SECTIONS = {
    "experiences": {
        "label": "Experience",
        "primary": "title",
        "secondary": "organization",
        "fields": [
            {"name": "title", "label": "Title", "required": True},
            {"name": "organization", "label": "Organization", "required": True},
            {"name": "description", "label": "Description"},
            {"name": "start_date", "label": "Start date", "type": "date"},
            {"name": "end_date", "label": "End date", "type": "date"},
        ],
    },
    "skills": {
        "label": "Skills",
        "primary": "name",
        "secondary": "category",
        "fields": [
            {"name": "name", "label": "Skill", "required": True},
            {"name": "category", "label": "Category"},
            {"name": "confidence_level", "label": "Confidence (1-5)", "type": "number"},
        ],
    },
    "identity_traits": {
        "label": "Identity traits",
        "primary": "trait_name",
        "secondary": "description",
        "fields": [
            {"name": "trait_name", "label": "Trait", "required": True},
            {"name": "trait_type", "label": "Type (strength/weakness/personality)"},
            {"name": "description", "label": "Description"},
        ],
    },
    "habits": {
        "label": "Habits",
        "primary": "name",
        "secondary": "identity_link",
        "fields": [
            {"name": "name", "label": "Habit", "required": True},
            {"name": "frequency", "label": "Frequency"},
            {"name": "identity_link", "label": "How it connects to identity"},
        ],
    },
}


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
    def create(cls, full_name, email, password_hash, activation_token=None):
        return db.execute(
            "INSERT INTO users (full_name, email, password_hash, activated, activation_token) VALUES (?, ?, ?, ?, ?)",
            (full_name, email, password_hash, False, activation_token),
        )

    @classmethod
    def resend_activation(cls, user_id, activation_token):
        return db.execute(
            "UPDATE users SET activation_token = ? WHERE id = ? AND activated = ?",
            (activation_token, user_id, False),
        )

    @classmethod
    def activate(cls, token):
        return db.execute(
            "UPDATE users SET activated = ? WHERE activation_token = ? AND activated = ?",
            (True, token, False),
        )

    @classmethod
    def find_by_activation_token(cls, token):
        return db.fetchone("SELECT * FROM users WHERE activation_token = ?", (token,))


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
    def set_avatar(cls, user_id, avatar_url, avatar_public_id=None):
        """Save the Cloudinary URL (and public_id, so a later upload can
        replace/delete the old asset) for this user's profile picture.
        Creates a bare profile row first if one doesn't exist yet, so a
        person can upload a photo before filling in the rest of the form.
        """
        existing = cls.get_by_user_id(user_id)
        if not existing:
            db.execute(
                "INSERT INTO profiles (user_id, display_name, headline, location, bio, avatar_url, avatar_public_id) "
                "VALUES (?, '', '', '', '', ?, ?)",
                (user_id, avatar_url, avatar_public_id),
            )
            return cls.get_by_user_id(user_id)

        db.execute(
            "UPDATE profiles SET avatar_url = ?, avatar_public_id = ? WHERE user_id = ?",
            (avatar_url, avatar_public_id, user_id),
        )
        return cls.get_by_user_id(user_id)

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
    SECTIONS = PORTFOLIO_SECTIONS

    @classmethod
    def get_schema(cls):
        return cls.SECTIONS

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


class PostModel:
    """Backs the Studio's visual posts (posts table). Each post is a saved
    Fabric.js canvas: full editable JSON for the owner, plus a PNG thumbnail
    everyone else can see on the person's Wall."""

    @classmethod
    def list_public(cls, limit=60):
        return db.fetchall(
            """SELECT posts.*, profiles.display_name, users.full_name
               FROM posts
               JOIN users ON users.id = posts.user_id
               LEFT JOIN profiles ON profiles.user_id = posts.user_id
               ORDER BY posts.id DESC LIMIT ?""",
            (limit,),
        )

    @classmethod
    def list_for_user(cls, user_id):
        return db.fetchall(
            """SELECT posts.*, profiles.display_name, users.full_name
               FROM posts
               JOIN users ON users.id = posts.user_id
               LEFT JOIN profiles ON profiles.user_id = posts.user_id
               WHERE posts.user_id = ?
               ORDER BY posts.id DESC""",
            (user_id,),
        )

    @classmethod
    def get_by_id(cls, post_id):
        return db.fetchone(
            """SELECT posts.*, profiles.display_name, users.full_name
               FROM posts
               JOIN users ON users.id = posts.user_id
               LEFT JOIN profiles ON profiles.user_id = posts.user_id
               WHERE posts.id = ?""",
            (post_id,),
        )

    @classmethod
    def create(cls, user_id, title, canvas_json, thumbnail, width, height):
        return db.execute(
            """INSERT INTO posts (user_id, title, canvas_json, thumbnail, width, height)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, canvas_json, thumbnail, width, height),
        )

    @classmethod
    def update(cls, post_id, title, canvas_json, thumbnail, width, height):
        return db.execute(
            """UPDATE posts
               SET title = ?, canvas_json = ?, thumbnail = ?, width = ?, height = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, canvas_json, thumbnail, width, height, post_id),
        )

    @classmethod
    def delete(cls, post_id):
        return db.execute("DELETE FROM posts WHERE id = ?", (post_id,))


class FeedbackModel:

    @classmethod
    def create(cls, visitor_name, clarity_rating, identity_rating, comments):
        return db.execute(
            """INSERT INTO usability_feedback
               (visitor_name, clarity_rating, identity_rating, comments) VALUES (?, ?, ?, ?)""",
            (visitor_name, clarity_rating, identity_rating, comments),
        )