from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import math
import json
from datetime import datetime

calculator_bp = Blueprint('calculator', __name__)

@calculator_bp.route('/api/calculator/calculate', methods=['POST'])
@login_required
def calculate():
    """Выполнение математических вычислений"""
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        angle_unit = data.get('angle_unit', 'degrees')  # degrees, radians
        
        if not expression:
            return jsonify({'error': 'Выражение не указано'}), 400
        
        # Безопасная оценка выражения
        result = evaluate_expression(expression, angle_unit)
        
        if result is None:
            return jsonify({'error': 'Недопустимое выражение'}), 400
        
        return jsonify({
            'expression': expression,
            'result': result,
            'angle_unit': angle_unit,
            'calculated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при вычислении'}), 500

@calculator_bp.route('/api/calculator/functions', methods=['GET'])
def get_calculator_functions():
    """Получение доступных функций калькулятора"""
    try:
        functions = {
            'basic': {
                'add': {'name': 'Сложение', 'symbol': '+', 'example': '2 + 3'},
                'subtract': {'name': 'Вычитание', 'symbol': '-', 'example': '5 - 2'},
                'multiply': {'name': 'Умножение', 'symbol': '*', 'example': '4 * 6'},
                'divide': {'name': 'Деление', 'symbol': '/', 'example': '8 / 2'},
                'power': {'name': 'Возведение в степень', 'symbol': '**', 'example': '2 ** 3'},
                'modulo': {'name': 'Остаток от деления', 'symbol': '%', 'example': '7 % 3'}
            },
            'trigonometric': {
                'sin': {'name': 'Синус', 'symbol': 'sin', 'example': 'sin(30)'},
                'cos': {'name': 'Косинус', 'symbol': 'cos', 'example': 'cos(45)'},
                'tan': {'name': 'Тангенс', 'symbol': 'tan', 'example': 'tan(60)'},
                'asin': {'name': 'Арксинус', 'symbol': 'asin', 'example': 'asin(0.5)'},
                'acos': {'name': 'Арккосинус', 'symbol': 'acos', 'example': 'acos(0.5)'},
                'atan': {'name': 'Арктангенс', 'symbol': 'atan', 'example': 'atan(1)'}
            },
            'logarithmic': {
                'log': {'name': 'Логарифм по основанию 10', 'symbol': 'log', 'example': 'log(100)'},
                'ln': {'name': 'Натуральный логарифм', 'symbol': 'ln', 'example': 'ln(e)'},
                'log2': {'name': 'Логарифм по основанию 2', 'symbol': 'log2', 'example': 'log2(8)'}
            },
            'exponential': {
                'exp': {'name': 'Экспонента', 'symbol': 'exp', 'example': 'exp(1)'},
                'sqrt': {'name': 'Квадратный корень', 'symbol': 'sqrt', 'example': 'sqrt(16)'},
                'cbrt': {'name': 'Кубический корень', 'symbol': 'cbrt', 'example': 'cbrt(27)'}
            },
            'statistical': {
                'factorial': {'name': 'Факториал', 'symbol': '!', 'example': '5!'},
                'abs': {'name': 'Абсолютное значение', 'symbol': 'abs', 'example': 'abs(-5)'},
                'ceil': {'name': 'Округление вверх', 'symbol': 'ceil', 'example': 'ceil(4.2)'},
                'floor': {'name': 'Округление вниз', 'symbol': 'floor', 'example': 'floor(4.8)'},
                'round': {'name': 'Округление', 'symbol': 'round', 'example': 'round(4.6)'}
            },
            'constants': {
                'pi': {'name': 'Число Пи', 'symbol': 'pi', 'value': math.pi},
                'e': {'name': 'Число Эйлера', 'symbol': 'e', 'value': math.e},
                'tau': {'name': 'Тау (2π)', 'symbol': 'tau', 'value': math.tau}
            }
        }
        
        return jsonify({'functions': functions})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении функций'}), 500

@calculator_bp.route('/api/calculator/convert', methods=['POST'])
@login_required
def convert_units():
    """Конвертация единиц измерения"""
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        from_unit = data.get('from_unit', '')
        to_unit = data.get('to_unit', '')
        category = data.get('category', 'length')  # length, weight, temperature, etc.
        
        if not from_unit or not to_unit:
            return jsonify({'error': 'Единицы измерения не указаны'}), 400
        
        # Конвертация
        result = convert_value(value, from_unit, to_unit, category)
        
        if result is None:
            return jsonify({'error': 'Неподдерживаемая конвертация'}), 400
        
        return jsonify({
            'value': value,
            'from_unit': from_unit,
            'to_unit': to_unit,
            'result': result,
            'category': category,
            'converted_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при конвертации'}), 500

@calculator_bp.route('/api/calculator/solve', methods=['POST'])
@login_required
def solve_equation():
    """Решение уравнений"""
    try:
        data = request.get_json()
        equation = data.get('equation', '')
        variable = data.get('variable', 'x')
        
        if not equation:
            return jsonify({'error': 'Уравнение не указано'}), 400
        
        # Решение уравнения
        solution = solve_linear_equation(equation, variable)
        
        if solution is None:
            return jsonify({'error': 'Не удалось решить уравнение'}), 400
        
        return jsonify({
            'equation': equation,
            'variable': variable,
            'solution': solution,
            'solved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при решении уравнения'}), 500

@calculator_bp.route('/api/calculator/graph', methods=['POST'])
@login_required
def generate_graph():
    """Генерация графика функции"""
    try:
        data = request.get_json()
        function = data.get('function', '')
        x_min = float(data.get('x_min', -10))
        x_max = float(data.get('x_max', 10))
        points = int(data.get('points', 100))
        
        if not function:
            return jsonify({'error': 'Функция не указана'}), 400
        
        # Генерация точек графика
        graph_data = generate_function_graph(function, x_min, x_max, points)
        
        if graph_data is None:
            return jsonify({'error': 'Не удалось построить график'}), 400
        
        return jsonify({
            'function': function,
            'x_min': x_min,
            'x_max': x_max,
            'points': points,
            'graph_data': graph_data,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при построении графика'}), 500

def evaluate_expression(expression, angle_unit):
    """Безопасная оценка математического выражения"""
    try:
        # Замена функций на безопасные версии
        safe_expression = make_expression_safe(expression, angle_unit)
        
        # Оценка выражения
        result = eval(safe_expression, {"__builtins__": {}}, {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log10,
            'ln': math.log,
            'log2': lambda x: math.log(x, 2),
            'exp': math.exp,
            'sqrt': math.sqrt,
            'cbrt': lambda x: x ** (1/3),
            'abs': abs,
            'ceil': math.ceil,
            'floor': math.floor,
            'round': round,
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'factorial': math.factorial
        })
        
        return result
        
    except Exception:
        return None

def make_expression_safe(expression, angle_unit):
    """Создание безопасного выражения"""
    # Замена угловых функций для работы с градусами
    if angle_unit == 'degrees':
        expression = expression.replace('sin(', 'sin(math.radians(')
        expression = expression.replace('cos(', 'cos(math.radians(')
        expression = expression.replace('tan(', 'tan(math.radians(')
        expression = expression.replace('asin(', 'math.degrees(asin(')
        expression = expression.replace('acos(', 'math.degrees(acos(')
        expression = expression.replace('atan(', 'math.degrees(atan(')
    
    # Замена факториала
    expression = expression.replace('!', 'factorial(')
    
    # Замена степеней
    expression = expression.replace('^', '**')
    
    return expression

def convert_value(value, from_unit, to_unit, category):
    """Конвертация единиц измерения"""
    conversion_factors = {
        'length': {
            'mm': 0.001, 'cm': 0.01, 'm': 1, 'km': 1000,
            'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mi': 1609.344
        },
        'weight': {
            'mg': 0.001, 'g': 1, 'kg': 1000, 't': 1000000,
            'oz': 28.3495, 'lb': 453.592, 'st': 6350.29
        },
        'temperature': {
            'c': 'celsius', 'f': 'fahrenheit', 'k': 'kelvin'
        },
        'area': {
            'mm²': 0.000001, 'cm²': 0.0001, 'm²': 1, 'km²': 1000000,
            'in²': 0.00064516, 'ft²': 0.092903, 'yd²': 0.836127, 'ac': 4046.86
        },
        'volume': {
            'ml': 0.001, 'l': 1, 'm³': 1000, 'cm³': 0.001,
            'in³': 0.0163871, 'ft³': 28.3168, 'gal': 3.78541
        }
    }
    
    if category not in conversion_factors:
        return None
    
    factors = conversion_factors[category]
    
    if category == 'temperature':
        return convert_temperature(value, from_unit, to_unit)
    
    if from_unit not in factors or to_unit not in factors:
        return None
    
    # Конвертация через метрическую систему
    base_value = value * factors[from_unit]
    result = base_value / factors[to_unit]
    
    return result

def convert_temperature(value, from_unit, to_unit):
    """Конвертация температуры"""
    # Конвертация в Цельсий
    if from_unit == 'f':
        celsius = (value - 32) * 5/9
    elif from_unit == 'k':
        celsius = value - 273.15
    else:  # celsius
        celsius = value
    
    # Конвертация из Цельсия
    if to_unit == 'f':
        return celsius * 9/5 + 32
    elif to_unit == 'k':
        return celsius + 273.15
    else:  # celsius
        return celsius

def solve_linear_equation(equation, variable):
    """Решение линейного уравнения"""
    try:
        # Простое решение для уравнений вида ax + b = 0
        equation = equation.replace(' ', '')
        
        # Поиск коэффициентов
        if '+' in equation:
            parts = equation.split('+')
            if len(parts) == 2:
                left, right = parts
                if variable in left:
                    # ax + b = 0 -> x = -b/a
                    a = float(left.replace(variable, '').replace('*', ''))
                    b = float(right)
                    return -b / a
                else:
                    # b + ax = 0 -> x = -b/a
                    b = float(left)
                    a = float(right.replace(variable, '').replace('*', ''))
                    return -b / a
        
        elif '-' in equation:
            parts = equation.split('-')
            if len(parts) == 2:
                left, right = parts
                if variable in left:
                    # ax - b = 0 -> x = b/a
                    a = float(left.replace(variable, '').replace('*', ''))
                    b = float(right)
                    return b / a
                else:
                    # b - ax = 0 -> x = b/a
                    b = float(left)
                    a = float(right.replace(variable, '').replace('*', ''))
                    return b / a
        
        return None
        
    except Exception:
        return None

def generate_function_graph(function, x_min, x_max, points):
    """Генерация графика функции"""
    try:
        x_values = []
        y_values = []
        
        step = (x_max - x_min) / points
        
        for i in range(points):
            x = x_min + i * step
            
            # Замена x в функции
            func_expr = function.replace('x', str(x))
            
            try:
                y = evaluate_expression(func_expr, 'radians')
                if y is not None and not (math.isnan(y) or math.isinf(y)):
                    x_values.append(round(x, 3))
                    y_values.append(round(y, 3))
            except:
                continue
        
        return {
            'x_values': x_values,
            'y_values': y_values,
            'points_count': len(x_values)
        }
        
    except Exception:
        return None

def get_calculator_history(user_id):
    """Получение истории вычислений пользователя"""
    # Здесь можно добавить сохранение истории в базу данных
    return []

def get_calculator_statistics(user_id):
    """Получение статистики использования калькулятора"""
    # Здесь можно добавить статистику использования
    return {
        'calculations_count': 0,
        'most_used_functions': [],
        'average_complexity': 0
    }

def get_calculator_tips():
    """Получение советов по использованию калькулятора"""
    tips = [
        "Используйте скобки для группировки операций",
        "Помните о порядке выполнения операций (PEMDAS)",
        "Для тригонометрических функций используйте правильные единицы измерения",
        "Проверяйте результат на разумность",
        "Используйте константы pi и e для точных вычислений",
        "Для сложных выражений разбивайте их на части",
        "Обращайте внимание на область определения функций",
        "Используйте научную нотацию для больших чисел"
    ]
    
    return tips
