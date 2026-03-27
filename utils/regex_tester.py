from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import re
import json
from datetime import datetime

regex_tester_bp = Blueprint('regex_tester', __name__)

# Предустановленные регулярные выражения
REGEX_PATTERNS = {
    'email': {
        'name': 'Email адрес',
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'description': 'Проверка валидности email адреса',
        'flags': ['IGNORECASE']
    },
    'phone': {
        'name': 'Номер телефона',
        'pattern': r'^\+?[\d\s\-\(\)]{10,}$',
        'description': 'Проверка номера телефона',
        'flags': []
    },
    'url': {
        'name': 'URL',
        'pattern': r'^https?://[^\s/$.?#].[^\s]*$',
        'description': 'Проверка URL',
        'flags': ['IGNORECASE']
    },
    'ipv4': {
        'name': 'IPv4 адрес',
        'pattern': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        'description': 'Проверка IPv4 адреса',
        'flags': []
    },
    'ipv6': {
        'name': 'IPv6 адрес',
        'pattern': r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
        'description': 'Проверка IPv6 адреса',
        'flags': ['IGNORECASE']
    },
    'date': {
        'name': 'Дата (YYYY-MM-DD)',
        'pattern': r'^\d{4}-\d{2}-\d{2}$',
        'description': 'Проверка даты в формате YYYY-MM-DD',
        'flags': []
    },
    'time': {
        'name': 'Время (HH:MM:SS)',
        'pattern': r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$',
        'description': 'Проверка времени в формате HH:MM:SS',
        'flags': []
    },
    'credit_card': {
        'name': 'Номер кредитной карты',
        'pattern': r'^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$',
        'description': 'Проверка номера кредитной карты',
        'flags': []
    },
    'password': {
        'name': 'Пароль (8+ символов, буквы и цифры)',
        'pattern': r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$',
        'description': 'Пароль минимум 8 символов, содержит буквы и цифры',
        'flags': []
    },
    'username': {
        'name': 'Имя пользователя',
        'pattern': r'^[a-zA-Z0-9_]{3,20}$',
        'description': 'Имя пользователя 3-20 символов, только буквы, цифры и подчеркивания',
        'flags': []
    }
}

@regex_tester_bp.route('/api/regex/test', methods=['POST'])
@login_required
def test_regex():
    """Тестирование регулярного выражения"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        text = data.get('text', '')
        flags = data.get('flags', [])
        global_match = data.get('global_match', False)
        
        if not pattern:
            return jsonify({'error': 'Регулярное выражение не указано'}), 400
        
        # Тестирование регулярного выражения
        test_result = test_regex_pattern(pattern, text, flags, global_match)
        
        return jsonify({
            'pattern': pattern,
            'text': text,
            'flags': flags,
            'global_match': global_match,
            'result': test_result,
            'tested_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при тестировании регулярного выражения'}), 500

@regex_tester_bp.route('/api/regex/validate', methods=['POST'])
@login_required
def validate_regex():
    """Валидация регулярного выражения"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        
        if not pattern:
            return jsonify({'error': 'Регулярное выражение не указано'}), 400
        
        # Валидация регулярного выражения
        validation_result = validate_regex_pattern(pattern)
        
        return jsonify({
            'pattern': pattern,
            'is_valid': validation_result['is_valid'],
            'error': validation_result.get('error'),
            'validated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации регулярного выражения'}), 500

@regex_tester_bp.route('/api/regex/replace', methods=['POST'])
@login_required
def replace_regex():
    """Замена по регулярному выражению"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        text = data.get('text', '')
        replacement = data.get('replacement', '')
        flags = data.get('flags', [])
        global_replace = data.get('global_replace', True)
        
        if not pattern or not text:
            return jsonify({'error': 'Регулярное выражение и текст должны быть указаны'}), 400
        
        # Замена по регулярному выражению
        replace_result = replace_regex_pattern(pattern, text, replacement, flags, global_replace)
        
        return jsonify({
            'pattern': pattern,
            'text': text,
            'replacement': replacement,
            'flags': flags,
            'global_replace': global_replace,
            'result': replace_result,
            'replaced_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при замене по регулярному выражению'}), 500

@regex_tester_bp.route('/api/regex/split', methods=['POST'])
@login_required
def split_regex():
    """Разделение по регулярному выражению"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        text = data.get('text', '')
        flags = data.get('flags', [])
        maxsplit = data.get('maxsplit', 0)
        
        if not pattern or not text:
            return jsonify({'error': 'Регулярное выражение и текст должны быть указаны'}), 400
        
        # Разделение по регулярному выражению
        split_result = split_regex_pattern(pattern, text, flags, maxsplit)
        
        return jsonify({
            'pattern': pattern,
            'text': text,
            'flags': flags,
            'maxsplit': maxsplit,
            'result': split_result,
            'split_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при разделении по регулярному выражению'}), 500

@regex_tester_bp.route('/api/regex/patterns', methods=['GET'])
def get_regex_patterns():
    """Получение предустановленных регулярных выражений"""
    try:
        return jsonify({'patterns': REGEX_PATTERNS})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении паттернов'}), 500

@regex_tester_bp.route('/api/regex/analyze', methods=['POST'])
@login_required
def analyze_regex():
    """Анализ регулярного выражения"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        
        if not pattern:
            return jsonify({'error': 'Регулярное выражение не указано'}), 400
        
        # Анализ регулярного выражения
        analysis_result = analyze_regex_pattern(pattern)
        
        return jsonify({
            'pattern': pattern,
            'analysis': analysis_result,
            'analyzed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при анализе регулярного выражения'}), 500

@regex_tester_bp.route('/api/regex/explain', methods=['POST'])
@login_required
def explain_regex():
    """Объяснение регулярного выражения"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        
        if not pattern:
            return jsonify({'error': 'Регулярное выражение не указано'}), 400
        
        # Объяснение регулярного выражения
        explanation = explain_regex_pattern(pattern)
        
        return jsonify({
            'pattern': pattern,
            'explanation': explanation,
            'explained_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при объяснении регулярного выражения'}), 500

@regex_tester_bp.route('/api/regex/batch', methods=['POST'])
@login_required
def batch_regex_test():
    """Пакетное тестирование регулярных выражений"""
    try:
        data = request.get_json()
        tests = data.get('tests', [])
        
        if not tests or len(tests) > 50:
            return jsonify({'error': 'Укажите от 1 до 50 тестов'}), 400
        
        results = []
        
        for test in tests:
            pattern = test.get('pattern', '')
            text = test.get('text', '')
            flags = test.get('flags', [])
            global_match = test.get('global_match', False)
            
            if pattern and text:
                result = test_regex_pattern(pattern, text, flags, global_match)
                results.append({
                    'pattern': pattern,
                    'text': text,
                    'flags': flags,
                    'global_match': global_match,
                    'result': result,
                    'success': True
                })
            else:
                results.append({
                    'pattern': pattern,
                    'text': text,
                    'flags': flags,
                    'global_match': global_match,
                    'result': None,
                    'success': False,
                    'error': 'Недостаточно данных для тестирования'
                })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'tested_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при пакетном тестировании'}), 500

def test_regex_pattern(pattern, text, flags, global_match):
    """Тестирование регулярного выражения"""
    try:
        # Компиляция флагов
        compiled_flags = compile_regex_flags(flags)
        
        # Компиляция регулярного выражения
        regex = re.compile(pattern, compiled_flags)
        
        # Поиск совпадений
        if global_match:
            matches = list(regex.finditer(text))
            match_data = []
            
            for i, match in enumerate(matches):
                match_data.append({
                    'match_index': i,
                    'start': match.start(),
                    'end': match.end(),
                    'match': match.group(),
                    'groups': match.groups(),
                    'named_groups': match.groupdict()
                })
            
            return {
                'matches': match_data,
                'match_count': len(matches),
                'has_matches': len(matches) > 0,
                'pattern': pattern,
                'flags': flags
            }
        else:
            match = regex.search(text)
            
            if match:
                return {
                    'matches': [{
                        'match_index': 0,
                        'start': match.start(),
                        'end': match.end(),
                        'match': match.group(),
                        'groups': match.groups(),
                        'named_groups': match.groupdict()
                    }],
                    'match_count': 1,
                    'has_matches': True,
                    'pattern': pattern,
                    'flags': flags
                }
            else:
                return {
                    'matches': [],
                    'match_count': 0,
                    'has_matches': False,
                    'pattern': pattern,
                    'flags': flags
                }
        
    except re.error as e:
        return {
            'matches': [],
            'match_count': 0,
            'has_matches': False,
            'error': f'Ошибка в регулярном выражении: {str(e)}',
            'pattern': pattern,
            'flags': flags
        }
    except Exception as e:
        return {
            'matches': [],
            'match_count': 0,
            'has_matches': False,
            'error': f'Ошибка при тестировании: {str(e)}',
            'pattern': pattern,
            'flags': flags
        }

def validate_regex_pattern(pattern):
    """Валидация регулярного выражения"""
    try:
        re.compile(pattern)
        return {
            'is_valid': True,
            'error': None
        }
    except re.error as e:
        return {
            'is_valid': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'is_valid': False,
            'error': f'Неожиданная ошибка: {str(e)}'
        }

def replace_regex_pattern(pattern, text, replacement, flags, global_replace):
    """Замена по регулярному выражению"""
    try:
        # Компиляция флагов
        compiled_flags = compile_regex_flags(flags)
        
        # Компиляция регулярного выражения
        regex = re.compile(pattern, compiled_flags)
        
        # Замена
        if global_replace:
            result_text = regex.sub(replacement, text)
            count = len(regex.findall(text))
        else:
            result_text = regex.sub(replacement, text, count=1)
            count = 1 if regex.search(text) else 0
        
        return {
            'original_text': text,
            'result_text': result_text,
            'replacements_count': count,
            'pattern': pattern,
            'replacement': replacement,
            'flags': flags
        }
        
    except re.error as e:
        return {
            'original_text': text,
            'result_text': text,
            'replacements_count': 0,
            'error': f'Ошибка в регулярном выражении: {str(e)}',
            'pattern': pattern,
            'replacement': replacement,
            'flags': flags
        }
    except Exception as e:
        return {
            'original_text': text,
            'result_text': text,
            'replacements_count': 0,
            'error': f'Ошибка при замене: {str(e)}',
            'pattern': pattern,
            'replacement': replacement,
            'flags': flags
        }

def split_regex_pattern(pattern, text, flags, maxsplit):
    """Разделение по регулярному выражению"""
    try:
        # Компиляция флагов
        compiled_flags = compile_regex_flags(flags)
        
        # Компиляция регулярного выражения
        regex = re.compile(pattern, compiled_flags)
        
        # Разделение
        if maxsplit > 0:
            parts = regex.split(text, maxsplit)
        else:
            parts = regex.split(text)
        
        return {
            'original_text': text,
            'parts': parts,
            'parts_count': len(parts),
            'pattern': pattern,
            'flags': flags,
            'maxsplit': maxsplit
        }
        
    except re.error as e:
        return {
            'original_text': text,
            'parts': [text],
            'parts_count': 1,
            'error': f'Ошибка в регулярном выражении: {str(e)}',
            'pattern': pattern,
            'flags': flags,
            'maxsplit': maxsplit
        }
    except Exception as e:
        return {
            'original_text': text,
            'parts': [text],
            'parts_count': 1,
            'error': f'Ошибка при разделении: {str(e)}',
            'pattern': pattern,
            'flags': flags,
            'maxsplit': maxsplit
        }

def analyze_regex_pattern(pattern):
    """Анализ регулярного выражения"""
    try:
        # Компиляция для анализа
        regex = re.compile(pattern)
        
        analysis = {
            'pattern': pattern,
            'is_valid': True,
            'length': len(pattern),
            'complexity': calculate_regex_complexity(pattern),
            'character_classes': find_character_classes(pattern),
            'quantifiers': find_quantifiers(pattern),
            'groups': find_groups(pattern),
            'anchors': find_anchors(pattern),
            'flags': []
        }
        
        return analysis
        
    except re.error as e:
        return {
            'pattern': pattern,
            'is_valid': False,
            'error': str(e),
            'length': len(pattern),
            'complexity': 0,
            'character_classes': [],
            'quantifiers': [],
            'groups': [],
            'anchors': [],
            'flags': []
        }
    except Exception as e:
        return {
            'pattern': pattern,
            'is_valid': False,
            'error': f'Неожиданная ошибка: {str(e)}',
            'length': len(pattern),
            'complexity': 0,
            'character_classes': [],
            'quantifiers': [],
            'groups': [],
            'anchors': [],
            'flags': []
        }

def explain_regex_pattern(pattern):
    """Объяснение регулярного выражения"""
    try:
        # Компиляция для проверки
        regex = re.compile(pattern)
        
        explanation = {
            'pattern': pattern,
            'is_valid': True,
            'explanation': generate_regex_explanation(pattern),
            'examples': generate_regex_examples(pattern)
        }
        
        return explanation
        
    except re.error as e:
        return {
            'pattern': pattern,
            'is_valid': False,
            'error': str(e),
            'explanation': 'Неверное регулярное выражение',
            'examples': []
        }
    except Exception as e:
        return {
            'pattern': pattern,
            'is_valid': False,
            'error': f'Неожиданная ошибка: {str(e)}',
            'explanation': 'Ошибка при анализе',
            'examples': []
        }

def compile_regex_flags(flags):
    """Компиляция флагов регулярного выражения"""
    compiled_flags = 0
    
    for flag in flags:
        if flag == 'IGNORECASE':
            compiled_flags |= re.IGNORECASE
        elif flag == 'MULTILINE':
            compiled_flags |= re.MULTILINE
        elif flag == 'DOTALL':
            compiled_flags |= re.DOTALL
        elif flag == 'VERBOSE':
            compiled_flags |= re.VERBOSE
        elif flag == 'ASCII':
            compiled_flags |= re.ASCII
        elif flag == 'LOCALE':
            compiled_flags |= re.LOCALE
        elif flag == 'UNICODE':
            compiled_flags |= re.UNICODE
        elif flag == 'DEBUG':
            compiled_flags |= re.DEBUG
    
    return compiled_flags

def calculate_regex_complexity(pattern):
    """Расчет сложности регулярного выражения"""
    complexity = 0
    
    # Подсчет метасимволов
    meta_chars = r'[]{}()*+?^$|\.'
    for char in meta_chars:
        complexity += pattern.count(char)
    
    # Подсчет квантификаторов
    quantifiers = ['*', '+', '?', '{', '}']
    for quantifier in quantifiers:
        complexity += pattern.count(quantifier)
    
    # Подсчет групп
    complexity += pattern.count('(') + pattern.count(')')
    
    # Подсчет альтернатив
    complexity += pattern.count('|')
    
    return complexity

def find_character_classes(pattern):
    """Поиск классов символов"""
    classes = []
    
    # Поиск символьных классов
    import re
    char_class_pattern = r'\[([^\]]+)\]'
    matches = re.findall(char_class_pattern, pattern)
    
    for match in matches:
        classes.append({
            'class': f'[{match}]',
            'description': f'Символьный класс: {match}'
        })
    
    return classes

def find_quantifiers(pattern):
    """Поиск квантификаторов"""
    quantifiers = []
    
    # Поиск квантификаторов
    quantifier_pattern = r'(\*|\+|\?|\{[^}]*\})'
    matches = re.findall(quantifier_pattern, pattern)
    
    for match in matches:
        quantifiers.append({
            'quantifier': match,
            'description': get_quantifier_description(match)
        })
    
    return quantifiers

def find_groups(pattern):
    """Поиск групп"""
    groups = []
    
    # Поиск групп
    group_pattern = r'\(([^)]*)\)'
    matches = re.findall(group_pattern, pattern)
    
    for i, match in enumerate(matches):
        groups.append({
            'group': f'({match})',
            'index': i + 1,
            'description': f'Группа {i + 1}: {match}'
        })
    
    return groups

def find_anchors(pattern):
    """Поиск якорей"""
    anchors = []
    
    if pattern.startswith('^'):
        anchors.append({
            'anchor': '^',
            'description': 'Начало строки'
        })
    
    if pattern.endswith('$'):
        anchors.append({
            'anchor': '$',
            'description': 'Конец строки'
        })
    
    return anchors

def generate_regex_explanation(pattern):
    """Генерация объяснения регулярного выражения"""
    explanation = []
    
    # Анализ основных компонентов
    if '^' in pattern:
        explanation.append('^ - Начало строки')
    
    if '$' in pattern:
        explanation.append('$ - Конец строки')
    
    if '.' in pattern:
        explanation.append('. - Любой символ')
    
    if '*' in pattern:
        explanation.append('* - Ноль или более повторений')
    
    if '+' in pattern:
        explanation.append('+ - Одно или более повторений')
    
    if '?' in pattern:
        explanation.append('? - Ноль или одно повторение')
    
    if '|' in pattern:
        explanation.append('| - Альтернатива (ИЛИ)')
    
    if '[]' in pattern:
        explanation.append('[] - Символьный класс')
    
    if '()' in pattern:
        explanation.append('() - Группа')
    
    return explanation

def generate_regex_examples(pattern):
    """Генерация примеров для регулярного выражения"""
    examples = []
    
    # Примеры для общих паттернов
    if 'email' in pattern.lower() or '@' in pattern:
        examples = [
            'user@example.com',
            'test.email@domain.org',
            'invalid.email'
        ]
    elif 'phone' in pattern.lower() or '\\d' in pattern:
        examples = [
            '+1234567890',
            '(123) 456-7890',
            '123-456-7890'
        ]
    elif 'url' in pattern.lower() or 'http' in pattern:
        examples = [
            'https://www.example.com',
            'http://example.org',
            'invalid.url'
        ]
    else:
        examples = [
            'test string',
            'example text',
            'sample data'
        ]
    
    return examples

def get_quantifier_description(quantifier):
    """Получение описания квантификатора"""
    descriptions = {
        '*': 'Ноль или более повторений',
        '+': 'Одно или более повторений',
        '?': 'Ноль или одно повторение',
        '{n}': 'Ровно n повторений',
        '{n,}': 'n или более повторений',
        '{n,m}': 'От n до m повторений'
    }
    
    if quantifier in descriptions:
        return descriptions[quantifier]
    elif quantifier.startswith('{') and quantifier.endswith('}'):
        return 'Квантификатор с диапазоном'
    else:
        return 'Неизвестный квантификатор'

def get_regex_tester_statistics(user_id):
    """Получение статистики использования тестера регулярных выражений"""
    # Здесь можно добавить статистику использования
    return {
        'tests_count': 0,
        'most_used_patterns': [],
        'most_used_flags': [],
        'total_batches': 0
    }

def get_regex_tester_tips():
    """Получение советов по использованию регулярных выражений"""
    tips = [
        "Используйте ^ и $ для точного соответствия начала и конца строки",
        "Экранируйте специальные символы с помощью \\",
        "Используйте [] для символьных классов",
        "Группы () помогают извлекать части совпадений",
        "Квантификаторы *, +, ? контролируют количество повторений",
        "Флаг IGNORECASE делает поиск нечувствительным к регистру",
        "Флаг MULTILINE позволяет ^ и $ работать с каждой строкой",
        "Тестируйте регулярные выражения на различных входных данных"
    ]
    
    return tips
