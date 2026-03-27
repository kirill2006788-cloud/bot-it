from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime

unit_converter_bp = Blueprint('unit_converter', __name__)

# Определения единиц измерения
UNIT_DEFINITIONS = {
    'length': {
        'name': 'Длина',
        'units': {
            'mm': {'name': 'Миллиметр', 'factor': 0.001, 'symbol': 'мм'},
            'cm': {'name': 'Сантиметр', 'factor': 0.01, 'symbol': 'см'},
            'm': {'name': 'Метр', 'factor': 1, 'symbol': 'м'},
            'km': {'name': 'Километр', 'factor': 1000, 'symbol': 'км'},
            'in': {'name': 'Дюйм', 'factor': 0.0254, 'symbol': 'дюйм'},
            'ft': {'name': 'Фут', 'factor': 0.3048, 'symbol': 'фут'},
            'yd': {'name': 'Ярд', 'factor': 0.9144, 'symbol': 'ярд'},
            'mi': {'name': 'Мили', 'factor': 1609.344, 'symbol': 'мили'},
            'nm': {'name': 'Морская миля', 'factor': 1852, 'symbol': 'нм'},
            'au': {'name': 'Астрономическая единица', 'factor': 149597870700, 'symbol': 'а.е.'},
            'ly': {'name': 'Световой год', 'factor': 9460730472580800, 'symbol': 'св.г.'}
        }
    },
    'weight': {
        'name': 'Вес/Масса',
        'units': {
            'mg': {'name': 'Миллиграмм', 'factor': 0.001, 'symbol': 'мг'},
            'g': {'name': 'Грамм', 'factor': 1, 'symbol': 'г'},
            'kg': {'name': 'Килограмм', 'factor': 1000, 'symbol': 'кг'},
            't': {'name': 'Тонна', 'factor': 1000000, 'symbol': 'т'},
            'oz': {'name': 'Унция', 'factor': 28.3495, 'symbol': 'унция'},
            'lb': {'name': 'Фунт', 'factor': 453.592, 'symbol': 'фунт'},
            'st': {'name': 'Стоун', 'factor': 6350.29, 'symbol': 'ст'},
            'ct': {'name': 'Карат', 'factor': 0.2, 'symbol': 'кар'},
            'gr': {'name': 'Гран', 'factor': 0.0647989, 'symbol': 'гран'}
        }
    },
    'temperature': {
        'name': 'Температура',
        'units': {
            'c': {'name': 'Цельсий', 'symbol': '°C'},
            'f': {'name': 'Фаренгейт', 'symbol': '°F'},
            'k': {'name': 'Кельвин', 'symbol': 'K'},
            'r': {'name': 'Ранкин', 'symbol': '°R'}
        }
    },
    'area': {
        'name': 'Площадь',
        'units': {
            'mm²': {'name': 'Квадратный миллиметр', 'factor': 0.000001, 'symbol': 'мм²'},
            'cm²': {'name': 'Квадратный сантиметр', 'factor': 0.0001, 'symbol': 'см²'},
            'm²': {'name': 'Квадратный метр', 'factor': 1, 'symbol': 'м²'},
            'km²': {'name': 'Квадратный километр', 'factor': 1000000, 'symbol': 'км²'},
            'in²': {'name': 'Квадратный дюйм', 'factor': 0.00064516, 'symbol': 'дюйм²'},
            'ft²': {'name': 'Квадратный фут', 'factor': 0.092903, 'symbol': 'фут²'},
            'yd²': {'name': 'Квадратный ярд', 'factor': 0.836127, 'symbol': 'ярд²'},
            'ac': {'name': 'Акр', 'factor': 4046.86, 'symbol': 'акр'},
            'ha': {'name': 'Гектар', 'factor': 10000, 'symbol': 'га'}
        }
    },
    'volume': {
        'name': 'Объем',
        'units': {
            'ml': {'name': 'Миллилитр', 'factor': 0.001, 'symbol': 'мл'},
            'l': {'name': 'Литр', 'factor': 1, 'symbol': 'л'},
            'm³': {'name': 'Кубический метр', 'factor': 1000, 'symbol': 'м³'},
            'cm³': {'name': 'Кубический сантиметр', 'factor': 0.001, 'symbol': 'см³'},
            'in³': {'name': 'Кубический дюйм', 'factor': 0.0163871, 'symbol': 'дюйм³'},
            'ft³': {'name': 'Кубический фут', 'factor': 28.3168, 'symbol': 'фут³'},
            'gal': {'name': 'Галлон (US)', 'factor': 3.78541, 'symbol': 'гал'},
            'qt': {'name': 'Кварта', 'factor': 0.946353, 'symbol': 'кварта'},
            'pt': {'name': 'Пинта', 'factor': 0.473176, 'symbol': 'пинта'},
            'cup': {'name': 'Чашка', 'factor': 0.236588, 'symbol': 'чашка'},
            'fl_oz': {'name': 'Жидкая унция', 'factor': 0.0295735, 'symbol': 'фл.унция'}
        }
    },
    'time': {
        'name': 'Время',
        'units': {
            'ns': {'name': 'Наносекунда', 'factor': 0.000000001, 'symbol': 'нс'},
            'μs': {'name': 'Микросекунда', 'factor': 0.000001, 'symbol': 'мкс'},
            'ms': {'name': 'Миллисекунда', 'factor': 0.001, 'symbol': 'мс'},
            's': {'name': 'Секунда', 'factor': 1, 'symbol': 'с'},
            'min': {'name': 'Минута', 'factor': 60, 'symbol': 'мин'},
            'h': {'name': 'Час', 'factor': 3600, 'symbol': 'ч'},
            'd': {'name': 'День', 'factor': 86400, 'symbol': 'д'},
            'wk': {'name': 'Неделя', 'factor': 604800, 'symbol': 'нед'},
            'mo': {'name': 'Месяц', 'factor': 2629746, 'symbol': 'мес'},
            'yr': {'name': 'Год', 'factor': 31556952, 'symbol': 'г'}
        }
    },
    'speed': {
        'name': 'Скорость',
        'units': {
            'm/s': {'name': 'Метр в секунду', 'factor': 1, 'symbol': 'м/с'},
            'km/h': {'name': 'Километр в час', 'factor': 0.277778, 'symbol': 'км/ч'},
            'mph': {'name': 'Мили в час', 'factor': 0.44704, 'symbol': 'миль/ч'},
            'ft/s': {'name': 'Фут в секунду', 'factor': 0.3048, 'symbol': 'фут/с'},
            'knot': {'name': 'Узел', 'factor': 0.514444, 'symbol': 'уз'},
            'c': {'name': 'Скорость света', 'factor': 299792458, 'symbol': 'c'}
        }
    },
    'pressure': {
        'name': 'Давление',
        'units': {
            'pa': {'name': 'Паскаль', 'factor': 1, 'symbol': 'Па'},
            'kpa': {'name': 'Килопаскаль', 'factor': 1000, 'symbol': 'кПа'},
            'mpa': {'name': 'Мегапаскаль', 'factor': 1000000, 'symbol': 'МПа'},
            'bar': {'name': 'Бар', 'factor': 100000, 'symbol': 'бар'},
            'atm': {'name': 'Атмосфера', 'factor': 101325, 'symbol': 'атм'},
            'psi': {'name': 'Фунт на квадратный дюйм', 'factor': 6894.76, 'symbol': 'psi'},
            'torr': {'name': 'Торр', 'factor': 133.322, 'symbol': 'торр'},
            'mmhg': {'name': 'Миллиметр ртутного столба', 'factor': 133.322, 'symbol': 'мм рт.ст.'}
        }
    },
    'energy': {
        'name': 'Энергия',
        'units': {
            'j': {'name': 'Джоуль', 'factor': 1, 'symbol': 'Дж'},
            'kj': {'name': 'Килоджоуль', 'factor': 1000, 'symbol': 'кДж'},
            'mj': {'name': 'Мегаджоуль', 'factor': 1000000, 'symbol': 'МДж'},
            'cal': {'name': 'Калория', 'factor': 4.184, 'symbol': 'кал'},
            'kcal': {'name': 'Килокалория', 'factor': 4184, 'symbol': 'ккал'},
            'wh': {'name': 'Ватт-час', 'factor': 3600, 'symbol': 'Вт·ч'},
            'kwh': {'name': 'Киловатт-час', 'factor': 3600000, 'symbol': 'кВт·ч'},
            'btu': {'name': 'Британская тепловая единица', 'factor': 1055.06, 'symbol': 'БТЕ'},
            'ev': {'name': 'Электрон-вольт', 'factor': 1.602176634e-19, 'symbol': 'эВ'}
        }
    },
    'power': {
        'name': 'Мощность',
        'units': {
            'w': {'name': 'Ватт', 'factor': 1, 'symbol': 'Вт'},
            'kw': {'name': 'Киловатт', 'factor': 1000, 'symbol': 'кВт'},
            'mw': {'name': 'Мегаватт', 'factor': 1000000, 'symbol': 'МВт'},
            'gw': {'name': 'Гигаватт', 'factor': 1000000000, 'symbol': 'ГВт'},
            'hp': {'name': 'Лошадиная сила', 'factor': 745.7, 'symbol': 'л.с.'},
            'btu/h': {'name': 'БТЕ в час', 'factor': 0.293071, 'symbol': 'БТЕ/ч'},
            'cal/s': {'name': 'Калория в секунду', 'factor': 4.184, 'symbol': 'кал/с'}
        }
    }
}

@unit_converter_bp.route('/api/units/convert', methods=['POST'])
@login_required
def convert_units():
    """Конвертация единиц измерения"""
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        from_unit = data.get('from_unit', '')
        to_unit = data.get('to_unit', '')
        category = data.get('category', 'length')
        
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

@unit_converter_bp.route('/api/units/categories', methods=['GET'])
def get_unit_categories():
    """Получение категорий единиц измерения"""
    try:
        categories = {}
        for category, info in UNIT_DEFINITIONS.items():
            categories[category] = {
                'name': info['name'],
                'units_count': len(info['units'])
            }
        
        return jsonify({'categories': categories})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении категорий'}), 500

@unit_converter_bp.route('/api/units/<category>', methods=['GET'])
def get_units_by_category(category):
    """Получение единиц измерения по категории"""
    try:
        if category not in UNIT_DEFINITIONS:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        units_info = UNIT_DEFINITIONS[category]
        
        return jsonify({
            'category': category,
            'name': units_info['name'],
            'units': units_info['units']
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении единиц'}), 500

@unit_converter_bp.route('/api/units/batch-convert', methods=['POST'])
@login_required
def batch_convert_units():
    """Пакетная конвертация единиц"""
    try:
        data = request.get_json()
        conversions = data.get('conversions', [])
        
        if not conversions or len(conversions) > 10:
            return jsonify({'error': 'Укажите от 1 до 10 конвертаций'}), 400
        
        results = []
        
        for conversion in conversions:
            value = float(conversion.get('value', 0))
            from_unit = conversion.get('from_unit', '')
            to_unit = conversion.get('to_unit', '')
            category = conversion.get('category', 'length')
            
            result = convert_value(value, from_unit, to_unit, category)
            
            results.append({
                'value': value,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'result': result,
                'category': category,
                'success': result is not None
            })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'converted_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при пакетной конвертации'}), 500

@unit_converter_bp.route('/api/units/compare', methods=['POST'])
@login_required
def compare_units():
    """Сравнение единиц измерения"""
    try:
        data = request.get_json()
        value1 = float(data.get('value1', 0))
        unit1 = data.get('unit1', '')
        value2 = float(data.get('value2', 0))
        unit2 = data.get('unit2', '')
        category = data.get('category', 'length')
        
        if not unit1 or not unit2:
            return jsonify({'error': 'Единицы измерения не указаны'}), 400
        
        # Конвертация в базовую единицу
        base_value1 = convert_to_base(value1, unit1, category)
        base_value2 = convert_to_base(value2, unit2, category)
        
        if base_value1 is None or base_value2 is None:
            return jsonify({'error': 'Неподдерживаемая конвертация'}), 400
        
        # Сравнение
        comparison = compare_values(base_value1, base_value2)
        
        return jsonify({
            'value1': value1,
            'unit1': unit1,
            'value2': value2,
            'unit2': unit2,
            'base_value1': base_value1,
            'base_value2': base_value2,
            'comparison': comparison,
            'category': category,
            'compared_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при сравнении единиц'}), 500

def convert_value(value, from_unit, to_unit, category):
    """Конвертация значения между единицами"""
    if category == 'temperature':
        return convert_temperature(value, from_unit, to_unit)
    
    if category not in UNIT_DEFINITIONS:
        return None
    
    units = UNIT_DEFINITIONS[category]['units']
    
    if from_unit not in units or to_unit not in units:
        return None
    
    # Конвертация через базовую единицу
    base_value = convert_to_base(value, from_unit, category)
    if base_value is None:
        return None
    
    result = convert_from_base(base_value, to_unit, category)
    return result

def convert_to_base(value, unit, category):
    """Конвертация в базовую единицу"""
    if category == 'temperature':
        return convert_temperature_to_celsius(value, unit)
    
    if category not in UNIT_DEFINITIONS:
        return None
    
    units = UNIT_DEFINITIONS[category]['units']
    
    if unit not in units:
        return None
    
    factor = units[unit]['factor']
    return value * factor

def convert_from_base(base_value, unit, category):
    """Конвертация из базовой единицы"""
    if category == 'temperature':
        return convert_temperature_from_celsius(base_value, unit)
    
    if category not in UNIT_DEFINITIONS:
        return None
    
    units = UNIT_DEFINITIONS[category]['units']
    
    if unit not in units:
        return None
    
    factor = units[unit]['factor']
    return base_value / factor

def convert_temperature(value, from_unit, to_unit):
    """Конвертация температуры"""
    # Конвертация в Цельсий
    celsius = convert_temperature_to_celsius(value, from_unit)
    if celsius is None:
        return None
    
    # Конвертация из Цельсия
    return convert_temperature_from_celsius(celsius, to_unit)

def convert_temperature_to_celsius(value, unit):
    """Конвертация температуры в Цельсий"""
    if unit == 'c':
        return value
    elif unit == 'f':
        return (value - 32) * 5/9
    elif unit == 'k':
        return value - 273.15
    elif unit == 'r':
        return (value - 491.67) * 5/9
    else:
        return None

def convert_temperature_from_celsius(celsius, unit):
    """Конвертация температуры из Цельсия"""
    if unit == 'c':
        return celsius
    elif unit == 'f':
        return celsius * 9/5 + 32
    elif unit == 'k':
        return celsius + 273.15
    elif unit == 'r':
        return celsius * 9/5 + 491.67
    else:
        return None

def compare_values(value1, value2):
    """Сравнение значений"""
    if value1 > value2:
        return {
            'result': 'greater',
            'difference': value1 - value2,
            'ratio': value1 / value2,
            'message': f'Первое значение больше второго на {value1 - value2:.6f}'
        }
    elif value1 < value2:
        return {
            'result': 'less',
            'difference': value2 - value1,
            'ratio': value2 / value1,
            'message': f'Первое значение меньше второго на {value2 - value1:.6f}'
        }
    else:
        return {
            'result': 'equal',
            'difference': 0,
            'ratio': 1,
            'message': 'Значения равны'
        }

def get_unit_converter_statistics(user_id):
    """Получение статистики использования конвертера единиц"""
    # Здесь можно добавить статистику использования
    return {
        'conversions_count': 0,
        'most_used_categories': [],
        'most_used_units': []
    }

def get_unit_converter_tips():
    """Получение советов по конвертации единиц"""
    tips = [
        "Используйте метрическую систему как базовую для большинства конвертаций",
        "Помните о точности - некоторые конвертации могут иметь погрешности",
        "Для температуры используйте специальные формулы конвертации",
        "Проверяйте результат на разумность",
        "Используйте научную нотацию для очень больших или очень малых чисел",
        "Обращайте внимание на единицы измерения в результатах",
        "Для точных вычислений используйте больше знаков после запятой",
        "Изучайте соотношения между единицами для лучшего понимания"
    ]
    
    return tips
