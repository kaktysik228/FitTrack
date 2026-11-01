import sqlite3
import os
from models.models import User

def get_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "fittrack.db")
    return sqlite3.connect(db_path)

def get_user_by_login(username: str) -> User | None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Проверяем, если таблица пустая, создадим тестового админа под вашу структуру
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT OR IGNORE INTO roles (id, code, name) VALUES (1, 'ADMIN', 'Admin');")
            cur.execute("INSERT OR IGNORE INTO users (id, role_id, username, password_hash, is_active) VALUES (1, 1, 'admin', 'admin123', 1);")
            conn.commit()

        cur.execute("SELECT id, username, password_hash, role_id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return User(*row) if row else None
    finally:
        conn.close()

def create_user(username: str, password_hash: str, role_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash, role_id, is_active) VALUES (?, ?, ?, 1)", 
                    (username, password_hash, role_id))
        user_id = cur.lastrowid
        conn.commit()
        return user_id
    finally:
        conn.close()
