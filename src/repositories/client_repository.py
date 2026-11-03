import sqlite3
import os
from models.models import Client

def get_connection():
    # Находим корень проекта, где лежит ваш настоящий fittrack.db
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "fittrack.db")
    return sqlite3.connect(db_path)

def create_client(user_id: int | None, first_name: str, last_name: str, middle_name: str, phone: str, birth_day: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO clients (user_id, first_name, last_name, middle_name, phone, birth_day, status) 
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (user_id, first_name, last_name, middle_name, phone, birth_day))
        client_id = cur.lastrowid
        conn.commit()
        return client_id
    finally:
        conn.close()



def get_client_by_user_id(user_id: int) -> Client | None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Связываем клиента с его учетной записью, чтобы забрать логин и пароль
        cur.execute("""
            SELECT c.id, c.user_id, c.first_name, c.last_name, c.middle_name, c.phone, 
                   c.email, c.birth_day, u.username, u.password_hash
            FROM clients c
            JOIN users u ON c.user_id = u.id
            WHERE c.user_id = ?
        """, (user_id,))
        row = cur.fetchone()
        if row:
            # Создаем объект клиента
            client = Client(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            # Временно сохраняем логин и хэш пароля прямо в объект для UI
            client.status = row[8]       # Используем как временное хранилище для username
            client.created_at = row[9]   # Используем как временное хранилище для password_hash
            return client
        return None
    finally:
        conn.close()


def delete_client_and_user(client_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Сначала узнаем user_id этого клиента, чтобы удалить его аккаунт
        cur.execute("SELECT user_id FROM clients WHERE id = ?", (client_id,))
        row = cur.fetchone()
        
        # 2. Удаляем самого клиента (каскадом удалятся и абонементы из-за внешних ключей)
        cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        
        # 3. Если у клиента был привязан аккаунт, удаляем его из таблицы users
        if row and row[0]:
            cur.execute("DELETE FROM users WHERE id = ?", (row[0],))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_clients() -> list[Client]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Связываем клиента с его активным абонементом и типом абонемента
        cur.execute("""
            SELECT c.id, c.user_id, c.first_name, c.last_name, c.middle_name, c.phone,
                   cm.card_number, cm.remaining_visits, cm.end_date, mt.name
            FROM clients c
            LEFT JOIN client_memberships cm ON c.id = cm.client_id AND cm.status = 'ACTIVE'
            LEFT JOIN membership_types mt ON cm.membership_type_id = mt.id
        """)
        rows = cur.fetchall()
        
        clients_list = []
        for r in rows:
            client = Client(
                id=r[0],
                user_id=r[1],
                first_name=r[2],
                last_name=r[3],
                middle_name=r[4],
                phone=r[5]
            )
            
            # Формируем текст статуса для интерфейса (UI), используя индексы от 6 до 9
            if r[6]:  # Если есть номер бесконтактной карты (card_number)
                card_num = r[6]
                visits = r[7] if r[7] is not None else 'Безлимит'
                expire_date = r[8]
                tariff_name = r[9]
                client.membership_info = f"Карта: {card_num} | Тариф: '{tariff_name}' | Визитов: {visits} | До: {expire_date}"
            else:
                client.membership_info = " Нет активного абонемента"
                
            clients_list.append(client)
            
        return clients_list
    finally:
        conn.close()




