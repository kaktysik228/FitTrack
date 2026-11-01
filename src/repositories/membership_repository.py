import sqlite3
import os
from models.models import ClientMembership
from datetime import datetime, timedelta

def get_connection():
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "fittrack.db")
    return sqlite3.connect(db_path)


def create_membership(client_id: int, type_id: int, card_number: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT total_visits, duration_days FROM membership_types WHERE id = ?", (type_id,))
        tariff = cur.fetchone()
        if not tariff:
            raise Exception("Тип абонемента с таким ID не найден в справочнике!")
            
        total_visits, duration_days = tariff
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d")
        
        # Деактивируем прошлые абонементы
        cur.execute("UPDATE client_memberships SET status = 'INACTIVE' WHERE client_id = ?", (client_id,))
        
        # Вставляем данные строго по вашей структуре из IntelliView
        cur.execute("""
            INSERT INTO client_memberships (client_id, membership_type_id, card_number, start_date, end_date, remaining_visits, status)
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (client_id, type_id, card_number, start_date, end_date, total_visits))
        
        conn.commit()
    finally:
        conn.close()

def get_active_membership(client_id: int) -> ClientMembership | None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Достаем абсолютно ВСЕ 8 колонок строго по вашей схеме из ER-диаграммы
        cur.execute("""
            SELECT id, client_id, membership_type_id, card_number, start_date, end_date, remaining_visits, status
            FROM client_memberships 
            WHERE client_id = ? AND status = 'ACTIVE'
        """, (client_id,))
        row = cur.fetchone()
        if row:
            return ClientMembership(*row)
        return None
    finally:
        conn.close()


def decrease_visits(membership_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Сначала проверяем, лимитный тариф или безлимитный (None)
        cur.execute("SELECT remaining_visits FROM client_memberships WHERE id = ?", (membership_id,))
        row = cur.fetchone()
        
        # 2. Уменьшаем счетчик ТОЛЬКО если там записано число (не None)
        if row and row[0] is not None:
            cur.execute("UPDATE client_memberships SET remaining_visits = remaining_visits - 1 WHERE id = ?", (membership_id,))
            conn.commit()
        else:
            # Если это безлимит (None), ничего не вычитаем, транзакция не нужна
            pass
    finally:
        conn.close()


def delete_membership_by_client_id(client_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM client_memberships WHERE client_id = ?", (client_id,))
        conn.commit()
    finally:
        conn.close()
