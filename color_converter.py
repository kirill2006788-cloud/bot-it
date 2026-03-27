from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import colorsys
import re

color_bp = Blueprint('color', __name__)

@color_bp.route('/api/color/convert', methods=['POST'])
@login_required
def convert_color():
    """Конвертация цвета между различными форматами"""
    try:
        data = request.get_json()
        color_value = data.get('color', '').strip()
        from_format = data.get('from_format', 'hex').lower()
        to_format = data.get('to_format', 'rgb').lower()
        
        if not color_value:
            return jsonify({'error': 'Цвет не указан'}), 400
        
        # Парсинг входного цвета
        input_rgb = parse_color(color_value, from_format)
        if not input_rgb:
            return jsonify({'error': f'Неверный формат цвета: {from_format}'}), 400
        
        # Конвертация в выходной формат
        output_color = convert_to_format(input_rgb, to_format)
        if not output_color:
            return jsonify({'error': f'Неподдерживаемый выходной формат: {to_format}'}), 400
        
        return jsonify({
            'input': {
                'value': color_value,
                'format': from_format
            },
            'output': {
                'value': output_color['value'],
                'format': to_format,
                'rgb': input_rgb
            },
            'conversion_info': {
                'from_format': from_format,
                'to_format': to_format,
                'converted_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при конвертации цвета'}), 500

@color_bp.route('/api/color/palette', methods=['POST'])
@login_required
def generate_palette():
    """Генерация цветовой палитры"""
    try:
        data = request.get_json()
        base_color = data.get('base_color', '#667eea').strip()
        palette_type = data.get('type', 'complementary').lower()
        count = min(int(data.get('count', 5)), 20)  # Максимум 20 цветов
        
        # Парсинг базового цвета
        base_rgb = parse_color(base_color, 'hex')
        if not base_rgb:
            return jsonify({'error': 'Неверный базовый цвет'}), 400
        
        # Генерация палитры
        palette = generate_color_palette(base_rgb, palette_type, count)
        
        return jsonify({
            'base_color': {
                'hex': rgb_to_hex(base_rgb),
                'rgb': base_rgb
            },
            'palette': palette,
            'type': palette_type,
            'count': len(palette)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации палитры'}), 500

@color_bp.route('/api/color/analyze', methods=['POST'])
@login_required
def analyze_color():
    """Анализ цвета"""
    try:
        data = request.get_json()
        color_value = data.get('color', '').strip()
        format_type = data.get('format', 'hex').lower()
        
        if not color_value:
            return jsonify({'error': 'Цвет не указан'}), 400
        
        # Парсинг цвета
        rgb = parse_color(color_value, format_type)
        if not rgb:
            return jsonify({'error': f'Неверный формат цвета: {format_type}'}), 400
        
        # Анализ цвета
        analysis = analyze_color_properties(rgb)
        
        return jsonify({
            'color': {
                'hex': rgb_to_hex(rgb),
                'rgb': rgb,
                'hsl': rgb_to_hsl(rgb),
                'hsv': rgb_to_hsv(rgb),
                'cmyk': rgb_to_cmyk(rgb)
            },
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при анализе цвета'}), 500

@color_bp.route('/api/color/blend', methods=['POST'])
@login_required
def blend_colors():
    """Смешивание цветов"""
    try:
        data = request.get_json()
        color1 = data.get('color1', '').strip()
        color2 = data.get('color2', '').strip()
        ratio = float(data.get('ratio', 0.5))  # От 0 до 1
        format_type = data.get('format', 'hex').lower()
        
        if not color1 or not color2:
            return jsonify({'error': 'Оба цвета должны быть указаны'}), 400
        
        if not 0 <= ratio <= 1:
            return jsonify({'error': 'Коэффициент смешивания должен быть от 0 до 1'}), 400
        
        # Парсинг цветов
        rgb1 = parse_color(color1, format_type)
        rgb2 = parse_color(color2, format_type)
        
        if not rgb1 or not rgb2:
            return jsonify({'error': 'Неверный формат одного из цветов'}), 400
        
        # Смешивание
        blended_rgb = blend_rgb_colors(rgb1, rgb2, ratio)
        
        return jsonify({
            'color1': {
                'value': color1,
                'rgb': rgb1,
                'hex': rgb_to_hex(rgb1)
            },
            'color2': {
                'value': color2,
                'rgb': rgb2,
                'hex': rgb_to_hex(rgb2)
            },
            'blended': {
                'rgb': blended_rgb,
                'hex': rgb_to_hex(blended_rgb),
                'ratio': ratio
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при смешивании цветов'}), 500

@color_bp.route('/api/color/formats', methods=['GET'])
def get_color_formats():
    """Получение поддерживаемых форматов цветов"""
    try:
        formats = {
            'hex': {
                'name': 'HEX',
                'description': 'Шестнадцатеричный формат (#RRGGBB)',
                'example': '#667eea',
                'regex': r'^#[0-9A-Fa-f]{6}$'
            },
            'rgb': {
                'name': 'RGB',
                'description': 'Красный, зеленый, синий (0-255)',
                'example': 'rgb(102, 126, 234)',
                'regex': r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'
            },
            'hsl': {
                'name': 'HSL',
                'description': 'Оттенок, насыщенность, яркость',
                'example': 'hsl(230, 75%, 66%)',
                'regex': r'^hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$'
            },
            'hsv': {
                'name': 'HSV',
                'description': 'Оттенок, насыщенность, значение',
                'example': 'hsv(230, 56%, 92%)',
                'regex': r'^hsv\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$'
            },
            'cmyk': {
                'name': 'CMYK',
                'description': 'Голубой, пурпурный, желтый, черный',
                'example': 'cmyk(56, 46, 0, 8)',
                'regex': r'^cmyk\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'
            }
        }
        
        return jsonify({'formats': formats})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении форматов'}), 500

def parse_color(color_value, format_type):
    """Парсинг цвета в RGB"""
    try:
        if format_type == 'hex':
            return parse_hex_color(color_value)
        elif format_type == 'rgb':
            return parse_rgb_color(color_value)
        elif format_type == 'hsl':
            return parse_hsl_color(color_value)
        elif format_type == 'hsv':
            return parse_hsv_color(color_value)
        elif format_type == 'cmyk':
            return parse_cmyk_color(color_value)
        else:
            return None
    except:
        return None

def parse_hex_color(hex_color):
    """Парсинг HEX цвета"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return None

def parse_rgb_color(rgb_color):
    """Парсинг RGB цвета"""
    match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', rgb_color)
    if match:
        return tuple(int(x) for x in match.groups())
    return None

def parse_hsl_color(hsl_color):
    """Парсинг HSL цвета"""
    match = re.match(r'hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)', hsl_color)
    if match:
        h, s, l = map(int, match.groups())
        return hsl_to_rgb(h, s/100, l/100)
    return None

def parse_hsv_color(hsv_color):
    """Парсинг HSV цвета"""
    match = re.match(r'hsv\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)', hsv_color)
    if match:
        h, s, v = map(int, match.groups())
        return hsv_to_rgb(h, s/100, v/100)
    return None

def parse_cmyk_color(cmyk_color):
    """Парсинг CMYK цвета"""
    match = re.match(r'cmyk\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', cmyk_color)
    if match:
        c, m, y, k = map(int, match.groups())
        return cmyk_to_rgb(c/100, m/100, y/100, k/100)
    return None

def convert_to_format(rgb, format_type):
    """Конвертация RGB в указанный формат"""
    try:
        if format_type == 'hex':
            return {'value': rgb_to_hex(rgb)}
        elif format_type == 'rgb':
            return {'value': f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'}
        elif format_type == 'hsl':
            hsl = rgb_to_hsl(rgb)
            return {'value': f'hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%)'}
        elif format_type == 'hsv':
            hsv = rgb_to_hsv(rgb)
            return {'value': f'hsv({hsv[0]}, {hsv[1]}%, {hsv[2]}%)'}
        elif format_type == 'cmyk':
            cmyk = rgb_to_cmyk(rgb)
            return {'value': f'cmyk({cmyk[0]}, {cmyk[1]}, {cmyk[2]}, {cmyk[3]})'}
        else:
            return None
    except:
        return None

def rgb_to_hex(rgb):
    """Конвертация RGB в HEX"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()

def rgb_to_hsl(rgb):
    """Конвертация RGB в HSL"""
    r, g, b = [x/255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (int(h*360), int(s*100), int(l*100))

def rgb_to_hsv(rgb):
    """Конвертация RGB в HSV"""
    r, g, b = [x/255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (int(h*360), int(s*100), int(v*100))

def rgb_to_cmyk(rgb):
    """Конвертация RGB в CMYK"""
    r, g, b = [x/255.0 for x in rgb]
    k = 1 - max(r, g, b)
    if k == 1:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return (int(c*100), int(m*100), int(y*100), int(k*100))

def hsl_to_rgb(h, s, l):
    """Конвертация HSL в RGB"""
    r, g, b = colorsys.hls_to_rgb(h/360, l, s)
    return (int(r*255), int(g*255), int(b*255))

def hsv_to_rgb(h, s, v):
    """Конвертация HSV в RGB"""
    r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
    return (int(r*255), int(g*255), int(b*255))

def cmyk_to_rgb(c, m, y, k):
    """Конвертация CMYK в RGB"""
    r = int(255 * (1 - c) * (1 - k))
    g = int(255 * (1 - m) * (1 - k))
    b = int(255 * (1 - y) * (1 - k))
    return (r, g, b)

def generate_color_palette(base_rgb, palette_type, count):
    """Генерация цветовой палитры"""
    palette = []
    
    if palette_type == 'complementary':
        # Дополнительные цвета
        h, s, l = rgb_to_hsl(base_rgb)
        comp_h = (h + 180) % 360
        palette = generate_harmony_palette(h, s, l, comp_h, count)
    
    elif palette_type == 'triadic':
        # Триадические цвета
        h, s, l = rgb_to_hsl(base_rgb)
        palette = generate_triadic_palette(h, s, l, count)
    
    elif palette_type == 'analogous':
        # Аналогичные цвета
        h, s, l = rgb_to_hsl(base_rgb)
        palette = generate_analogous_palette(h, s, l, count)
    
    elif palette_type == 'monochromatic':
        # Монохроматические цвета
        h, s, l = rgb_to_hsl(base_rgb)
        palette = generate_monochromatic_palette(h, s, l, count)
    
    elif palette_type == 'split_complementary':
        # Раздельно-дополнительные цвета
        h, s, l = rgb_to_hsl(base_rgb)
        palette = generate_split_complementary_palette(h, s, l, count)
    
    else:
        # По умолчанию - аналогичные цвета
        h, s, l = rgb_to_hsl(base_rgb)
        palette = generate_analogous_palette(h, s, l, count)
    
    return palette

def generate_harmony_palette(h1, s, l, h2, count):
    """Генерация гармоничной палитры"""
    palette = []
    step = 360 / count
    
    for i in range(count):
        if i % 2 == 0:
            hue = (h1 + (i//2) * step) % 360
        else:
            hue = (h2 + (i//2) * step) % 360
        
        rgb = hsl_to_rgb(hue, s/100, l/100)
        palette.append({
            'hex': rgb_to_hex(rgb),
            'rgb': rgb,
            'hsl': (int(hue), s, l)
        })
    
    return palette

def generate_triadic_palette(h, s, l, count):
    """Генерация триадической палитры"""
    palette = []
    hues = [h, (h + 120) % 360, (h + 240) % 360]
    
    for i in range(count):
        hue = hues[i % 3]
        rgb = hsl_to_rgb(hue, s/100, l/100)
        palette.append({
            'hex': rgb_to_hex(rgb),
            'rgb': rgb,
            'hsl': (int(hue), s, l)
        })
    
    return palette

def generate_analogous_palette(h, s, l, count):
    """Генерация аналогичной палитры"""
    palette = []
    step = 30 / count
    
    for i in range(count):
        hue = (h + (i - count//2) * step) % 360
        rgb = hsl_to_rgb(hue, s/100, l/100)
        palette.append({
            'hex': rgb_to_hex(rgb),
            'rgb': rgb,
            'hsl': (int(hue), s, l)
        })
    
    return palette

def generate_monochromatic_palette(h, s, l, count):
    """Генерация монохроматической палитры"""
    palette = []
    step = 80 / count
    
    for i in range(count):
        lightness = max(10, min(90, l + (i - count//2) * step))
        rgb = hsl_to_rgb(h, s/100, lightness/100)
        palette.append({
            'hex': rgb_to_hex(rgb),
            'rgb': rgb,
            'hsl': (h, s, int(lightness))
        })
    
    return palette

def generate_split_complementary_palette(h, s, l, count):
    """Генерация раздельно-дополнительной палитры"""
    palette = []
    hues = [h, (h + 150) % 360, (h + 210) % 360]
    
    for i in range(count):
        hue = hues[i % 3]
        rgb = hsl_to_rgb(hue, s/100, l/100)
        palette.append({
            'hex': rgb_to_hex(rgb),
            'rgb': rgb,
            'hsl': (int(hue), s, l)
        })
    
    return palette

def analyze_color_properties(rgb):
    """Анализ свойств цвета"""
    r, g, b = rgb
    
    # Яркость
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    # Насыщенность
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    saturation = (max_val - min_val) / max_val if max_val > 0 else 0
    
    # Температура цвета
    if r > b:
        temperature = 'warm'  # Теплый
    elif b > r:
        temperature = 'cool'  # Холодный
    else:
        temperature = 'neutral'  # Нейтральный
    
    # Контрастность
    contrast = 'high' if brightness > 128 else 'low'
    
    # Цветовая категория
    if r > g and r > b:
        category = 'red'
    elif g > r and g > b:
        category = 'green'
    elif b > r and b > g:
        category = 'blue'
    elif r == g == b:
        category = 'gray'
    else:
        category = 'mixed'
    
    return {
        'brightness': round(brightness, 2),
        'saturation': round(saturation * 100, 2),
        'temperature': temperature,
        'contrast': contrast,
        'category': category,
        'luminance': round(0.299 * r + 0.587 * g + 0.114 * b, 2)
    }

def blend_rgb_colors(rgb1, rgb2, ratio):
    """Смешивание RGB цветов"""
    r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
    g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
    b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
    return (r, g, b)
