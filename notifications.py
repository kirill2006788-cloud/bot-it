from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Notification, User
from datetime import datetime, timedelta
import json

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Получение уведомлений пользователя"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': notifications.total,
                'pages': notifications.pages,
                'has_next': notifications.has_next,
                'has_prev': notifications.has_prev
            },
            'unread_count': Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении уведомлений'}), 500

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Отметить уведомление как прочитанное"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Уведомление не найдено'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'message': 'Уведомление отмечено как прочитанное'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении уведомления'}), 500

@notifications_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Отметить все уведомления как прочитанные"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        
        return jsonify({'message': 'Все уведомления отмечены как прочитанные'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении уведомлений'}), 500

@notifications_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """Удалить уведомление"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Уведомление не найдено'}), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({'message': 'Уведомление удалено'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при удалении уведомления'}), 500

@notifications_bp.route('/api/notifications/settings', methods=['GET'])
@login_required
def get_notification_settings():
    """Получение настроек уведомлений"""
    try:
        from models import UserSettings
        
        settings = UserSettings.query.filter_by(user_id=current_user.id).all()
        settings_dict = {setting.setting_key: setting.setting_value for setting in settings}
        
        return jsonify({
            'notifications_enabled': settings_dict.get('notifications_enabled', 'true') == 'true',
            'email_notifications': settings_dict.get('email_notifications', 'true') == 'true',
            'push_notifications': settings_dict.get('push_notifications', 'true') == 'true',
            'achievement_notifications': settings_dict.get('achievement_notifications', 'true') == 'true',
            'game_notifications': settings_dict.get('game_notifications', 'true') == 'true',
            'tool_notifications': settings_dict.get('tool_notifications', 'false') == 'true',
            'social_notifications': settings_dict.get('social_notifications', 'true') == 'true',
            'marketing_notifications': settings_dict.get('marketing_notifications', 'false') == 'true'
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении настроек уведомлений'}), 500

@notifications_bp.route('/api/notifications/settings', methods=['PUT'])
@login_required
def update_notification_settings():
    """Обновление настроек уведомлений"""
    try:
        from models import UserSettings
        
        data = request.get_json()
        
        settings_map = {
            'notifications_enabled': 'notifications_enabled',
            'email_notifications': 'email_notifications',
            'push_notifications': 'push_notifications',
            'achievement_notifications': 'achievement_notifications',
            'game_notifications': 'game_notifications',
            'tool_notifications': 'tool_notifications',
            'social_notifications': 'social_notifications',
            'marketing_notifications': 'marketing_notifications'
        }
        
        for key, db_key in settings_map.items():
            if key in data:
                setting = UserSettings.query.filter_by(
                    user_id=current_user.id, setting_key=db_key
                ).first()
                
                value = 'true' if data[key] else 'false'
                
                if setting:
                    setting.setting_value = value
                    setting.updated_at = datetime.utcnow()
                else:
                    setting = UserSettings(
                        user_id=current_user.id,
                        setting_key=db_key,
                        setting_value=value
                    )
                    db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'message': 'Настройки уведомлений обновлены'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении настроек'}), 500

def create_notification(user_id, title, message, type='info', action_url=None):
    """Создание уведомления"""
    try:
        # Проверяем настройки пользователя
        from models import UserSettings
        settings = UserSettings.query.filter_by(user_id=user_id).all()
        settings_dict = {setting.setting_key: setting.setting_value for setting in settings}
        
        # Проверяем, включены ли уведомления
        if settings_dict.get('notifications_enabled', 'true') != 'true':
            return False
        
        # Проверяем тип уведомления
        if type == 'achievement' and settings_dict.get('achievement_notifications', 'true') != 'true':
            return False
        elif type == 'game' and settings_dict.get('game_notifications', 'true') != 'true':
            return False
        elif type == 'tool' and settings_dict.get('tool_notifications', 'false') != 'true':
            return False
        elif type == 'social' and settings_dict.get('social_notifications', 'true') != 'true':
            return False
        elif type == 'marketing' and settings_dict.get('marketing_notifications', 'false') != 'true':
            return False
        
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            action_url=action_url
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при создании уведомления: {e}")
        return False

def create_bulk_notification(user_ids, title, message, type='info', action_url=None):
    """Создание массового уведомления"""
    try:
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                action_url=action_url
            )
            notifications.append(notification)
        
        db.session.add_all(notifications)
        db.session.commit()
        
        return len(notifications)
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при создании массовых уведомлений: {e}")
        return 0

def create_achievement_notification(user_id, achievement_name, achievement_description):
    """Создание уведомления о достижении"""
    return create_notification(
        user_id=user_id,
        title=f"🎉 Новое достижение: {achievement_name}",
        message=achievement_description,
        type='achievement',
        action_url='/achievements'
    )

def create_game_notification(user_id, game_type, score, message):
    """Создание уведомления о игре"""
    return create_notification(
        user_id=user_id,
        title=f"🎮 {game_type.title()}",
        message=message,
        type='game',
        action_url='/games'
    )

def create_tool_notification(user_id, tool_name, result_message):
    """Создание уведомления об использовании инструмента"""
    return create_notification(
        user_id=user_id,
        title=f"🛠️ {tool_name}",
        message=result_message,
        type='tool',
        action_url='/tools'
    )

def create_social_notification(user_id, title, message, action_url=None):
    """Создание социального уведомления"""
    return create_notification(
        user_id=user_id,
        title=title,
        message=message,
        type='social',
        action_url=action_url
    )

def create_system_notification(user_id, title, message, type='info'):
    """Создание системного уведомления"""
    return create_notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type
    )

def create_marketing_notification(user_ids, title, message, action_url=None):
    """Создание маркетингового уведомления"""
    return create_bulk_notification(
        user_ids=user_ids,
        title=title,
        message=message,
        type='marketing',
        action_url=action_url
    )

def cleanup_old_notifications(days=30):
    """Очистка старых уведомлений"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Удаляем прочитанные уведомления старше указанного количества дней
        deleted_count = Notification.query.filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()
        
        db.session.commit()
        
        print(f"✅ Удалено {deleted_count} старых уведомлений")
        return deleted_count
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при очистке уведомлений: {e}")
        return 0

def get_notification_stats():
    """Получение статистики уведомлений"""
    try:
        total_notifications = Notification.query.count()
        unread_notifications = Notification.query.filter_by(is_read=False).count()
        
        # Статистика по типам
        type_stats = db.session.query(
            Notification.type,
            db.func.count(Notification.id).label('count')
        ).group_by(Notification.type).all()
        
        # Статистика за последние 7 дней
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_notifications = Notification.query.filter(
            Notification.created_at >= week_ago
        ).count()
        
        return {
            'total': total_notifications,
            'unread': unread_notifications,
            'recent': recent_notifications,
            'by_type': {stat.type: stat.count for stat in type_stats}
        }
        
    except Exception as e:
        print(f"Ошибка при получении статистики уведомлений: {e}")
        return {
            'total': 0,
            'unread': 0,
            'recent': 0,
            'by_type': {}
        }

def send_welcome_notifications(user_id):
    """Отправка приветственных уведомлений новому пользователю"""
    notifications = [
        {
            'title': '🎉 Добро пожаловать в IT Helper Bot!',
            'message': 'Исследуйте все возможности бота: игры, инструменты и достижения!',
            'type': 'info',
            'action_url': '/'
        },
        {
            'title': '🎮 Попробуйте игры',
            'message': 'Начните с игры "Угадай число" или викторины по программированию!',
            'type': 'game',
            'action_url': '/games'
        },
        {
            'title': '🛠️ Используйте инструменты',
            'message': 'Генератор паролей, QR-коды, погода и многое другое!',
            'type': 'tool',
            'action_url': '/tools'
        },
        {
            'title': '🏆 Зарабатывайте достижения',
            'message': 'Выполняйте различные задачи и получайте бейджи!',
            'type': 'achievement',
            'action_url': '/achievements'
        }
    ]
    
    for notification_data in notifications:
        create_notification(
            user_id=user_id,
            title=notification_data['title'],
            message=notification_data['message'],
            type=notification_data['type'],
            action_url=notification_data['action_url']
        )

def send_daily_notifications():
    """Отправка ежедневных уведомлений"""
    try:
        # Получаем активных пользователей
        active_users = User.query.filter_by(is_active=True).all()
        
        for user in active_users:
            # Проверяем, когда пользователь последний раз заходил
            if user.last_login and (datetime.utcnow() - user.last_login).days >= 1:
                create_notification(
                    user_id=user.id,
                    title='👋 Мы скучаем!',
                    message='Возвращайтесь в IT Helper Bot и продолжайте зарабатывать достижения!',
                    type='marketing',
                    action_url='/'
                )
        
        print(f"✅ Отправлены ежедневные уведомления {len(active_users)} пользователям")
        
    except Exception as e:
        print(f"❌ Ошибка при отправке ежедневных уведомлений: {e}")

def send_feature_announcement(title, message, action_url=None):
    """Отправка объявления о новой функции"""
    try:
        # Получаем всех активных пользователей
        active_users = User.query.filter_by(is_active=True).all()
        user_ids = [user.id for user in active_users]
        
        return create_marketing_notification(
            user_ids=user_ids,
            title=title,
            message=message,
            action_url=action_url
        )
        
    except Exception as e:
        print(f"❌ Ошибка при отправке объявления: {e}")
        return 0
