import sqlite3
import os
from models.models import Visit
from datetime import datetime

def get_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "fittrack.db")
    return sqlite3.connect(db_path)

def log_visit(client_id: int, membership_id: int, staff_id: int = 1):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Проверяем, есть ли сотрудники в таблице staff, если пусто — создаем дефолтного ресепшиониста
        cur.execute("SELECT COUNT(*) FROM staff")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT OR IGNORE INTO staff (id, full_name, position) VALUES (1, 'Дежурный администратор', 'Ресепшен');")
            conn.commit()

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO visits (client_id, client_membership_id, registered_by_staff_id, check_in_at, status) 
            VALUES (?, ?, ?, ?, 'CHECKED_IN')
        """, (client_id, membership_id, staff_id, now_str))
        conn.commit()
    finally:
        conn.close()

def get_all_visits() -> list[Visit]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT v.id, v.client_id, v.client_membership_id, v.registered_by_staff_id, v.check_in_at, 
                   c.last_name || ' ' || c.first_name
            FROM visits v
            JOIN clients c ON v.client_id = c.id
            ORDER BY v.check_in_at DESC
        """)
        rows = cur.fetchall()
        return [Visit(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]
    finally:
        conn.close()

def get_client_visits(client_id: int) -> list[Visit]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, client_id, client_membership_id, registered_by_staff_id, check_in_at FROM visits WHERE client_id = ?", (client_id,))
        rows = cur.fetchall()
        return [Visit(r[0], r[1], r[2], r[3], r[4], "Вы") for r in rows]
    finally:
        conn.close()
