from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserSettings, Achievement, UserAchievement
from config import SUPPORTED_LANGUAGES
import re
import secrets
import string
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Валидация email адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Валидация пароля"""
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    if not re.search(r'[A-Z]', password):
        return False, "Пароль должен содержать заглавную букву"
    if not re.search(r'[a-z]', password):
        return False, "Пароль должен содержать строчную букву"
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать цифру"
    return True, "Пароль валиден"

def generate_username_from_email(email):
    """Генерация username из email"""
    username = email.split('@')[0]
    # Убираем недопустимые символы
    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    # Добавляем случайные цифры если username уже существует
    original_username = username
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f"{original_username}{counter}"
        counter += 1
    return username

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    data = request.get_json()
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    language = data.get('language', 'ru')
    
    # Валидация
    if not email or not password:
        return jsonify({'error': 'Email и пароль обязательны'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Неверный формат email'}), 400
    
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    if language not in SUPPORTED_LANGUAGES:
        language = 'ru'
    
    # Проверка существования пользователя
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
    
    try:
        # Создание пользователя
        username = generate_username_from_email(email)
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            language=language
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Создание настроек по умолчанию
        default_settings = [
            ('notifications_enabled', 'true'),
            ('email_notifications', 'true'),
            ('theme', 'light'),
            ('privacy_level', '1'),
            ('game_difficulty', 'medium'),
            ('auto_save', 'true')
        ]
        
        for key, value in default_settings:
            setting = UserSettings(
                user_id=user.id,
                setting_key=key,
                setting_value=value
            )
            db.session.add(setting)
        
        db.session.commit()
        
        # Автоматический вход
        login_user(user)
        
        # Создание первого достижения
        create_welcome_achievement(user.id)
        
        return jsonify({
            'message': 'Регистрация успешна',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при регистрации'}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Вход пользователя"""
    data = request.get_json()
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not email or not password:
        return jsonify({'error': 'Email и пароль обязательны'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        if not user.is_active:
            return jsonify({'error': 'Аккаунт заблокирован'}), 403
        
        # Обновление времени последнего входа
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember)
        
        return jsonify({
            'message': 'Вход успешен',
            'user': user.to_dict()
        })
    else:
        return jsonify({'error': 'Неверный email или пароль'}), 401

@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Выход пользователя"""
    logout_user()
    return jsonify({'message': 'Выход успешен'})

@auth_bp.route('/api/auth/profile', methods=['GET'])
@login_required
def get_profile():
    """Получение профиля пользователя"""
    return jsonify({
        'user': current_user.to_dict(),
        'achievements': [ua.to_dict() for ua in current_user.achievements],
        'total_score': sum(gs.score for gs in current_user.game_scores)
    })

@auth_bp.route('/api/auth/profile', methods=['PUT'])
@login_required
def update_profile():
    """Обновление профиля пользователя"""
    data = request.get_json()
    
    try:
        # Обновление основных данных
        if 'first_name' in data:
            current_user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            current_user.last_name = data['last_name'].strip()
        if 'language' in data and data['language'] in SUPPORTED_LANGUAGES:
            current_user.language = data['language']
        if 'theme' in data and data['theme'] in ['light', 'dark']:
            current_user.theme = data['theme']
        if 'privacy_level' in data and data['privacy_level'] in [1, 2, 3]:
            current_user.privacy_level = data['privacy_level']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Профиль обновлен',
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении профиля'}), 500

@auth_bp.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Смена пароля"""
    data = request.get_json()
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Текущий и новый пароль обязательны'}), 400
    
    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'error': 'Неверный текущий пароль'}), 401
    
    is_valid, error_msg = validate_password(new_password)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    try:
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Пароль изменен успешно'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при смене пароля'}), 500

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Сброс пароля"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email обязателен'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    try:
        # Генерация временного пароля
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        user.password_hash = generate_password_hash(temp_password)
        db.session.commit()
        
        # Здесь должна быть отправка email с временным паролем
        # send_reset_password_email(user.email, temp_password)
        
        return jsonify({
            'message': 'Временный пароль отправлен на email',
            'temp_password': temp_password  # Только для демонстрации!
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при сбросе пароля'}), 500

@auth_bp.route('/api/auth/telegram-link', methods=['POST'])
@login_required
def link_telegram():
    """Привязка Telegram аккаунта"""
    data = request.get_json()
    telegram_id = data.get('telegram_id', '')
    
    if not telegram_id:
        return jsonify({'error': 'Telegram ID обязателен'}), 400
    
    # Проверка, не привязан ли уже этот Telegram ID
    existing_user = User.query.filter_by(telegram_id=telegram_id).first()
    if existing_user and existing_user.id != current_user.id:
        return jsonify({'error': 'Этот Telegram аккаунт уже привязан к другому пользователю'}), 400
    
    try:
        current_user.telegram_id = telegram_id
        db.session.commit()
        
        return jsonify({'message': 'Telegram аккаунт привязан успешно'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при привязке Telegram'}), 500

def create_welcome_achievement(user_id):
    """Создание достижения 'Добро пожаловать'"""
    try:
        achievement = Achievement.query.filter_by(name='Добро пожаловать').first()
        if not achievement:
            achievement = Achievement(
                name='Добро пожаловать',
                description='Зарегистрировались в IT Helper Bot',
                icon='🎉',
                category='social',
                points_required=0,
                badge_color='#28a745'
            )
            db.session.add(achievement)
            db.session.commit()
        
        # Проверяем, есть ли уже это достижение у пользователя
        existing = UserAchievement.query.filter_by(
            user_id=user_id, 
            achievement_id=achievement.id
        ).first()
        
        if not existing:
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                points_earned=10
            )
            db.session.add(user_achievement)
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при создании достижения: {e}")

def check_and_award_achievements(user_id, action_type, value=None):
    """Проверка и награждение достижений"""
    try:
        user = User.query.get(user_id)
        if not user:
            return
        
        # Достижения за игры
        if action_type == 'game_completed':
            game_scores = GameScore.query.filter_by(user_id=user_id).all()
            total_games = len(game_scores)
            
            # Первая игра
            if total_games == 1:
                award_achievement(user_id, 'Первая игра', 'Сыграли первую игру', '🎮', 'games', 20)
            
            # 10 игр
            elif total_games == 10:
                award_achievement(user_id, 'Игрок', 'Сыграли 10 игр', '🏆', 'games', 50)
            
            # 100 игр
            elif total_games == 100:
                award_achievement(user_id, 'Мастер игр', 'Сыграли 100 игр', '👑', 'games', 200)
        
        # Достижения за инструменты
        elif action_type == 'tool_used':
            tool_usages = ToolUsage.query.filter_by(user_id=user_id).all()
            total_tools = sum(tu.usage_count for tu in tool_usages)
            
            if total_tools == 1:
                award_achievement(user_id, 'Первый инструмент', 'Использовали первый инструмент', '🔧', 'tools', 15)
            elif total_tools == 50:
                award_achievement(user_id, 'Мастер инструментов', 'Использовали инструменты 50 раз', '⚙️', 'tools', 100)
        
        # Достижения за очки
        elif action_type == 'score_earned':
            total_score = sum(gs.score for gs in user.game_scores)
            
            if total_score >= 1000:
                award_achievement(user_id, 'Тысячник', 'Набрали 1000 очков', '💯', 'games', 100)
            elif total_score >= 5000:
                award_achievement(user_id, 'Пятитысячник', 'Набрали 5000 очков', '🌟', 'games', 300)
            elif total_score >= 10000:
                award_achievement(user_id, 'Десятитысячник', 'Набрали 10000 очков', '💎', 'games', 500)
                
    except Exception as e:
        print(f"Ошибка при проверке достижений: {e}")

def award_achievement(user_id, name, description, icon, category, points):
    """Награждение достижением"""
    try:
        # Находим или создаем достижение
        achievement = Achievement.query.filter_by(name=name).first()
        if not achievement:
            achievement = Achievement(
                name=name,
                description=description,
                icon=icon,
                category=category,
                points_required=0,
                badge_color='#667eea'
            )
            db.session.add(achievement)
            db.session.commit()
        
        # Проверяем, есть ли уже это достижение у пользователя
        existing = UserAchievement.query.filter_by(
            user_id=user_id, 
            achievement_id=achievement.id
        ).first()
        
        if not existing:
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                points_earned=points
            )
            db.session.add(user_achievement)
            db.session.commit()
            
            # Отправляем уведомление
            create_notification(user_id, f"Новое достижение: {name}", description, 'success')
            
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при награждении достижением: {e}")

def create_notification(user_id, title, message, type='info'):
    """Создание уведомления"""
    try:
        from models import Notification
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type
        )
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при создании уведомления: {e}")
