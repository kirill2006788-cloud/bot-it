from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import json
import jsonschema
from datetime import datetime

json_validator_bp = Blueprint('json_validator', __name__)

@json_validator_bp.route('/api/json/validate', methods=['POST'])
@login_required
def validate_json():
    """Валидация JSON"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        schema = data.get('schema', None)
        strict_mode = data.get('strict_mode', False)
        
        if not json_text:
            return jsonify({'error': 'JSON текст не указан'}), 400
        
        # Валидация JSON
        validation_result = validate_json_text(json_text, schema, strict_mode)
        
        return jsonify({
            'json': json_text,
            'is_valid': validation_result['is_valid'],
            'errors': validation_result.get('errors', []),
            'warnings': validation_result.get('warnings', []),
            'parsed_data': validation_result.get('parsed_data'),
            'schema_valid': validation_result.get('schema_valid', True),
            'validated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации JSON'}), 500

@json_validator_bp.route('/api/json/format', methods=['POST'])
@login_required
def format_json():
    """Форматирование JSON"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        indent = int(data.get('indent', 2))
        sort_keys = data.get('sort_keys', False)
        ensure_ascii = data.get('ensure_ascii', True)
        
        if not json_text:
            return jsonify({'error': 'JSON текст не указан'}), 400
        
        # Форматирование JSON
        formatted_result = format_json_text(json_text, indent, sort_keys, ensure_ascii)
        
        if formatted_result is None:
            return jsonify({'error': 'Ошибка при форматировании JSON'}), 500
        
        return jsonify({
            'original': json_text,
            'formatted': formatted_result['formatted'],
            'indent': indent,
            'sort_keys': sort_keys,
            'ensure_ascii': ensure_ascii,
            'formatted_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при форматировании JSON'}), 500

@json_validator_bp.route('/api/json/minify', methods=['POST'])
@login_required
def minify_json():
    """Минификация JSON"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        
        if not json_text:
            return jsonify({'error': 'JSON текст не указан'}), 400
        
        # Минификация JSON
        minified_result = minify_json_text(json_text)
        
        if minified_result is None:
            return jsonify({'error': 'Ошибка при минификации JSON'}), 500
        
        return jsonify({
            'original': json_text,
            'minified': minified_result['minified'],
            'original_size': len(json_text),
            'minified_size': len(minified_result['minified']),
            'compression_ratio': minified_result['compression_ratio'],
            'minified_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при минификации JSON'}), 500

@json_validator_bp.route('/api/json/compare', methods=['POST'])
@login_required
def compare_json():
    """Сравнение JSON"""
    try:
        data = request.get_json()
        json1 = data.get('json1', '')
        json2 = data.get('json2', '')
        ignore_order = data.get('ignore_order', False)
        ignore_case = data.get('ignore_case', False)
        
        if not json1 or not json2:
            return jsonify({'error': 'Оба JSON должны быть указаны'}), 400
        
        # Сравнение JSON
        comparison_result = compare_json_texts(json1, json2, ignore_order, ignore_case)
        
        return jsonify({
            'json1': json1,
            'json2': json2,
            'are_equal': comparison_result['are_equal'],
            'differences': comparison_result.get('differences', []),
            'ignore_order': ignore_order,
            'ignore_case': ignore_case,
            'compared_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при сравнении JSON'}), 500

@json_validator_bp.route('/api/json/merge', methods=['POST'])
@login_required
def merge_json():
    """Объединение JSON"""
    try:
        data = request.get_json()
        json_objects = data.get('json_objects', [])
        merge_strategy = data.get('strategy', 'deep')  # deep, shallow, replace
        
        if not json_objects or len(json_objects) < 2:
            return jsonify({'error': 'Необходимо указать минимум 2 JSON объекта'}), 400
        
        # Объединение JSON
        merged_result = merge_json_objects(json_objects, merge_strategy)
        
        if merged_result is None:
            return jsonify({'error': 'Ошибка при объединении JSON'}), 500
        
        return jsonify({
            'json_objects': json_objects,
            'merged': merged_result['merged'],
            'strategy': merge_strategy,
            'objects_count': len(json_objects),
            'merged_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при объединении JSON'}), 500

@json_validator_bp.route('/api/json/extract', methods=['POST'])
@login_required
def extract_json():
    """Извлечение данных из JSON"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        path = data.get('path', '')
        
        if not json_text:
            return jsonify({'error': 'JSON текст не указан'}), 400
        
        # Извлечение данных
        extraction_result = extract_from_json(json_text, path)
        
        if extraction_result is None:
            return jsonify({'error': 'Ошибка при извлечении данных'}), 500
        
        return jsonify({
            'json': json_text,
            'path': path,
            'extracted': extraction_result['extracted'],
            'data_type': extraction_result['data_type'],
            'extracted_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при извлечении данных'}), 500

@json_validator_bp.route('/api/json/schema', methods=['POST'])
@login_required
def validate_json_schema():
    """Валидация JSON по схеме"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        schema_text = data.get('schema', '')
        
        if not json_text or not schema_text:
            return jsonify({'error': 'JSON и схема должны быть указаны'}), 400
        
        # Валидация по схеме
        schema_validation = validate_json_against_schema(json_text, schema_text)
        
        return jsonify({
            'json': json_text,
            'schema': schema_text,
            'is_valid': schema_validation['is_valid'],
            'errors': schema_validation.get('errors', []),
            'validated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации по схеме'}), 500

@json_validator_bp.route('/api/json/generate-schema', methods=['POST'])
@login_required
def generate_json_schema():
    """Генерация схемы JSON"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        schema_type = data.get('type', 'draft-07')  # draft-07, draft-06, draft-04
        
        if not json_text:
            return jsonify({'error': 'JSON текст не указан'}), 400
        
        # Генерация схемы
        schema_result = generate_schema_from_json(json_text, schema_type)
        
        if schema_result is None:
            return jsonify({'error': 'Ошибка при генерации схемы'}), 500
        
        return jsonify({
            'json': json_text,
            'schema': schema_result['schema'],
            'schema_type': schema_type,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации схемы'}), 500

def validate_json_text(json_text, schema=None, strict_mode=False):
    """Валидация JSON текста"""
    try:
        # Парсинг JSON
        parsed_data = json.loads(json_text)
        
        result = {
            'is_valid': True,
            'parsed_data': parsed_data,
            'errors': [],
            'warnings': []
        }
        
        # Валидация по схеме
        if schema:
            schema_validation = validate_json_against_schema(json_text, schema)
            result['schema_valid'] = schema_validation['is_valid']
            if not schema_validation['is_valid']:
                result['errors'].extend(schema_validation['errors'])
        
        # Строгая валидация
        if strict_mode:
            strict_validation = perform_strict_validation(parsed_data)
            result['warnings'].extend(strict_validation['warnings'])
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            'is_valid': False,
            'errors': [f'Ошибка парсинга JSON: {str(e)}'],
            'warnings': []
        }
    except Exception as e:
        return {
            'is_valid': False,
            'errors': [f'Ошибка валидации: {str(e)}'],
            'warnings': []
        }

def format_json_text(json_text, indent, sort_keys, ensure_ascii):
    """Форматирование JSON текста"""
    try:
        # Парсинг JSON
        parsed_data = json.loads(json_text)
        
        # Форматирование
        formatted_text = json.dumps(
            parsed_data,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii
        )
        
        return {
            'formatted': formatted_text,
            'indent': indent,
            'sort_keys': sort_keys,
            'ensure_ascii': ensure_ascii
        }
        
    except Exception:
        return None

def minify_json_text(json_text):
    """Минификация JSON текста"""
    try:
        # Парсинг JSON
        parsed_data = json.loads(json_text)
        
        # Минификация
        minified_text = json.dumps(parsed_data, separators=(',', ':'))
        
        # Расчет коэффициента сжатия
        original_size = len(json_text)
        minified_size = len(minified_text)
        compression_ratio = round((1 - minified_size / original_size) * 100, 2)
        
        return {
            'minified': minified_text,
            'compression_ratio': compression_ratio
        }
        
    except Exception:
        return None

def compare_json_texts(json1, json2, ignore_order, ignore_case):
    """Сравнение JSON текстов"""
    try:
        # Парсинг JSON
        data1 = json.loads(json1)
        data2 = json.loads(json2)
        
        # Сравнение
        if ignore_order:
            data1 = sort_json_recursively(data1)
            data2 = sort_json_recursively(data2)
        
        if ignore_case:
            data1 = normalize_case_recursively(data1)
            data2 = normalize_case_recursively(data2)
        
        are_equal = data1 == data2
        
        result = {
            'are_equal': are_equal,
            'differences': []
        }
        
        if not are_equal:
            result['differences'] = find_json_differences(data1, data2)
        
        return result
        
    except Exception:
        return {
            'are_equal': False,
            'differences': ['Ошибка при сравнении JSON']
        }

def merge_json_objects(json_objects, strategy):
    """Объединение JSON объектов"""
    try:
        # Парсинг JSON объектов
        parsed_objects = []
        for json_obj in json_objects:
            parsed_objects.append(json.loads(json_obj))
        
        # Объединение
        if strategy == 'deep':
            merged = deep_merge_objects(parsed_objects)
        elif strategy == 'shallow':
            merged = shallow_merge_objects(parsed_objects)
        else:  # replace
            merged = replace_merge_objects(parsed_objects)
        
        return {
            'merged': merged
        }
        
    except Exception:
        return None

def extract_from_json(json_text, path):
    """Извлечение данных из JSON по пути"""
    try:
        # Парсинг JSON
        parsed_data = json.loads(json_text)
        
        # Извлечение по пути
        if not path:
            extracted = parsed_data
        else:
            extracted = get_nested_value(parsed_data, path)
        
        # Определение типа данных
        data_type = type(extracted).__name__
        
        return {
            'extracted': extracted,
            'data_type': data_type
        }
        
    except Exception:
        return None

def validate_json_against_schema(json_text, schema_text):
    """Валидация JSON по схеме"""
    try:
        # Парсинг JSON и схемы
        json_data = json.loads(json_text)
        schema_data = json.loads(schema_text)
        
        # Валидация
        validator = jsonschema.Draft7Validator(schema_data)
        errors = list(validator.iter_errors(json_data))
        
        return {
            'is_valid': len(errors) == 0,
            'errors': [str(error) for error in errors]
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'errors': [f'Ошибка валидации схемы: {str(e)}']
        }

def generate_schema_from_json(json_text, schema_type):
    """Генерация схемы из JSON"""
    try:
        # Парсинг JSON
        parsed_data = json.loads(json_text)
        
        # Генерация схемы
        schema = generate_schema_recursive(parsed_data)
        
        # Добавление метаданных схемы
        schema['$schema'] = f'http://json-schema.org/draft-07/schema#'
        schema['title'] = 'Generated Schema'
        schema['description'] = 'Автоматически сгенерированная схема'
        
        return {
            'schema': schema
        }
        
    except Exception:
        return None

def perform_strict_validation(data):
    """Строгая валидация JSON"""
    warnings = []
    
    # Проверка на пустые объекты
    if isinstance(data, dict) and len(data) == 0:
        warnings.append('Пустой объект')
    
    # Проверка на пустые массивы
    if isinstance(data, list) and len(data) == 0:
        warnings.append('Пустой массив')
    
    # Проверка на дублирующиеся ключи
    if isinstance(data, dict):
        keys = list(data.keys())
        if len(keys) != len(set(keys)):
            warnings.append('Дублирующиеся ключи')
    
    return {
        'warnings': warnings
    }

def sort_json_recursively(data):
    """Рекурсивная сортировка JSON"""
    if isinstance(data, dict):
        return {k: sort_json_recursively(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [sort_json_recursively(item) for item in data]
    else:
        return data

def normalize_case_recursively(data):
    """Рекурсивная нормализация регистра"""
    if isinstance(data, dict):
        return {k.lower(): normalize_case_recursively(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_case_recursively(item) for item in data]
    elif isinstance(data, str):
        return data.lower()
    else:
        return data

def find_json_differences(data1, data2, path=''):
    """Поиск различий в JSON"""
    differences = []
    
    if type(data1) != type(data2):
        differences.append(f'Разные типы на пути {path}: {type(data1).__name__} vs {type(data2).__name__}')
        return differences
    
    if isinstance(data1, dict):
        all_keys = set(data1.keys()) | set(data2.keys())
        for key in all_keys:
            if key not in data1:
                differences.append(f'Ключ {key} отсутствует в первом объекте на пути {path}')
            elif key not in data2:
                differences.append(f'Ключ {key} отсутствует во втором объекте на пути {path}')
            else:
                differences.extend(find_json_differences(data1[key], data2[key], f'{path}.{key}' if path else key))
    
    elif isinstance(data1, list):
        if len(data1) != len(data2):
            differences.append(f'Разная длина массивов на пути {path}: {len(data1)} vs {len(data2)}')
        else:
            for i, (item1, item2) in enumerate(zip(data1, data2)):
                differences.extend(find_json_differences(item1, item2, f'{path}[{i}]'))
    
    else:
        if data1 != data2:
            differences.append(f'Разные значения на пути {path}: {data1} vs {data2}')
    
    return differences

def deep_merge_objects(objects):
    """Глубокое объединение объектов"""
    result = {}
    
    for obj in objects:
        for key, value in obj.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge_objects([result[key], value])
            else:
                result[key] = value
    
    return result

def shallow_merge_objects(objects):
    """Поверхностное объединение объектов"""
    result = {}
    
    for obj in objects:
        result.update(obj)
    
    return result

def replace_merge_objects(objects):
    """Объединение объектов с заменой"""
    result = {}
    
    for obj in objects:
        result = obj
    
    return result

def get_nested_value(data, path):
    """Получение вложенного значения по пути"""
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            raise KeyError(f'Путь {path} не найден')
    
    return current

def generate_schema_recursive(data):
    """Рекурсивная генерация схемы"""
    if isinstance(data, dict):
        properties = {}
        required = []
        
        for key, value in data.items():
            properties[key] = generate_schema_recursive(value)
            required.append(key)
        
        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }
    
    elif isinstance(data, list):
        if len(data) == 0:
            return {'type': 'array', 'items': {}}
        
        # Анализ элементов массива
        item_schemas = [generate_schema_recursive(item) for item in data]
        
        # Если все элементы имеют одинаковую схему
        if all(schema == item_schemas[0] for schema in item_schemas):
            return {
                'type': 'array',
                'items': item_schemas[0]
            }
        else:
            return {
                'type': 'array',
                'items': {'anyOf': item_schemas}
            }
    
    elif isinstance(data, str):
        return {'type': 'string'}
    
    elif isinstance(data, int):
        return {'type': 'integer'}
    
    elif isinstance(data, float):
        return {'type': 'number'}
    
    elif isinstance(data, bool):
        return {'type': 'boolean'}
    
    elif data is None:
        return {'type': 'null'}
    
    else:
        return {'type': 'string'}

def get_json_validator_statistics(user_id):
    """Получение статистики использования JSON валидатора"""
    # Здесь можно добавить статистику использования
    return {
        'validations_count': 0,
        'formatting_count': 0,
        'minifications_count': 0,
        'comparisons_count': 0,
        'most_used_operation': 'validate'
    }

def get_json_validator_tips():
    """Получение советов по использованию JSON валидатора"""
    tips = [
        "Всегда валидируйте JSON перед использованием",
        "Используйте схемы для проверки структуры данных",
        "Форматирование JSON улучшает читаемость",
        "Минификация уменьшает размер JSON",
        "Проверяйте валидность JSON при получении от внешних источников",
        "Используйте строгую валидацию для критических данных",
        "Сравнение JSON помогает найти различия",
        "Объединение JSON объектов требует осторожности"
    ]
    
    return tips
