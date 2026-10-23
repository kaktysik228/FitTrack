import os
import sqlite3

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fittrack.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def init_database():
    print(f"[*] Инициализация базы данных: {DB_PATH}")

    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Файл схемы не найден: {SCHEMA_PATH}")

    # Подключение к SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Обязательно включаем поддержку внешних ключей в SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Читаем и выполняем весь SQL-скрипт
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()

        cursor.executescript(sql_script)
        conn.commit()
        print("База данных успешно создана и заполнена тестовыми данными!\n")

        # Проверка: выводим список таблиц и количество строк
        check_database(cursor)

    except sqlite3.Error as e:
        print(f"[-] Ошибка SQLite: {e}")
    finally:
        conn.close()


def check_database(cursor):
    """Выводит сводку по созданным таблицам для проверки."""
    tables = [
        "roles",
        "users",
        "staff",
        "membership_types",
        "clients",
        "client_memberships",
        "visits",
    ]

    print("=" * 60)
    print(f"{'ТАБЛИЦА':<25} | {'КОЛ-ВО ЗАПИСЕЙ':<15}")
    print("=" * 60)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"{table:<25} | {count:<15}")

    print("=" * 60)
    print("\nПример выборки визитов с именами клиентов:")
    cursor.execute("""
        SELECT 
            v.id,
            c.last_name || ' ' || c.first_name AS client_name,
            cm.card_number,
            v.check_in_at,
            s.full_name AS staff_name
        FROM visits v
        JOIN clients c ON v.client_id = c.id
        JOIN client_memberships cm ON v.client_membership_id = cm.id
        JOIN staff s ON v.registered_by_staff_id = s.id;
    """)
    for row in cursor.fetchall():
        print(f"Визит #{row[0]}: {row[1]} (Карта: {row[2]}) в {row[3]} — проверил(а): {row[4]}")


if __name__ == "__main__":
    init_database()