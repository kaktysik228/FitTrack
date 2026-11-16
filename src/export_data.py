import sqlite3
import os
import json
import csv
import xml.etree.ElementTree as ET
import yaml

def dict_to_xml(parent, data):
    """Универсальная функция для перевода любого словаря в XML-теги."""
    if isinstance(data, dict):
        for key, value in data.items():
            child = ET.SubElement(parent, str(key))
            dict_to_xml(child, value)
    elif isinstance(data, list):
        for item in data:
            item_el = ET.SubElement(parent, "item")
            dict_to_xml(item_el, item)
    else:
        parent.text = "" if data is None else str(data)

def flatten_dict(d, parent_key=""):
    """Универсальная функция для разворачивания вложенных данных в плоскую строку для CSV."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

def export_all_formats():
    # 1. Находим базу данных fittrack.db и создаем папку 'out', если её нет
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "fittrack.db")
    out_dir = os.path.join(base_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    
    # 2. Подключаемся к БД с автоматическим чтением названий колонок
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Извлекаем главную таблицу клиентов
    cur.execute("SELECT id, first_name, last_name, phone, birth_day FROM clients")
    main_rows = cur.fetchall()
    
    records = []
    for row in main_rows:
        item = dict(row)
        
        # Извлекаем связанные данные из таблицы абонементов и тарифов
        cur.execute("""
            SELECT cm.card_number, cm.remaining_visits, cm.end_date, mt.name AS tariff_name
            FROM client_memberships cm
            LEFT JOIN membership_types mt ON cm.membership_type_id = mt.id
            WHERE cm.client_id = ? AND cm.status = 'ACTIVE'
        """, (item["id"],))
        related_row = cur.fetchone()
        
        # Вкладываем абонемент внутрь объекта клиента
        item["membership"] = dict(related_row) if related_row else None
        records.append(item)
        
    conn.close()

    # =========================================================================
    # 1. Сохранение в JSON
    # =========================================================================
    with open(os.path.join(out_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    # =========================================================================
    # 2. Сохранение в CSV
    # =========================================================================
    flat_records = [flatten_dict(r) for r in records]
    if flat_records:
        headers = []
        for r in flat_records:
            for k in r.keys():
                if k not in headers:
                    headers.append(k)
                    
        with open(os.path.join(out_dir, "data.csv"), "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
            writer.writeheader()
            writer.writerows(flat_records)

    # =========================================================================
    # 3. Сохранение в XML
    # =========================================================================
    root = ET.Element("clients_export")
    for r in records:
        record_el = ET.SubElement(root, "client")
        dict_to_xml(record_el, r)
        
    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(os.path.join(out_dir, "data.xml"), encoding="utf-8", xml_declaration=True)

    # =========================================================================
    # 4. Сохранение в YAML
    # =========================================================================
    with open(os.path.join(out_dir, "data.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(records, f, allow_unicode=True, sort_keys=False)

    print(f" Готово! Все 4 файла успешно созданы в папке: {out_dir}")

if __name__ == "__main__":
    export_all_formats()
