import csv
from .base_table import Table

def load_csv(*files, detect_types=False, delimiter=',', encoding='utf-8'):
    """Загрузка из CSV файла(ов)"""
    all_data = []
    columns = None
    
    for file_path in files:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            try:
                file_columns = next(reader)
            except StopIteration:
                continue
            
            if columns is None:
                columns = file_columns
            elif file_columns != columns:
                raise ValueError(f"Column mismatch in {file_path}")
            
            all_data.extend(list(reader))
    
    table = Table(all_data, columns)
    if detect_types:
        table.auto_detect_column_types()
    return table

def save_csv(table, file_path, delimiter=',', encoding='utf-8'):
    """Сохранение в CSV"""
    with open(file_path, 'w', newline='', encoding=encoding) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(table._columns)
        for row in table._data:
            writer.writerow([cell if cell is not None else '' for cell in row])
