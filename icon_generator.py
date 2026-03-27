from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import random
import string
from datetime import datetime

icon_bp = Blueprint('icon', __name__)

@icon_bp.route('/api/icon/generate', methods=['POST'])
@login_required
def generate_icon():
    """Генерация иконки"""
    try:
        data = request.get_json()
        
        # Параметры иконки
        text = data.get('text', 'A')
        size = int(data.get('size', 64))
        background_color = data.get('background_color', '#667eea')
        text_color = data.get('text_color', '#ffffff')
        icon_type = data.get('type', 'text')  # text, gradient, pattern, logo
        format_type = data.get('format', 'png')  # png, jpg, ico
        
        # Валидация размера
        size = max(16, min(size, 512))
        
        # Генерация иконки
        if icon_type == 'text':
            icon_data = generate_text_icon(text, size, background_color, text_color)
        elif icon_type == 'gradient':
            icon_data = generate_gradient_icon(text, size, background_color, text_color)
        elif icon_type == 'pattern':
            icon_data = generate_pattern_icon(text, size, background_color, text_color)
        elif icon_type == 'logo':
            icon_data = generate_logo_icon(text, size, background_color, text_color)
        else:
            return jsonify({'error': 'Неподдерживаемый тип иконки'}), 400
        
        # Конвертация в нужный формат
        if format_type == 'ico':
            icon_data = convert_to_ico(icon_data)
        elif format_type == 'jpg':
            icon_data = convert_to_jpg(icon_data)
        
        # Кодирование в base64
        buffer = io.BytesIO()
        icon_data.save(buffer, format=format_type.upper())
        buffer.seek(0)
        
        icon_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'icon': icon_base64,
            'format': format_type,
            'size': size,
            'text': text,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации иконки'}), 500

@icon_bp.route('/api/icon/favicon', methods=['POST'])
@login_required
def generate_favicon():
    """Генерация favicon"""
    try:
        data = request.get_json()
        
        text = data.get('text', 'F')
        background_color = data.get('background_color', '#667eea')
        text_color = data.get('text_color', '#ffffff')
        
        # Генерация favicon в разных размерах
        sizes = [16, 32, 48, 64]
        favicons = {}
        
        for size in sizes:
            icon_data = generate_text_icon(text, size, background_color, text_color)
            
            buffer = io.BytesIO()
            icon_data.save(buffer, format='ICO')
            buffer.seek(0)
            
            favicons[f'{size}x{size}'] = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'favicons': favicons,
            'text': text,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации favicon'}), 500

@icon_bp.route('/api/icon/batch', methods=['POST'])
@login_required
def generate_batch_icons():
    """Генерация пакета иконок"""
    try:
        data = request.get_json()
        
        texts = data.get('texts', ['A', 'B', 'C'])
        size = int(data.get('size', 64))
        background_color = data.get('background_color', '#667eea')
        text_color = data.get('text_color', '#ffffff')
        icon_type = data.get('type', 'text')
        
        icons = []
        
        for text in texts:
            if icon_type == 'text':
                icon_data = generate_text_icon(text, size, background_color, text_color)
            elif icon_type == 'gradient':
                icon_data = generate_gradient_icon(text, size, background_color, text_color)
            elif icon_type == 'pattern':
                icon_data = generate_pattern_icon(text, size, background_color, text_color)
            else:
                continue
            
            buffer = io.BytesIO()
            icon_data.save(buffer, format='PNG')
            buffer.seek(0)
            
            icon_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            icons.append({
                'text': text,
                'icon': icon_base64,
                'size': size
            })
        
        return jsonify({
            'icons': icons,
            'count': len(icons),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации пакета иконок'}), 500

@icon_bp.route('/api/icon/templates', methods=['GET'])
def get_icon_templates():
    """Получение шаблонов иконок"""
    try:
        templates = {
            'colors': {
                'blue': '#667eea',
                'green': '#28a745',
                'red': '#dc3545',
                'orange': '#fd7e14',
                'purple': '#6f42c1',
                'pink': '#e83e8c',
                'teal': '#20c997',
                'indigo': '#6610f2'
            },
            'sizes': [16, 24, 32, 48, 64, 96, 128, 256, 512],
            'formats': ['png', 'jpg', 'ico'],
            'types': {
                'text': 'Текстовая иконка',
                'gradient': 'Градиентная иконка',
                'pattern': 'Иконка с паттерном',
                'logo': 'Логотип'
            },
            'presets': [
                {
                    'name': 'Классический синий',
                    'background': '#667eea',
                    'text': '#ffffff',
                    'type': 'text'
                },
                {
                    'name': 'Градиентный',
                    'background': '#667eea',
                    'text': '#ffffff',
                    'type': 'gradient'
                },
                {
                    'name': 'Темная тема',
                    'background': '#2d2d2d',
                    'text': '#ffffff',
                    'type': 'text'
                },
                {
                    'name': 'Светлая тема',
                    'background': '#ffffff',
                    'text': '#333333',
                    'type': 'text'
                }
            ]
        }
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении шаблонов'}), 500

def generate_text_icon(text, size, background_color, text_color):
    """Генерация текстовой иконки"""
    # Создание изображения
    img = Image.new('RGBA', (size, size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Определение размера шрифта
    font_size = int(size * 0.6)
    
    try:
        # Попытка использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except:
            # Использование стандартного шрифта
            font = ImageFont.load_default()
    
    # Получение размеров текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Центрирование текста
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Рисование текста
    draw.text((x, y), text, fill=text_color, font=font)
    
    return img

def generate_gradient_icon(text, size, background_color, text_color):
    """Генерация градиентной иконки"""
    # Создание изображения
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Создание градиента
    for i in range(size):
        # Интерполяция цвета
        ratio = i / size
        r1, g1, b1 = hex_to_rgb(background_color)
        r2, g2, b2 = hex_to_rgb(text_color)
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        draw.line([(0, i), (size, i)], fill=(r, g, b, 255))
    
    # Добавление текста
    font_size = int(size * 0.4)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Рисование текста с тенью
    draw.text((x + 1, y + 1), text, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    return img

def generate_pattern_icon(text, size, background_color, text_color):
    """Генерация иконки с паттерном"""
    # Создание изображения
    img = Image.new('RGBA', (size, size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Создание паттерна
    pattern_size = size // 8
    
    for i in range(0, size, pattern_size):
        for j in range(0, size, pattern_size):
            if (i + j) % (pattern_size * 2) == 0:
                draw.rectangle([i, j, i + pattern_size, j + pattern_size], 
                             fill=text_color, outline=None)
    
    # Добавление текста
    font_size = int(size * 0.5)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Рисование текста
    draw.text((x, y), text, fill=background_color, font=font)
    
    return img

def generate_logo_icon(text, size, background_color, text_color):
    """Генерация логотипа"""
    # Создание изображения
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Рисование фона с закругленными углами
    margin = size // 8
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], 
                          radius=size // 6, fill=background_color)
    
    # Добавление текста
    font_size = int(size * 0.4)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Рисование текста
    draw.text((x, y), text, fill=text_color, font=font)
    
    return img

def convert_to_ico(img):
    """Конвертация в ICO формат"""
    # ICO требует несколько размеров
    sizes = [16, 32, 48]
    ico_images = []
    
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        ico_images.append(resized)
    
    # Сохранение как ICO
    buffer = io.BytesIO()
    ico_images[0].save(buffer, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
    buffer.seek(0)
    
    return Image.open(buffer)

def convert_to_jpg(img):
    """Конвертация в JPG формат"""
    # JPG не поддерживает прозрачность, поэтому создаем белый фон
    jpg_img = Image.new('RGB', img.size, (255, 255, 255))
    jpg_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
    
    return jpg_img

def hex_to_rgb(hex_color):
    """Конвертация HEX в RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_random_icon(size=64):
    """Генерация случайной иконки"""
    # Случайные параметры
    text = random.choice(string.ascii_uppercase)
    background_color = random.choice(['#667eea', '#28a745', '#dc3545', '#fd7e14', '#6f42c1'])
    text_color = '#ffffff'
    
    return generate_text_icon(text, size, background_color, text_color)

def create_icon_pack(texts, size=64, background_color='#667eea', text_color='#ffffff'):
    """Создание пакета иконок"""
    icons = []
    
    for text in texts:
        icon = generate_text_icon(text, size, background_color, text_color)
        
        buffer = io.BytesIO()
        icon.save(buffer, format='PNG')
        buffer.seek(0)
        
        icons.append({
            'text': text,
            'data': buffer.getvalue(),
            'size': size
        })
    
    return icons
