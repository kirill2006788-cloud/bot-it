from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import re
import ast
import json
from datetime import datetime

code_checker_bp = Blueprint('code_checker', __name__)

@code_checker_bp.route('/api/code/check', methods=['POST'])
@login_required
def check_code():
    """Проверка кода"""
    try:
        data = request.get_json()
        
        code = data.get('code', '')
        language = data.get('language', 'python').lower()
        check_types = data.get('check_types', ['syntax', 'style', 'security'])
        
        if not code:
            return jsonify({'error': 'Код не предоставлен'}), 400
        
        # Проверка кода
        if language == 'python':
            result = check_python_code(code, check_types)
        elif language == 'javascript':
            result = check_javascript_code(code, check_types)
        elif language == 'java':
            result = check_java_code(code, check_types)
        elif language == 'html':
            result = check_html_code(code, check_types)
        elif language == 'css':
            result = check_css_code(code, check_types)
        else:
            return jsonify({'error': 'Неподдерживаемый язык программирования'}), 400
        
        return jsonify({
            'language': language,
            'check_types': check_types,
            'result': result,
            'checked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при проверке кода'}), 500

@code_checker_bp.route('/api/code/languages', methods=['GET'])
def get_supported_languages():
    """Получение поддерживаемых языков"""
    try:
        languages = {
            'python': {
                'name': 'Python',
                'description': 'Язык программирования Python',
                'extensions': ['.py'],
                'check_types': ['syntax', 'style', 'security', 'performance']
            },
            'javascript': {
                'name': 'JavaScript',
                'description': 'Язык программирования JavaScript',
                'extensions': ['.js', '.jsx'],
                'check_types': ['syntax', 'style', 'security']
            },
            'java': {
                'name': 'Java',
                'description': 'Язык программирования Java',
                'extensions': ['.java'],
                'check_types': ['syntax', 'style', 'security']
            },
            'html': {
                'name': 'HTML',
                'description': 'Язык разметки HTML',
                'extensions': ['.html', '.htm'],
                'check_types': ['syntax', 'accessibility', 'seo']
            },
            'css': {
                'name': 'CSS',
                'description': 'Язык стилей CSS',
                'extensions': ['.css'],
                'check_types': ['syntax', 'style', 'performance']
            }
        }
        
        return jsonify({'languages': languages})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении языков'}), 500

@code_checker_bp.route('/api/code/metrics', methods=['POST'])
@login_required
def get_code_metrics():
    """Получение метрик кода"""
    try:
        data = request.get_json()
        
        code = data.get('code', '')
        language = data.get('language', 'python').lower()
        
        if not code:
            return jsonify({'error': 'Код не предоставлен'}), 400
        
        # Расчет метрик
        metrics = calculate_code_metrics(code, language)
        
        return jsonify({
            'language': language,
            'metrics': metrics,
            'analyzed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при расчете метрик'}), 500

def check_python_code(code, check_types):
    """Проверка Python кода"""
    result = {
        'syntax_valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': [],
        'score': 100
    }
    
    # Проверка синтаксиса
    if 'syntax' in check_types:
        try:
            ast.parse(code)
            result['syntax_valid'] = True
        except SyntaxError as e:
            result['syntax_valid'] = False
            result['errors'].append(f'Синтаксическая ошибка: {str(e)}')
            result['score'] -= 30
    
    # Проверка стиля
    if 'style' in check_types:
        style_issues = check_python_style(code)
        result['warnings'].extend(style_issues['warnings'])
        result['suggestions'].extend(style_issues['suggestions'])
        result['score'] -= len(style_issues['warnings']) * 2
    
    # Проверка безопасности
    if 'security' in check_types:
        security_issues = check_python_security(code)
        result['warnings'].extend(security_issues['warnings'])
        result['suggestions'].extend(security_issues['suggestions'])
        result['score'] -= len(security_issues['warnings']) * 5
    
    # Проверка производительности
    if 'performance' in check_types:
        performance_issues = check_python_performance(code)
        result['suggestions'].extend(performance_issues['suggestions'])
        result['score'] -= len(performance_issues['suggestions'])
    
    result['score'] = max(0, result['score'])
    
    return result

def check_python_style(code):
    """Проверка стиля Python кода"""
    issues = {'warnings': [], 'suggestions': []}
    
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Проверка длины строки
        if len(line) > 79:
            issues['warnings'].append(f'Строка {i}: Слишком длинная строка ({len(line)} символов)')
        
        # Проверка отступов
        if line.strip() and not line.startswith((' ', '\t')) and not line.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ', 'elif ', 'else:')):
            if i > 1 and lines[i-2].strip().endswith(':'):
                issues['warnings'].append(f'Строка {i}: Неправильный отступ')
        
        # Проверка пробелов
        if line.strip().startswith(' ') and '\t' in line:
            issues['warnings'].append(f'Строка {i}: Смешивание пробелов и табов')
        
        # Проверка trailing whitespace
        if line.endswith(' ') or line.endswith('\t'):
            issues['warnings'].append(f'Строка {i}: Лишние пробелы в конце строки')
        
        # Проверка импортов
        if line.strip().startswith('import ') and ',' in line:
            issues['suggestions'].append(f'Строка {i}: Рекомендуется импортировать модули отдельными строками')
    
    return issues

def check_python_security(code):
    """Проверка безопасности Python кода"""
    issues = {'warnings': [], 'suggestions': []}
    
    # Опасные функции
    dangerous_functions = [
        'eval', 'exec', 'compile', '__import__',
        'input', 'raw_input', 'file', 'open'
    ]
    
    for func in dangerous_functions:
        if func in code:
            issues['warnings'].append(f'Использование потенциально опасной функции: {func}')
    
    # SQL инъекции
    sql_patterns = [
        r'execute\s*\(\s*["\'].*%s.*["\']',
        r'execute\s*\(\s*f["\'].*\{.*\}.*["\']',
        r'execute\s*\(\s*["\'].*\+.*["\']'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, code):
            issues['warnings'].append('Возможная SQL инъекция: используйте параметризованные запросы')
    
    # Проверка паролей
    if 'password' in code.lower() and 'input' in code:
        issues['warnings'].append('Пароли не должны вводиться через input()')
    
    return issues

def check_python_performance(code):
    """Проверка производительности Python кода"""
    issues = {'suggestions': []}
    
    # Неэффективные циклы
    if 'for i in range(len(' in code:
        issues['suggestions'].append('Используйте enumerate() вместо range(len())')
    
    # Проверка использования list comprehensions
    if 'for ' in code and 'append(' in code:
        issues['suggestions'].append('Рассмотрите использование list comprehensions')
    
    # Проверка глобальных переменных
    if 'global ' in code:
        issues['suggestions'].append('Избегайте использования глобальных переменных')
    
    return issues

def check_javascript_code(code, check_types):
    """Проверка JavaScript кода"""
    result = {
        'syntax_valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': [],
        'score': 100
    }
    
    # Проверка синтаксиса (базовая)
    if 'syntax' in check_types:
        syntax_issues = check_javascript_syntax(code)
        result['errors'].extend(syntax_issues['errors'])
        result['warnings'].extend(syntax_issues['warnings'])
        result['score'] -= len(syntax_issues['errors']) * 10
        result['score'] -= len(syntax_issues['warnings']) * 2
    
    # Проверка стиля
    if 'style' in check_types:
        style_issues = check_javascript_style(code)
        result['warnings'].extend(style_issues['warnings'])
        result['suggestions'].extend(style_issues['suggestions'])
        result['score'] -= len(style_issues['warnings']) * 2
    
    # Проверка безопасности
    if 'security' in check_types:
        security_issues = check_javascript_security(code)
        result['warnings'].extend(security_issues['warnings'])
        result['suggestions'].extend(security_issues['suggestions'])
        result['score'] -= len(security_issues['warnings']) * 5
    
    result['score'] = max(0, result['score'])
    
    return result

def check_javascript_syntax(code):
    """Проверка синтаксиса JavaScript"""
    issues = {'errors': [], 'warnings': []}
    
    # Проверка скобок
    open_braces = code.count('{')
    close_braces = code.count('}')
    if open_braces != close_braces:
        issues['errors'].append('Несоответствие фигурных скобок')
    
    open_parens = code.count('(')
    close_parens = code.count(')')
    if open_parens != close_parens:
        issues['errors'].append('Несоответствие круглых скобок')
    
    # Проверка точек с запятой
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.endswith((';', '{', '}', ':', ',')) and not line.startswith(('//', '/*', '*', 'if', 'for', 'while', 'function', 'var', 'let', 'const')):
            issues['warnings'].append(f'Строка {i}: Рекомендуется добавить точку с запятой')
    
    return issues

def check_javascript_style(code):
    """Проверка стиля JavaScript кода"""
    issues = {'warnings': [], 'suggestions': []}
    
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Проверка длины строки
        if len(line) > 80:
            issues['warnings'].append(f'Строка {i}: Слишком длинная строка ({len(line)} символов)')
        
        # Проверка отступов
        if line.strip() and not line.startswith((' ', '\t')) and not line.startswith(('function', 'if', 'for', 'while', 'try', 'catch', 'else', 'var', 'let', 'const')):
            if i > 1 and lines[i-2].strip().endswith('{'):
                issues['warnings'].append(f'Строка {i}: Неправильный отступ')
        
        # Проверка использования var
        if 'var ' in line:
            issues['suggestions'].append(f'Строка {i}: Используйте let или const вместо var')
    
    return issues

def check_javascript_security(code):
    """Проверка безопасности JavaScript кода"""
    issues = {'warnings': [], 'suggestions': []}
    
    # Опасные функции
    dangerous_functions = ['eval', 'Function', 'setTimeout', 'setInterval']
    
    for func in dangerous_functions:
        if func in code:
            issues['warnings'].append(f'Использование потенциально опасной функции: {func}')
    
    # Проверка innerHTML
    if 'innerHTML' in code:
        issues['warnings'].append('Использование innerHTML может привести к XSS атакам')
    
    # Проверка document.write
    if 'document.write' in code:
        issues['warnings'].append('Использование document.write не рекомендуется')
    
    return issues

def check_java_code(code, check_types):
    """Проверка Java кода"""
    result = {
        'syntax_valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': [],
        'score': 100
    }
    
    # Проверка синтаксиса (базовая)
    if 'syntax' in check_types:
        syntax_issues = check_java_syntax(code)
        result['errors'].extend(syntax_issues['errors'])
        result['warnings'].extend(syntax_issues['warnings'])
        result['score'] -= len(syntax_issues['errors']) * 10
        result['score'] -= len(syntax_issues['warnings']) * 2
    
    # Проверка стиля
    if 'style' in check_types:
        style_issues = check_java_style(code)
        result['warnings'].extend(style_issues['warnings'])
        result['suggestions'].extend(style_issues['suggestions'])
        result['score'] -= len(style_issues['warnings']) * 2
    
    result['score'] = max(0, result['score'])
    
    return result

def check_java_syntax(code):
    """Проверка синтаксиса Java"""
    issues = {'errors': [], 'warnings': []}
    
    # Проверка скобок
    open_braces = code.count('{')
    close_braces = code.count('}')
    if open_braces != close_braces:
        issues['errors'].append('Несоответствие фигурных скобок')
    
    # Проверка точек с запятой
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.endswith((';', '{', '}', ':', ',')) and not line.startswith(('//', '/*', '*', 'if', 'for', 'while', 'public', 'private', 'protected', 'class', 'interface')):
            issues['warnings'].append(f'Строка {i}: Возможно отсутствует точка с запятой')
    
    return issues

def check_java_style(code):
    """Проверка стиля Java кода"""
    issues = {'warnings': [], 'suggestions': []}
    
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Проверка длины строки
        if len(line) > 120:
            issues['warnings'].append(f'Строка {i}: Слишком длинная строка ({len(line)} символов)')
        
        # Проверка именования классов
        if 'class ' in line:
            class_name = line.split('class ')[1].split()[0]
            if not class_name[0].isupper():
                issues['warnings'].append(f'Строка {i}: Имя класса должно начинаться с заглавной буквы')
        
        # Проверка именования методов
        if '(' in line and 'public' in line or 'private' in line or 'protected' in line:
            if 'void ' in line or 'int ' in line or 'String ' in line:
                method_name = line.split()[-1].split('(')[0]
                if not method_name[0].islower():
                    issues['warnings'].append(f'Строка {i}: Имя метода должно начинаться со строчной буквы')
    
    return issues

def check_html_code(code, check_types):
    """Проверка HTML кода"""
    result = {
        'syntax_valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': [],
        'score': 100
    }
    
    # Проверка синтаксиса
    if 'syntax' in check_types:
        syntax_issues = check_html_syntax(code)
        result['errors'].extend(syntax_issues['errors'])
        result['warnings'].extend(syntax_issues['warnings'])
        result['score'] -= len(syntax_issues['errors']) * 10
        result['score'] -= len(syntax_issues['warnings']) * 2
    
    # Проверка доступности
    if 'accessibility' in check_types:
        accessibility_issues = check_html_accessibility(code)
        result['warnings'].extend(accessibility_issues['warnings'])
        result['suggestions'].extend(accessibility_issues['suggestions'])
        result['score'] -= len(accessibility_issues['warnings']) * 3
    
    # Проверка SEO
    if 'seo' in check_types:
        seo_issues = check_html_seo(code)
        result['warnings'].extend(seo_issues['warnings'])
        result['suggestions'].extend(seo_issues['suggestions'])
        result['score'] -= len(seo_issues['warnings']) * 2
    
    result['score'] = max(0, result['score'])
    
    return result

def check_html_syntax(code):
    """Проверка синтаксиса HTML"""
    issues = {'errors': [], 'warnings': []}
    
    # Проверка тегов
    open_tags = re.findall(r'<([^/][^>]*)>', code)
    close_tags = re.findall(r'</([^>]*)>', code)
    
    # Проверка самозакрывающихся тегов
    self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link']
    
    # Проверка DOCTYPE
    if not code.strip().startswith('<!DOCTYPE'):
        issues['warnings'].append('Отсутствует DOCTYPE')
    
    # Проверка кодировки
    if 'charset' not in code:
        issues['warnings'].append('Не указана кодировка')
    
    return issues

def check_html_accessibility(code):
    """Проверка доступности HTML"""
    issues = {'warnings': [], 'suggestions': []}
    
    # Проверка alt атрибутов
    img_tags = re.findall(r'<img[^>]*>', code)
    for img in img_tags:
        if 'alt=' not in img:
            issues['warnings'].append('Изображения должны иметь alt атрибут')
    
    # Проверка заголовков
    if '<h1>' not in code:
        issues['warnings'].append('Страница должна содержать заголовок H1')
    
    # Проверка форм
    form_tags = re.findall(r'<form[^>]*>', code)
    for form in form_tags:
        if 'action=' not in form:
            issues['warnings'].append('Формы должны иметь action атрибут')
    
    return issues

def check_html_seo(code):
    """Проверка SEO HTML"""
    issues = {'warnings': [], 'suggestions': []}
    
    # Проверка title
    if '<title>' not in code:
        issues['warnings'].append('Отсутствует тег title')
    
    # Проверка meta description
    if 'name="description"' not in code:
        issues['warnings'].append('Отсутствует meta description')
    
    # Проверка заголовков
    h_tags = re.findall(r'<h[1-6][^>]*>', code)
    if len(h_tags) == 0:
        issues['warnings'].append('Отсутствуют заголовки')
    
    return issues

def check_css_code(code, check_types):
    """Проверка CSS кода"""
    result = {
        'syntax_valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': [],
        'score': 100
    }
    
    # Проверка синтаксиса
    if 'syntax' in check_types:
        syntax_issues = check_css_syntax(code)
        result['errors'].extend(syntax_issues['errors'])
        result['warnings'].extend(syntax_issues['warnings'])
        result['score'] -= len(syntax_issues['errors']) * 10
        result['score'] -= len(syntax_issues['warnings']) * 2
    
    # Проверка стиля
    if 'style' in check_types:
        style_issues = check_css_style(code)
        result['warnings'].extend(style_issues['warnings'])
        result['suggestions'].extend(style_issues['suggestions'])
        result['score'] -= len(style_issues['warnings']) * 2
    
    # Проверка производительности
    if 'performance' in check_types:
        performance_issues = check_css_performance(code)
        result['suggestions'].extend(performance_issues['suggestions'])
        result['score'] -= len(performance_issues['suggestions'])
    
    result['score'] = max(0, result['score'])
    
    return result

def check_css_syntax(code):
    """Проверка синтаксиса CSS"""
    issues = {'errors': [], 'warnings': []}
    
    # Проверка скобок
    open_braces = code.count('{')
    close_braces = code.count('}')
    if open_braces != close_braces:
        issues['errors'].append('Несоответствие фигурных скобок')
    
    # Проверка точек с запятой
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.endswith((';', '{', '}', ':', ',')) and ':' in line:
            issues['warnings'].append(f'Строка {i}: Возможно отсутствует точка с запятой')
    
    return issues

def check_css_style(code):
    """Проверка стиля CSS"""
    issues = {'warnings': [], 'suggestions': []}
    
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Проверка длины строки
        if len(line) > 120:
            issues['warnings'].append(f'Строка {i}: Слишком длинная строка ({len(line)} символов)')
        
        # Проверка отступов
        if line.strip() and not line.startswith((' ', '\t')) and not line.startswith(('@', '/*', '*', '}')):
            if i > 1 and lines[i-2].strip().endswith('{'):
                issues['warnings'].append(f'Строка {i}: Неправильный отступ')
    
    return issues

def check_css_performance(code):
    """Проверка производительности CSS"""
    issues = {'suggestions': []}
    
    # Проверка использования !important
    if '!important' in code:
        issues['suggestions'].append('Избегайте чрезмерного использования !important')
    
    # Проверка глубокой вложенности
    nesting_level = 0
    max_nesting = 0
    for char in code:
        if char == '{':
            nesting_level += 1
            max_nesting = max(max_nesting, nesting_level)
        elif char == '}':
            nesting_level -= 1
    
    if max_nesting > 4:
        issues['suggestions'].append('Избегайте глубокой вложенности селекторов')
    
    return issues

def calculate_code_metrics(code, language):
    """Расчет метрик кода"""
    metrics = {
        'lines_of_code': len([line for line in code.split('\n') if line.strip()]),
        'total_lines': len(code.split('\n')),
        'characters': len(code),
        'complexity': 0,
        'functions': 0,
        'classes': 0,
        'comments': 0
    }
    
    if language == 'python':
        metrics.update(calculate_python_metrics(code))
    elif language == 'javascript':
        metrics.update(calculate_javascript_metrics(code))
    elif language == 'java':
        metrics.update(calculate_java_metrics(code))
    elif language == 'html':
        metrics.update(calculate_html_metrics(code))
    elif language == 'css':
        metrics.update(calculate_css_metrics(code))
    
    return metrics

def calculate_python_metrics(code):
    """Расчет метрик Python кода"""
    metrics = {}
    
    # Количество функций
    metrics['functions'] = len(re.findall(r'def\s+\w+', code))
    
    # Количество классов
    metrics['classes'] = len(re.findall(r'class\s+\w+', code))
    
    # Количество комментариев
    metrics['comments'] = len(re.findall(r'#.*', code))
    
    # Цикломатическая сложность (упрощенная)
    complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with']
    metrics['complexity'] = sum(code.count(keyword) for keyword in complexity_keywords)
    
    return metrics

def calculate_javascript_metrics(code):
    """Расчет метрик JavaScript кода"""
    metrics = {}
    
    # Количество функций
    metrics['functions'] = len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(', code))
    
    # Количество классов
    metrics['classes'] = len(re.findall(r'class\s+\w+', code))
    
    # Количество комментариев
    metrics['comments'] = len(re.findall(r'//.*|/\*.*?\*/', code, re.DOTALL))
    
    # Цикломатическая сложность
    complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch', '&&', '||']
    metrics['complexity'] = sum(code.count(keyword) for keyword in complexity_keywords)
    
    return metrics

def calculate_java_metrics(code):
    """Расчет метрик Java кода"""
    metrics = {}
    
    # Количество методов
    metrics['functions'] = len(re.findall(r'public\s+\w+\s+\w+\s*\(|private\s+\w+\s+\w+\s*\(|protected\s+\w+\s+\w+\s*\(', code))
    
    # Количество классов
    metrics['classes'] = len(re.findall(r'class\s+\w+', code))
    
    # Количество комментариев
    metrics['comments'] = len(re.findall(r'//.*|/\*.*?\*/', code, re.DOTALL))
    
    # Цикломатическая сложность
    complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch', '&&', '||']
    metrics['complexity'] = sum(code.count(keyword) for keyword in complexity_keywords)
    
    return metrics

def calculate_html_metrics(code):
    """Расчет метрик HTML кода"""
    metrics = {}
    
    # Количество тегов
    metrics['tags'] = len(re.findall(r'<[^/][^>]*>', code))
    
    # Количество форм
    metrics['forms'] = len(re.findall(r'<form[^>]*>', code))
    
    # Количество изображений
    metrics['images'] = len(re.findall(r'<img[^>]*>', code))
    
    # Количество ссылок
    metrics['links'] = len(re.findall(r'<a[^>]*>', code))
    
    return metrics

def calculate_css_metrics(code):
    """Расчет метрик CSS кода"""
    metrics = {}
    
    # Количество селекторов
    metrics['selectors'] = len(re.findall(r'[^{]+\s*{', code))
    
    # Количество правил
    metrics['rules'] = len(re.findall(r'[^;]+;', code))
    
    # Количество медиа-запросов
    metrics['media_queries'] = len(re.findall(r'@media', code))
    
    return metrics
