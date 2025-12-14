import pickle
from .base_table import Table

def load_pickle(*files, detect_types=False):
    """Загрузка из Pickle файла(ов)"""
    tables = []
    for file_path in files:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            if isinstance(data, Table):
                tables.append(data)
            elif isinstance(data, dict):
                tables.append(Table(data.get('data', []), 
                                  data.get('columns', []), 
                                  data.get('column_types', {})))
    
    if not tables:
        raise ValueError("No valid data loaded")
    
    # Объединяем таблицы
    main_table = tables[0]
    for table in tables[1:]:
        if (main_table._columns != table._columns or 
            len(main_table._columns) != len(table._columns)):
            raise ValueError("Table structure mismatch")
        main_table._data.extend(table._data)
    
    if detect_types:
        main_table.auto_detect_column_types()
    return main_table

def save_pickle(table, file_path):
    """Сохранение в Pickle"""
    data = {
        'data': table._data,
        'columns': table._columns,
        'column_types': table._column_types
    }
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
