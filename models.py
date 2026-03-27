from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Модель пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    telegram_id = db.Column(db.String(50), unique=True, nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(200), nullable=True)
    language = db.Column(db.String(5), default='ru')
    theme = db.Column(db.String(10), default='light')
    privacy_level = db.Column(db.Integer, default=1)  # 1=public, 2=friends, 3=private
    is_active = db.Column(db.Boolean, default=True)
    is_premium = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Связи
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)
    game_scores = db.relationship('GameScore', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    settings = db.relationship('UserSettings', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar_url': self.avatar_url,
            'language': self.language,
            'theme': self.theme,
            'privacy_level': self.privacy_level,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Achievement(db.Model):
    """Модель достижения"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # games, tools, social
    points_required = db.Column(db.Integer, default=0)
    badge_color = db.Column(db.String(20), default='#667eea')
    is_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'points_required': self.points_required,
            'badge_color': self.badge_color,
            'is_hidden': self.is_hidden
        }

class UserAchievement(db.Model):
    """Связь пользователя и достижений"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_earned = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'achievement': self.achievement.to_dict(),
            'earned_at': self.earned_at.isoformat(),
            'points_earned': self.points_earned
        }

class GameScore(db.Model):
    """Модель очков в играх"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)  # guess, quiz, sudoku, etc.
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    time_spent = db.Column(db.Integer, default=0)  # в секундах
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_type': self.game_type,
            'score': self.score,
            'level': self.level,
            'time_spent': self.time_spent,
            'completed_at': self.completed_at.isoformat()
        }

class Notification(db.Model):
    """Модель уведомлений"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'action_url': self.action_url,
            'created_at': self.created_at.isoformat()
        }

class UserSettings(db.Model):
    """Настройки пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    setting_key = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'updated_at': self.updated_at.isoformat()
        }

class GameSession(db.Model):
    """Активные игровые сессии"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    game_data = db.Column(db.Text, nullable=True)  # JSON данные игры
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    def get_game_data(self):
        if self.game_data:
            return json.loads(self.game_data)
        return {}
    
    def set_game_data(self, data):
        self.game_data = json.dumps(data)

class ToolUsage(db.Model):
    """Статистика использования инструментов"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    tool_name = db.Column(db.String(100), nullable=False)
    usage_count = db.Column(db.Integer, default=1)
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tool_name': self.tool_name,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat()
        }

class Leaderboard(db.Model):
    """Таблица лидеров"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # overall, games, tools
    score = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'category': self.category,
            'score': self.score,
            'rank': self.rank,
            'updated_at': self.updated_at.isoformat()
        }

class Language(db.Model):
    """Поддерживаемые языки"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    native_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'native_name': self.native_name,
            'is_active': self.is_active
        }

class Translation(db.Model):
    """Переводы"""
    id = db.Column(db.Integer, primary_key=True)
    language_code = db.Column(db.String(5), nullable=False)
    key = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # ui, messages, games
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'language_code': self.language_code,
            'key': self.key,
            'value': self.value,
            'category': self.category
        }

class GitHubIntegration(db.Model):
    """GitHub интеграция"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    github_username = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.String(200), nullable=True)
    repositories_count = db.Column(db.Integer, default=0)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    last_sync = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'github_username': self.github_username,
            'repositories_count': self.repositories_count,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'is_active': self.is_active
        }

class PremiumSubscription(db.Model):
    """Премиум подписки"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # monthly, yearly, lifetime
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_type': self.plan_type,
            'price': self.price,
            'currency': self.currency,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class ForumPost(db.Model):
    """Посты форума"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'is_pinned': self.is_pinned,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BlogPost(db.Model):
    """Посты блога"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    featured_image = db.Column(db.String(200), nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'featured_image': self.featured_image,
            'tags': self.tags.split(',') if self.tags else [],
            'is_published': self.is_published,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
