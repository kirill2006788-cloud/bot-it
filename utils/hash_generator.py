from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import hashlib
import hmac
import secrets
import base64
from datetime import datetime

hash_generator_bp = Blueprint('hash_generator', __name__)

# Поддерживаемые алгоритмы хеширования
HASH_ALGORITHMS = {
    'md5': {
        'name': 'MD5',
        'description': 'Message Digest 5 - устаревший алгоритм',
        'output_length': 32,
        'secure': False,
        'use_case': 'Не рекомендуется для безопасности'
    },
    'sha1': {
        'name': 'SHA-1',
        'description': 'Secure Hash Algorithm 1 - устаревший алгоритм',
        'output_length': 40,
        'secure': False,
        'use_case': 'Не рекомендуется для безопасности'
    },
    'sha256': {
        'name': 'SHA-256',
        'description': 'Secure Hash Algorithm 256 - рекомендуемый алгоритм',
        'output_length': 64,
        'secure': True,
        'use_case': 'Рекомендуется для большинства случаев'
    },
    'sha512': {
        'name': 'SHA-512',
        'description': 'Secure Hash Algorithm 512 - более длинный хеш',
        'output_length': 128,
        'secure': True,
        'use_case': 'Для высоких требований безопасности'
    },
    'sha3_256': {
        'name': 'SHA-3-256',
        'description': 'SHA-3 с выходной длиной 256 бит',
        'output_length': 64,
        'secure': True,
        'use_case': 'Современный стандарт'
    },
    'sha3_512': {
        'name': 'SHA-3-512',
        'description': 'SHA-3 с выходной длиной 512 бит',
        'output_length': 128,
        'secure': True,
        'use_case': 'Высокая безопасность'
    },
    'blake2b': {
        'name': 'BLAKE2b',
        'description': 'Быстрый криптографический хеш',
        'output_length': 64,
        'secure': True,
        'use_case': 'Высокая производительность'
    },
    'blake2s': {
        'name': 'BLAKE2s',
        'description': 'Быстрый криптографический хеш (32 байта)',
        'output_length': 64,
        'secure': True,
        'use_case': 'Высокая производительность'
    }
}

@hash_generator_bp.route('/api/hash/generate', methods=['POST'])
@login_required
def generate_hash():
    """Генерация хеша"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        algorithm = data.get('algorithm', 'sha256')
        encoding = data.get('encoding', 'utf-8')
        output_format = data.get('format', 'hex')  # hex, base64, binary
        
        if not text:
            return jsonify({'error': 'Текст для хеширования не указан'}), 400
        
        if algorithm not in HASH_ALGORITHMS:
            return jsonify({'error': 'Неподдерживаемый алгоритм хеширования'}), 400
        
        # Генерация хеша
        hash_result = generate_hash_value(text, algorithm, encoding, output_format)
        
        if hash_result is None:
            return jsonify({'error': 'Ошибка при генерации хеша'}), 500
        
        return jsonify({
            'text': text,
            'algorithm': algorithm,
            'hash': hash_result['hash'],
            'format': output_format,
            'length': len(hash_result['hash']),
            'algorithm_info': HASH_ALGORITHMS[algorithm],
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации хеша'}), 500

@hash_generator_bp.route('/api/hash/verify', methods=['POST'])
@login_required
def verify_hash():
    """Проверка хеша"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        hash_value = data.get('hash', '')
        algorithm = data.get('algorithm', 'sha256')
        encoding = data.get('encoding', 'utf-8')
        
        if not text or not hash_value:
            return jsonify({'error': 'Текст и хеш должны быть указаны'}), 400
        
        if algorithm not in HASH_ALGORITHMS:
            return jsonify({'error': 'Неподдерживаемый алгоритм хеширования'}), 400
        
        # Генерация хеша для сравнения
        generated_hash = generate_hash_value(text, algorithm, encoding, 'hex')
        
        if generated_hash is None:
            return jsonify({'error': 'Ошибка при генерации хеша'}), 500
        
        # Сравнение хешей
        is_valid = generated_hash['hash'].lower() == hash_value.lower()
        
        return jsonify({
            'text': text,
            'provided_hash': hash_value,
            'generated_hash': generated_hash['hash'],
            'algorithm': algorithm,
            'is_valid': is_valid,
            'verified_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при проверке хеша'}), 500

@hash_generator_bp.route('/api/hash/hmac', methods=['POST'])
@login_required
def generate_hmac():
    """Генерация HMAC"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        key = data.get('key', '')
        algorithm = data.get('algorithm', 'sha256')
        encoding = data.get('encoding', 'utf-8')
        output_format = data.get('format', 'hex')
        
        if not text or not key:
            return jsonify({'error': 'Текст и ключ должны быть указаны'}), 400
        
        if algorithm not in HASH_ALGORITHMS:
            return jsonify({'error': 'Неподдерживаемый алгоритм хеширования'}), 400
        
        # Генерация HMAC
        hmac_result = generate_hmac_value(text, key, algorithm, encoding, output_format)
        
        if hmac_result is None:
            return jsonify({'error': 'Ошибка при генерации HMAC'}), 500
        
        return jsonify({
            'text': text,
            'key': key,
            'hmac': hmac_result['hmac'],
            'algorithm': algorithm,
            'format': output_format,
            'length': len(hmac_result['hmac']),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации HMAC'}), 500

@hash_generator_bp.route('/api/hash/password', methods=['POST'])
@login_required
def hash_password():
    """Хеширование пароля"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        salt = data.get('salt', '')
        algorithm = data.get('algorithm', 'sha256')
        iterations = int(data.get('iterations', 100000))
        
        if not password:
            return jsonify({'error': 'Пароль не указан'}), 400
        
        # Генерация соли если не указана
        if not salt:
            salt = secrets.token_hex(16)
        
        # Хеширование пароля
        hashed_password = hash_password_with_salt(password, salt, algorithm, iterations)
        
        if hashed_password is None:
            return jsonify({'error': 'Ошибка при хешировании пароля'}), 500
        
        return jsonify({
            'password': password,
            'salt': salt,
            'hashed_password': hashed_password,
            'algorithm': algorithm,
            'iterations': iterations,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при хешировании пароля'}), 500

@hash_generator_bp.route('/api/hash/algorithms', methods=['GET'])
def get_hash_algorithms():
    """Получение доступных алгоритмов хеширования"""
    try:
        return jsonify({'algorithms': HASH_ALGORITHMS})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении алгоритмов'}), 500

@hash_generator_bp.route('/api/hash/compare', methods=['POST'])
@login_required
def compare_hashes():
    """Сравнение хешей"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        hash1 = data.get('hash1', '')
        hash2 = data.get('hash2', '')
        algorithm = data.get('algorithm', 'sha256')
        encoding = data.get('encoding', 'utf-8')
        
        if not text or not hash1 or not hash2:
            return jsonify({'error': 'Текст и оба хеша должны быть указаны'}), 400
        
        if algorithm not in HASH_ALGORITHMS:
            return jsonify({'error': 'Неподдерживаемый алгоритм хеширования'}), 400
        
        # Генерация хеша для сравнения
        generated_hash = generate_hash_value(text, algorithm, encoding, 'hex')
        
        if generated_hash is None:
            return jsonify({'error': 'Ошибка при генерации хеша'}), 500
        
        # Сравнение хешей
        comparison = {
            'text': text,
            'generated_hash': generated_hash['hash'],
            'hash1': hash1,
            'hash2': hash2,
            'algorithm': algorithm,
            'hash1_matches': generated_hash['hash'].lower() == hash1.lower(),
            'hash2_matches': generated_hash['hash'].lower() == hash2.lower(),
            'hashes_match': hash1.lower() == hash2.lower(),
            'compared_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(comparison)
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при сравнении хешей'}), 500

@hash_generator_bp.route('/api/hash/batch', methods=['POST'])
@login_required
def batch_generate_hashes():
    """Пакетная генерация хешей"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        algorithm = data.get('algorithm', 'sha256')
        encoding = data.get('encoding', 'utf-8')
        output_format = data.get('format', 'hex')
        
        if not texts or len(texts) > 100:
            return jsonify({'error': 'Укажите от 1 до 100 текстов'}), 400
        
        if algorithm not in HASH_ALGORITHMS:
            return jsonify({'error': 'Неподдерживаемый алгоритм хеширования'}), 400
        
        results = []
        
        for text in texts:
            hash_result = generate_hash_value(text, algorithm, encoding, output_format)
            
            if hash_result:
                results.append({
                    'text': text,
                    'hash': hash_result['hash'],
                    'success': True
                })
            else:
                results.append({
                    'text': text,
                    'hash': None,
                    'success': False,
                    'error': 'Ошибка при генерации хеша'
                })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'algorithm': algorithm,
            'format': output_format,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при пакетной генерации хешей'}), 500

def generate_hash_value(text, algorithm, encoding, output_format):
    """Генерация хеша для текста"""
    try:
        # Кодирование текста
        text_bytes = text.encode(encoding)
        
        # Выбор алгоритма хеширования
        if algorithm == 'md5':
            hash_obj = hashlib.md5(text_bytes)
        elif algorithm == 'sha1':
            hash_obj = hashlib.sha1(text_bytes)
        elif algorithm == 'sha256':
            hash_obj = hashlib.sha256(text_bytes)
        elif algorithm == 'sha512':
            hash_obj = hashlib.sha512(text_bytes)
        elif algorithm == 'sha3_256':
            hash_obj = hashlib.sha3_256(text_bytes)
        elif algorithm == 'sha3_512':
            hash_obj = hashlib.sha3_512(text_bytes)
        elif algorithm == 'blake2b':
            hash_obj = hashlib.blake2b(text_bytes)
        elif algorithm == 'blake2s':
            hash_obj = hashlib.blake2s(text_bytes)
        else:
            return None
        
        # Получение хеша в нужном формате
        if output_format == 'hex':
            hash_value = hash_obj.hexdigest()
        elif output_format == 'base64':
            hash_value = base64.b64encode(hash_obj.digest()).decode('utf-8')
        elif output_format == 'binary':
            hash_value = hash_obj.digest().hex()
        else:
            hash_value = hash_obj.hexdigest()
        
        return {
            'hash': hash_value,
            'algorithm': algorithm,
            'format': output_format
        }
        
    except Exception:
        return None

def generate_hmac_value(text, key, algorithm, encoding, output_format):
    """Генерация HMAC для текста"""
    try:
        # Кодирование текста и ключа
        text_bytes = text.encode(encoding)
        key_bytes = key.encode(encoding)
        
        # Выбор алгоритма хеширования для HMAC
        if algorithm == 'md5':
            hash_func = hashlib.md5
        elif algorithm == 'sha1':
            hash_func = hashlib.sha1
        elif algorithm == 'sha256':
            hash_func = hashlib.sha256
        elif algorithm == 'sha512':
            hash_func = hashlib.sha512
        elif algorithm == 'sha3_256':
            hash_func = hashlib.sha3_256
        elif algorithm == 'sha3_512':
            hash_func = hashlib.sha3_512
        elif algorithm == 'blake2b':
            hash_func = hashlib.blake2b
        elif algorithm == 'blake2s':
            hash_func = hashlib.blake2s
        else:
            return None
        
        # Генерация HMAC
        hmac_obj = hmac.new(key_bytes, text_bytes, hash_func)
        
        # Получение HMAC в нужном формате
        if output_format == 'hex':
            hmac_value = hmac_obj.hexdigest()
        elif output_format == 'base64':
            hmac_value = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        elif output_format == 'binary':
            hmac_value = hmac_obj.digest().hex()
        else:
            hmac_value = hmac_obj.hexdigest()
        
        return {
            'hmac': hmac_value,
            'algorithm': algorithm,
            'format': output_format
        }
        
    except Exception:
        return None

def hash_password_with_salt(password, salt, algorithm, iterations):
    """Хеширование пароля с солью"""
    try:
        # Кодирование пароля и соли
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        # Выбор алгоритма хеширования
        if algorithm == 'sha256':
            hash_func = hashlib.sha256
        elif algorithm == 'sha512':
            hash_func = hashlib.sha512
        else:
            hash_func = hashlib.sha256
        
        # Хеширование с итерациями
        hash_obj = hash_func(salt_bytes + password_bytes)
        
        for _ in range(iterations - 1):
            hash_obj = hash_func(hash_obj.digest())
        
        return hash_obj.hexdigest()
        
    except Exception:
        return None

def get_hash_generator_statistics(user_id):
    """Получение статистики использования генератора хешей"""
    # Здесь можно добавить статистику использования
    return {
        'hashes_generated': 0,
        'most_used_algorithm': 'sha256',
        'most_used_format': 'hex',
        'total_batches': 0
    }

def get_hash_generator_tips():
    """Получение советов по использованию хешей"""
    tips = [
        "Используйте SHA-256 или SHA-512 для большинства случаев",
        "MD5 и SHA-1 устарели и не рекомендуются для безопасности",
        "HMAC обеспечивает дополнительную безопасность с ключом",
        "Всегда используйте соль при хешировании паролей",
        "Проверяйте хеши для обеспечения целостности данных",
        "SHA-3 и BLAKE2 - современные и безопасные алгоритмы",
        "Для паролей используйте специальные функции как bcrypt",
        "Храните хеши в безопасном месте"
    ]
    
    return tips
