from flask import Blueprint, jsonify, request, g
from flask_login import login_required, current_user
from models import db, Language, Translation, User
from config import SUPPORTED_LANGUAGES
import json

i18n_bp = Blueprint('i18n', __name__)

def initialize_languages():
    """Инициализация языков в базе данных"""
    try:
        for code, name in SUPPORTED_LANGUAGES.items():
            existing = Language.query.filter_by(code=code).first()
            if not existing:
                language = Language(
                    code=code,
                    name=name,
                    native_name=get_native_name(code),
                    is_active=True
                )
                db.session.add(language)
        
        db.session.commit()
        print("✅ Языки инициализированы")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при инициализации языков: {e}")

def get_native_name(code):
    """Получение родного названия языка"""
    native_names = {
        'ru': 'Русский',
        'en': 'English',
        'es': 'Español'
    }
    return native_names.get(code, code)

def initialize_translations():
    """Инициализация переводов"""
    translations = {
        'ru': {
            'ui': {
                'welcome': 'Добро пожаловать',
                'games': 'Игры',
                'tools': 'Инструменты',
                'achievements': 'Достижения',
                'leaderboard': 'Таблица лидеров',
                'profile': 'Профиль',
                'settings': 'Настройки',
                'logout': 'Выход',
                'login': 'Вход',
                'register': 'Регистрация',
                'password': 'Пароль',
                'email': 'Email',
                'username': 'Имя пользователя',
                'save': 'Сохранить',
                'cancel': 'Отмена',
                'delete': 'Удалить',
                'edit': 'Редактировать',
                'back': 'Назад',
                'next': 'Далее',
                'previous': 'Предыдущий',
                'loading': 'Загрузка...',
                'error': 'Ошибка',
                'success': 'Успешно',
                'warning': 'Предупреждение',
                'info': 'Информация'
            },
            'games': {
                'guess_number': 'Угадай число',
                'quiz': 'Викторина',
                'sudoku': 'Судоку',
                'crossword': 'Кроссворд',
                'hangman': 'Виселица',
                'memory': 'Память',
                'typing': 'Скоростная печать',
                'algorithms': 'Алгоритмы',
                'maze': 'Лабиринт',
                'tetris': 'Тетрис',
                'minesweeper': 'Сапер'
            },
            'tools': {
                'password_generator': 'Генератор паролей',
                'qr_generator': 'QR-код генератор',
                'weather': 'Погода',
                'currency_converter': 'Конвертер валют',
                'code_generator': 'Генератор кода',
                'calculator': 'Калькулятор',
                'color_converter': 'Конвертер цветов',
                'hash_generator': 'Генератор хешей',
                'base64_encoder': 'Base64 кодировщик',
                'json_validator': 'JSON валидатор'
            },
            'messages': {
                'welcome_message': 'Добро пожаловать в IT Helper Bot!',
                'game_won': 'Поздравляем! Вы выиграли!',
                'game_lost': 'Попробуйте еще раз!',
                'achievement_earned': 'Новое достижение!',
                'profile_updated': 'Профиль обновлен',
                'password_changed': 'Пароль изменен',
                'login_success': 'Вход выполнен успешно',
                'logout_success': 'Выход выполнен успешно'
            }
        },
        'en': {
            'ui': {
                'welcome': 'Welcome',
                'games': 'Games',
                'tools': 'Tools',
                'achievements': 'Achievements',
                'leaderboard': 'Leaderboard',
                'profile': 'Profile',
                'settings': 'Settings',
                'logout': 'Logout',
                'login': 'Login',
                'register': 'Register',
                'password': 'Password',
                'email': 'Email',
                'username': 'Username',
                'save': 'Save',
                'cancel': 'Cancel',
                'delete': 'Delete',
                'edit': 'Edit',
                'back': 'Back',
                'next': 'Next',
                'previous': 'Previous',
                'loading': 'Loading...',
                'error': 'Error',
                'success': 'Success',
                'warning': 'Warning',
                'info': 'Info'
            },
            'games': {
                'guess_number': 'Guess Number',
                'quiz': 'Quiz',
                'sudoku': 'Sudoku',
                'crossword': 'Crossword',
                'hangman': 'Hangman',
                'memory': 'Memory',
                'typing': 'Speed Typing',
                'algorithms': 'Algorithms',
                'maze': 'Maze',
                'tetris': 'Tetris',
                'minesweeper': 'Minesweeper'
            },
            'tools': {
                'password_generator': 'Password Generator',
                'qr_generator': 'QR Code Generator',
                'weather': 'Weather',
                'currency_converter': 'Currency Converter',
                'code_generator': 'Code Generator',
                'calculator': 'Calculator',
                'color_converter': 'Color Converter',
                'hash_generator': 'Hash Generator',
                'base64_encoder': 'Base64 Encoder',
                'json_validator': 'JSON Validator'
            },
            'messages': {
                'welcome_message': 'Welcome to IT Helper Bot!',
                'game_won': 'Congratulations! You won!',
                'game_lost': 'Try again!',
                'achievement_earned': 'New achievement!',
                'profile_updated': 'Profile updated',
                'password_changed': 'Password changed',
                'login_success': 'Login successful',
                'logout_success': 'Logout successful'
            }
        },
        'es': {
            'ui': {
                'welcome': 'Bienvenido',
                'games': 'Juegos',
                'tools': 'Herramientas',
                'achievements': 'Logros',
                'leaderboard': 'Tabla de clasificación',
                'profile': 'Perfil',
                'settings': 'Configuración',
                'logout': 'Cerrar sesión',
                'login': 'Iniciar sesión',
                'register': 'Registrarse',
                'password': 'Contraseña',
                'email': 'Email',
                'username': 'Nombre de usuario',
                'save': 'Guardar',
                'cancel': 'Cancelar',
                'delete': 'Eliminar',
                'edit': 'Editar',
                'back': 'Atrás',
                'next': 'Siguiente',
                'previous': 'Anterior',
                'loading': 'Cargando...',
                'error': 'Error',
                'success': 'Éxito',
                'warning': 'Advertencia',
                'info': 'Información'
            },
            'games': {
                'guess_number': 'Adivina el número',
                'quiz': 'Quiz',
                'sudoku': 'Sudoku',
                'crossword': 'Crucigrama',
                'hangman': 'Ahorcado',
                'memory': 'Memoria',
                'typing': 'Escritura rápida',
                'algorithms': 'Algoritmos',
                'maze': 'Laberinto',
                'tetris': 'Tetris',
                'minesweeper': 'Buscaminas'
            },
            'tools': {
                'password_generator': 'Generador de contraseñas',
                'qr_generator': 'Generador de códigos QR',
                'weather': 'Clima',
                'currency_converter': 'Convertidor de moneda',
                'code_generator': 'Generador de código',
                'calculator': 'Calculadora',
                'color_converter': 'Convertidor de colores',
                'hash_generator': 'Generador de hash',
                'base64_encoder': 'Codificador Base64',
                'json_validator': 'Validador JSON'
            },
            'messages': {
                'welcome_message': '¡Bienvenido a IT Helper Bot!',
                'game_won': '¡Felicidades! ¡Ganaste!',
                'game_lost': '¡Inténtalo de nuevo!',
                'achievement_earned': '¡Nuevo logro!',
                'profile_updated': 'Perfil actualizado',
                'password_changed': 'Contraseña cambiada',
                'login_success': 'Inicio de sesión exitoso',
                'logout_success': 'Cierre de sesión exitoso'
            }
        }
    }
    
    try:
        for lang_code, categories in translations.items():
            for category, keys in categories.items():
                for key, value in keys.items():
                    existing = Translation.query.filter_by(
                        language_code=lang_code,
                        key=key,
                        category=category
                    ).first()
                    
                    if not existing:
                        translation = Translation(
                            language_code=lang_code,
                            key=key,
                            value=value,
                            category=category
                        )
                        db.session.add(translation)
        
        db.session.commit()
        print("✅ Переводы инициализированы")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при инициализации переводов: {e}")

def get_translation(key, category='ui', language=None):
    """Получение перевода"""
    if not language:
        language = get_current_language()
    
    try:
        translation = Translation.query.filter_by(
            language_code=language,
            key=key,
            category=category
        ).first()
        
        if translation:
            return translation.value
        
        # Если перевод не найден, возвращаем ключ
        return key
        
    except Exception as e:
        print(f"Ошибка при получении перевода: {e}")
        return key

def get_current_language():
    """Получение текущего языка"""
    if current_user.is_authenticated:
        return current_user.language
    return 'ru'  # Язык по умолчанию

@i18n_bp.route('/api/i18n/languages', methods=['GET'])
def get_languages():
    """Получение доступных языков"""
    try:
        languages = Language.query.filter_by(is_active=True).all()
        return jsonify({
            'languages': [language.to_dict() for language in languages],
            'current': get_current_language()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении языков'}), 500

@i18n_bp.route('/api/i18n/translations', methods=['GET'])
def get_translations():
    """Получение переводов для текущего языка"""
    try:
        language = request.args.get('language', get_current_language())
        category = request.args.get('category', 'ui')
        
        translations = Translation.query.filter_by(
            language_code=language,
            category=category
        ).all()
        
        translations_dict = {t.key: t.value for t in translations}
        
        return jsonify({
            'language': language,
            'category': category,
            'translations': translations_dict
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении переводов'}), 500

@i18n_bp.route('/api/i18n/set-language', methods=['POST'])
@login_required
def set_language():
    """Установка языка пользователя"""
    try:
        data = request.get_json()
        language = data.get('language', 'ru')
        
        if language not in SUPPORTED_LANGUAGES:
            return jsonify({'error': 'Неподдерживаемый язык'}), 400
        
        current_user.language = language
        db.session.commit()
        
        return jsonify({
            'message': 'Язык изменен',
            'language': language
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при изменении языка'}), 500

def t(key, category='ui', **kwargs):
    """Функция для получения перевода (аналог Flask-Babel)"""
    translation = get_translation(key, category)
    
    # Простая замена переменных
    if kwargs:
        for k, v in kwargs.items():
            translation = translation.replace(f'{{{k}}}', str(v))
    
    return translation
