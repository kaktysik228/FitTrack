import sys
from datetime import datetime
import services.services as svc

def main():
    print("=== Добро пожаловать в ИС 'FitTrack' ===")
    while True:
        print("\n1. Войти в систему")
        print("0. Выйти")
        choice = input("Выберите действие: ")
        if choice == "1":
            login = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            
            # Проверяем пользователя через слой бизнес-логики
            user = svc.authenticate(login, password)
            if user:
                if user.role_id == 1:
                    admin_menu()
                else:
                    client_menu(user.id)
            else:
                # Наш скрытный вывод ошибки ради безопасности
                print(" Данные введены неверно")
        elif choice == "0":
            print("Программа завершена.")
            

def admin_menu():
    while True:
        print("\n--- МЕНЮ АДМИНИСТРАТОРА (Ресепшен) ---")
        print("1. Зарегистрировать нового клиента")
        print("2. Оформить абонемент клиенту")
        print("3. Отметить визит клиента (Турникет)")
        print("4. Просмотреть список всех клиентов")
        print("5. Посмотреть общий журнал визитов")
        print("6. Удалить абонемент клиента")
        print("7. Полностью удалить клиента из системы")
        print("0. Выйти в главное меню")

        choice = input("Выберите пункт меню: ")
        try:
            if choice == "1":
                print("\n--- Регистрация нового клиента ---")
                
                # 1. Интерактивный ввод ЛОГИНА
                while True:
                    l = input("Придумайте ЛОГИН для входа: ").strip().lower()
                    if not (3 <= len(l) <= 20):
                        print(" Ошибка: ...Логин должен быть длиной от 3 до 20 символов! Попробуйте снова.")
                        continue
                    valid = True
                    for char in l:
                        if not (char.isalnum() or char == "_") or not char.isascii():
                            valid = False
                            break
                    if not valid:
                        print(" Ошибка: Логин может содержать только латинские буквы, цифры и (_)! Попробуйте снова.")
                        continue
                    
                    import repositories.user_repository as user_repo
                    if user_repo.get_user_by_login(l):
                        print(" Ошибка: Этот логин уже занят! Придумайте другой.")
                        continue
                    break

                # 2. Интерактивный ввод ПАРОЛЯ
                while True:
                    p = input("Придумайте ПАРОЛЬ: ").strip()
                    if len(p) < 6:
                        print(" Ошибка: Пароль должен быть не короче 6 символов! Попробуйте снова.")
                        continue
                    if " " in p:
                        print(" Ошибка: Пароль не должен содержать пробелы! Попробуйте снова.")
                        continue
                    break

                def check_name(name_str: str) -> bool:
                    return name_str.replace("-", "").isalpha() and 2 <= len(name_str) <= 40

                # 3. Интерактивный ввод ФАМИЛИИ
                while True:
                    ln = input("Фамилия: ").strip()
                    if not check_name(ln):
                        print(" Ошибка: Фамилия должна состоять только из букв (от 2 до 40)! Попробуйте снова.")
                        continue
                    ln = ln.capitalize()
                    break

                # 4. Интерактивный ввод ИМЕНИ
                while True:
                    fn = input("Имя: ").strip()
                    if not check_name(fn):
                        print(" Ошибка: Имя должно состоять только из букв (от 2 до 40)! Попробуйте снова.")
                        continue
                    fn = fn.capitalize()
                    break

                # 5. Интерактивный ввод ОТЧЕСТВА
                while True:
                    mn = input("Отчество (нажмите Enter, если нет): ").strip()
                    if mn and not check_name(mn):
                        print(" Ошибка: Отчество должно состоять только из букв (от 2 до 40)! Попробуйте снова.")
                        continue
                    if mn:
                        mn = mn.capitalize()
                    break

                # 6. Интерактивный ввод ТЕЛЕФОНА (Строго с +7)
                while True:
                    ph = input("Телефон (только через +7): ").strip()
                    
                    # Жесткая проверка: строка обязана начинаться строго с символов "+7"
                    if not ph.startswith("+7"):
                        print(" Ошибка: Номер телефона должен обязательно начинаться с +7! Попробуйте снова.")
                        continue
                    
                    # Очищаем всё, кроме цифр, для проверки длины
                    digits = "".join([char for char in ph if char.isdigit()])
                    
                    # Для номеров РФ длина цифровой части должна быть ровно 11 цифр (включая семерку)
                    if len(digits) != 11:
                        print(" Ошибка: Неверное количество цифр в номере! Должно быть ровно 11 цифр. Попробуйте снова.")
                        continue
                        
                    # Собираем итоговую чистую строку
                    clean_phone = f"+{digits}"
                    break

                # 7. Интерактивный ввод ДАТЫ РОЖДЕНИЯ (С ОГРАНИЧЕНИЕМ 14+)
                while True:
                    bd = input("Дата рождения (ДД.ММ.ГГГГ): ").strip()
                    try:
                        parts = bd.replace("/", ".").replace(" ", ".").replace(",", ".").split(".")
                        if len(parts) != 3:
                            raise Exception
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        
                        birth_date = datetime(year, month, day)
                        today = datetime.now()
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        
                        if age < 14:
                            print(f" Ошибка: Регистрация разрешена только с 14 лет! (Текущий возраст: {age} лет). Попробуйте снова.")
                            continue
                            
                        if age > 120:
                            print(" Ошибка: Некорректный возраст (больше 120 лет)! Попробуйте снова.")
                            continue
                        
                        birth_day_sql = f"{year}.{month:02d}.{day:02d}"
                        break
                    except ValueError:
                        print(" Ошибка: Такой даты не существует в календаре! Попробуйте снова.")
                        continue
                    except:
                        print(" Ошибка: Неверный формат! Вводите в формате ДД.ММ.ГГГГ (например: 17.12.2007).")
                        continue

                                # ---------------------------------------------------------------------
                # ШАГ ПОДТВЕРЖДЕНИЯ ДАННЫХ ПЕРЕД ЗАПИСЬЮ В БАЗУ ДАННЫХ
                # ---------------------------------------------------------------------
                print("\n ПРОВЕРКА ВВЕДЕННЫХ ДАННЫХ КЛИЕНТА:")
                print(f"  ● Логин: {l}")
                print(f"  ● Пароль: {p}")
                print(f"  ● ФИО: {ln} {fn} {mn if mn else '(нет)'}")
                print(f"  ● Телефон: {clean_phone}")
                print(f"  ● Дата рождения: {bd}")
                print("-" * 40)
                
                confirm = input(" Все данные введены верно? (да/нет): ").strip().lower()
                
                if confirm == "нет":
                    print(" Регистрация отменена. Данные не были сохранены.")
                    continue
                
             
                import sqlite3
                import os
                
                # Находим корень проекта, где лежит настоящий fittrack.db
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_path = os.path.join(base_dir, "fittrack.db")
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                
                try:
                    # 1. Создаем пользователя в таблице users
                    cur.execute("INSERT INTO users (username, password_hash, role_id, is_active) VALUES (?, ?, 2, 1)", (l, p))
                    user_id = cur.lastrowid
                    
                    # 2. Создаем клиента в таблице clients
                    cur.execute("""
                        INSERT INTO clients (user_id, first_name, last_name, middle_name, phone, birth_day, status) 
                        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
                    """, (user_id, fn, ln, mn if mn else None, clean_phone, birth_day_sql))
                    c_id = cur.lastrowid
                    
                    # Если оба запроса прошли успешно — сохраняем изменения в файл базы данных
                    conn.commit()
                    print(f"\n Клиент успешно создан! Присвоен ID клиента: {c_id}")
                    
                except sqlite3.IntegrityError as ie:
                    # Если упал уникальный телефон или любая другая ошибка БД — отменяем ВСЁ (делаем откат)
                    conn.rollback()
                    print(f" Ошибка базы данных: Данные не сохранены! Проверьте уникальность телефона. ({ie})")
                finally:
                    conn.close()

                
            elif choice == "2":
                print("\n--- Оформление абонемента клиенту ---")
                try:
                    c_id = int(input("Введите ID клиента: "))
                except ValueError:
                    print(" Ошибка: ID клиента должен быть целым числом!")
                    continue
                
                # Показываем доступные тарифы из базы данных
                import repositories.membership_repository as mem_repo
                conn = mem_repo.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT id, name, total_visits, duration_days FROM membership_types WHERE is_active = 1")
                tariffs = cur.fetchall()
                
                print("\n ДОСТУПНЫЕ ТАРИФЫ КЛУБА:")
                for t in tariffs:
                    print(f"  [{t[0]}] Тариф: '{t[1]}' | Занятий: {t[2]} | Срок: {t[3]} дней")
                print("-" * 40)
                
                try:
                    t_id = int(input("Выберите ID нужного тарифа из списка выше: "))
                except ValueError:
                    print(" Ошибка: Вы должны ввести числовой ID тарифа!")
                    conn.close()
                    continue

                
                cur.execute("SELECT MAX(id) FROM client_memberships")
                max_id_row = cur.fetchone()
                # Если база пустая, max_id будет 0, иначе берем максимальное число
                max_id = max_id_row[0] if max_id_row[0] is not None else 0
                conn.close()
                
                # Карта всегда будет уникальной (базовое число 10001 + максимальный ID в базе)
                next_card_number = f"CARD-{10001 + max_id + 1}"
                
                try:
                    svc.assign_membership_to_client(c_id, t_id, next_card_number, override=False)
                    print(f" Абонемент успешно оформлен! Клиенту присвоена карта: {next_card_number}")
                except ValueError as ve:
                    print(f"\n Предупреждение системы безопасности ➔ {ve}")
                    confirm = input(" Вы уверены, что хотите аннулировать текущий тариф и оформить новый поверх? (да/нет): ").strip().lower()
                    if confirm == "да":
                        svc.assign_membership_to_client(c_id, t_id, next_card_number, override=True)
                        print(f" Предыдущий абонемент аннулирован. Новый успешно оформлен! Карта: {next_card_number}")
                    else:
                        print(" Операция отменена. Текущий тариф клиента остался нетронутым.")


            elif choice == "3":
                c_id = int(input("Введите ID клиента для прохода: "))
                svc.check_in_client(c_id)
                print(" Доступ разрешен! Визит зафиксирован, занятие списано.")
                
            elif choice == "4":
                clients = svc.get_all_clients_list()
                print("\n РЕЕСТР КЛИЕНТОВ И ОНЛАЙН-СТАТУС АБОНЕМЕНТОВ:")
                if not clients:
                    print("База клиентов пуста.")
                for c in clients:
                    # Собираем ФИО и телефон через запятую в одну строчку
                    fio = f"{c.last_name} {c.first_name} {c.middle_name if c.middle_name else ''}".strip()
                    print(f"● ID: {c.id}, {fio}, Тел: {c.phone} ➔ {c.membership_info}")
                print("-" * 50)


                    
            elif choice == "5":
                visits = svc.get_global_visit_log()
                print("\nЖУРНАЛ ВСЕХ ПОСЕЩЕНИЙ КЛУБА:")
                if not visits:
                    print("Журнал визитов пуст.")
                for v in visits:
                    print(f"[{v.check_in_at}] ID Клиента: {v.client_id} (Зафиксирован проход)")

            elif choice == "6":
                print("\n--- Аннулирование/Удаление абонемента ---")
                c_id = int(input("Введите ID клиента, чей абонемент нужно удалить: "))
                confirm = input(" Вы точно хотите полностью удалить активный абонемент клиента? (да/нет): ").strip().lower()
                if confirm == "да":
                    svc.cancel_client_membership(c_id)
                    print(" Абонемент клиента успешно удален из базы данных!")
                else:
                    print("Операция отменена.")
                    
            elif choice == "7":
                print("\n--- Полное удаление клиента из системы ---")
                c_id = int(input("Введите ID клиента для удаления: "))
                confirm = input(" ВНИМАНИЕ: Это полностью удалит клиента, его абонементы и аккаунт! Вы уверены? (да/нет): ").strip().lower()
                if confirm == "да":
                    svc.remove_client_from_system(c_id)
                    print(" Клиент и все связанные с ним учетные записи успешно стёрты.")
                else:
                    print("Операция отменена.")
        
            elif choice == "0":
                break
        except Exception as e:
            print(f" Ошибка: {e}")

def client_menu(user_id: int):
    while True:
        try:
            client, membership = svc.get_client_profile_by_user(user_id)
        except Exception as e:
            print(f" Ошибка профиля: {e}")
            return
        print(f"\n--- ЛИЧНЫЙ КАБИНЕТ КЛИЕНТА: {client.first_name} ---")
        print("1. Мой профиль и статус абонемента")
        print("2. Посмотреть мою историю посещений")
        print("0. Выйти из аккаунта")
        choice = input("Выберите действие: ")
        if choice == "1":
            print("\n ПЕРСОНАЛЬНЫЕ ДАННЫХ ПРОФИЛЯ:")
            print(f"  ● ФИО: {client.last_name} {client.first_name} {client.middle_name if client.middle_name else ''}")
            print(f"  ● Телефон: {client.phone}")
            print(f"  ● Email/Почта: {client.email if client.email else 'Не указан'}")
            print(f"  ● Дата рождения: {client.birth_day}")
            print("-" * 40)
            print(" ДАННЫЕ ДЛЯ ВХОДА В СИСТЕМУ:")
            print(f"  ● Логин: {client.status}") # Из репозитория подтянули username
            print(f"  ● Пароль: {'*' * len(str(client.created_at)) if client.created_at else '******'} (Зашифрован)")
            print("-" * 40)
            print(" СТАТУС ТЕКУЩЕГО АБОНЕМЕНТА:")
            if membership:
                # Находим человеческое имя тарифа онлайн из базы
                import repositories.membership_repository as mem_repo
                conn = mem_repo.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT name FROM membership_types WHERE id = ?", (membership.membership_type_id,))
                t_name = cur.fetchone()
                conn.close()
                
                print(f"  ● Тип тарифа: '{t_name[0] if t_name else 'Базовый'}'")
                print(f"  ● Номер карты: {membership.card_number}")
                print(f"  ● Осталось визитов: {membership.remaining_visits if membership.remaining_visits is not None else 'Безлимит'}")
                print(f"  ● Срок действия до: {membership.end_date}")
            else:
                print("  ● Статус: Активный абонемент отсутствует. Обратитесь на ресепшен клуба.")
            print("-" * 40)
        elif choice == "2":
            history = svc.get_client_personal_history(client.id)
            print("\nИСТОРИЯ ВАШИХ ТРЕНИРОВОК:")
            if not history:
                print("Вы еще не посещали тренировки.")
            for v in history:
                print(f"  Визит зафиксирован: {v.check_in_at}")
        elif choice == "0":
            print("Выход из личного кабинета клиента...")
            break

if __name__ == "__main__":
    main()
