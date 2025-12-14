#!/usr/bin/env python3
"""
БЫСТРАЯ ДЕМОНСТРАЦИЯ всех возможностей.
Запуск: python demo.py
"""

from table_processor import Table, load_table, save_table
import os

def demo():
    print("🚀 ДЕМОНСТРАЦИЯ TABLE-PROCESSOR")
    print("=" * 50)
    
    # 1. Создание таблицы
    print("\n1. 📊 Создание таблицы с разными типами данных:")
    data = [
        [1, "Яблоки", 10.5, 100, True, "2023-10-01"],
        [2, "Бананы", 7.99, 50, False, "2023-10-02"],
        [3, "Апельсины", 15.0, None, True, None],
        [4, None, 12.5, 75, None, "2023-10-04"]
    ]
    
    columns = ["ID", "Товар", "Цена", "Количество", "В_наличии", "Дата_поступления"]
    table = Table(data, columns)
    table.print_table()
    
    # 2. Автоопределение типов
    print("\n2. 🔍 Автоматическое определение типов:")
    table.auto_detect_column_types()
    print("Определенные типы:")
    for col, typ in table.get_column_types(by_number=False).items():
        print(f"  {col}: {typ}")
    
    # 3. Фильтрация
    print("\n3. ⚙️  Фильтрация строк:")
    print("Первые 2 строки:")
    table.get_rows_by_number(0, 2).print_table()
    
    print("\nСтроки с ID 1 и 3:")
    table.get_rows_by_index(1, 3).print_table()
    
    # 4. Работа со значениями
    print("\n4. 📈 Работа со значениями:")
    print("Цены товаров:", table.get_values("Цена"))
    
    # Изменяем цену первого товара
    subtable = table.get_rows_by_number(0)
    subtable.set_value(12.0, "Цена")
    print("После изменения цены первого товара:", table.get_values("Цена")[0])
    
    # 5. Сохранение и загрузка
    print("\n5. 💾 Сохранение и загрузка:")
    
    # Сохраняем во все форматы
    save_table(table, "demo.csv")
    save_table(table, "demo.pkl")
    save_table(table, "demo.txt", file_type='txt')
    
    print("Сохранено в: demo.csv, demo.pkl, demo.txt")
    
    # Загружаем обратно
    print("\nЗагружаем из CSV:")
    loaded = load_table("demo.csv", detect_types=True)
    loaded.print_table(max_rows=2)
    
    # 6. Очистка
    for f in ["demo.csv", "demo.pkl", "demo.txt"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n" + "=" * 50)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("\n📌 Для полного тестирования запустите: python test_all.py")

if __name__ == "__main__":
    demo()
