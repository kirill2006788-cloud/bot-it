from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import uuid
import random
import string
from datetime import datetime

uuid_generator_bp = Blueprint('uuid_generator', __name__)

@uuid_generator_bp.route('/api/uuid/generate', methods=['POST'])
@login_required
def generate_uuid():
    """Генерация UUID"""
    try:
        data = request.get_json()
        uuid_type = data.get('type', 'uuid4')  # uuid1, uuid3, uuid4, uuid5
        count = int(data.get('count', 1))
        format_type = data.get('format', 'string')  # string, hex, int, urn
        
        if count < 1 or count > 100:
            return jsonify({'error': 'Количество должно быть от 1 до 100'}), 400
        
        uuids = []
        
        for _ in range(count):
            if uuid_type == 'uuid1':
                # UUID1 - основан на времени и MAC-адресе
                generated_uuid = uuid.uuid1()
            elif uuid_type == 'uuid3':
                # UUID3 - основан на MD5 хеше
                namespace = data.get('namespace', uuid.NAMESPACE_DNS)
                name = data.get('name', 'example.com')
                generated_uuid = uuid.uuid3(namespace, name)
            elif uuid_type == 'uuid4':
                # UUID4 - случайный
                generated_uuid = uuid.uuid4()
            elif uuid_type == 'uuid5':
                # UUID5 - основан на SHA-1 хеше
                namespace = data.get('namespace', uuid.NAMESPACE_DNS)
                name = data.get('name', 'example.com')
                generated_uuid = uuid.uuid5(namespace, name)
            else:
                return jsonify({'error': 'Неподдерживаемый тип UUID'}), 400
            
            # Форматирование
            if format_type == 'string':
                formatted_uuid = str(generated_uuid)
            elif format_type == 'hex':
                formatted_uuid = generated_uuid.hex
            elif format_type == 'int':
                formatted_uuid = generated_uuid.int
            elif format_type == 'urn':
                formatted_uuid = generated_uuid.urn
            else:
                formatted_uuid = str(generated_uuid)
            
            uuids.append({
                'uuid': formatted_uuid,
                'type': uuid_type,
                'format': format_type,
                'version': generated_uuid.version if hasattr(generated_uuid, 'version') else None,
                'variant': generated_uuid.variant if hasattr(generated_uuid, 'variant') else None
            })
        
        return jsonify({
            'uuids': uuids,
            'count': count,
            'type': uuid_type,
            'format': format_type,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации UUID'}), 500

@uuid_generator_bp.route('/api/uuid/validate', methods=['POST'])
@login_required
def validate_uuid():
    """Валидация UUID"""
    try:
        data = request.get_json()
        uuid_string = data.get('uuid', '').strip()
        
        if not uuid_string:
            return jsonify({'error': 'UUID не указан'}), 400
        
        try:
            # Попытка парсинга UUID
            parsed_uuid = uuid.UUID(uuid_string)
            
            return jsonify({
                'uuid': uuid_string,
                'valid': True,
                'version': parsed_uuid.version,
                'variant': parsed_uuid.variant,
                'hex': parsed_uuid.hex,
                'int': parsed_uuid.int,
                'urn': parsed_uuid.urn,
                'validated_at': datetime.utcnow().isoformat()
            })
            
        except ValueError:
            return jsonify({
                'uuid': uuid_string,
                'valid': False,
                'error': 'Неверный формат UUID',
                'validated_at': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации UUID'}), 500

@uuid_generator_bp.route('/api/uuid/convert', methods=['POST'])
@login_required
def convert_uuid():
    """Конвертация UUID между форматами"""
    try:
        data = request.get_json()
        uuid_string = data.get('uuid', '').strip()
        target_format = data.get('format', 'string')  # string, hex, int, urn
        
        if not uuid_string:
            return jsonify({'error': 'UUID не указан'}), 400
        
        try:
            # Парсинг UUID
            parsed_uuid = uuid.UUID(uuid_string)
            
            # Конвертация в целевой формат
            if target_format == 'string':
                converted = str(parsed_uuid)
            elif target_format == 'hex':
                converted = parsed_uuid.hex
            elif target_format == 'int':
                converted = parsed_uuid.int
            elif target_format == 'urn':
                converted = parsed_uuid.urn
            else:
                converted = str(parsed_uuid)
            
            return jsonify({
                'original_uuid': uuid_string,
                'converted_uuid': converted,
                'format': target_format,
                'version': parsed_uuid.version,
                'variant': parsed_uuid.variant,
                'converted_at': datetime.utcnow().isoformat()
            })
            
        except ValueError:
            return jsonify({'error': 'Неверный формат UUID'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при конвертации UUID'}), 500

@uuid_generator_bp.route('/api/uuid/compare', methods=['POST'])
@login_required
def compare_uuids():
    """Сравнение UUID"""
    try:
        data = request.get_json()
        uuid1 = data.get('uuid1', '').strip()
        uuid2 = data.get('uuid2', '').strip()
        
        if not uuid1 or not uuid2:
            return jsonify({'error': 'Необходимо указать два UUID'}), 400
        
        try:
            # Парсинг UUID
            parsed_uuid1 = uuid.UUID(uuid1)
            parsed_uuid2 = uuid.UUID(uuid2)
            
            # Сравнение
            comparison = {
                'uuid1': uuid1,
                'uuid2': uuid2,
                'equal': parsed_uuid1 == parsed_uuid2,
                'uuid1_version': parsed_uuid1.version,
                'uuid2_version': parsed_uuid2.version,
                'uuid1_variant': parsed_uuid1.variant,
                'uuid2_variant': parsed_uuid2.variant,
                'compared_at': datetime.utcnow().isoformat()
            }
            
            return jsonify(comparison)
            
        except ValueError as e:
            return jsonify({'error': f'Неверный формат UUID: {str(e)}'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при сравнении UUID'}), 500

@uuid_generator_bp.route('/api/uuid/namespaces', methods=['GET'])
def get_uuid_namespaces():
    """Получение доступных пространств имен UUID"""
    try:
        namespaces = {
            'DNS': {
                'name': 'DNS',
                'value': str(uuid.NAMESPACE_DNS),
                'description': 'Пространство имен DNS'
            },
            'URL': {
                'name': 'URL',
                'value': str(uuid.NAMESPACE_URL),
                'description': 'Пространство имен URL'
            },
            'OID': {
                'name': 'OID',
                'value': str(uuid.NAMESPACE_OID),
                'description': 'Пространство имен OID'
            },
            'X500': {
                'name': 'X500',
                'value': str(uuid.NAMESPACE_X500),
                'description': 'Пространство имен X.500'
            }
        }
        
        return jsonify({'namespaces': namespaces})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении пространств имен'}), 500

@uuid_generator_bp.route('/api/uuid/types', methods=['GET'])
def get_uuid_types():
    """Получение типов UUID"""
    try:
        types = {
            'uuid1': {
                'name': 'UUID1',
                'description': 'Основан на времени и MAC-адресе',
                'pros': ['Уникальность', 'Сортировка по времени'],
                'cons': ['Раскрывает MAC-адрес', 'Может быть предсказуемым']
            },
            'uuid3': {
                'name': 'UUID3',
                'description': 'Основан на MD5 хеше',
                'pros': ['Детерминированный', 'Быстрый'],
                'cons': ['MD5 устарел', 'Возможны коллизии']
            },
            'uuid4': {
                'name': 'UUID4',
                'description': 'Случайный UUID',
                'pros': ['Случайность', 'Безопасность'],
                'cons': ['Не детерминированный', 'Может быть медленным']
            },
            'uuid5': {
                'name': 'UUID5',
                'description': 'Основан на SHA-1 хеше',
                'pros': ['Детерминированный', 'Безопасный'],
                'cons': ['Медленнее UUID3', 'SHA-1 устарел']
            }
        }
        
        return jsonify({'types': types})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении типов UUID'}), 500

@uuid_generator_bp.route('/api/uuid/batch-generate', methods=['POST'])
@login_required
def batch_generate_uuids():
    """Пакетная генерация UUID"""
    try:
        data = request.get_json()
        batch_size = int(data.get('batch_size', 10))
        uuid_type = data.get('type', 'uuid4')
        format_type = data.get('format', 'string')
        
        if batch_size < 1 or batch_size > 1000:
            return jsonify({'error': 'Размер пакета должен быть от 1 до 1000'}), 400
        
        uuids = []
        
        for _ in range(batch_size):
            if uuid_type == 'uuid1':
                generated_uuid = uuid.uuid1()
            elif uuid_type == 'uuid4':
                generated_uuid = uuid.uuid4()
            else:
                generated_uuid = uuid.uuid4()
            
            # Форматирование
            if format_type == 'string':
                formatted_uuid = str(generated_uuid)
            elif format_type == 'hex':
                formatted_uuid = generated_uuid.hex
            elif format_type == 'int':
                formatted_uuid = generated_uuid.int
            elif format_type == 'urn':
                formatted_uuid = generated_uuid.urn
            else:
                formatted_uuid = str(generated_uuid)
            
            uuids.append(formatted_uuid)
        
        return jsonify({
            'uuids': uuids,
            'batch_size': batch_size,
            'type': uuid_type,
            'format': format_type,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при пакетной генерации UUID'}), 500

@uuid_generator_bp.route('/api/uuid/analyze', methods=['POST'])
@login_required
def analyze_uuid():
    """Анализ UUID"""
    try:
        data = request.get_json()
        uuid_string = data.get('uuid', '').strip()
        
        if not uuid_string:
            return jsonify({'error': 'UUID не указан'}), 400
        
        try:
            # Парсинг UUID
            parsed_uuid = uuid.UUID(uuid_string)
            
            # Анализ
            analysis = {
                'uuid': uuid_string,
                'version': parsed_uuid.version,
                'variant': parsed_uuid.variant,
                'hex': parsed_uuid.hex,
                'int': parsed_uuid.int,
                'urn': parsed_uuid.urn,
                'length': len(uuid_string),
                'format': 'standard' if '-' in uuid_string else 'compact',
                'analysis': {
                    'is_valid': True,
                    'version_info': get_version_info(parsed_uuid.version),
                    'variant_info': get_variant_info(parsed_uuid.variant),
                    'entropy': calculate_entropy(uuid_string),
                    'uniqueness': 'high' if parsed_uuid.version == 4 else 'medium'
                },
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
            return jsonify(analysis)
            
        except ValueError:
            return jsonify({
                'uuid': uuid_string,
                'is_valid': False,
                'error': 'Неверный формат UUID',
                'analyzed_at': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при анализе UUID'}), 500

def get_version_info(version):
    """Получение информации о версии UUID"""
    version_info = {
        1: 'Временной UUID с MAC-адресом',
        3: 'UUID на основе MD5 хеша',
        4: 'Случайный UUID',
        5: 'UUID на основе SHA-1 хеша'
    }
    return version_info.get(version, 'Неизвестная версия')

def get_variant_info(variant):
    """Получение информации о варианте UUID"""
    variant_info = {
        'reserved_ncs': 'Зарезервировано для NCS',
        'rfc_4122': 'RFC 4122',
        'reserved_microsoft': 'Зарезервировано для Microsoft',
        'reserved_future': 'Зарезервировано для будущего использования'
    }
    return variant_info.get(variant, 'Неизвестный вариант')

def calculate_entropy(uuid_string):
    """Расчет энтропии UUID"""
    # Простой расчет энтропии на основе уникальных символов
    unique_chars = len(set(uuid_string.lower()))
    total_chars = len(uuid_string)
    
    if total_chars == 0:
        return 0
    
    entropy = unique_chars / total_chars
    return round(entropy, 3)

def get_uuid_generator_statistics(user_id):
    """Получение статистики использования генератора UUID"""
    # Здесь можно добавить статистику использования
    return {
        'uuids_generated': 0,
        'most_used_type': 'uuid4',
        'most_used_format': 'string',
        'total_batches': 0
    }

def get_uuid_generator_tips():
    """Получение советов по использованию UUID"""
    tips = [
        "Используйте UUID4 для большинства случаев - он случайный и безопасный",
        "UUID1 хорош для сортировки по времени, но раскрывает MAC-адрес",
        "UUID3 и UUID5 детерминированы - одинаковый ввод даст одинаковый UUID",
        "Проверяйте валидность UUID перед использованием",
        "Для больших объемов используйте пакетную генерацию",
        "UUID4 имеет наивысшую энтропию и уникальность",
        "Используйте подходящий формат для вашего случая использования",
        "Помните о производительности - UUID4 может быть медленнее других типов"
    ]
    
    return tips
