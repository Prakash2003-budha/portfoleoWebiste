from database import db

PORTFOLIO_SECTIONS = {
    "education": {
        "label": "Education",
        "primary": "institution",
        "secondary": "qualification",
        "fields": [
            {"name": "institution", "label": "Institution", "required": True},
            {"name": "qualification", "label": "Qualification", "required": True},
            {"name": "start_year", "label": "Start year", "type": "number"},
            {"name": "end_year", "label": "End year", "type": "number"},
        ],
    },
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
    "achievements": {
        "label": "Achievements",
        "primary": "title",
        "secondary": "description",
        "fields": [
            {"name": "title", "label": "Title", "required": True},
            {"name": "description", "label": "Description"},
            {"name": "achieved_on", "label": "Date", "type": "date"},
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


class CanvasModel:
    """Freeform 'poster / collage' layout: one row per user holding a JSON
    array of positioned elements (text blocks, photos, portfolio-data
    blocks). The frontend owns the shape of each element; the backend just
    stores and returns the blob so the design surface can evolve without
    schema migrations for every new element type.
    """

    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 1300
    DEFAULT_BACKGROUND = "#ffffff"

    @classmethod
    def get_by_user(cls, user_id):
        return db.fetchone("SELECT * FROM canvas_layouts WHERE user_id = ?", (user_id,))

    @classmethod
    def upsert(cls, user_id, canvas_width, canvas_height, background_color, elements_json):
        existing = cls.get_by_user(user_id)
        if existing:
            db.execute(
                """UPDATE canvas_layouts
                   SET canvas_width = ?, canvas_height = ?, background_color = ?,
                       elements = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE user_id = ?""",
                (canvas_width, canvas_height, background_color, elements_json, user_id),
            )
            return existing["id"]

        return db.execute(
            """INSERT INTO canvas_layouts
               (user_id, canvas_width, canvas_height, background_color, elements)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, canvas_width, canvas_height, background_color, elements_json),
        )


class FeedbackModel:
    @classmethod
    def create(cls, visitor_name, clarity_rating, identity_rating, comments):
        return db.execute(
            """INSERT INTO usability_feedback
               (visitor_name, clarity_rating, identity_rating, comments) VALUES (?, ?, ?, ?)""",
            (visitor_name, clarity_rating, identity_rating, comments),
        )