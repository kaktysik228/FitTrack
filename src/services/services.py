import repositories.user_repository as user_repo
import repositories.client_repository as client_repo
import repositories.membership_repository as mem_repo
import repositories.visit_repository as visit_repo
from models.models import User, Client, ClientMembership, Visit
from datetime import datetime

def authenticate(username: str, password_hash: str) -> User | None:
    user = user_repo.get_user_by_login(username)
    if user and user.password_hash == password_hash:
        return user
    return None

def register_new_client(username: str, password_hash: str, first_name: str, last_name: str, middle_name: str, phone: str, birth_day_ru: str) -> int:
    # -------------------------------------------------------------------------
    # 1. Очистка входных данных от случайных пробелов по краям
    # -------------------------------------------------------------------------
    username = username.strip()
    password_hash = password_hash.strip()
    first_name = first_name.strip()
    last_name = last_name.strip()
    middle_name = middle_name.strip() if middle_name else ""
    phone = phone.strip()
    birth_day_ru = birth_day_ru.strip()

    # -------------------------------------------------------------------------
    # 2. Валидация ЛОГИНА (Username)
    # -------------------------------------------------------------------------
    if not (3 <= len(username) <= 20):
        raise Exception("Ошибка: Логин должен быть длиной от 3 до 20 символов!")
    
    # Разрешаем только латинские буквы, цифры и символ подчеркивания
    for char in username:
        if not (char.isalnum() or char == "_") or (char.isascii() is False):
            raise Exception("Ошибка: Логин может содержать только латинские буквы, цифры и нижнее подчеркивание (_)!")

    # -------------------------------------------------------------------------
    # 3. Валидация ПАРОЛЯ
    # -------------------------------------------------------------------------
    if len(password_hash) < 6:
        raise Exception("Ошибка: Пароль должен быть не короче 6 символов!")
    if " " in password_hash:
        raise Exception("Ошибка: Пароль не должен содержать пробелы!")

    # -------------------------------------------------------------------------
    # 4. Валидация ФИО (Используем нашу функцию проверки на буквы)
    # -------------------------------------------------------------------------
    def is_valid_name(name_str: str) -> bool:
        clean_name = name_str.replace("-", "")
        return clean_name.isalpha() and 2 <= len(name_str) <= 40

    if not is_valid_name(first_name):
        raise Exception("Ошибка: Имя должно состоять только из букв и быть длиной от 2 до 40 символов!")

    if not is_valid_name(last_name):
        raise Exception("Ошибка: Фамилия должна состоять только из букв и быть длиной от 2 до 40 символов!")

    if middle_name and not is_valid_name(middle_name):
        raise Exception("Ошибка: Отчество должно состоять только из букв и быть длиной от 2 до 40 символов!")

    # -------------------------------------------------------------------------
    # 5. Валидация ТЕЛЕФОНА
    # -------------------------------------------------------------------------
    # Удаляем из ввода пользователя всё, кроме цифр (плюсы, скобки, дефисы, пробелы)
    clean_phone = "".join([char for char in phone if char.isdigit()])
    
    if not (10 <= len(clean_phone) <= 11):
        raise Exception("Ошибка: Номер телефона должен содержать 10 или 11 цифр!")

    # -------------------------------------------------------------------------
    # 6. Валидация и конвертация ДАТЫ РОЖДЕНИЯ
    # -------------------------------------------------------------------------
    try:
        parts = birth_day_ru.replace("/", ".").replace(" ", ".").split(".")
        if len(parts) != 3:
            raise Exception
        
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
        
        # Проверяем реальность существования даты (например, чтобы не ввели 45-й день или 15-й месяц)
        test_date = datetime(year, month, day)
        
        # Проверяем адекватность возраста (клиент не может родиться в будущем или быть старше 120 лет)
        current_year = datetime.now().year
        if year > current_year or year < (current_year - 120):
            raise Exception
            
        birth_day_sql = f"{parts[2]}-{parts[1]}-{parts[0]}"
    except:
        raise Exception("Ошибка: Неверная дата рождения! Вводите реальную дату в формате ДД.ММ.ГГГГ (например: 17.12.2007)")

    # -------------------------------------------------------------------------
    # 7. Проверка уникальности логина в базе данных
    # -------------------------------------------------------------------------
    if user_repo.get_user_by_login(username):
        raise Exception("Ошибка: Этот логин уже занят другим пользователем!")
        
    # -------------------------------------------------------------------------
    # 8. Если все 7 кругов проверок пройдены — сохраняем данные в БД
    # -------------------------------------------------------------------------
    user_id = user_repo.create_user(username, password_hash, role_id=2)
    return client_repo.create_client(user_id, first_name, last_name, middle_name if middle_name else None, clean_phone, birth_day_sql)

# --- ОСТАЛЬНЫЕ ФУНКЦИИ СЕРВИСА ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ ---
def assign_membership_to_client(client_id: int, type_id: int, card_number: str, override: bool = False):
    card_number = card_number.strip()
    if not card_number:
        raise Exception("Номер карты не может быть пустым!")
        
    # Ищем, есть ли у клиента УЖЕ активный абонемент в базе данных
    existing_membership = mem_repo.get_active_membership(client_id)
    
    # Если абонемент найден, а администратор ЕЩЕ НЕ подтвердил перезапись (override == False)
    if existing_membership and not override:
        # Выбрасываем специальную ошибку с информацией о текущей карте
        raise ValueError(
            f"У клиента уже есть АКТИВНЫЙ абонемент (Карта: {existing_membership.card_number}, "
            f"остаток визитов: {existing_membership.remaining_visits if existing_membership.remaining_visits is not None else 'Безлимит'})."
        )
        
    # Если абонемента не было или администратор осознанно согласился его заменить — создаем новую карту
    mem_repo.create_membership(client_id, type_id, card_number)


def check_in_client(client_id: int):
    # 1. Ищем активный абонемент клиента в базе данных
    membership = mem_repo.get_active_membership(client_id)
    if not membership:
        raise Exception("У этого клиента нет активного абонемента!")
        
    # 2. Проверяем срок действия карты (для всех тарифов)
    current_date = datetime.now().strftime("%Y-%m-%d")
    if membership.end_date < current_date:
        raise Exception(f"Срок действия абонемента истёк! (Был активен до: {membership.end_date})")
        
    # 3. ЕСЛИ ТАРИФ ЛИМИТНЫЙ (количество визитов — это число, а не None)
    if membership.remaining_visits is not None:
        if membership.remaining_visits <= 0:
            raise Exception("На абонементе закончились доступные занятия!")
        # Списываем 1 занятие
        mem_repo.decrease_visits(membership.id)
    else:
        # ЕСЛИ ТАРИФ БЕЗЛИМИТНЫЙ (remaining_visits равен None)
        # Просто пропускаем списание, ничего не вычитая
        pass
        
    # 4. Фиксируем успешный проход клиента в электронном журнале визитов
    visit_repo.log_visit(client_id, membership.id, staff_id=1)


def get_all_clients_list() -> list[Client]:
    return client_repo.get_all_clients()

def get_global_visit_log() -> list[Visit]:
    return visit_repo.get_all_visits()

def get_client_profile_by_user(user_id: int) -> tuple[Client, ClientMembership | None]:
    client = client_repo.get_client_by_user_id(user_id)
    if not client:
        raise Exception("Профиль клиента не найден в базе!")
    membership = mem_repo.get_active_membership(client.id)
    return client, membership

def get_client_personal_history(client_id: int) -> list[Visit]:
    return visit_repo.get_client_visits(client_id)

def cancel_client_membership(client_id: int):
    # Проверяем, есть ли вообще активный абонемент перед удалением
    membership = mem_repo.get_active_membership(client_id)
    if not membership:
        raise Exception("У этого клиента и так нет активного абонемента!")
    # Удаляем абонемент
    mem_repo.delete_membership_by_client_id(client_id)

def remove_client_from_system(client_id: int):
    # Проверяем, существует ли вообще такой клиент в списке
    clients = client_repo.get_all_clients()
    exists = any(c.id == client_id for c in clients)
    if not exists:
        raise Exception("Клиент с таким ID не найден в системе!")
    # Вызываем репозиторий для полного удаления
    client_repo.delete_client_and_user(client_id)
