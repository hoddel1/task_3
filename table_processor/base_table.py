import csv
import pickle
import copy
from datetime import datetime
from typing import List, Dict, Any, Union

class TableError(Exception):
    pass

class Table:
    def __init__(self, data=None, columns=None, column_types=None, parent=None):
        self._parent = parent
        self._data = [list(row) for row in data] if data else []
        self._columns = list(columns) if columns else []
        self._column_types = dict(column_types) if column_types else {}
        
        if not self._columns and self._data:
            self._columns = [f"col_{i}" for i in range(len(self._data[0]))]
        
        self._normalize_data()
    
    def _normalize_data(self):
        """Выравнивает строки по количеству колонок"""
        for i in range(len(self._data)):
            while len(self._data[i]) < len(self._columns):
                self._data[i].append(None)
            if len(self._data[i]) > len(self._columns):
                self._data[i] = self._data[i][:len(self._columns)]
    
    def _ensure_copy(self):
        """Создает копию, если это представление"""
        if self._parent is not None:
            self._data = [list(row) for row in self._data]
            self._parent = None
    
    def _detect_cell_type(self, value):
        """Определяет тип одной ячейки"""
        if value is None or value == '':
            return 'none'
        
        if isinstance(value, bool):
            return 'bool'
        
        if isinstance(value, str):
            lower_val = value.lower().strip()
            if lower_val in ('true', 'false', 'yes', 'no', '1', '0'):
                return 'bool'
            
            try:
                int_val = int(value)
                if '.' not in value:
                    return 'int'
            except:
                try:
                    float(value)
                    return 'float'
                except:
                    pass
            
            # Проверка на дату
            date_formats = ['%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', 
                          '%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M:%S']
            for fmt in date_formats:
                try:
                    datetime.strptime(value, fmt)
                    return 'datetime'
                except:
                    continue
        
        if isinstance(value, (int, float, datetime)):
            return type(value).__name__
        
        return 'str'
    
    def _cast_cell(self, value, target_type):
        """Приводит ячейку к целевому типу"""
        if target_type == 'none' or value is None or value == '':
            return None
        
        if target_type == 'str':
            return str(value)
        
        if target_type == 'int':
            try:
                return int(float(value))
            except:
                return None
        
        if target_type == 'float':
            try:
                return float(value)
            except:
                return None
        
        if target_type == 'bool':
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lower_val = value.lower().strip()
                if lower_val in ('true', '1', 'yes', 't', 'y'):
                    return True
                elif lower_val in ('false', '0', 'no', 'f', 'n'):
                    return False
            try:
                return bool(int(value))
            except:
                return bool(value)
        
        if target_type == 'datetime':
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                formats = ['%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', 
                          '%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M:%S']
                for fmt in formats:
                    try:
                        return datetime.strptime(value.strip(), fmt)
                    except:
                        continue
            return None
        
        return value
    
    # === ОСНОВНЫЕ МЕТОДЫ ===
    
    def get_rows_by_number(self, start, stop=None, copy_table=False):
        """Получение строк по номеру"""
        if not 0 <= start < len(self._data):
            raise TableError(f"Invalid start index: {start}")
        
        if stop is not None:
            if not 0 <= stop <= len(self._data) or stop <= start:
                raise TableError(f"Invalid stop index: {stop}")
            selected = self._data[start:stop]
        else:
            selected = [self._data[start]]
        
        if copy_table:
            return Table(copy.deepcopy(selected), self._columns, self._column_types)
        else:
            return Table(selected, self._columns, self._column_types, parent=self)
    
    def get_rows_by_index(self, *values, copy_table=False):
        """Получение строк по значениям в первой колонке"""
        if not values:
            raise TableError("No values provided")
        
        selected = []
        for row in self._data:
            if row and row[0] is not None and str(row[0]) in [str(v) for v in values]:
                selected.append(row)
        
        if not selected:
            raise TableError(f"No rows found with values: {values}")
        
        if copy_table:
            return Table(copy.deepcopy(selected), self._columns, self._column_types)
        else:
            return Table(selected, self._columns, self._column_types, parent=self)
    
    def get_column_types(self, by_number=True):
        """Получение типов колонок"""
        result = {}
        for i, col in enumerate(self._columns):
            key = i if by_number else col
            result[key] = self._column_types.get(col, 'str')
        return result
    
    def set_column_types(self, types_dict, by_number=True):
        """Установка типов колонок"""
        self._ensure_copy()
        
        for key, col_type in types_dict.items():
            if by_number:
                if not 0 <= key < len(self._columns):
                    raise TableError(f"Invalid column index: {key}")
                col_name = self._columns[key]
            else:
                if key not in self._columns:
                    raise TableError(f"Column not found: {key}")
                col_name = key
            
            if col_type not in ('int', 'float', 'bool', 'str', 'datetime', 'none'):
                raise TableError(f"Invalid type: {col_type}")
            
            self._column_types[col_name] = col_type
            
            # Применяем тип ко всем ячейкам
            col_idx = self._columns.index(col_name)
            for row in self._data:
                if col_idx < len(row):
                    row[col_idx] = self._cast_cell(row[col_idx], col_type)
    
    def auto_detect_column_types(self, samples=10):
        """Автоматическое определение типов"""
        self._ensure_copy()
        
        for col_idx in range(len(self._columns)):
            col_name = self._columns[col_idx]
            
            # Собираем образцы
            sample_types = []
            for i in range(min(samples, len(self._data))):
                if col_idx < len(self._data[i]):
                    val = self._data[i][col_idx]
                    if val is not None and val != '':
                        sample_types.append(self._detect_cell_type(val))
            
            if not sample_types:
                col_type = 'str'
            else:
                # Считаем частоту типов
                type_counts = {}
                for t in sample_types:
                    if t != 'none':
                        type_counts[t] = type_counts.get(t, 0) + 1
                
                if not type_counts:
                    col_type = 'str'
                else:
                    # Приоритет: datetime > int > float > bool > str
                    priority = {'datetime': 5, 'int': 4, 'float': 3, 'bool': 2, 'str': 1}
                    col_type = max(type_counts.keys(), 
                                  key=lambda t: (type_counts[t], priority.get(t, 0)))
            
            self._column_types[col_name] = col_type
            
            # Применяем тип
            for row in self._data:
                if col_idx < len(row):
                    row[col_idx] = self._cast_cell(row[col_idx], col_type)
    
    def get_values(self, column=0):
        """Получение значений колонки"""
        if isinstance(column, int):
            if not 0 <= column < len(self._columns):
                raise TableError(f"Invalid column index: {column}")
            col_name = self._columns[column]
        elif isinstance(column, str):
            if column not in self._columns:
                raise TableError(f"Column not found: {column}")
            col_name = column
        else:
            raise TableError("Column must be int or str")
        
        col_type = self._column_types.get(col_name, 'str')
        col_idx = self._columns.index(col_name)
        
        values = []
        for row in self._data:
            if col_idx < len(row):
                values.append(self._cast_cell(row[col_idx], col_type))
            else:
                values.append(None)
        
        return values
    
    def get_value(self, column=0):
        """Получение значения из таблицы с одной строкой"""
        if len(self._data) != 1:
            raise TableError("Table must have exactly one row")
        return self.get_values(column)[0]
    
    def set_values(self, values, column=0):
        """Установка значений колонки"""
        self._ensure_copy()
        
        if len(values) != len(self._data):
            raise TableError(f"Values count ({len(values)}) doesn't match row count ({len(self._data)})")
        
        if isinstance(column, int):
            col_name = self._columns[column]
        else:
            col_name = column
        
        col_type = self._column_types.get(col_name, 'str')
        col_idx = self._columns.index(col_name)
        
        for i, value in enumerate(values):
            casted = self._cast_cell(value, col_type)
            while len(self._data[i]) <= col_idx:
                self._data[i].append(None)
            self._data[i][col_idx] = casted
    
    def set_value(self, value, column=0):
        """Установка значения в таблице с одной строкой"""
        if len(self._data) != 1:
            raise TableError("Table must have exactly one row")
        self.set_values([value], column)
    
    def print_table(self, max_rows=20):
        """Вывод таблицы"""
        if not self._data:
            print("Empty table")
            return
        
        # Определяем ширину колонок
        widths = []
        for i, col in enumerate(self._columns):
            width = len(str(col))
            for j in range(min(max_rows, len(self._data))):
                if i < len(self._data[j]):
                    cell = str(self._data[j][i])
                    width = max(width, len(cell))
            widths.append(min(width, 30))
        
        # Заголовок
        header = " | ".join(f"{col:<{widths[i]}}" for i, col in enumerate(self._columns))
        print(header)
        print("-" * len(header))
        
        # Данные
        for j in range(min(max_rows, len(self._data))):
            row_parts = []
            for i in range(len(self._columns)):
                if i < len(self._data[j]):
                    cell = str(self._data[j][i])[:30]
                    row_parts.append(f"{cell:<{widths[i]}}")
                else:
                    row_parts.append(" " * widths[i])
            print(" | ".join(row_parts))
        
        if len(self._data) > max_rows:
            print(f"... and {len(self._data) - max_rows} more rows")
    
    def __repr__(self):
        return f"Table(rows={len(self._data)}, cols={len(self._columns)})"
