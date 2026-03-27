from flask import Blueprint, jsonify, request, g
from flask_login import login_required, current_user
from models import db, User, ApiKey, ApiKeyUsage
import secrets
import hashlib
from datetime import datetime, timedelta
import json

api_keys_bp = Blueprint('api_keys', __name__)

@api_keys_bp.route('/api/keys/generate', methods=['POST'])
@login_required
def generate_api_key():
    """Генерация нового API ключа"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        description = data.get('description', '')
        permissions = data.get('permissions', [])
        expires_in_days = data.get('expires_in_days', None)
        rate_limit = data.get('rate_limit', 1000)  # запросов в час
        
        if not name:
            return jsonify({'error': 'Название API ключа обязательно'}), 400
        
        # Генерация API ключа
        api_key_value = generate_api_key_value()
        api_key_hash = hash_api_key(api_key_value)
        
        # Определение даты истечения
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Создание записи в базе данных
        api_key = ApiKey(
            user_id=current_user.id,
            name=name,
            description=description,
            key_hash=api_key_hash,
            permissions=json.dumps(permissions),
            rate_limit=rate_limit,
            expires_at=expires_at,
            is_active=True
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        return jsonify({
            'api_key': api_key_value,
            'key_id': api_key.id,
            'name': name,
            'description': description,
            'permissions': permissions,
            'rate_limit': rate_limit,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'created_at': api_key.created_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при генерации API ключа'}), 500

@api_keys_bp.route('/api/keys', methods=['GET'])
@login_required
def get_api_keys():
    """Получение списка API ключей пользователя"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Получение API ключей пользователя
        api_keys_query = ApiKey.query.filter_by(user_id=current_user.id)
        
        # Пагинация
        api_keys = api_keys_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        keys_data = []
        for key in api_keys.items:
            keys_data.append({
                'id': key.id,
                'name': key.name,
                'description': key.description,
                'permissions': json.loads(key.permissions) if key.permissions else [],
                'rate_limit': key.rate_limit,
                'is_active': key.is_active,
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'created_at': key.created_at.isoformat(),
                'last_used_at': key.last_used_at.isoformat() if key.last_used_at else None,
                'usage_count': key.usage_count
            })
        
        return jsonify({
            'api_keys': keys_data,
            'total': api_keys.total,
            'page': page,
            'per_page': per_page,
            'pages': api_keys.pages
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении API ключей'}), 500

@api_keys_bp.route('/api/keys/<int:key_id>', methods=['GET'])
@login_required
def get_api_key(key_id):
    """Получение конкретного API ключа"""
    try:
        api_key = ApiKey.query.filter_by(
            id=key_id, 
            user_id=current_user.id
        ).first()
        
        if not api_key:
            return jsonify({'error': 'API ключ не найден'}), 404
        
        return jsonify({
            'id': api_key.id,
            'name': api_key.name,
            'description': api_key.description,
            'permissions': json.loads(api_key.permissions) if api_key.permissions else [],
            'rate_limit': api_key.rate_limit,
            'is_active': api_key.is_active,
            'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None,
            'created_at': api_key.created_at.isoformat(),
            'last_used_at': api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            'usage_count': api_key.usage_count
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении API ключа'}), 500

@api_keys_bp.route('/api/keys/<int:key_id>', methods=['PUT'])
@login_required
def update_api_key(key_id):
    """Обновление API ключа"""
    try:
        data = request.get_json()
        api_key = ApiKey.query.filter_by(
            id=key_id, 
            user_id=current_user.id
        ).first()
        
        if not api_key:
            return jsonify({'error': 'API ключ не найден'}), 404
        
        # Обновление полей
        if 'name' in data:
            api_key.name = data['name']
        if 'description' in data:
            api_key.description = data['description']
        if 'permissions' in data:
            api_key.permissions = json.dumps(data['permissions'])
        if 'rate_limit' in data:
            api_key.rate_limit = data['rate_limit']
        if 'is_active' in data:
            api_key.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'API ключ обновлен',
            'api_key': {
                'id': api_key.id,
                'name': api_key.name,
                'description': api_key.description,
                'permissions': json.loads(api_key.permissions) if api_key.permissions else [],
                'rate_limit': api_key.rate_limit,
                'is_active': api_key.is_active
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении API ключа'}), 500

@api_keys_bp.route('/api/keys/<int:key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id):
    """Удаление API ключа"""
    try:
        api_key = ApiKey.query.filter_by(
            id=key_id, 
            user_id=current_user.id
        ).first()
        
        if not api_key:
            return jsonify({'error': 'API ключ не найден'}), 404
        
        # Удаление связанных записей об использовании
        ApiKeyUsage.query.filter_by(api_key_id=key_id).delete()
        
        # Удаление API ключа
        db.session.delete(api_key)
        db.session.commit()
        
        return jsonify({'message': 'API ключ удален'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при удалении API ключа'}), 500

@api_keys_bp.route('/api/keys/<int:key_id>/regenerate', methods=['POST'])
@login_required
def regenerate_api_key(key_id):
    """Перегенерация API ключа"""
    try:
        api_key = ApiKey.query.filter_by(
            id=key_id, 
            user_id=current_user.id
        ).first()
        
        if not api_key:
            return jsonify({'error': 'API ключ не найден'}), 404
        
        # Генерация нового ключа
        new_api_key_value = generate_api_key_value()
        new_api_key_hash = hash_api_key(new_api_key_value)
        
        # Обновление хеша
        api_key.key_hash = new_api_key_hash
        api_key.last_used_at = None
        api_key.usage_count = 0
        
        db.session.commit()
        
        return jsonify({
            'api_key': new_api_key_value,
            'message': 'API ключ перегенерирован'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при перегенерации API ключа'}), 500

@api_keys_bp.route('/api/keys/<int:key_id>/usage', methods=['GET'])
@login_required
def get_api_key_usage(key_id):
    """Получение статистики использования API ключа"""
    try:
        api_key = ApiKey.query.filter_by(
            id=key_id, 
            user_id=current_user.id
        ).first()
        
        if not api_key:
            return jsonify({'error': 'API ключ не найден'}), 404
        
        # Получение статистики использования
        usage_stats = get_usage_statistics(key_id)
        
        return jsonify({
            'api_key_id': key_id,
            'usage_stats': usage_stats
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении статистики'}), 500

@api_keys_bp.route('/api/keys/validate', methods=['POST'])
def validate_api_key():
    """Валидация API ключа"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        required_permission = data.get('permission', None)
        
        if not api_key:
            return jsonify({'error': 'API ключ не указан'}), 400
        
        # Поиск API ключа
        api_key_hash = hash_api_key(api_key)
        api_key_obj = ApiKey.query.filter_by(
            key_hash=api_key_hash,
            is_active=True
        ).first()
        
        if not api_key_obj:
            return jsonify({
                'valid': False,
                'error': 'Неверный или неактивный API ключ'
            })
        
        # Проверка истечения
        if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
            return jsonify({
                'valid': False,
                'error': 'API ключ истек'
            })
        
        # Проверка разрешений
        permissions = json.loads(api_key_obj.permissions) if api_key_obj.permissions else []
        if required_permission and required_permission not in permissions:
            return jsonify({
                'valid': False,
                'error': 'Недостаточно прав доступа'
            })
        
        # Обновление статистики использования
        update_usage_statistics(api_key_obj.id)
        
        return jsonify({
            'valid': True,
            'user_id': api_key_obj.user_id,
            'permissions': permissions,
            'rate_limit': api_key_obj.rate_limit
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при валидации API ключа'}), 500

def generate_api_key_value():
    """Генерация значения API ключа"""
    # Генерация случайной строки
    random_bytes = secrets.token_bytes(32)
    api_key = hashlib.sha256(random_bytes).hexdigest()
    
    # Добавление префикса
    return f"itb_{api_key}"

def hash_api_key(api_key):
    """Хеширование API ключа для хранения"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def update_usage_statistics(api_key_id):
    """Обновление статистики использования"""
    try:
        api_key = ApiKey.query.get(api_key_id)
        if api_key:
            api_key.usage_count += 1
            api_key.last_used_at = datetime.utcnow()
            db.session.commit()
        
        # Запись детальной статистики
        usage_record = ApiKeyUsage(
            api_key_id=api_key_id,
            used_at=datetime.utcnow(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            endpoint=request.endpoint or 'unknown'
        )
        
        db.session.add(usage_record)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()

def get_usage_statistics(api_key_id):
    """Получение статистики использования"""
    try:
        # Общая статистика
        api_key = ApiKey.query.get(api_key_id)
        if not api_key:
            return {}
        
        # Статистика за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_usage = ApiKeyUsage.query.filter(
            ApiKeyUsage.api_key_id == api_key_id,
            ApiKeyUsage.used_at >= thirty_days_ago
        ).count()
        
        # Статистика по дням
        daily_usage = db.session.query(
            db.func.date(ApiKeyUsage.used_at).label('date'),
            db.func.count(ApiKeyUsage.id).label('count')
        ).filter(
            ApiKeyUsage.api_key_id == api_key_id,
            ApiKeyUsage.used_at >= thirty_days_ago
        ).group_by(
            db.func.date(ApiKeyUsage.used_at)
        ).all()
        
        # Статистика по эндпоинтам
        endpoint_usage = db.session.query(
            ApiKeyUsage.endpoint,
            db.func.count(ApiKeyUsage.id).label('count')
        ).filter(
            ApiKeyUsage.api_key_id == api_key_id,
            ApiKeyUsage.used_at >= thirty_days_ago
        ).group_by(
            ApiKeyUsage.endpoint
        ).all()
        
        return {
            'total_usage': api_key.usage_count,
            'recent_usage_30_days': recent_usage,
            'daily_usage': [
                {'date': str(day.date), 'count': day.count} 
                for day in daily_usage
            ],
            'endpoint_usage': [
                {'endpoint': endpoint.endpoint, 'count': endpoint.count} 
                for endpoint in endpoint_usage
            ],
            'last_used_at': api_key.last_used_at.isoformat() if api_key.last_used_at else None
        }
        
    except Exception as e:
        return {}

def get_api_key_statistics(user_id):
    """Получение общей статистики API ключей пользователя"""
    try:
        # Общее количество ключей
        total_keys = ApiKey.query.filter_by(user_id=user_id).count()
        active_keys = ApiKey.query.filter_by(user_id=user_id, is_active=True).count()
        
        # Общее использование
        total_usage = db.session.query(
            db.func.sum(ApiKey.usage_count)
        ).filter_by(user_id=user_id).scalar() or 0
        
        # Ключи с истекающим сроком (в течение 7 дней)
        expiring_soon = ApiKey.query.filter(
            ApiKey.user_id == user_id,
            ApiKey.expires_at.isnot(None),
            ApiKey.expires_at <= datetime.utcnow() + timedelta(days=7)
        ).count()
        
        return {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'total_usage': total_usage,
            'expiring_soon': expiring_soon
        }
        
    except Exception as e:
        return {
            'total_keys': 0,
            'active_keys': 0,
            'total_usage': 0,
            'expiring_soon': 0
        }

def get_api_key_tips():
    """Получение советов по использованию API ключей"""
    tips = [
        "Храните API ключи в безопасном месте",
        "Используйте разные ключи для разных приложений",
        "Регулярно ротируйте API ключи",
        "Устанавливайте разумные лимиты запросов",
        "Мониторьте использование API ключей",
        "Удаляйте неиспользуемые ключи",
        "Используйте минимально необходимые разрешения",
        "Логируйте все запросы с API ключами"
    ]
    
    return tips
