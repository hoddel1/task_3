def save_text(table, file_path, max_rows=50):
    """Сохранение в читаемый текстовый файл"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"Table: {len(table._data)} rows, {len(table._columns)} columns\n")
        f.write("=" * 60 + "\n\n")
        
        if not table._data:
            f.write("Empty table\n")
            return
        
        # Копируем логику print_table
        widths = []
        for i, col in enumerate(table._columns):
            width = len(str(col))
            for j in range(min(max_rows, len(table._data))):
                if i < len(table._data[j]):
                    cell = str(table._data[j][i])
                    width = max(width, len(cell))
            widths.append(min(width, 30))
        
        # Заголовок
        header = " | ".join(f"{col:<{widths[i]}}" for i, col in enumerate(table._columns))
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")
        
        # Данные
        for j in range(min(max_rows, len(table._data))):
            row_parts = []
            for i in range(len(table._columns)):
                if i < len(table._data[j]):
                    cell = str(table._data[j][i])[:30]
                    row_parts.append(f"{cell:<{widths[i]}}")
                else:
                    row_parts.append(" " * widths[i])
            f.write(" | ".join(row_parts) + "\n")
        
        if len(table._data) > max_rows:
            f.write(f"\n... and {len(table._data) - max_rows} more rows\n")
