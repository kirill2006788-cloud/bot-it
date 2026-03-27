from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import json
from datetime import datetime
import re

test_generator_bp = Blueprint('test_generator', __name__)

@test_generator_bp.route('/api/test/generate', methods=['POST'])
@login_required
def generate_tests():
    """Генерация тестов"""
    try:
        data = request.get_json()
        
        # Параметры тестов
        code = data.get('code', '')
        language = data.get('language', 'python').lower()
        test_framework = data.get('test_framework', 'pytest')  # pytest, unittest, jest, junit
        test_type = data.get('test_type', 'unit')  # unit, integration, e2e
        coverage_level = data.get('coverage_level', 'basic')  # basic, comprehensive, full
        
        if not code:
            return jsonify({'error': 'Код не предоставлен'}), 400
        
        # Генерация тестов
        if language == 'python':
            test_code = generate_python_tests(code, test_framework, test_type, coverage_level)
        elif language == 'javascript':
            test_code = generate_javascript_tests(code, test_framework, test_type, coverage_level)
        elif language == 'java':
            test_code = generate_java_tests(code, test_framework, test_type, coverage_level)
        else:
            return jsonify({'error': 'Неподдерживаемый язык программирования'}), 400
        
        return jsonify({
            'test_code': test_code,
            'language': language,
            'test_framework': test_framework,
            'test_type': test_type,
            'coverage_level': coverage_level,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации тестов'}), 500

@test_generator_bp.route('/api/test/frameworks', methods=['GET'])
def get_test_frameworks():
    """Получение поддерживаемых фреймворков тестирования"""
    try:
        frameworks = {
            'python': {
                'pytest': {
                    'name': 'pytest',
                    'description': 'Современный фреймворк для тестирования Python',
                    'features': ['Простой синтаксис', 'Фикстуры', 'Параметризация', 'Плагины']
                },
                'unittest': {
                    'name': 'unittest',
                    'description': 'Встроенный модуль тестирования Python',
                    'features': ['Стандартная библиотека', 'JUnit-стиль', 'Автоматическое обнаружение']
                }
            },
            'javascript': {
                'jest': {
                    'name': 'Jest',
                    'description': 'Фреймворк тестирования JavaScript от Facebook',
                    'features': ['Автоматическое обнаружение', 'Моки', 'Снапшоты', 'Покрытие кода']
                },
                'mocha': {
                    'name': 'Mocha',
                    'description': 'Гибкий фреймворк тестирования JavaScript',
                    'features': ['Асинхронное тестирование', 'Гибкость', 'Поддержка браузеров']
                }
            },
            'java': {
                'junit': {
                    'name': 'JUnit',
                    'description': 'Стандартный фреймворк тестирования Java',
                    'features': ['Аннотации', 'Утверждения', 'Параметризация', 'Правила']
                },
                'testng': {
                    'name': 'TestNG',
                    'description': 'Продвинутый фреймворк тестирования Java',
                    'features': ['Группы тестов', 'Параметризация', 'Зависимости', 'Отчеты']
                }
            }
        }
        
        return jsonify({'frameworks': frameworks})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении фреймворков'}), 500

@test_generator_bp.route('/api/test/templates', methods=['GET'])
def get_test_templates():
    """Получение шаблонов тестов"""
    try:
        templates = {
            'python': {
                'function_test': {
                    'name': 'Тест функции',
                    'description': 'Базовый тест для функции',
                    'template': '''def test_{function_name}():
    """Тест функции {function_name}"""
    # Arrange
    input_data = "test_input"
    expected_output = "expected_result"
    
    # Act
    result = {function_name}(input_data)
    
    # Assert
    assert result == expected_output'''
                },
                'class_test': {
                    'name': 'Тест класса',
                    'description': 'Тест для класса и его методов',
                    'template': '''class Test{ClassName}:
    """Тесты для класса {ClassName}"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.instance = {ClassName}()
    
    def test_{method_name}(self):
        """Тест метода {method_name}"""
        # Arrange
        input_data = "test_input"
        expected_output = "expected_result"
        
        # Act
        result = self.instance.{method_name}(input_data)
        
        # Assert
        assert result == expected_output'''
                }
            },
            'javascript': {
                'function_test': {
                    'name': 'Тест функции',
                    'description': 'Базовый тест для функции',
                    'template': '''describe('{function_name}', () => {{
    test('should return expected result', () => {{
        // Arrange
        const input = 'test_input';
        const expected = 'expected_result';
        
        // Act
        const result = {function_name}(input);
        
        // Assert
        expect(result).toBe(expected);
    }});
}});'''
                }
            },
            'java': {
                'method_test': {
                    'name': 'Тест метода',
                    'description': 'Тест для метода класса',
                    'template': '''@Test
public void test{MethodName}() {{
    // Arrange
    {ClassName} instance = new {ClassName}();
    String input = "test_input";
    String expected = "expected_result";
    
    // Act
    String result = instance.{methodName}(input);
    
    // Assert
    assertEquals(expected, result);
}}'''
                }
            }
        }
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении шаблонов'}), 500

def generate_python_tests(code, test_framework, test_type, coverage_level):
    """Генерация Python тестов"""
    test_code = []
    
    # Импорты
    if test_framework == 'pytest':
        test_code.append('import pytest')
    else:
        test_code.append('import unittest')
    
    test_code.append('')
    
    # Анализ кода для извлечения функций и классов
    functions = extract_python_functions(code)
    classes = extract_python_classes(code)
    
    # Генерация тестов для функций
    for func in functions:
        test_code.extend(generate_python_function_tests(func, test_framework, coverage_level))
        test_code.append('')
    
    # Генерация тестов для классов
    for cls in classes:
        test_code.extend(generate_python_class_tests(cls, test_framework, coverage_level))
        test_code.append('')
    
    return '\n'.join(test_code)

def generate_python_function_tests(func, test_framework, coverage_level):
    """Генерация тестов для Python функции"""
    tests = []
    
    if test_framework == 'pytest':
        tests.append(f'def test_{func["name"]}():')
        tests.append(f'    """Тест функции {func["name"]}"""')
        
        # Базовые тесты
        tests.append('    # Тест с валидными данными')
        tests.append(f'    result = {func["name"]}("test_input")')
        tests.append('    assert result is not None')
        tests.append('')
        
        # Тест с None
        if coverage_level in ['comprehensive', 'full']:
            tests.append('    # Тест с None')
            tests.append(f'    result = {func["name"]}(None)')
            tests.append('    # Добавьте проверку для None')
            tests.append('')
        
        # Тест с пустой строкой
        if coverage_level in ['comprehensive', 'full']:
            tests.append('    # Тест с пустой строкой')
            tests.append(f'    result = {func["name"]}("")')
            tests.append('    # Добавьте проверку для пустой строки')
            tests.append('')
        
        # Тест с исключением
        if coverage_level == 'full':
            tests.append('    # Тест с исключением')
            tests.append(f'    with pytest.raises(Exception):')
            tests.append(f'        {func["name"]}("invalid_input")')
    
    else:  # unittest
        tests.append(f'class Test{func["name"].title()}(unittest.TestCase):')
        tests.append(f'    """Тесты для функции {func["name"]}"""')
        tests.append('')
        tests.append('    def test_valid_input(self):')
        tests.append(f'        """Тест с валидными данными"""')
        tests.append(f'        result = {func["name"]}("test_input")')
        tests.append('        self.assertIsNotNone(result)')
        tests.append('')
        
        if coverage_level in ['comprehensive', 'full']:
            tests.append('    def test_none_input(self):')
            tests.append(f'        """Тест с None"""')
            tests.append(f'        result = {func["name"]}(None)')
            tests.append('        # Добавьте проверку для None')
            tests.append('')
    
    return tests

def generate_python_class_tests(cls, test_framework, coverage_level):
    """Генерация тестов для Python класса"""
    tests = []
    
    if test_framework == 'pytest':
        tests.append(f'class Test{cls["name"]}:')
        tests.append(f'    """Тесты для класса {cls["name"]}"""')
        tests.append('')
        tests.append('    def setup_method(self):')
        tests.append(f'        """Настройка перед каждым тестом"""')
        tests.append(f'        self.instance = {cls["name"]}()')
        tests.append('')
        
        # Тесты для методов
        for method in cls.get('methods', []):
            tests.append(f'    def test_{method["name"]}(self):')
            tests.append(f'        """Тест метода {method["name"]}"""')
            tests.append(f'        result = self.instance.{method["name"]}("test_input")')
            tests.append('        assert result is not None')
            tests.append('')
    
    else:  # unittest
        tests.append(f'class Test{cls["name"]}(unittest.TestCase):')
        tests.append(f'    """Тесты для класса {cls["name"]}"""')
        tests.append('')
        tests.append('    def setUp(self):')
        tests.append(f'        """Настройка перед каждым тестом"""')
        tests.append(f'        self.instance = {cls["name"]}()')
        tests.append('')
        
        # Тесты для методов
        for method in cls.get('methods', []):
            tests.append(f'    def test_{method["name"]}(self):')
            tests.append(f'        """Тест метода {method["name"]}"""')
            tests.append(f'        result = self.instance.{method["name"]}("test_input")')
            tests.append('        self.assertIsNotNone(result)')
            tests.append('')
    
    return tests

def generate_javascript_tests(code, test_framework, test_type, coverage_level):
    """Генерация JavaScript тестов"""
    test_code = []
    
    # Импорты
    if test_framework == 'jest':
        test_code.append('// Jest тесты')
    else:
        test_code.append('// Mocha тесты')
        test_code.append('const assert = require("assert");')
    
    test_code.append('')
    
    # Анализ кода для извлечения функций и классов
    functions = extract_javascript_functions(code)
    classes = extract_javascript_classes(code)
    
    # Генерация тестов для функций
    for func in functions:
        test_code.extend(generate_javascript_function_tests(func, test_framework, coverage_level))
        test_code.append('')
    
    # Генерация тестов для классов
    for cls in classes:
        test_code.extend(generate_javascript_class_tests(cls, test_framework, coverage_level))
        test_code.append('')
    
    return '\n'.join(test_code)

def generate_javascript_function_tests(func, test_framework, coverage_level):
    """Генерация тестов для JavaScript функции"""
    tests = []
    
    if test_framework == 'jest':
        tests.append(f'describe("{func["name"]}", () => {{')
        tests.append('    test("should return expected result", () => {')
        tests.append('        // Arrange')
        tests.append('        const input = "test_input";')
        tests.append('        const expected = "expected_result";')
        tests.append('')
        tests.append('        // Act')
        tests.append(f'        const result = {func["name"]}(input);')
        tests.append('')
        tests.append('        // Assert')
        tests.append('        expect(result).toBe(expected);')
        tests.append('    });')
        
        if coverage_level in ['comprehensive', 'full']:
            tests.append('')
            tests.append('    test("should handle null input", () => {')
            tests.append(f'        const result = {func["name"]}(null);')
            tests.append('        // Добавьте проверку для null')
            tests.append('    });')
        
        tests.append('});')
    
    else:  # Mocha
        tests.append(f'describe("{func["name"]}", function() {{')
        tests.append('    it("should return expected result", function() {')
        tests.append('        // Arrange')
        tests.append('        const input = "test_input";')
        tests.append('        const expected = "expected_result";')
        tests.append('')
        tests.append('        // Act')
        tests.append(f'        const result = {func["name"]}(input);')
        tests.append('')
        tests.append('        // Assert')
        tests.append('        assert.strictEqual(result, expected);')
        tests.append('    });')
        tests.append('});')
    
    return tests

def generate_javascript_class_tests(cls, test_framework, coverage_level):
    """Генерация тестов для JavaScript класса"""
    tests = []
    
    if test_framework == 'jest':
        tests.append(f'describe("{cls["name"]}", () => {{')
        tests.append('    let instance;')
        tests.append('')
        tests.append('    beforeEach(() => {')
        tests.append(f'        instance = new {cls["name"]}();')
        tests.append('    });')
        tests.append('')
        
        # Тесты для методов
        for method in cls.get('methods', []):
            tests.append(f'    describe("{method["name"]}", () => {{')
            tests.append('        test("should work correctly", () => {')
            tests.append('            // Arrange')
            tests.append('            const input = "test_input";')
            tests.append('')
            tests.append('            // Act')
            tests.append(f'            const result = instance.{method["name"]}(input);')
            tests.append('')
            tests.append('            // Assert')
            tests.append('            expect(result).toBeDefined();')
            tests.append('        });')
            tests.append('    });')
            tests.append('')
        
        tests.append('});')
    
    else:  # Mocha
        tests.append(f'describe("{cls["name"]}", function() {{')
        tests.append('    let instance;')
        tests.append('')
        tests.append('    beforeEach(function() {')
        tests.append(f'        instance = new {cls["name"]}();')
        tests.append('    });')
        tests.append('')
        
        # Тесты для методов
        for method in cls.get('methods', []):
            tests.append(f'    describe("{method["name"]}", function() {{')
            tests.append('        it("should work correctly", function() {')
            tests.append('            // Arrange')
            tests.append('            const input = "test_input";')
            tests.append('')
            tests.append('            // Act')
            tests.append(f'            const result = instance.{method["name"]}(input);')
            tests.append('')
            tests.append('            // Assert')
            tests.append('            assert.ok(result);')
            tests.append('        });')
            tests.append('    });')
            tests.append('')
        
        tests.append('});')
    
    return tests

def generate_java_tests(code, test_framework, test_type, coverage_level):
    """Генерация Java тестов"""
    test_code = []
    
    # Импорты
    if test_framework == 'junit':
        test_code.append('import org.junit.Test;')
        test_code.append('import org.junit.Before;')
        test_code.append('import static org.junit.Assert.*;')
    else:  # TestNG
        test_code.append('import org.testng.annotations.Test;')
        test_code.append('import org.testng.annotations.BeforeMethod;')
        test_code.append('import static org.testng.Assert.*;')
    
    test_code.append('')
    
    # Анализ кода для извлечения классов
    classes = extract_java_classes(code)
    
    # Генерация тестов для классов
    for cls in classes:
        test_code.extend(generate_java_class_tests(cls, test_framework, coverage_level))
        test_code.append('')
    
    return '\n'.join(test_code)

def generate_java_class_tests(cls, test_framework, coverage_level):
    """Генерация тестов для Java класса"""
    tests = []
    
    if test_framework == 'junit':
        tests.append(f'public class Test{cls["name"]} {{')
        tests.append('')
        tests.append(f'    private {cls["name"]} instance;')
        tests.append('')
        tests.append('    @Before')
        tests.append('    public void setUp() {')
        tests.append(f'        instance = new {cls["name"]}();')
        tests.append('    }')
        tests.append('')
        
        # Тесты для методов
        for method in cls.get('methods', []):
            tests.append(f'    @Test')
            tests.append(f'    public void test{method["name"].title()}() {{')
            tests.append('        // Arrange')
            tests.append('        String input = "test_input";')
            tests.append('        String expected = "expected_result";')
            tests.append('')
            tests.append('        // Act')
            tests.append(f'        String result = instance.{method["name"]}(input);')
            tests.append('')
            tests.append('        // Assert')
            tests.append('        assertEquals(expected, result);')
            tests.append('    }')
            tests.append('')
        
        tests.append('}')
    
    else:  # TestNG
        tests.append(f'public class Test{cls["name"]} {{')
        tests.append('')
        tests.append(f'    private {cls["name"]} instance;')
        tests.append('')
        tests.append('    @BeforeMethod')
        tests.append('    public void setUp() {')
        tests.append(f'        instance = new {cls["name"]}();')
        tests.append('    }')
        tests.append('')
        
        # Тесты для методов
        for method in cls.get('methods', []):
            tests.append(f'    @Test')
            tests.append(f'    public void test{method["name"].title()}() {{')
            tests.append('        // Arrange')
            tests.append('        String input = "test_input";')
            tests.append('        String expected = "expected_result";')
            tests.append('')
            tests.append('        // Act')
            tests.append(f'        String result = instance.{method["name"]}(input);')
            tests.append('')
            tests.append('        // Assert')
            tests.append('        assertEquals(expected, result);')
            tests.append('    }')
            tests.append('')
        
        tests.append('}')
    
    return tests

def extract_python_functions(code):
    """Извлечение функций из Python кода"""
    functions = []
    
    # Поиск определений функций
    function_pattern = r'def\s+(\w+)\s*\('
    matches = re.finditer(function_pattern, code)
    
    for match in matches:
        function_name = match.group(1)
        functions.append({
            'name': function_name,
            'type': 'function'
        })
    
    return functions

def extract_python_classes(code):
    """Извлечение классов из Python кода"""
    classes = []
    
    # Поиск определений классов
    class_pattern = r'class\s+(\w+)\s*[\(:]'
    matches = re.finditer(class_pattern, code)
    
    for match in matches:
        class_name = match.group(1)
        
        # Поиск методов в классе
        methods = []
        method_pattern = r'def\s+(\w+)\s*\('
        method_matches = re.finditer(method_pattern, code)
        
        for method_match in method_matches:
            method_name = method_match.group(1)
            if method_name != '__init__':
                methods.append({
                    'name': method_name,
                    'type': 'method'
                })
        
        classes.append({
            'name': class_name,
            'type': 'class',
            'methods': methods
        })
    
    return classes

def extract_javascript_functions(code):
    """Извлечение функций из JavaScript кода"""
    functions = []
    
    # Поиск определений функций
    function_patterns = [
        r'function\s+(\w+)\s*\(',
        r'const\s+(\w+)\s*=\s*\(',
        r'let\s+(\w+)\s*=\s*\(',
        r'var\s+(\w+)\s*=\s*\('
    ]
    
    for pattern in function_patterns:
        matches = re.finditer(pattern, code)
        for match in matches:
            function_name = match.group(1)
            functions.append({
                'name': function_name,
                'type': 'function'
            })
    
    return functions

def extract_javascript_classes(code):
    """Извлечение классов из JavaScript кода"""
    classes = []
    
    # Поиск определений классов
    class_pattern = r'class\s+(\w+)\s*[\(\{]'
    matches = re.finditer(class_pattern, code)
    
    for match in matches:
        class_name = match.group(1)
        
        # Поиск методов в классе
        methods = []
        method_pattern = r'(\w+)\s*\([^)]*\)\s*\{'
        method_matches = re.finditer(method_pattern, code)
        
        for method_match in method_matches:
            method_name = method_match.group(1)
            if method_name not in ['constructor', 'if', 'for', 'while']:
                methods.append({
                    'name': method_name,
                    'type': 'method'
                })
        
        classes.append({
            'name': class_name,
            'type': 'class',
            'methods': methods
        })
    
    return classes

def extract_java_classes(code):
    """Извлечение классов из Java кода"""
    classes = []
    
    # Поиск определений классов
    class_pattern = r'public\s+class\s+(\w+)\s*[\(\{]'
    matches = re.finditer(class_pattern, code)
    
    for match in matches:
        class_name = match.group(1)
        
        # Поиск методов в классе
        methods = []
        method_pattern = r'public\s+\w+\s+(\w+)\s*\('
        method_matches = re.finditer(method_pattern, code)
        
        for method_match in method_matches:
            method_name = method_match.group(1)
            if method_name != 'main':
                methods.append({
                    'name': method_name,
                    'type': 'method'
                })
        
        classes.append({
            'name': class_name,
            'type': 'class',
            'methods': methods
        })
    
    return classes

def generate_test_configuration(language, test_framework):
    """Генерация конфигурации тестов"""
    configs = {
        'python': {
            'pytest': {
                'pytest.ini': '''[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
'''
            },
            'unittest': {
                'requirements.txt': 'unittest2'
            }
        },
        'javascript': {
            'jest': {
                'package.json': '''{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "jest": "^27.0.0"
  }
}'''
            },
            'mocha': {
                'package.json': '''{
  "scripts": {
    "test": "mocha",
    "test:watch": "mocha --watch"
  },
  "devDependencies": {
    "mocha": "^9.0.0",
    "chai": "^4.0.0"
  }
}'''
            }
        },
        'java': {
            'junit': {
                'pom.xml': '''<dependency>
    <groupId>junit</groupId>
    <artifactId>junit</artifactId>
    <version>4.13.2</version>
    <scope>test</scope>
</dependency>'''
            },
            'testng': {
                'pom.xml': '''<dependency>
    <groupId>org.testng</groupId>
    <artifactId>testng</artifactId>
    <version>7.4.0</version>
    <scope>test</scope>
</dependency>'''
            }
        }
    }
    
    return configs.get(language, {}).get(test_framework, {})
