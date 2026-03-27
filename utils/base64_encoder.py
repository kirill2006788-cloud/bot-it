from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import base64
import binascii
from datetime import datetime

base64_encoder_bp = Blueprint('base64_encoder', __name__)

@base64_encoder_bp.route('/api/base64/encode', methods=['POST'])
@login_required
def encode_base64():
    """Кодирование в Base64"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        encoding = data.get('encoding', 'utf-8')
        format_type = data.get('format', 'standard')  # standard, url_safe, custom
        
        if not text:
            return jsonify({'error': 'Текст для кодирования не указан'}), 400
        
        # Кодирование в Base64
        encoded_result = encode_to_base64(text, encoding, format_type)
        
        if encoded_result is None:
            return jsonify({'error': 'Ошибка при кодировании в Base64'}), 500
        
        return jsonify({
            'text': text,
            'encoded': encoded_result['encoded'],
            'encoding': encoding,
            'format': format_type,
            'length': len(encoded_result['encoded']),
            'encoded_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при кодировании в Base64'}), 500

@base64_encoder_bp.route('/api/base64/decode', methods=['POST'])
@login_required
def decode_base64():
    """Декодирование из Base64"""
    try:
        data = request.get_json()
        encoded_text = data.get('encoded', '')
        encoding = data.get('encoding', 'utf-8')
        format_type = data.get('format', 'standard')  # standard, url_safe, custom
        
        if not encoded_text:
            return jsonify({'error': 'Закодированный текст не указан'}), 400
        
        # Декодирование из Base64
        decoded_result = decode_from_base64(encoded_text, encoding, format_type)
        
        if decoded_result is None:
            return jsonify({'error': 'Ошибка при декодировании из Base64'}), 500
        
        return jsonify({
            'encoded': encoded_text,
            'decoded': decoded_result['decoded'],
            'encoding': encoding,
            'format': format_type,
            'length': len(decoded_result['decoded']),
            'decoded_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при декодировании из Base64'}), 500

@base64_encoder_bp.route('/api/base64/validate', methods=['POST'])
@login_required
def validate_base64():
    """Валидация Base64"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        format_type = data.get('format', 'standard')
        
        if not text:
            return jsonify({'error': 'Текст для валидации не указан'}), 400
        
        # Валидация Base64
        is_valid = validate_base64_text(text, format_type)
        
        return jsonify({
            'text': text,
            'is_valid': is_valid,
            'format': format_type,
            'validated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации Base64'}), 500

@base64_encoder_bp.route('/api/base64/compare', methods=['POST'])
@login_required
def compare_base64():
    """Сравнение Base64"""
    try:
        data = request.get_json()
        text1 = data.get('text1', '')
        text2 = data.get('text2', '')
        encoding = data.get('encoding', 'utf-8')
        format_type = data.get('format', 'standard')
        
        if not text1 or not text2:
            return jsonify({'error': 'Оба текста должны быть указаны'}), 400
        
        # Кодирование обоих текстов
        encoded1 = encode_to_base64(text1, encoding, format_type)
        encoded2 = encode_to_base64(text2, encoding, format_type)
        
        if encoded1 is None or encoded2 is None:
            return jsonify({'error': 'Ошибка при кодировании текстов'}), 500
        
        # Сравнение
        comparison = {
            'text1': text1,
            'text2': text2,
            'encoded1': encoded1['encoded'],
            'encoded2': encoded2['encoded'],
            'encoding': encoding,
            'format': format_type,
            'texts_equal': text1 == text2,
            'encoded_equal': encoded1['encoded'] == encoded2['encoded'],
            'compared_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(comparison)
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при сравнении Base64'}), 500

@base64_encoder_bp.route('/api/base64/batch', methods=['POST'])
@login_required
def batch_base64():
    """Пакетное кодирование/декодирование Base64"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        operation = data.get('operation', 'encode')  # encode, decode
        encoding = data.get('encoding', 'utf-8')
        format_type = data.get('format', 'standard')
        
        if not texts or len(texts) > 100:
            return jsonify({'error': 'Укажите от 1 до 100 текстов'}), 400
        
        results = []
        
        for text in texts:
            if operation == 'encode':
                result = encode_to_base64(text, encoding, format_type)
                if result:
                    results.append({
                        'text': text,
                        'result': result['encoded'],
                        'success': True
                    })
                else:
                    results.append({
                        'text': text,
                        'result': None,
                        'success': False,
                        'error': 'Ошибка при кодировании'
                    })
            else:  # decode
                result = decode_from_base64(text, encoding, format_type)
                if result:
                    results.append({
                        'text': text,
                        'result': result['decoded'],
                        'success': True
                    })
                else:
                    results.append({
                        'text': text,
                        'result': None,
                        'success': False,
                        'error': 'Ошибка при декодировании'
                    })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'operation': operation,
            'encoding': encoding,
            'format': format_type,
            'processed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при пакетной обработке Base64'}), 500

@base64_encoder_bp.route('/api/base64/formats', methods=['GET'])
def get_base64_formats():
    """Получение доступных форматов Base64"""
    try:
        formats = {
            'standard': {
                'name': 'Стандартный Base64',
                'description': 'Стандартное кодирование Base64 с символами + и /',
                'alphabet': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                'padding': '=',
                'use_case': 'Общее использование'
            },
            'url_safe': {
                'name': 'URL-безопасный Base64',
                'description': 'Base64 с заменой + на - и / на _',
                'alphabet': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_',
                'padding': '=',
                'use_case': 'Использование в URL'
            },
            'custom': {
                'name': 'Пользовательский Base64',
                'description': 'Base64 с пользовательским алфавитом',
                'alphabet': 'Настраивается пользователем',
                'padding': 'Настраивается пользователем',
                'use_case': 'Специальные случаи'
            }
        }
        
        return jsonify({'formats': formats})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении форматов Base64'}), 500

@base64_encoder_bp.route('/api/base64/analyze', methods=['POST'])
@login_required
def analyze_base64():
    """Анализ Base64"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        format_type = data.get('format', 'standard')
        
        if not text:
            return jsonify({'error': 'Текст для анализа не указан'}), 400
        
        # Анализ Base64
        analysis = analyze_base64_text(text, format_type)
        
        return jsonify({
            'text': text,
            'format': format_type,
            'analysis': analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при анализе Base64'}), 500

def encode_to_base64(text, encoding, format_type):
    """Кодирование текста в Base64"""
    try:
        # Кодирование текста в байты
        text_bytes = text.encode(encoding)
        
        # Выбор формата Base64
        if format_type == 'standard':
            encoded_bytes = base64.b64encode(text_bytes)
        elif format_type == 'url_safe':
            encoded_bytes = base64.urlsafe_b64encode(text_bytes)
        else:  # custom
            encoded_bytes = base64.b64encode(text_bytes)
        
        # Декодирование в строку
        encoded_text = encoded_bytes.decode('ascii')
        
        return {
            'encoded': encoded_text,
            'encoding': encoding,
            'format': format_type
        }
        
    except Exception:
        return None

def decode_from_base64(encoded_text, encoding, format_type):
    """Декодирование текста из Base64"""
    try:
        # Кодирование строки в байты
        encoded_bytes = encoded_text.encode('ascii')
        
        # Выбор формата Base64
        if format_type == 'standard':
            decoded_bytes = base64.b64decode(encoded_bytes)
        elif format_type == 'url_safe':
            decoded_bytes = base64.urlsafe_b64decode(encoded_bytes)
        else:  # custom
            decoded_bytes = base64.b64decode(encoded_bytes)
        
        # Декодирование в текст
        decoded_text = decoded_bytes.decode(encoding)
        
        return {
            'decoded': decoded_text,
            'encoding': encoding,
            'format': format_type
        }
        
    except Exception:
        return None

def validate_base64_text(text, format_type):
    """Валидация Base64 текста"""
    try:
        # Проверка базовых характеристик
        if not text:
            return False
        
        # Проверка длины (должна быть кратна 4)
        if len(text) % 4 != 0:
            return False
        
        # Проверка символов
        if format_type == 'standard':
            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        elif format_type == 'url_safe':
            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=')
        else:
            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        
        if not set(text).issubset(valid_chars):
            return False
        
        # Попытка декодирования
        try:
            if format_type == 'standard':
                base64.b64decode(text)
            elif format_type == 'url_safe':
                base64.urlsafe_b64decode(text)
            else:
                base64.b64decode(text)
            return True
        except binascii.Error:
            return False
        
    except Exception:
        return False

def analyze_base64_text(text, format_type):
    """Анализ Base64 текста"""
    try:
        analysis = {
            'length': len(text),
            'is_valid': validate_base64_text(text, format_type),
            'format': format_type,
            'character_count': {},
            'padding_count': text.count('='),
            'estimated_original_length': 0
        }
        
        # Подсчет символов
        for char in text:
            analysis['character_count'][char] = analysis['character_count'].get(char, 0) + 1
        
        # Оценка длины оригинального текста
        if analysis['is_valid']:
            try:
                if format_type == 'standard':
                    decoded_bytes = base64.b64decode(text)
                elif format_type == 'url_safe':
                    decoded_bytes = base64.urlsafe_b64decode(text)
                else:
                    decoded_bytes = base64.b64decode(text)
                
                analysis['estimated_original_length'] = len(decoded_bytes)
            except:
                analysis['estimated_original_length'] = 0
        
        # Определение типа данных
        if analysis['is_valid']:
            try:
                if format_type == 'standard':
                    decoded_bytes = base64.b64decode(text)
                elif format_type == 'url_safe':
                    decoded_bytes = base64.urlsafe_b64decode(text)
                else:
                    decoded_bytes = base64.b64decode(text)
                
                # Попытка декодирования как текст
                try:
                    decoded_text = decoded_bytes.decode('utf-8')
                    analysis['data_type'] = 'text'
                    analysis['encoding'] = 'utf-8'
                except:
                    analysis['data_type'] = 'binary'
                    analysis['encoding'] = 'unknown'
                
            except:
                analysis['data_type'] = 'unknown'
                analysis['encoding'] = 'unknown'
        else:
            analysis['data_type'] = 'invalid'
            analysis['encoding'] = 'unknown'
        
        return analysis
        
    except Exception:
        return {
            'length': 0,
            'is_valid': False,
            'format': format_type,
            'character_count': {},
            'padding_count': 0,
            'estimated_original_length': 0,
            'data_type': 'unknown',
            'encoding': 'unknown'
        }

def get_base64_encoder_statistics(user_id):
    """Получение статистики использования Base64 кодировщика"""
    # Здесь можно добавить статистику использования
    return {
        'encodings_count': 0,
        'decodings_count': 0,
        'most_used_format': 'standard',
        'most_used_encoding': 'utf-8',
        'total_batches': 0
    }

def get_base64_encoder_tips():
    """Получение советов по использованию Base64"""
    tips = [
        "Base64 используется для кодирования бинарных данных в текстовый формат",
        "URL-безопасный Base64 подходит для использования в URL",
        "Base64 увеличивает размер данных примерно на 33%",
        "Всегда проверяйте валидность Base64 перед декодированием",
        "Используйте правильную кодировку для текстовых данных",
        "Base64 не является шифрованием - это только кодирование",
        "Для больших объемов данных используйте пакетную обработку",
        "Помните о ограничениях длины Base64 в различных системах"
    ]
    
    return tips
