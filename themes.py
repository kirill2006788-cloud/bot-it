from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, User, UserSettings
import json

themes_bp = Blueprint('themes', __name__)

# Определения тем
THEMES = {
    'light': {
        'name': 'Светлая тема',
        'description': 'Классическая светлая тема',
        'colors': {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'text': '#333333',
            'text_secondary': '#666666',
            'border': '#e0e0e0',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'info': '#17a2b8'
        },
        'gradients': {
            'primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'success': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'warning': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
        }
    },
    'dark': {
        'name': 'Темная тема',
        'description': 'Современная темная тема',
        'colors': {
            'primary': '#8b5cf6',
            'secondary': '#a855f7',
            'background': '#1a1a1a',
            'surface': '#2d2d2d',
            'text': '#ffffff',
            'text_secondary': '#b3b3b3',
            'border': '#404040',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#06b6d4'
        },
        'gradients': {
            'primary': 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
            'secondary': 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
            'success': 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
            'warning': 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)'
        }
    },
    'blue': {
        'name': 'Синяя тема',
        'description': 'Профессиональная синяя тема',
        'colors': {
            'primary': '#3b82f6',
            'secondary': '#1d4ed8',
            'background': '#f8fafc',
            'surface': '#ffffff',
            'text': '#1e293b',
            'text_secondary': '#64748b',
            'border': '#e2e8f0',
            'success': '#059669',
            'warning': '#d97706',
            'error': '#dc2626',
            'info': '#0891b2'
        },
        'gradients': {
            'primary': 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
            'secondary': 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
            'success': 'linear-gradient(135deg, #059669 0%, #047857 100%)',
            'warning': 'linear-gradient(135deg, #d97706 0%, #b45309 100%)'
        }
    },
    'green': {
        'name': 'Зеленая тема',
        'description': 'Природная зеленая тема',
        'colors': {
            'primary': '#10b981',
            'secondary': '#059669',
            'background': '#f0fdf4',
            'surface': '#ffffff',
            'text': '#064e3b',
            'text_secondary': '#047857',
            'border': '#d1fae5',
            'success': '#059669',
            'warning': '#d97706',
            'error': '#dc2626',
            'info': '#0891b2'
        },
        'gradients': {
            'primary': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'secondary': 'linear-gradient(135deg, #84cc16 0%, #65a30d 100%)',
            'success': 'linear-gradient(135deg, #059669 0%, #047857 100%)',
            'warning': 'linear-gradient(135deg, #d97706 0%, #b45309 100%)'
        }
    },
    'purple': {
        'name': 'Фиолетовая тема',
        'description': 'Креативная фиолетовая тема',
        'colors': {
            'primary': '#8b5cf6',
            'secondary': '#7c3aed',
            'background': '#faf5ff',
            'surface': '#ffffff',
            'text': '#581c87',
            'text_secondary': '#7c3aed',
            'border': '#e9d5ff',
            'success': '#059669',
            'warning': '#d97706',
            'error': '#dc2626',
            'info': '#0891b2'
        },
        'gradients': {
            'primary': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
            'secondary': 'linear-gradient(135deg, #ec4899 0%, #be185d 100%)',
            'success': 'linear-gradient(135deg, #059669 0%, #047857 100%)',
            'warning': 'linear-gradient(135deg, #d97706 0%, #b45309 100%)'
        }
    },
    'orange': {
        'name': 'Оранжевая тема',
        'description': 'Энергичная оранжевая тема',
        'colors': {
            'primary': '#f97316',
            'secondary': '#ea580c',
            'background': '#fff7ed',
            'surface': '#ffffff',
            'text': '#9a3412',
            'text_secondary': '#c2410c',
            'border': '#fed7aa',
            'success': '#059669',
            'warning': '#d97706',
            'error': '#dc2626',
            'info': '#0891b2'
        },
        'gradients': {
            'primary': 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
            'secondary': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            'success': 'linear-gradient(135deg, #059669 0%, #047857 100%)',
            'warning': 'linear-gradient(135deg, #d97706 0%, #b45309 100%)'
        }
    }
}

@themes_bp.route('/api/themes', methods=['GET'])
def get_themes():
    """Получение доступных тем"""
    try:
        return jsonify({
            'themes': THEMES,
            'current_theme': get_current_theme()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении тем'}), 500

@themes_bp.route('/api/themes/current', methods=['GET'])
def get_current_theme():
    """Получение текущей темы"""
    try:
        if current_user.is_authenticated:
            theme = current_user.theme
        else:
            # Для неавторизованных пользователей используем тему из сессии
            theme = request.cookies.get('theme', 'light')
        
        return jsonify({
            'theme': theme,
            'theme_data': THEMES.get(theme, THEMES['light'])
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении текущей темы'}), 500

@themes_bp.route('/api/themes/set', methods=['POST'])
@login_required
def set_theme():
    """Установка темы пользователя"""
    try:
        data = request.get_json()
        theme = data.get('theme', 'light')
        
        if theme not in THEMES:
            return jsonify({'error': 'Неподдерживаемая тема'}), 400
        
        current_user.theme = theme
        db.session.commit()
        
        return jsonify({
            'message': 'Тема изменена',
            'theme': theme,
            'theme_data': THEMES[theme]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при изменении темы'}), 500

@themes_bp.route('/api/themes/preview', methods=['POST'])
def preview_theme():
    """Предварительный просмотр темы"""
    try:
        data = request.get_json()
        theme = data.get('theme', 'light')
        
        if theme not in THEMES:
            return jsonify({'error': 'Неподдерживаемая тема'}), 400
        
        return jsonify({
            'theme': theme,
            'theme_data': THEMES[theme]
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при предварительном просмотре темы'}), 500

@themes_bp.route('/api/themes/custom', methods=['POST'])
@login_required
def create_custom_theme():
    """Создание пользовательской темы"""
    try:
        data = request.get_json()
        
        theme_name = data.get('name', 'custom')
        colors = data.get('colors', {})
        gradients = data.get('gradients', {})
        
        # Валидация цветов
        required_colors = ['primary', 'secondary', 'background', 'surface', 'text']
        for color in required_colors:
            if color not in colors:
                return jsonify({'error': f'Отсутствует обязательный цвет: {color}'}), 400
        
        # Сохраняем пользовательскую тему в настройках
        custom_theme = {
            'name': theme_name,
            'description': 'Пользовательская тема',
            'colors': colors,
            'gradients': gradients
        }
        
        # Сохраняем в настройках пользователя
        setting = UserSettings.query.filter_by(
            user_id=current_user.id,
            setting_key='custom_theme'
        ).first()
        
        if setting:
            setting.setting_value = json.dumps(custom_theme)
        else:
            setting = UserSettings(
                user_id=current_user.id,
                setting_key='custom_theme',
                setting_value=json.dumps(custom_theme)
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Пользовательская тема создана',
            'theme': custom_theme
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при создании пользовательской темы'}), 500

@themes_bp.route('/api/themes/custom', methods=['GET'])
@login_required
def get_custom_theme():
    """Получение пользовательской темы"""
    try:
        setting = UserSettings.query.filter_by(
            user_id=current_user.id,
            setting_key='custom_theme'
        ).first()
        
        if setting:
            custom_theme = json.loads(setting.setting_value)
            return jsonify({
                'custom_theme': custom_theme
            })
        else:
            return jsonify({
                'custom_theme': None
            })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении пользовательской темы'}), 500

def get_current_theme():
    """Получение текущей темы пользователя"""
    try:
        if current_user.is_authenticated:
            return current_user.theme
        else:
            return 'light'
    except:
        return 'light'

def get_theme_css(theme_name):
    """Генерация CSS для темы"""
    theme = THEMES.get(theme_name, THEMES['light'])
    
    css = f"""
    :root {{
        --primary-color: {theme['colors']['primary']};
        --secondary-color: {theme['colors']['secondary']};
        --background-color: {theme['colors']['background']};
        --surface-color: {theme['colors']['surface']};
        --text-color: {theme['colors']['text']};
        --text-secondary-color: {theme['colors']['text_secondary']};
        --border-color: {theme['colors']['border']};
        --success-color: {theme['colors']['success']};
        --warning-color: {theme['colors']['warning']};
        --error-color: {theme['colors']['error']};
        --info-color: {theme['colors']['info']};
        
        --primary-gradient: {theme['gradients']['primary']};
        --secondary-gradient: {theme['gradients']['secondary']};
        --success-gradient: {theme['gradients']['success']};
        --warning-gradient: {theme['gradients']['warning']};
    }}
    
    body {{
        background-color: var(--background-color);
        color: var(--text-color);
    }}
    
    .header {{
        background-color: var(--surface-color);
        border-bottom: 1px solid var(--border-color);
    }}
    
    .btn-primary {{
        background: var(--primary-gradient);
        border-color: var(--primary-color);
    }}
    
    .btn-primary:hover {{
        background: var(--secondary-gradient);
    }}
    
    .tool-card, .game-card, .stat-item {{
        background-color: var(--surface-color);
        border: 1px solid var(--border-color);
    }}
    
    .result {{
        background-color: var(--surface-color);
        border-left-color: var(--primary-color);
    }}
    
    .success {{
        background-color: var(--success-color);
        color: white;
    }}
    
    .error {{
        background-color: var(--error-color);
        color: white;
    }}
    
    .warning {{
        background-color: var(--warning-color);
        color: white;
    }}
    
    .info {{
        background-color: var(--info-color);
        color: white;
    }}
    """
    
    return css

def apply_theme_to_response(response, theme_name):
    """Применение темы к ответу"""
    if theme_name in THEMES:
        css = get_theme_css(theme_name)
        response.headers['X-Theme-CSS'] = css
    return response
