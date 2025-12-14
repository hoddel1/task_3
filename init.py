from .base_table import Table
from .csv_handler import load_csv, save_csv
from .pickle_handler import load_pickle, save_pickle
from .text_handler import save_text

def load_table(*files, file_type=None, detect_types=False, **kwargs):
    """Универсальная загрузка"""
    if file_type is None:
        ext = files[0].split('.')[-1].lower()
        file_type = 'csv' if ext == 'csv' else 'pickle' if ext in ('pkl', 'pickle') else None
    
    if file_type == 'csv':
        return load_csv(*files, detect_types=detect_types, **kwargs)
    elif file_type == 'pickle':
        return load_pickle(*files, detect_types=detect_types)
    else:
        raise ValueError(f"Unknown file type: {file_type}")

def save_table(table, file_path, file_type=None, **kwargs):
    """Универсальное сохранение"""
    if file_type is None:
        ext = file_path.split('.')[-1].lower()
        file_type = 'csv' if ext == 'csv' else 'pickle' if ext in ('pkl', 'pickle') else 'txt'
    
    if file_type == 'csv':
        save_csv(table, file_path, **kwargs)
    elif file_type == 'pickle':
        save_pickle(table, file_path)
    elif file_type == 'txt':
        save_text(table, file_path, **kwargs)
    else:
        raise ValueError(f"Unknown file type: {file_type}")

__all__ = ['Table', 'load_table', 'save_table']
