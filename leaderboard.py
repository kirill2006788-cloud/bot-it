from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import db, User, GameScore, UserAchievement, Leaderboard, ToolUsage
from datetime import datetime, timedelta
import math

leaderboard_bp = Blueprint('leaderboard', __name__)

def calculate_user_score(user_id):
    """Расчет общего очка пользователя"""
    try:
        # Очки из игр
        game_score = db.session.query(db.func.sum(GameScore.score)).filter_by(user_id=user_id).scalar() or 0
        
        # Очки из достижений
        achievement_score = db.session.query(db.func.sum(UserAchievement.points_earned)).filter_by(user_id=user_id).scalar() or 0
        
        # Бонус за активность (количество использованных инструментов)
        tool_bonus = db.session.query(db.func.sum(ToolUsage.usage_count)).filter_by(user_id=user_id).scalar() or 0
        tool_bonus = min(tool_bonus * 2, 500)  # Максимум 500 бонусных очков
        
        # Бонус за разнообразие (количество разных инструментов)
        unique_tools = db.session.query(db.func.count(db.distinct(ToolUsage.tool_name))).filter_by(user_id=user_id).scalar() or 0
        diversity_bonus = unique_tools * 10  # 10 очков за каждый уникальный инструмент
        
        total_score = game_score + achievement_score + tool_bonus + diversity_bonus
        
        return {
            'game_score': game_score,
            'achievement_score': achievement_score,
            'tool_bonus': tool_bonus,
            'diversity_bonus': diversity_bonus,
            'total_score': total_score
        }
        
    except Exception as e:
        print(f"Ошибка при расчете очков: {e}")
        return {
            'game_score': 0,
            'achievement_score': 0,
            'tool_bonus': 0,
            'diversity_bonus': 0,
            'total_score': 0
        }

def update_leaderboard():
    """Обновление таблицы лидеров"""
    try:
        # Получаем всех активных пользователей
        users = User.query.filter_by(is_active=True).all()
        
        # Очищаем старую таблицу лидеров
        Leaderboard.query.delete()
        
        leaderboard_entries = []
        
        for user in users:
            score_data = calculate_user_score(user.id)
            total_score = score_data['total_score']
            
            if total_score > 0:  # Только пользователи с очками
                entry = Leaderboard(
                    user_id=user.id,
                    category='overall',
                    score=total_score
                )
                leaderboard_entries.append(entry)
        
        # Сортируем по очкам
        leaderboard_entries.sort(key=lambda x: x.score, reverse=True)
        
        # Устанавливаем ранги
        for i, entry in enumerate(leaderboard_entries, 1):
            entry.rank = i
            db.session.add(entry)
        
        db.session.commit()
        print(f"✅ Таблица лидеров обновлена: {len(leaderboard_entries)} пользователей")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при обновлении таблицы лидеров: {e}")

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы лидеров"""
    try:
        category = request.args.get('category', 'overall')
        period = request.args.get('period', 'all')  # all, week, month
        limit = min(int(request.args.get('limit', 50)), 100)
        
        # Определяем временной фильтр
        date_filter = None
        if period == 'week':
            date_filter = datetime.utcnow() - timedelta(days=7)
        elif period == 'month':
            date_filter = datetime.utcnow() - timedelta(days=30)
        
        if category == 'overall':
            # Общая таблица лидеров
            query = db.session.query(
                Leaderboard.rank,
                User.id,
                User.username,
                User.first_name,
                User.last_name,
                User.avatar_url,
                Leaderboard.score,
                User.is_premium
            ).join(User).filter(Leaderboard.category == 'overall')
            
            if date_filter:
                query = query.filter(Leaderboard.updated_at >= date_filter)
            
            leaderboard_data = query.order_by(Leaderboard.rank).limit(limit).all()
            
        elif category == 'games':
            # Таблица лидеров по играм
            query = db.session.query(
                User.id,
                User.username,
                User.first_name,
                User.last_name,
                User.avatar_url,
                db.func.sum(GameScore.score).label('score'),
                db.func.count(GameScore.id).label('games_count'),
                User.is_premium
            ).join(GameScore).group_by(User.id)
            
            if date_filter:
                query = query.filter(GameScore.completed_at >= date_filter)
            
            leaderboard_data = query.order_by(db.func.sum(GameScore.score).desc()).limit(limit).all()
            
            # Добавляем ранги
            for i, user_data in enumerate(leaderboard_data, 1):
                user_data.rank = i
        
        elif category == 'achievements':
            # Таблица лидеров по достижениям
            query = db.session.query(
                User.id,
                User.username,
                User.first_name,
                User.last_name,
                User.avatar_url,
                db.func.count(UserAchievement.id).label('achievements_count'),
                db.func.sum(UserAchievement.points_earned).label('score'),
                User.is_premium
            ).join(UserAchievement).group_by(User.id)
            
            if date_filter:
                query = query.filter(UserAchievement.earned_at >= date_filter)
            
            leaderboard_data = query.order_by(db.func.count(UserAchievement.id).desc()).limit(limit).all()
            
            # Добавляем ранги
            for i, user_data in enumerate(leaderboard_data, 1):
                user_data.rank = i
        
        elif category == 'tools':
            # Таблица лидеров по использованию инструментов
            query = db.session.query(
                User.id,
                User.username,
                User.first_name,
                User.last_name,
                User.avatar_url,
                db.func.sum(ToolUsage.usage_count).label('score'),
                db.func.count(db.distinct(ToolUsage.tool_name)).label('tools_count'),
                User.is_premium
            ).join(ToolUsage).group_by(User.id)
            
            if date_filter:
                query = query.filter(ToolUsage.last_used >= date_filter)
            
            leaderboard_data = query.order_by(db.func.sum(ToolUsage.usage_count).desc()).limit(limit).all()
            
            # Добавляем ранги
            for i, user_data in enumerate(leaderboard_data, 1):
                user_data.rank = i
        
        else:
            return jsonify({'error': 'Неверная категория'}), 400
        
        # Формируем ответ
        leaderboard = []
        for user_data in leaderboard_data:
            leaderboard.append({
                'rank': user_data.rank,
                'user_id': user_data.id,
                'username': user_data.username,
                'name': f"{user_data.first_name or ''} {user_data.last_name or ''}".strip() or user_data.username,
                'avatar_url': user_data.avatar_url,
                'score': user_data.score,
                'is_premium': user_data.is_premium,
                'additional_data': get_additional_data(user_data, category)
            })
        
        # Получаем позицию текущего пользователя
        current_user_position = None
        if current_user.is_authenticated:
            current_user_position = get_user_position(current_user.id, category, period)
        
        return jsonify({
            'leaderboard': leaderboard,
            'category': category,
            'period': period,
            'current_user_position': current_user_position,
            'total_users': len(leaderboard)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении таблицы лидеров'}), 500

@leaderboard_bp.route('/api/leaderboard/user/<int:user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Получение статистики конкретного пользователя"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        # Основная статистика
        game_stats = db.session.query(
            db.func.count(GameScore.id).label('games_played'),
            db.func.sum(GameScore.score).label('total_score'),
            db.func.avg(GameScore.score).label('avg_score')
        ).filter_by(user_id=user_id).first()
        
        achievement_stats = db.session.query(
            db.func.count(UserAchievement.id).label('achievements_count'),
            db.func.sum(UserAchievement.points_earned).label('achievement_points')
        ).filter_by(user_id=user_id).first()
        
        tool_stats = db.session.query(
            db.func.sum(ToolUsage.usage_count).label('tools_used'),
            db.func.count(db.distinct(ToolUsage.tool_name)).label('unique_tools')
        ).filter_by(user_id=user_id).first()
        
        # Ранги в разных категориях
        overall_rank = get_user_position(user_id, 'overall', 'all')
        games_rank = get_user_position(user_id, 'games', 'all')
        achievements_rank = get_user_position(user_id, 'achievements', 'all')
        tools_rank = get_user_position(user_id, 'tools', 'all')
        
        # Недавняя активность
        recent_games = GameScore.query.filter_by(user_id=user_id).order_by(
            GameScore.completed_at.desc()
        ).limit(5).all()
        
        recent_achievements = UserAchievement.query.filter_by(user_id=user_id).order_by(
            UserAchievement.earned_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'user': user.to_dict(),
            'stats': {
                'games': {
                    'played': game_stats.games_played or 0,
                    'total_score': game_stats.total_score or 0,
                    'avg_score': round(game_stats.avg_score or 0, 2),
                    'rank': games_rank
                },
                'achievements': {
                    'count': achievement_stats.achievements_count or 0,
                    'points': achievement_stats.achievement_points or 0,
                    'rank': achievements_rank
                },
                'tools': {
                    'used': tool_stats.tools_used or 0,
                    'unique': tool_stats.unique_tools or 0,
                    'rank': tools_rank
                },
                'overall': {
                    'rank': overall_rank,
                    'score': calculate_user_score(user_id)['total_score']
                }
            },
            'recent_activity': {
                'games': [game.to_dict() for game in recent_games],
                'achievements': [achievement.to_dict() for achievement in recent_achievements]
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении статистики пользователя'}), 500

@leaderboard_bp.route('/api/leaderboard/update', methods=['POST'])
@login_required
def update_user_leaderboard():
    """Обновление позиции пользователя в таблице лидеров"""
    try:
        # Обновляем общую таблицу лидеров
        update_leaderboard()
        
        # Получаем новую позицию пользователя
        user_position = get_user_position(current_user.id, 'overall', 'all')
        
        return jsonify({
            'message': 'Таблица лидеров обновлена',
            'user_position': user_position
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при обновлении таблицы лидеров'}), 500

def get_user_position(user_id, category, period):
    """Получение позиции пользователя в таблице лидеров"""
    try:
        if category == 'overall':
            entry = Leaderboard.query.filter_by(user_id=user_id, category='overall').first()
            return entry.rank if entry else None
        
        elif category == 'games':
            # Подсчитываем количество пользователей с большим количеством очков
            user_score = db.session.query(db.func.sum(GameScore.score)).filter_by(user_id=user_id).scalar() or 0
            
            better_users = db.session.query(db.func.count(db.distinct(GameScore.user_id))).filter(
                GameScore.user_id != user_id
            ).group_by(GameScore.user_id).having(
                db.func.sum(GameScore.score) > user_score
            ).count()
            
            return better_users + 1 if user_score > 0 else None
        
        elif category == 'achievements':
            user_achievements = db.session.query(db.func.count(UserAchievement.id)).filter_by(user_id=user_id).scalar() or 0
            
            better_users = db.session.query(db.func.count(db.distinct(UserAchievement.user_id))).filter(
                UserAchievement.user_id != user_id
            ).group_by(UserAchievement.user_id).having(
                db.func.count(UserAchievement.id) > user_achievements
            ).count()
            
            return better_users + 1 if user_achievements > 0 else None
        
        elif category == 'tools':
            user_tools = db.session.query(db.func.sum(ToolUsage.usage_count)).filter_by(user_id=user_id).scalar() or 0
            
            better_users = db.session.query(db.func.count(db.distinct(ToolUsage.user_id))).filter(
                ToolUsage.user_id != user_id
            ).group_by(ToolUsage.user_id).having(
                db.func.sum(ToolUsage.usage_count) > user_tools
            ).count()
            
            return better_users + 1 if user_tools > 0 else None
        
        return None
        
    except Exception as e:
        print(f"Ошибка при получении позиции пользователя: {e}")
        return None

def get_additional_data(user_data, category):
    """Получение дополнительных данных для таблицы лидеров"""
    try:
        if category == 'games':
            return {
                'games_count': getattr(user_data, 'games_count', 0),
                'avg_score': round(getattr(user_data, 'avg_score', 0), 2)
            }
        elif category == 'achievements':
            return {
                'achievements_count': getattr(user_data, 'achievements_count', 0),
                'points': getattr(user_data, 'score', 0)
            }
        elif category == 'tools':
            return {
                'tools_count': getattr(user_data, 'tools_count', 0),
                'usage_count': getattr(user_data, 'score', 0)
            }
        else:
            return {}
    except Exception as e:
        return {}

def get_leaderboard_categories():
    """Получение доступных категорий таблицы лидеров"""
    return {
        'overall': 'Общий рейтинг',
        'games': 'Игры',
        'achievements': 'Достижения',
        'tools': 'Инструменты'
    }

def get_leaderboard_periods():
    """Получение доступных периодов"""
    return {
        'all': 'За все время',
        'month': 'За месяц',
        'week': 'За неделю'
    }
