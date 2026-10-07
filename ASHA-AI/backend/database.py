import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


# Database file lives in the same folder as this file
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "asha.db"


def get_db():
    connection = sqlite3.connect(DATABASE)

    # Lets us access columns by name
    connection.row_factory = sqlite3.Row

    # Make sure foreign keys work
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# DATABASE SETUP
# ============================================================

def init_db():

    connection = get_db()

    connection.executescript("""
    
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        risk_level TEXT DEFAULT 'low',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );


    CREATE TABLE IF NOT EXISTS moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mood INTEGER NOT NULL,
        note TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );


    CREATE TABLE IF NOT EXISTS journals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT DEFAULT '',
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );

    """)

    connection.commit()
    connection.close()


# ============================================================
# USERS
# ============================================================

def create_user(name, email, password):

    connection = get_db()

    try:

        password_hash = generate_password_hash(password)

        cursor = connection.execute(
            """
            INSERT INTO users
            (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                name.strip(),
                email.lower().strip(),
                password_hash
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


def authenticate(email, password):

    connection = get_db()

    try:

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email.lower().strip(),)
        ).fetchone()

    finally:

        connection.close()

    if not user:
        return None

    if not check_password_hash(
        user["password_hash"],
        password
    ):
        return None

    return dict(user)


def get_user(user_id):

    connection = get_db()

    try:

        user = connection.execute(
            """
            SELECT id, name, email, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

    finally:

        connection.close()

    if not user:
        return None

    return dict(user)


# ============================================================
# CHAT MESSAGES
# ============================================================

def save_message(user_id, role, content, risk_level="low"):

    connection = get_db()

    try:

        cursor = connection.execute(
            """
            INSERT INTO messages
            (user_id, role, content, risk_level)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                role,
                content,
                risk_level
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


def get_messages(user_id):

    connection = get_db()

    try:

        messages = connection.execute(
            """
            SELECT
                id,
                role,
                content,
                risk_level,
                created_at
            FROM messages
            WHERE user_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (user_id,)
        ).fetchall()

    finally:

        connection.close()

    return [dict(message) for message in messages]


# ============================================================
# MOODS
# ============================================================

def save_mood(user_id, mood, note=""):

    connection = get_db()

    try:

        cursor = connection.execute(
            """
            INSERT INTO moods
            (user_id, mood, note)
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                mood,
                note
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


def get_moods(user_id):

    connection = get_db()

    try:

        moods = connection.execute(
            """
            SELECT
                id,
                mood,
                note,
                created_at
            FROM moods
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,)
        ).fetchall()

    finally:

        connection.close()

    return [dict(mood) for mood in moods]


# ============================================================
# JOURNALS
# ============================================================

def save_journal(user_id, title, content):

    connection = get_db()

    try:

        cursor = connection.execute(
            """
            INSERT INTO journals
            (user_id, title, content)
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                title,
                content
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


def get_journals(user_id):

    connection = get_db()

    try:

        journals = connection.execute(
            """
            SELECT
                id,
                title,
                content,
                created_at,
                updated_at
            FROM journals
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,)
        ).fetchall()

    finally:

        connection.close()

    return [dict(journal) for journal in journals]


def get_journal(user_id, journal_id):

    connection = get_db()

    try:

        journal = connection.execute(
            """
            SELECT
                id,
                title,
                content,
                created_at,
                updated_at
            FROM journals
            WHERE id = ?
            AND user_id = ?
            """,
            (
                journal_id,
                user_id
            )
        ).fetchone()

    finally:

        connection.close()

    if not journal:
        return None

    return dict(journal)


def update_journal(
    user_id,
    journal_id,
    title,
    content
):

    connection = get_db()

    try:

        cursor = connection.execute(
            """
            UPDATE journals

            SET
                title = ?,
                content = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
            AND user_id = ?
            """,
            (
                title,
                content,
                journal_id,
                user_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


def delete_journal(user_id, journal_id):

    connection = get_db()

    try:

        cursor = connection.execute(
            """
            DELETE FROM journals

            WHERE id = ?
            AND user_id = ?
            """,
            (
                journal_id,
                user_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()