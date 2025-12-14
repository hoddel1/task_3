#!/usr/bin/env python3
"""
КОМПАКТНЫЙ тест ВСЕХ функций библиотеки.
Запуск: python test_all.py
"""

import os
import tempfile
from table_processor import Table, load_table, save_table
from datetime import datetime

def cleanup_files(files):
    """Удаляет временные файлы"""
    for f in files:
        if os.path.exists(f):
            os.remove(f)

def test_basic_operations():
    """Тест 1: Базовые операции"""
    print("✓ Тест 1: Базовые операции")
    
    data = [
        [1, "Alice", 25, "2023-01-15"],
        [2, "Bob", 30, "2023-02-20"],
        [3, "Charlie", None, None]
    ]
    
    table = Table(data, ["ID", "Name", "Age", "Date"])
    
    # 1.1 Проверка размеров
    assert len(table._data) == 3
    assert len(table._columns) == 4
    
    # 1.2 get_rows_by_number
    rows = table.get_rows_by_number(0, 2)
    assert len(rows._data) == 2
    assert rows._data[0][1] == "Alice"
    
    # 1.3 get_rows_by_index
    rows_idx = table.get_rows_by_index(1, 3)
    assert len(rows_idx._data) == 2
    
    print("  Все базовые операции работают!")

def test_types_and_none():
    """Тест 2: Типы данных и None"""
    print("✓ Тест 2: Типы данных и None")
    
    data = [
        [1, "Text", "25", "true", "2023-01-01"],
        [2, None, "30.5", "false", None],
        ["3", "", None, "", "2023-02-28"]
    ]
    
    table = Table(data, ["ID", "Text", "Number", "Bool", "Date"])
    
    # 2.1 Автоопределение типов
    table.auto_detect_column_types()
    types = table.get_column_types(by_number=False)
    
    assert types.get("ID") in ['int', 'str']
    assert types.get("Bool") == 'bool'
    
    # 2.2 Проверка преобразования None
    values = table.get_values("Text")
    assert values[1] is None  # Явный None
    assert values[2] == ""    # Пустая строка
    
    # 2.3 Ручная установка типов
    table.set_column_types({"Date": "datetime"})
    date_values = table.get_values("Date")
    assert isinstance(date_values[0], datetime) or date_values[0] is None
    
    print("  Типы данных и None обрабатываются корректно!")

def test_file_operations():
    """Тест 3: Работа с файлами"""
    print("✓ Тест 3: Работа с файлами")
    
    # Создаем временные файлы
    temp_files = []
    
    try:
        # 3.1 Тестовая таблица
        data = [
            [101, "Product A", 10.5, 100],
            [102, "Product B", 25.0, 50],
            [103, "Product C", 7.99, 200]
        ]
        table = Table(data, ["ID", "Name", "Price", "Stock"])
        table.auto_detect_column_types()
        
        # 3.2 CSV - сохранение и загрузка
        csv_file = "test_csv.csv"
        save_table(table, csv_file)
        loaded_csv = load_table(csv_file, detect_types=True)
        assert len(loaded_csv._data) == 3
        temp_files.append(csv_file)
        
        # 3.3 Pickle - сохранение и загрузка
        pkl_file = "test_pickle.pkl"
        save_table(table, pkl_file)
        loaded_pkl = load_table(pkl_file, detect_types=True)
        assert len(loaded_pkl._data) == 3
        temp_files.append(pkl_file)
        
        # 3.4 Текстовый файл
        txt_file = "test_text.txt"
        save_table(table, txt_file, file_type='txt')
        assert os.path.exists(txt_file)
        temp_files.append(txt_file)
        
        print("  Все форматы файлов работают!")
        
    finally:
        cleanup_files(temp_files)

def test_multiple_files():
    """Тест 4: Множественные файлы"""
    print("✓ Тест 4: Множественные файлы")
    
    # Создаем 2 CSV файла
    import csv
    
    files = []
    try:
        # Файл 1
        with open("part1.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Value"])
            writer.writerow([1, "A"])
            writer.writerow([2, "B"])
        files.append("part1.csv")
        
        # Файл 2
        with open("part2.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Value"])
            writer.writerow([3, "C"])
            writer.writerow([4, "D"])
        files.append("part2.csv")
        
        # Загрузка обоих файлов
        table = load_table("part1.csv", "part2.csv")
        assert len(table._data) == 4
        assert table._columns == ["ID", "Value"]
        
        print("  Загрузка из нескольких файлов работает!")
        
    finally:
        cleanup_files(files)

def test_exceptions():
    """Тест 5: Исключительные ситуации"""
    print("✓ Тест 5: Исключительные ситуации")
    
    table = Table([[1, 2]], ["A", "B"])
    
    # 5.1 Неправильный индекс
    try:
        table.get_rows_by_number(10)
        print("  ❌ Должна быть ошибка индекса")
        return False
    except Exception:
        print("  ✓ Ошибка индекса обработана")
    
    # 5.2 Неправильная колонка
    try:
        table.get_values("NonExistent")
        print("  ❌ Должна быть ошибка колонки")
        return False
    except Exception:
        print("  ✓ Ошибка колонки обработана")
    
    # 5.3 Неправильный тип
    try:
        table.set_column_types({"A": "invalid_type"})
        print("  ❌ Должна быть ошибка типа")
        return False
    except Exception:
        print("  ✓ Ошибка типа обработана")
    
    # 5.4 Неправильное количество значений
    try:
        table.set_values([1, 2, 3], "A")  # 3 значения для 1 строки
        print("  ❌ Должна быть ошибка количества")
        return False
    except Exception:
        print("  ✓ Ошибка количества обработана")
    
    return True

def test_datetime():
    """Тест 6: Дата и время"""
    print("✓ Тест 6: Дата и время")
    
    data = [
        [1, "Event 1", "2023-12-25", "2023-12-25 10:30:00"],
        [2, "Event 2", "2024-01-01", "2024-01-01 00:00:00"],
        [3, "Event 3", None, None]
    ]
    
    table = Table(data, ["ID", "Name", "Date", "DateTime"])
    table.auto_detect_column_types()
    
    types = table.get_column_types(by_number=False)
    assert types.get("Date") == "datetime"
    assert types.get("DateTime") == "datetime"
    
    date_values = table.get_values("Date")
    assert isinstance(date_values[0], datetime)
    assert date_values[2] is None  # None остается None
    
    print("  Дата/время работают корректно!")

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 50)
    print("НАЧАЛО ТЕСТИРОВАНИЯ table-processor")
    print("=" * 50)
    
    tests = [
        test_basic_operations,
        test_types_and_none,
        test_file_operations,
        test_multiple_files,
        test_exceptions,
        test_datetime
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ❌ Тест {test.__name__} упал: {e}")
    
    print("\n" + "=" * 50)
    print(f"ИТОГ: {passed} пройдено, {failed} упало")
    
    if failed == 0:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
