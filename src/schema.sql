-- Включаем поддержку внешних ключей в SQLite
PRAGMA foreign_keys = ON;

-- ========================================================
-- 1. УДАЛЕНИЕ ТАБЛИЦ (в обратном порядке зависимостей)
-- ========================================================
DROP TABLE IF EXISTS visits;
DROP TABLE IF EXISTS client_memberships;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS membership_types;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- ========================================================
-- 2. СОЗДАНИЕ ТАБЛИЦ (по порядку зависимостей)
-- ========================================================

-- Таблица ролей пользователей (справочник)
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

-- Таблица аккаунтов пользователей
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE RESTRICT
);

-- Таблица сотрудников клуба (администраторы ресепшена)
CREATE TABLE staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL,
    phone TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Таблица справочника тарифов / типов абонементов
CREATE TABLE membership_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    duration_days INTEGER NOT NULL,
    total_visits INTEGER, -- NULL означает безлимитный абонемент
    is_active INTEGER NOT NULL DEFAULT 1
);

-- Таблица профилей клиентов клуба
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE, -- NULL, если клиент не пользуется личным кабинетом
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    birth_day DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Таблица купленных абонементов (клубных карт)
CREATE TABLE client_memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    membership_type_id INTEGER NOT NULL,
    card_number TEXT NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    remaining_visits INTEGER, -- остаток занятий
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    purchased_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
    FOREIGN KEY (membership_type_id) REFERENCES membership_types (id) ON DELETE RESTRICT
);

-- Таблица журнала посещений
CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    client_membership_id INTEGER NOT NULL,
    registered_by_staff_id INTEGER NOT NULL,
    check_in_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    check_out_at TEXT,
    status TEXT NOT NULL DEFAULT 'SUCCESS',
    notes TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
    FOREIGN KEY (client_membership_id) REFERENCES client_memberships (id) ON DELETE CASCADE,
    FOREIGN KEY (registered_by_staff_id) REFERENCES staff (id) ON DELETE RESTRICT
);

-- ========================================================
-- 3. ТЕСТОВЫЕ ДАННЫЕ (INSERT INTO)
-- ========================================================

-- Роли
INSERT INTO roles (code, name) VALUES
('ADMIN', 'Администратор'),
('CLIENT', 'Клиент клуба');

-- Пользователи (аккаунты)
INSERT INTO users (role_id, username, password_hash, is_active) VALUES
(1, 'admin_kitik', 'hash_admin_123', 1),
(2, 'varya_tikhova', 'hash_varya_123', 1),
(2, 'anatolii_rusanov', 'hash_anatolii_123', 1);

-- Персонал
INSERT INTO staff (user_id, full_name, position, phone) VALUES
(1, 'Китов Артем Андреевич', 'Старший администратор', '+79001112233');

-- Тарифные планы
INSERT INTO membership_types (name, description, price, duration_days, total_visits, is_active) VALUES
('Разовый', 'Однократное посещение тренажерного зала', 500.00, 1, 1, 1),
('Стандарт 12', '12 тренировок на 30 дней', 3500.00, 30, 12, 1),
('Безлимит Месяц', 'Неограниченное число визитов на 30 дней', 4500.00, 30, NULL, 1);

-- Клиенты
INSERT INTO clients (user_id, first_name, last_name, middle_name, phone, email, birth_day, status) VALUES
(2, 'Варвара', 'Тихова', 'Алексеевна', '+79101234567', 'ivan@mail.ru', '1995-05-14', 'ACTIVE'),
(3, 'Анатолий', 'Русанов', 'Дмитриевич', '+79207654321', 'anna@yandex.ru', '2001-09-20', 'ACTIVE'),
(NULL, 'Иван', 'Петров', 'Алексеевич', '+79035554433', NULL, '1988-12-03', 'ACTIVE');

-- Выданные абонементы
INSERT INTO client_memberships (client_id, membership_type_id, card_number, start_date, end_date, remaining_visits, status) VALUES
(1, 2, 'CARD-10001', '2026-03-01', '2026-03-31', 11, 'ACTIVE'),
(2, 3, 'CARD-10002', '2026-03-05', '2026-04-04', NULL, 'ACTIVE'),
(3, 1, 'CARD-10003', '2026-03-10', '2026-03-10', 0, 'DEPLETED');

-- Журнал визитов
INSERT INTO visits (client_id, client_membership_id, registered_by_staff_id, check_in_at, check_out_at, status, notes) VALUES
(1, 1, 1, '2026-03-02 18:30:00', '2026-03-02 20:15:00', 'SUCCESS', 'Первая тренировка'),
(2, 2, 1, '2026-03-06 09:00:00', '2026-03-06 10:30:00', 'SUCCESS', 'Утренняя тренировка');