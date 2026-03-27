from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
from datetime import datetime
import os

image_bp = Blueprint('image', __name__)

@image_bp.route('/api/image/convert', methods=['POST'])
@login_required
def convert_image():
    """Конвертация изображения"""
    try:
        data = request.get_json()
        
        # Получение данных изображения
        image_data = data.get('image_data', '')
        from_format = data.get('from_format', 'png').lower()
        to_format = data.get('to_format', 'jpg').lower()
        quality = int(data.get('quality', 95))
        
        if not image_data:
            return jsonify({'error': 'Данные изображения не предоставлены'}), 400
        
        # Декодирование base64
        try:
            image_bytes = base64.b64decode(image_data)
        except:
            return jsonify({'error': 'Неверный формат base64'}), 400
        
        # Открытие изображения
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except:
            return jsonify({'error': 'Не удалось открыть изображение'}), 400
        
        # Конвертация формата
        converted_image = convert_image_format(image, to_format, quality)
        
        # Кодирование в base64
        buffer = io.BytesIO()
        converted_image.save(buffer, format=to_format.upper(), quality=quality)
        buffer.seek(0)
        
        converted_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'converted_image': converted_base64,
            'from_format': from_format,
            'to_format': to_format,
            'original_size': len(image_bytes),
            'converted_size': len(buffer.getvalue()),
            'compression_ratio': round((1 - len(buffer.getvalue()) / len(image_bytes)) * 100, 2),
            'converted_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при конвертации изображения'}), 500

@image_bp.route('/api/image/resize', methods=['POST'])
@login_required
def resize_image():
    """Изменение размера изображения"""
    try:
        data = request.get_json()
        
        image_data = data.get('image_data', '')
        width = int(data.get('width', 0))
        height = int(data.get('height', 0))
        maintain_aspect_ratio = data.get('maintain_aspect_ratio', True)
        resize_method = data.get('resize_method', 'resize')  # resize, thumbnail, crop
        
        if not image_data or not width or not height:
            return jsonify({'error': 'Необходимо указать данные изображения и размеры'}), 400
        
        # Декодирование изображения
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Изменение размера
        resized_image = resize_image_method(image, width, height, maintain_aspect_ratio, resize_method)
        
        # Кодирование результата
        buffer = io.BytesIO()
        resized_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        resized_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'resized_image': resized_base64,
            'original_size': (image.width, image.height),
            'new_size': (resized_image.width, resized_image.height),
            'resize_method': resize_method,
            'maintain_aspect_ratio': maintain_aspect_ratio,
            'resized_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при изменении размера изображения'}), 500

@image_bp.route('/api/image/compress', methods=['POST'])
@login_required
def compress_image():
    """Сжатие изображения"""
    try:
        data = request.get_json()
        
        image_data = data.get('image_data', '')
        compression_level = int(data.get('compression_level', 80))  # 1-100
        format_type = data.get('format', 'jpg').lower()
        
        if not image_data:
            return jsonify({'error': 'Данные изображения не предоставлены'}), 400
        
        # Декодирование изображения
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Сжатие изображения
        compressed_image = compress_image_method(image, compression_level, format_type)
        
        # Кодирование результата
        buffer = io.BytesIO()
        compressed_image.save(buffer, format=format_type.upper(), quality=compression_level, optimize=True)
        buffer.seek(0)
        
        compressed_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        original_size = len(image_bytes)
        compressed_size = len(buffer.getvalue())
        compression_ratio = round((1 - compressed_size / original_size) * 100, 2)
        
        return jsonify({
            'compressed_image': compressed_base64,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'compression_level': compression_level,
            'format': format_type,
            'compressed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при сжатии изображения'}), 500

@image_bp.route('/api/image/enhance', methods=['POST'])
@login_required
def enhance_image():
    """Улучшение изображения"""
    try:
        data = request.get_json()
        
        image_data = data.get('image_data', '')
        brightness = float(data.get('brightness', 1.0))  # 0.0 - 2.0
        contrast = float(data.get('contrast', 1.0))  # 0.0 - 2.0
        saturation = float(data.get('saturation', 1.0))  # 0.0 - 2.0
        sharpness = float(data.get('sharpness', 1.0))  # 0.0 - 2.0
        
        if not image_data:
            return jsonify({'error': 'Данные изображения не предоставлены'}), 400
        
        # Декодирование изображения
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Улучшение изображения
        enhanced_image = enhance_image_method(image, brightness, contrast, saturation, sharpness)
        
        # Кодирование результата
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        enhanced_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'enhanced_image': enhanced_base64,
            'enhancements': {
                'brightness': brightness,
                'contrast': contrast,
                'saturation': saturation,
                'sharpness': sharpness
            },
            'enhanced_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при улучшении изображения'}), 500

@image_bp.route('/api/image/filters', methods=['POST'])
@login_required
def apply_filters():
    """Применение фильтров к изображению"""
    try:
        data = request.get_json()
        
        image_data = data.get('image_data', '')
        filters = data.get('filters', [])  # Список фильтров для применения
        
        if not image_data or not filters:
            return jsonify({'error': 'Необходимо указать данные изображения и фильтры'}), 400
        
        # Декодирование изображения
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Применение фильтров
        filtered_image = apply_image_filters(image, filters)
        
        # Кодирование результата
        buffer = io.BytesIO()
        filtered_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        filtered_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'filtered_image': filtered_base64,
            'applied_filters': filters,
            'filtered_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при применении фильтров'}), 500

@image_bp.route('/api/image/analyze', methods=['POST'])
@login_required
def analyze_image():
    """Анализ изображения"""
    try:
        data = request.get_json()
        
        image_data = data.get('image_data', '')
        
        if not image_data:
            return jsonify({'error': 'Данные изображения не предоставлены'}), 400
        
        # Декодирование изображения
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Анализ изображения
        analysis = analyze_image_properties(image)
        
        return jsonify({
            'analysis': analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при анализе изображения'}), 500

@image_bp.route('/api/image/formats', methods=['GET'])
def get_image_formats():
    """Получение поддерживаемых форматов изображений"""
    try:
        formats = {
            'input_formats': ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'TIFF', 'WEBP'],
            'output_formats': ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'TIFF', 'WEBP'],
            'compression_formats': ['JPEG', 'JPG', 'WEBP'],
            'lossless_formats': ['PNG', 'BMP', 'TIFF'],
            'animated_formats': ['GIF', 'WEBP']
        }
        
        return jsonify({'formats': formats})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении форматов'}), 500

def convert_image_format(image, target_format, quality=95):
    """Конвертация формата изображения"""
    try:
        # Конвертация в RGB для JPEG
        if target_format.lower() in ['jpg', 'jpeg']:
            if image.mode in ('RGBA', 'LA', 'P'):
                # Создание белого фона для прозрачных изображений
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
        
        return image
        
    except Exception as e:
        raise Exception(f'Ошибка конвертации формата: {str(e)}')

def resize_image_method(image, width, height, maintain_aspect_ratio, method):
    """Изменение размера изображения"""
    try:
        if method == 'resize':
            if maintain_aspect_ratio:
                # Сохранение пропорций
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
                return image
            else:
                return image.resize((width, height), Image.Resampling.LANCZOS)
        
        elif method == 'thumbnail':
            return image.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        elif method == 'crop':
            # Обрезка по центру
            return crop_to_size(image, width, height)
        
        else:
            return image.resize((width, height), Image.Resampling.LANCZOS)
            
    except Exception as e:
        raise Exception(f'Ошибка изменения размера: {str(e)}')

def crop_to_size(image, width, height):
    """Обрезка изображения до указанного размера"""
    # Вычисление центральной области
    left = (image.width - width) // 2
    top = (image.height - height) // 2
    right = left + width
    bottom = top + height
    
    return image.crop((left, top, right, bottom))

def compress_image_method(image, compression_level, format_type):
    """Сжатие изображения"""
    try:
        # Конвертация в нужный формат
        compressed_image = convert_image_format(image, format_type, compression_level)
        
        return compressed_image
        
    except Exception as e:
        raise Exception(f'Ошибка сжатия: {str(e)}')

def enhance_image_method(image, brightness, contrast, saturation, sharpness):
    """Улучшение изображения"""
    try:
        enhanced_image = image.copy()
        
        # Яркость
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = enhancer.enhance(brightness)
        
        # Контрастность
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = enhancer.enhance(contrast)
        
        # Насыщенность
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(enhanced_image)
            enhanced_image = enhancer.enhance(saturation)
        
        # Резкость
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(enhanced_image)
            enhanced_image = enhancer.enhance(sharpness)
        
        return enhanced_image
        
    except Exception as e:
        raise Exception(f'Ошибка улучшения: {str(e)}')

def apply_image_filters(image, filters):
    """Применение фильтров к изображению"""
    try:
        filtered_image = image.copy()
        
        for filter_name in filters:
            if filter_name == 'blur':
                filtered_image = filtered_image.filter(ImageFilter.BLUR)
            elif filter_name == 'sharpen':
                filtered_image = filtered_image.filter(ImageFilter.SHARPEN)
            elif filter_name == 'edge_enhance':
                filtered_image = filtered_image.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_name == 'emboss':
                filtered_image = filtered_image.filter(ImageFilter.EMBOSS)
            elif filter_name == 'contour':
                filtered_image = filtered_image.filter(ImageFilter.CONTOUR)
            elif filter_name == 'smooth':
                filtered_image = filtered_image.filter(ImageFilter.SMOOTH)
            elif filter_name == 'detail':
                filtered_image = filtered_image.filter(ImageFilter.DETAIL)
            elif filter_name == 'gaussian_blur':
                filtered_image = filtered_image.filter(ImageFilter.GaussianBlur(radius=2))
            elif filter_name == 'median_filter':
                filtered_image = filtered_image.filter(ImageFilter.MedianFilter(size=3))
            elif filter_name == 'min_filter':
                filtered_image = filtered_image.filter(ImageFilter.MinFilter(size=3))
            elif filter_name == 'max_filter':
                filtered_image = filtered_image.filter(ImageFilter.MaxFilter(size=3))
        
        return filtered_image
        
    except Exception as e:
        raise Exception(f'Ошибка применения фильтров: {str(e)}')

def analyze_image_properties(image):
    """Анализ свойств изображения"""
    try:
        analysis = {
            'dimensions': {
                'width': image.width,
                'height': image.height,
                'aspect_ratio': round(image.width / image.height, 2)
            },
            'format': image.format,
            'mode': image.mode,
            'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info,
            'color_count': len(image.getcolors(maxcolors=256*256*256)) if image.mode == 'P' else 'N/A',
            'file_size_estimate': estimate_file_size(image),
            'recommendations': get_image_recommendations(image)
        }
        
        # Анализ цветов (для RGB изображений)
        if image.mode == 'RGB':
            analysis['color_analysis'] = analyze_colors(image)
        
        return analysis
        
    except Exception as e:
        raise Exception(f'Ошибка анализа: {str(e)}')

def estimate_file_size(image):
    """Оценка размера файла"""
    # Примерная оценка размера в байтах
    if image.mode == 'RGB':
        return image.width * image.height * 3
    elif image.mode == 'RGBA':
        return image.width * image.height * 4
    elif image.mode == 'L':
        return image.width * image.height
    else:
        return image.width * image.height * 3  # По умолчанию RGB

def analyze_colors(image):
    """Анализ цветов изображения"""
    try:
        # Получение цветовой палитры
        colors = image.getcolors(maxcolors=256*256*256)
        
        if colors:
            # Сортировка по частоте
            colors.sort(key=lambda x: x[0], reverse=True)
            
            # Топ-5 цветов
            top_colors = colors[:5]
            
            return {
                'total_colors': len(colors),
                'top_colors': [
                    {
                        'color': f'rgb({color[1][0]}, {color[1][1]}, {color[1][2]})',
                        'frequency': color[0],
                        'percentage': round((color[0] / (image.width * image.height)) * 100, 2)
                    }
                    for color in top_colors
                ]
            }
        else:
            return {'total_colors': 'N/A', 'top_colors': []}
            
    except Exception as e:
        return {'error': str(e)}

def get_image_recommendations(image):
    """Рекомендации по оптимизации изображения"""
    recommendations = []
    
    # Размер изображения
    if image.width > 1920 or image.height > 1080:
        recommendations.append('Рассмотрите уменьшение размера изображения для веб-использования')
    
    # Формат изображения
    if image.format == 'PNG' and image.mode == 'RGB':
        recommendations.append('Для RGB изображений без прозрачности рассмотрите использование JPEG')
    
    # Прозрачность
    if image.mode in ('RGBA', 'LA') and not has_transparent_pixels(image):
        recommendations.append('Изображение имеет альфа-канал, но не содержит прозрачных пикселей')
    
    # Размер файла
    estimated_size = estimate_file_size(image)
    if estimated_size > 1024 * 1024:  # Больше 1MB
        recommendations.append('Рассмотрите сжатие изображения для уменьшения размера файла')
    
    if not recommendations:
        recommendations.append('Изображение оптимизировано')
    
    return recommendations

def has_transparent_pixels(image):
    """Проверка наличия прозрачных пикселей"""
    if image.mode not in ('RGBA', 'LA'):
        return False
    
    # Проверка альфа-канала
    if image.mode == 'RGBA':
        alpha = image.split()[-1]
        return any(pixel < 255 for pixel in alpha.getdata())
    elif image.mode == 'LA':
        alpha = image.split()[-1]
        return any(pixel < 255 for pixel in alpha.getdata())
    
    return False
