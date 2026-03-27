from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import json
from datetime import datetime
import io
import base64

schema_bp = Blueprint('schema', __name__)

@schema_bp.route('/api/schema/generate', methods=['POST'])
@login_required
def generate_database_schema():
    """Генерация схемы базы данных"""
    try:
        data = request.get_json()
        
        # Параметры схемы
        schema_name = data.get('schema_name', 'MyDatabase')
        database_type = data.get('database_type', 'mysql')  # mysql, postgresql, sqlite, mongodb
        tables = data.get('tables', [])
        format_type = data.get('format', 'sql')  # sql, json, yaml, mermaid
        
        if not tables:
            return jsonify({'error': 'Необходимо указать хотя бы одну таблицу'}), 400
        
        # Генерация схемы
        if format_type == 'sql':
            schema_content = generate_sql_schema(schema_name, database_type, tables)
        elif format_type == 'json':
            schema_content = generate_json_schema(schema_name, database_type, tables)
        elif format_type == 'yaml':
            schema_content = generate_yaml_schema(schema_name, database_type, tables)
        elif format_type == 'mermaid':
            schema_content = generate_mermaid_schema(schema_name, tables)
        else:
            return jsonify({'error': 'Неподдерживаемый формат схемы'}), 400
        
        return jsonify({
            'schema_content': schema_content,
            'schema_name': schema_name,
            'database_type': database_type,
            'format': format_type,
            'tables_count': len(tables),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации схемы БД'}), 500

@schema_bp.route('/api/schema/templates', methods=['GET'])
def get_schema_templates():
    """Получение шаблонов схем БД"""
    try:
        templates = {
            'database_types': {
                'mysql': {
                    'name': 'MySQL',
                    'description': 'Реляционная БД MySQL',
                    'features': ['ACID', 'Транзакции', 'Индексы', 'Внешние ключи']
                },
                'postgresql': {
                    'name': 'PostgreSQL',
                    'description': 'Продвинутая реляционная БД',
                    'features': ['ACID', 'JSON', 'Массивы', 'Полнотекстовый поиск']
                },
                'sqlite': {
                    'name': 'SQLite',
                    'description': 'Встроенная БД',
                    'features': ['Легковесная', 'Файловая', 'ACID', 'Без сервера']
                },
                'mongodb': {
                    'name': 'MongoDB',
                    'description': 'NoSQL документная БД',
                    'features': ['Документы', 'Гибкая схема', 'Масштабируемость', 'JSON']
                }
            },
            'table_templates': [
                {
                    'name': 'users',
                    'description': 'Таблица пользователей',
                    'columns': [
                        {'name': 'id', 'type': 'INT', 'primary_key': True, 'auto_increment': True},
                        {'name': 'username', 'type': 'VARCHAR(50)', 'unique': True, 'not_null': True},
                        {'name': 'email', 'type': 'VARCHAR(100)', 'unique': True, 'not_null': True},
                        {'name': 'password_hash', 'type': 'VARCHAR(255)', 'not_null': True},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                        {'name': 'updated_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'}
                    ]
                },
                {
                    'name': 'posts',
                    'description': 'Таблица постов',
                    'columns': [
                        {'name': 'id', 'type': 'INT', 'primary_key': True, 'auto_increment': True},
                        {'name': 'title', 'type': 'VARCHAR(200)', 'not_null': True},
                        {'name': 'content', 'type': 'TEXT'},
                        {'name': 'author_id', 'type': 'INT', 'not_null': True},
                        {'name': 'status', 'type': 'ENUM("draft", "published", "archived")', 'default': 'draft'},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
                        {'name': 'updated_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'}
                    ],
                    'foreign_keys': [
                        {'column': 'author_id', 'references_table': 'users', 'references_column': 'id'}
                    ]
                },
                {
                    'name': 'categories',
                    'description': 'Таблица категорий',
                    'columns': [
                        {'name': 'id', 'type': 'INT', 'primary_key': True, 'auto_increment': True},
                        {'name': 'name', 'type': 'VARCHAR(100)', 'not_null': True, 'unique': True},
                        {'name': 'description', 'type': 'TEXT'},
                        {'name': 'parent_id', 'type': 'INT', 'null': True},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}
                    ],
                    'foreign_keys': [
                        {'column': 'parent_id', 'references_table': 'categories', 'references_column': 'id'}
                    ]
                }
            ],
            'data_types': {
                'mysql': {
                    'integer': ['TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'BIGINT'],
                    'string': ['CHAR', 'VARCHAR', 'TEXT', 'TINYTEXT', 'MEDIUMTEXT', 'LONGTEXT'],
                    'decimal': ['DECIMAL', 'FLOAT', 'DOUBLE'],
                    'date': ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR'],
                    'binary': ['BINARY', 'VARBINARY', 'BLOB', 'TINYBLOB', 'MEDIUMBLOB', 'LONGBLOB'],
                    'other': ['ENUM', 'SET', 'JSON', 'GEOMETRY']
                },
                'postgresql': {
                    'integer': ['SMALLINT', 'INTEGER', 'BIGINT', 'SERIAL', 'BIGSERIAL'],
                    'string': ['CHAR', 'VARCHAR', 'TEXT'],
                    'decimal': ['DECIMAL', 'NUMERIC', 'REAL', 'DOUBLE PRECISION'],
                    'date': ['DATE', 'TIME', 'TIMESTAMP', 'TIMESTAMPTZ', 'INTERVAL'],
                    'binary': ['BYTEA'],
                    'other': ['BOOLEAN', 'ARRAY', 'JSON', 'JSONB', 'UUID', 'INET', 'CIDR']
                },
                'sqlite': {
                    'integer': ['INTEGER'],
                    'string': ['TEXT'],
                    'decimal': ['REAL'],
                    'date': ['DATETIME'],
                    'binary': ['BLOB'],
                    'other': ['NUMERIC']
                }
            }
        }
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении шаблонов'}), 500

@schema_bp.route('/api/schema/validate', methods=['POST'])
@login_required
def validate_schema():
    """Валидация схемы БД"""
    try:
        data = request.get_json()
        tables = data.get('tables', [])
        database_type = data.get('database_type', 'mysql')
        
        if not tables:
            return jsonify({'error': 'Необходимо указать таблицы'}), 400
        
        # Валидация схемы
        validation_result = validate_database_schema(tables, database_type)
        
        return jsonify({
            'valid': validation_result['valid'],
            'errors': validation_result.get('errors', []),
            'warnings': validation_result.get('warnings', []),
            'database_type': database_type
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации схемы'}), 500

@schema_bp.route('/api/schema/er-diagram', methods=['POST'])
@login_required
def generate_er_diagram():
    """Генерация ER диаграммы"""
    try:
        data = request.get_json()
        tables = data.get('tables', [])
        diagram_type = data.get('type', 'mermaid')  # mermaid, plantuml
        
        if not tables:
            return jsonify({'error': 'Необходимо указать таблицы'}), 400
        
        # Генерация ER диаграммы
        if diagram_type == 'mermaid':
            diagram_content = generate_mermaid_er_diagram(tables)
        elif diagram_type == 'plantuml':
            diagram_content = generate_plantuml_er_diagram(tables)
        else:
            return jsonify({'error': 'Неподдерживаемый тип диаграммы'}), 400
        
        return jsonify({
            'diagram_content': diagram_content,
            'diagram_type': diagram_type,
            'tables_count': len(tables),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации ER диаграммы'}), 500

def generate_sql_schema(schema_name, database_type, tables):
    """Генерация SQL схемы"""
    sql_lines = []
    
    # Заголовок
    if database_type == 'mysql':
        sql_lines.append(f"-- Схема базы данных: {schema_name}")
        sql_lines.append(f"CREATE DATABASE IF NOT EXISTS `{schema_name}`;")
        sql_lines.append(f"USE `{schema_name}`;")
        sql_lines.append("")
    elif database_type == 'postgresql':
        sql_lines.append(f"-- Схема базы данных: {schema_name}")
        sql_lines.append(f"CREATE DATABASE {schema_name};")
        sql_lines.append(f"\\c {schema_name};")
        sql_lines.append("")
    
    # Генерация таблиц
    for table in tables:
        table_name = table.get('name', '')
        description = table.get('description', '')
        columns = table.get('columns', [])
        foreign_keys = table.get('foreign_keys', [])
        
        if not table_name or not columns:
            continue
        
        # Комментарий к таблице
        sql_lines.append(f"-- {description}")
        
        # Создание таблицы
        sql_lines.append(f"CREATE TABLE {table_name} (")
        
        # Колонки
        column_definitions = []
        for column in columns:
            column_def = generate_column_definition(column, database_type)
            column_definitions.append(f"    {column_def}")
        
        sql_lines.extend(column_definitions)
        
        # Внешние ключи
        if foreign_keys:
            for fk in foreign_keys:
                fk_def = generate_foreign_key_definition(fk, database_type)
                sql_lines.append(f"    {fk_def}")
        
        sql_lines.append(");")
        sql_lines.append("")
        
        # Индексы
        indexes = generate_indexes(table, database_type)
        if indexes:
            sql_lines.extend(indexes)
            sql_lines.append("")
    
    return "\n".join(sql_lines)

def generate_column_definition(column, database_type):
    """Генерация определения колонки"""
    name = column.get('name', '')
    data_type = column.get('type', 'VARCHAR(255)')
    not_null = column.get('not_null', False)
    unique = column.get('unique', False)
    primary_key = column.get('primary_key', False)
    auto_increment = column.get('auto_increment', False)
    default_value = column.get('default', None)
    
    definition_parts = [name, data_type]
    
    if primary_key:
        if database_type == 'mysql':
            definition_parts.append("PRIMARY KEY")
        elif database_type == 'postgresql':
            definition_parts.append("PRIMARY KEY")
    
    if auto_increment:
        if database_type == 'mysql':
            definition_parts.append("AUTO_INCREMENT")
        elif database_type == 'postgresql':
            definition_parts.append("SERIAL")
    
    if not_null:
        definition_parts.append("NOT NULL")
    
    if unique and not primary_key:
        definition_parts.append("UNIQUE")
    
    if default_value is not None:
        if isinstance(default_value, str) and default_value.upper() in ['CURRENT_TIMESTAMP', 'NOW()']:
            definition_parts.append(f"DEFAULT {default_value}")
        else:
            definition_parts.append(f"DEFAULT '{default_value}'")
    
    return " ".join(definition_parts)

def generate_foreign_key_definition(fk, database_type):
    """Генерация определения внешнего ключа"""
    column = fk.get('column', '')
    references_table = fk.get('references_table', '')
    references_column = fk.get('references_column', 'id')
    on_delete = fk.get('on_delete', 'RESTRICT')
    on_update = fk.get('on_update', 'RESTRICT')
    
    fk_name = f"fk_{column}_{references_table}"
    
    return f"CONSTRAINT {fk_name} FOREIGN KEY ({column}) REFERENCES {references_table}({references_column}) ON DELETE {on_delete} ON UPDATE {on_update}"

def generate_indexes(table, database_type):
    """Генерация индексов"""
    indexes = []
    table_name = table.get('name', '')
    columns = table.get('columns', [])
    
    # Индексы для уникальных колонок
    for column in columns:
        if column.get('unique', False) and not column.get('primary_key', False):
            index_name = f"idx_{table_name}_{column['name']}"
            indexes.append(f"CREATE UNIQUE INDEX {index_name} ON {table_name} ({column['name']});")
    
    return indexes

def generate_json_schema(schema_name, database_type, tables):
    """Генерация JSON схемы"""
    schema = {
        "schema_name": schema_name,
        "database_type": database_type,
        "tables": []
    }
    
    for table in tables:
        table_schema = {
            "name": table.get('name', ''),
            "description": table.get('description', ''),
            "columns": table.get('columns', []),
            "foreign_keys": table.get('foreign_keys', []),
            "indexes": table.get('indexes', [])
        }
        schema["tables"].append(table_schema)
    
    return json.dumps(schema, indent=2, ensure_ascii=False)

def generate_yaml_schema(schema_name, database_type, tables):
    """Генерация YAML схемы"""
    import yaml
    
    schema = {
        "schema_name": schema_name,
        "database_type": database_type,
        "tables": tables
    }
    
    return yaml.dump(schema, default_flow_style=False, allow_unicode=True)

def generate_mermaid_schema(schema_name, tables):
    """Генерация Mermaid схемы"""
    mermaid_lines = ["erDiagram"]
    
    for table in tables:
        table_name = table.get('name', '')
        columns = table.get('columns', [])
        
        if not table_name or not columns:
            continue
        
        # Определение таблицы
        mermaid_lines.append(f"    {table_name} {{")
        
        for column in columns:
            name = column.get('name', '')
            data_type = column.get('type', 'VARCHAR')
            primary_key = column.get('primary_key', False)
            not_null = column.get('not_null', False)
            unique = column.get('unique', False)
            
            # Форматирование типа колонки
            if primary_key:
                mermaid_lines.append(f"        {data_type} {name} PK")
            elif unique:
                mermaid_lines.append(f"        {data_type} {name} UK")
            elif not_null:
                mermaid_lines.append(f"        {data_type} {name}")
            else:
                mermaid_lines.append(f"        {data_type} {name} \"nullable\"")
        
        mermaid_lines.append("    }")
    
    # Связи между таблицами
    for table in tables:
        table_name = table.get('name', '')
        foreign_keys = table.get('foreign_keys', [])
        
        for fk in foreign_keys:
            column = fk.get('column', '')
            references_table = fk.get('references_table', '')
            references_column = fk.get('references_column', 'id')
            
            mermaid_lines.append(f"    {table_name} ||--o{{ {references_table} : \"{column} -> {references_column}\"")
    
    return "\n".join(mermaid_lines)

def generate_mermaid_er_diagram(tables):
    """Генерация Mermaid ER диаграммы"""
    return generate_mermaid_schema("ER_Diagram", tables)

def generate_plantuml_er_diagram(tables):
    """Генерация PlantUML ER диаграммы"""
    plantuml_lines = ["@startuml", "!define TABLE(name,desc) class name as \"desc\" << (T,#FFAAAA) >>"]
    
    for table in tables:
        table_name = table.get('name', '')
        description = table.get('description', '')
        columns = table.get('columns', [])
        
        if not table_name or not columns:
            continue
        
        plantuml_lines.append(f"TABLE({table_name}, \"{description}\")")
        plantuml_lines.append(f"{table_name} {{")
        
        for column in columns:
            name = column.get('name', '')
            data_type = column.get('type', 'VARCHAR')
            primary_key = column.get('primary_key', False)
            
            if primary_key:
                plantuml_lines.append(f"  ** {name} : {data_type}")
            else:
                plantuml_lines.append(f"  {name} : {data_type}")
        
        plantuml_lines.append("}")
    
    # Связи
    for table in tables:
        table_name = table.get('name', '')
        foreign_keys = table.get('foreign_keys', [])
        
        for fk in foreign_keys:
            column = fk.get('column', '')
            references_table = fk.get('references_table', '')
            
            plantuml_lines.append(f"{table_name} ||--o{{ {references_table} : {column}")
    
    plantuml_lines.append("@enduml")
    
    return "\n".join(plantuml_lines)

def validate_database_schema(tables, database_type):
    """Валидация схемы БД"""
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    table_names = set()
    
    for table in tables:
        table_name = table.get('name', '')
        
        # Проверка имени таблицы
        if not table_name:
            validation_result['errors'].append('Имя таблицы не может быть пустым')
            validation_result['valid'] = False
            continue
        
        if table_name in table_names:
            validation_result['errors'].append(f'Дублирующееся имя таблицы: {table_name}')
            validation_result['valid'] = False
        
        table_names.add(table_name)
        
        # Проверка колонок
        columns = table.get('columns', [])
        if not columns:
            validation_result['errors'].append(f'Таблица {table_name} не содержит колонок')
            validation_result['valid'] = False
            continue
        
        column_names = set()
        primary_keys = []
        
        for column in columns:
            column_name = column.get('name', '')
            
            if not column_name:
                validation_result['errors'].append(f'Имя колонки в таблице {table_name} не может быть пустым')
                validation_result['valid'] = False
                continue
            
            if column_name in column_names:
                validation_result['errors'].append(f'Дублирующееся имя колонки {column_name} в таблице {table_name}')
                validation_result['valid'] = False
            
            column_names.add(column_name)
            
            if column.get('primary_key', False):
                primary_keys.append(column_name)
        
        # Проверка первичных ключей
        if len(primary_keys) == 0:
            validation_result['warnings'].append(f'Таблица {table_name} не имеет первичного ключа')
        elif len(primary_keys) > 1:
            validation_result['warnings'].append(f'Таблица {table_name} имеет составной первичный ключ')
        
        # Проверка внешних ключей
        foreign_keys = table.get('foreign_keys', [])
        for fk in foreign_keys:
            fk_column = fk.get('column', '')
            fk_table = fk.get('references_table', '')
            
            if fk_column not in column_names:
                validation_result['errors'].append(f'Внешний ключ ссылается на несуществующую колонку {fk_column} в таблице {table_name}')
                validation_result['valid'] = False
            
            if fk_table not in table_names and fk_table != table_name:
                validation_result['warnings'].append(f'Внешний ключ ссылается на таблицу {fk_table}, которая не определена')
    
    return validation_result

def generate_crud_operations(table_name, columns):
    """Генерация CRUD операций для таблицы"""
    operations = {
        'create': f"INSERT INTO {table_name} (...) VALUES (...);",
        'read': f"SELECT * FROM {table_name} WHERE id = ?;",
        'update': f"UPDATE {table_name} SET ... WHERE id = ?;",
        'delete': f"DELETE FROM {table_name} WHERE id = ?;"
    }
    
    return operations

def generate_sample_data(table_name, columns):
    """Генерация примеров данных"""
    sample_data = []
    
    # Генерация 3 примеров записей
    for i in range(3):
        record = {}
        for column in columns:
            name = column.get('name', '')
            data_type = column.get('type', 'VARCHAR')
            
            if column.get('primary_key', False) and column.get('auto_increment', False):
                record[name] = i + 1
            elif 'VARCHAR' in data_type or 'TEXT' in data_type:
                record[name] = f"Sample {name} {i + 1}"
            elif 'INT' in data_type:
                record[name] = (i + 1) * 10
            elif 'DATE' in data_type or 'TIMESTAMP' in data_type:
                record[name] = "2024-01-01"
            else:
                record[name] = f"value_{i + 1}"
        
        sample_data.append(record)
    
    return sample_data
