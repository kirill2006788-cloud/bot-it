from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import db, Achievement, UserAchievement, User
from config import ACHIEVEMENT_CATEGORIES
import random

achievements_bp = Blueprint('achievements', __name__)

def initialize_achievements():
    """Инициализация всех достижений в базе данных"""
    achievements_data = [
        # Социальные достижения
        {
            'name': 'Добро пожаловать',
            'description': 'Зарегистрировались в IT Helper Bot',
            'icon': '🎉',
            'category': 'social',
            'points_required': 0,
            'badge_color': '#28a745'
        },
        {
            'name': 'Первая игра',
            'description': 'Сыграли первую игру',
            'icon': '🎮',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#17a2b8'
        },
        {
            'name': 'Игрок',
            'description': 'Сыграли 10 игр',
            'icon': '🏆',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#ffc107'
        },
        {
            'name': 'Мастер игр',
            'description': 'Сыграли 100 игр',
            'icon': '👑',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#dc3545'
        },
        {
            'name': 'Первый инструмент',
            'description': 'Использовали первый инструмент',
            'icon': '🔧',
            'category': 'tools',
            'points_required': 0,
            'badge_color': '#6f42c1'
        },
        {
            'name': 'Мастер инструментов',
            'description': 'Использовали инструменты 50 раз',
            'icon': '⚙️',
            'category': 'tools',
            'points_required': 0,
            'badge_color': '#fd7e14'
        },
        {
            'name': 'Тысячник',
            'description': 'Набрали 1000 очков',
            'icon': '💯',
            'category': 'games',
            'points_required': 1000,
            'badge_color': '#20c997'
        },
        {
            'name': 'Пятитысячник',
            'description': 'Набрали 5000 очков',
            'icon': '🌟',
            'category': 'games',
            'points_required': 5000,
            'badge_color': '#e83e8c'
        },
        {
            'name': 'Десятитысячник',
            'description': 'Набрали 10000 очков',
            'icon': '💎',
            'category': 'games',
            'points_required': 10000,
            'badge_color': '#6c757d'
        },
        {
            'name': 'Угадайка',
            'description': 'Выиграли игру "Угадай число"',
            'icon': '🎯',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#007bff'
        },
        {
            'name': 'Эрудит',
            'description': 'Правильно ответили на 10 вопросов викторины',
            'icon': '🧠',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#6610f2'
        },
        {
            'name': 'Генератор',
            'description': 'Сгенерировали 10 паролей',
            'icon': '🔐',
            'category': 'tools',
            'points_required': 0,
            'badge_color': '#28a745'
        },
        {
            'name': 'QR Мастер',
            'description': 'Создали 20 QR-кодов',
            'icon': '📱',
            'category': 'tools',
            'points_required': 0,
            'badge_color': '#17a2b8'
        },
        {
            'name': 'Программист',
            'description': 'Сгенерировали код на 5 разных языках',
            'icon': '💻',
            'category': 'tools',
            'points_required': 0,
            'badge_color': '#ffc107'
        },
        {
            'name': 'Метеоролог',
            'description': 'Узнали погоду в 10 разных городах',
            'icon': '🌤️',
            'category': 'tools',
            'points_required': 0,
            'badge_color': '#20c997'
        },
        {
            'name': 'Трейдер',
            'description': 'Конвертировали валюту 25 раз',
            'icon': '💱',
            'category': 'tools',
            'points_required': 0,
            'badge_color': '#fd7e14'
        },
        {
            'name': 'Судоку Мастер',
            'description': 'Решили 5 судоку',
            'icon': '🔢',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#6f42c1'
        },
        {
            'name': 'Кроссвордист',
            'description': 'Решили 3 кроссворда',
            'icon': '📝',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#e83e8c'
        },
        {
            'name': 'Память',
            'description': 'Выиграли игру "Память"',
            'icon': '🧩',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#007bff'
        },
        {
            'name': 'Скоростник',
            'description': 'Напечатали 100 слов в минуту',
            'icon': '⌨️',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#28a745'
        },
        {
            'name': 'Алгоритмист',
            'description': 'Визуализировали 3 алгоритма сортировки',
            'icon': '📊',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#17a2b8'
        },
        {
            'name': 'Лабиринт',
            'description': 'Прошли лабиринт за 30 секунд',
            'icon': '🏃',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#ffc107'
        },
        {
            'name': 'Тетрис Мастер',
            'description': 'Набрали 10000 очков в Тетрисе',
            'icon': '🧱',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#dc3545'
        },
        {
            'name': 'Сапер',
            'description': 'Разминировали поле за 60 секунд',
            'icon': '💣',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#6c757d'
        },
        {
            'name': 'Виселица',
            'description': 'Угадали слово за 3 попытки',
            'icon': '🎭',
            'category': 'games',
            'points_required': 0,
            'badge_color': '#6610f2'
        },
        {
            'name': 'Премиум',
            'description': 'Активировали премиум подписку',
            'icon': '⭐',
            'category': 'premium',
            'points_required': 0,
            'badge_color': '#ffd700'
        },
        {
            'name': 'Социальный',
            'description': 'Пригласили 5 друзей',
            'icon': '👥',
            'category': 'social',
            'points_required': 0,
            'badge_color': '#20c997'
        },
        {
            'name': 'Активный',
            'description': 'Заходили в бот 7 дней подряд',
            'icon': '🔥',
            'category': 'social',
            'points_required': 0,
            'badge_color': '#fd7e14'
        },
        {
            'name': 'Ночной сов',
            'description': 'Играли после полуночи',
            'icon': '🦉',
            'category': 'social',
            'points_required': 0,
            'badge_color': '#6f42c1'
        },
        {
            'name': 'Ранняя пташка',
            'description': 'Играли до 6 утра',
            'icon': '🐦',
            'category': 'social',
            'points_required': 0,
            'badge_color': '#e83e8c'
        }
    ]
    
    try:
        for achievement_data in achievements_data:
            existing = Achievement.query.filter_by(name=achievement_data['name']).first()
            if not existing:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
        
        db.session.commit()
        print("✅ Все достижения инициализированы")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при инициализации достижений: {e}")

@achievements_bp.route('/api/achievements', methods=['GET'])
@login_required
def get_achievements():
    """Получение всех достижений пользователя"""
    try:
        user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
        all_achievements = Achievement.query.all()
        
        # Создаем словарь достижений пользователя
        user_achievements_dict = {ua.achievement_id: ua for ua in user_achievements}
        
        achievements_list = []
        for achievement in all_achievements:
            achievement_data = achievement.to_dict()
            if achievement.id in user_achievements_dict:
                achievement_data['earned'] = True
                achievement_data['earned_at'] = user_achievements_dict[achievement.id].earned_at.isoformat()
                achievement_data['points_earned'] = user_achievements_dict[achievement.id].points_earned
            else:
                achievement_data['earned'] = False
                achievement_data['earned_at'] = None
                achievement_data['points_earned'] = 0
            
            achievements_list.append(achievement_data)
        
        # Группировка по категориям
        categories = {}
        for achievement in achievements_list:
            category = achievement['category']
            if category not in categories:
                categories[category] = {
                    'name': ACHIEVEMENT_CATEGORIES.get(category, category),
                    'achievements': []
                }
            categories[category]['achievements'].append(achievement)
        
        return jsonify({
            'categories': categories,
            'total_earned': len(user_achievements),
            'total_available': len(all_achievements),
            'total_points': sum(ua.points_earned for ua in user_achievements)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении достижений'}), 500

@achievements_bp.route('/api/achievements/leaderboard', methods=['GET'])
def get_achievements_leaderboard():
    """Таблица лидеров по достижениям"""
    try:
        # Получаем топ-10 пользователей по количеству достижений
        top_users = db.session.query(
            User.id,
            User.username,
            User.first_name,
            User.last_name,
            db.func.count(UserAchievement.id).label('achievements_count'),
            db.func.sum(UserAchievement.points_earned).label('total_points')
        ).join(UserAchievement).group_by(User.id).order_by(
            db.func.count(UserAchievement.id).desc()
        ).limit(10).all()
        
        leaderboard = []
        for i, user_data in enumerate(top_users, 1):
            leaderboard.append({
                'rank': i,
                'user_id': user_data.id,
                'username': user_data.username,
                'name': f"{user_data.first_name or ''} {user_data.last_name or ''}".strip() or user_data.username,
                'achievements_count': user_data.achievements_count,
                'total_points': user_data.total_points or 0
            })
        
        return jsonify({
            'leaderboard': leaderboard,
            'current_user_rank': get_user_rank(current_user.id) if current_user.is_authenticated else None
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении таблицы лидеров'}), 500

@achievements_bp.route('/api/achievements/random', methods=['GET'])
@login_required
def get_random_achievement():
    """Получение случайного достижения для мотивации"""
    try:
        # Получаем не заработанные достижения
        earned_achievement_ids = [ua.achievement_id for ua in current_user.achievements]
        available_achievements = Achievement.query.filter(
            ~Achievement.id.in_(earned_achievement_ids)
        ).all()
        
        if not available_achievements:
            return jsonify({'message': 'Все достижения заработаны!'})
        
        random_achievement = random.choice(available_achievements)
        
        return jsonify({
            'achievement': random_achievement.to_dict(),
            'progress': get_achievement_progress(current_user.id, random_achievement)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении случайного достижения'}), 500

def get_user_rank(user_id):
    """Получение ранга пользователя"""
    try:
        user_achievements_count = UserAchievement.query.filter_by(user_id=user_id).count()
        
        users_with_more_achievements = db.session.query(User.id).join(UserAchievement).group_by(User.id).having(
            db.func.count(UserAchievement.id) > user_achievements_count
        ).count()
        
        return users_with_more_achievements + 1
        
    except Exception as e:
        return None

def get_achievement_progress(user_id, achievement):
    """Получение прогресса по достижению"""
    try:
        if achievement.name == 'Игрок':
            game_count = db.session.query(db.func.count(GameScore.id)).filter_by(user_id=user_id).scalar()
            return {'current': game_count, 'target': 10, 'percentage': min(100, (game_count / 10) * 100)}
        
        elif achievement.name == 'Мастер игр':
            game_count = db.session.query(db.func.count(GameScore.id)).filter_by(user_id=user_id).scalar()
            return {'current': game_count, 'target': 100, 'percentage': min(100, (game_count / 100) * 100)}
        
        elif achievement.name == 'Тысячник':
            total_score = db.session.query(db.func.sum(GameScore.score)).filter_by(user_id=user_id).scalar() or 0
            return {'current': total_score, 'target': 1000, 'percentage': min(100, (total_score / 1000) * 100)}
        
        elif achievement.name == 'Мастер инструментов':
            tool_usage = db.session.query(db.func.sum(ToolUsage.usage_count)).filter_by(user_id=user_id).scalar() or 0
            return {'current': tool_usage, 'target': 50, 'percentage': min(100, (tool_usage / 50) * 100)}
        
        else:
            return {'current': 0, 'target': 1, 'percentage': 0}
            
    except Exception as e:
        return {'current': 0, 'target': 1, 'percentage': 0}

def check_game_achievements(user_id, game_type, score=None, time_spent=None):
    """Проверка достижений после игры"""
    try:
        if game_type == 'guess' and score:
            award_achievement(user_id, 'Угадайка', 'Выиграли игру "Угадай число"', '🎯', 'games', 25)
        
        elif game_type == 'quiz':
            # Проверяем количество правильных ответов в викторине
            quiz_scores = GameScore.query.filter_by(user_id=user_id, game_type='quiz').all()
            if len(quiz_scores) >= 10:
                award_achievement(user_id, 'Эрудит', 'Правильно ответили на 10 вопросов викторины', '🧠', 'games', 50)
        
        elif game_type == 'sudoku':
            sudoku_count = GameScore.query.filter_by(user_id=user_id, game_type='sudoku').count()
            if sudoku_count >= 5:
                award_achievement(user_id, 'Судоку Мастер', 'Решили 5 судоку', '🔢', 'games', 100)
        
        elif game_type == 'typing' and time_spent:
            # Проверяем скорость печати (слов в минуту)
            words_per_minute = score / (time_spent / 60) if time_spent > 0 else 0
            if words_per_minute >= 100:
                award_achievement(user_id, 'Скоростник', 'Напечатали 100 слов в минуту', '⌨️', 'games', 75)
        
        elif game_type == 'tetris' and score:
            if score >= 10000:
                award_achievement(user_id, 'Тетрис Мастер', 'Набрали 10000 очков в Тетрисе', '🧱', 'games', 150)
        
        elif game_type == 'minesweeper' and time_spent:
            if time_spent <= 60:
                award_achievement(user_id, 'Сапер', 'Разминировали поле за 60 секунд', '💣', 'games', 100)
        
        elif game_type == 'hangman' and time_spent:
            if time_spent <= 3:
                award_achievement(user_id, 'Виселица', 'Угадали слово за 3 попытки', '🎭', 'games', 50)
        
        elif game_type == 'memory':
            award_achievement(user_id, 'Память', 'Выиграли игру "Память"', '🧩', 'games', 75)
        
        elif game_type == 'maze' and time_spent:
            if time_spent <= 30:
                award_achievement(user_id, 'Лабиринт', 'Прошли лабиринт за 30 секунд', '🏃', 'games', 100)
        
        elif game_type == 'algorithms':
            algo_count = GameScore.query.filter_by(user_id=user_id, game_type='algorithms').count()
            if algo_count >= 3:
                award_achievement(user_id, 'Алгоритмист', 'Визуализировали 3 алгоритма сортировки', '📊', 'games', 125)
        
        elif game_type == 'crossword':
            crossword_count = GameScore.query.filter_by(user_id=user_id, game_type='crossword').count()
            if crossword_count >= 3:
                award_achievement(user_id, 'Кроссвордист', 'Решили 3 кроссворда', '📝', 'games', 100)
                
    except Exception as e:
        print(f"Ошибка при проверке игровых достижений: {e}")

def check_tool_achievements(user_id, tool_name):
    """Проверка достижений после использования инструмента"""
    try:
        from models import ToolUsage
        
        # Обновляем статистику использования инструмента
        tool_usage = ToolUsage.query.filter_by(user_id=user_id, tool_name=tool_name).first()
        if tool_usage:
            tool_usage.usage_count += 1
            tool_usage.last_used = datetime.utcnow()
        else:
            tool_usage = ToolUsage(user_id=user_id, tool_name=tool_name, usage_count=1)
            db.session.add(tool_usage)
        
        db.session.commit()
        
        # Проверяем достижения
        if tool_name == 'password_generator':
            if tool_usage.usage_count == 1:
                award_achievement(user_id, 'Первый инструмент', 'Использовали первый инструмент', '🔧', 'tools', 15)
            elif tool_usage.usage_count == 10:
                award_achievement(user_id, 'Генератор', 'Сгенерировали 10 паролей', '🔐', 'tools', 50)
        
        elif tool_name == 'qr_generator':
            if tool_usage.usage_count == 20:
                award_achievement(user_id, 'QR Мастер', 'Создали 20 QR-кодов', '📱', 'tools', 75)
        
        elif tool_name == 'code_generator':
            # Проверяем количество разных языков программирования
            code_usage = ToolUsage.query.filter_by(user_id=user_id, tool_name='code_generator').first()
            if code_usage and code_usage.usage_count >= 5:
                award_achievement(user_id, 'Программист', 'Сгенерировали код на 5 разных языках', '💻', 'tools', 100)
        
        elif tool_name == 'weather_checker':
            if tool_usage.usage_count == 10:
                award_achievement(user_id, 'Метеоролог', 'Узнали погоду в 10 разных городах', '🌤️', 'tools', 75)
        
        elif tool_name == 'currency_converter':
            if tool_usage.usage_count == 25:
                award_achievement(user_id, 'Трейдер', 'Конвертировали валюту 25 раз', '💱', 'tools', 100)
        
        # Общее достижение за использование инструментов
        total_tool_usage = db.session.query(db.func.sum(ToolUsage.usage_count)).filter_by(user_id=user_id).scalar() or 0
        if total_tool_usage == 50:
            award_achievement(user_id, 'Мастер инструментов', 'Использовали инструменты 50 раз', '⚙️', 'tools', 200)
            
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при проверке достижений инструментов: {e}")

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
            create_notification(user_id, f"🎉 Новое достижение: {name}", description, 'success')
            
            return True
            
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при награждении достижением: {e}")
        return False

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
