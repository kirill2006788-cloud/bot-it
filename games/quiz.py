from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, GameScore, GameSession
import random
import json
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)

# База вопросов IT квиза
IT_QUESTIONS = {
    'programming_basics': [
        {
            'question': 'Что такое переменная в программировании?',
            'options': ['Константа', 'Именованная область памяти', 'Функция', 'Класс'],
            'correct': 1,
            'explanation': 'Переменная - это именованная область памяти для хранения данных.'
        },
        {
            'question': 'Какой оператор используется для присваивания в большинстве языков программирования?',
            'options': ['=', '==', ':=', '->'],
            'correct': 0,
            'explanation': 'Оператор = используется для присваивания значений переменным.'
        },
        {
            'question': 'Что такое функция в программировании?',
            'options': ['Переменная', 'Блок кода, выполняющий определенную задачу', 'Цикл', 'Условие'],
            'correct': 1,
            'explanation': 'Функция - это блок кода, который выполняет определенную задачу и может быть вызван из других частей программы.'
        },
        {
            'question': 'Какой тип данных используется для хранения целых чисел?',
            'options': ['String', 'Float', 'Integer', 'Boolean'],
            'correct': 2,
            'explanation': 'Integer (int) используется для хранения целых чисел.'
        },
        {
            'question': 'Что такое массив?',
            'options': ['Функция', 'Коллекция элементов одного типа', 'Переменная', 'Цикл'],
            'correct': 1,
            'explanation': 'Массив - это коллекция элементов одного типа, расположенных в памяти последовательно.'
        }
    ],
    'web_development': [
        {
            'question': 'Что означает HTML?',
            'options': ['HyperText Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlink Text Management Language'],
            'correct': 0,
            'explanation': 'HTML расшифровывается как HyperText Markup Language - язык гипертекстовой разметки.'
        },
        {
            'question': 'Что такое CSS?',
            'options': ['Computer Style Sheets', 'Cascading Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'],
            'correct': 1,
            'explanation': 'CSS расшифровывается как Cascading Style Sheets - каскадные таблицы стилей.'
        },
        {
            'question': 'Какой тег используется для создания ссылки в HTML?',
            'options': ['<link>', '<a>', '<href>', '<url>'],
            'correct': 1,
            'explanation': 'Тег <a> используется для создания ссылок в HTML.'
        },
        {
            'question': 'Что такое DOM?',
            'options': ['Document Object Model', 'Data Object Management', 'Dynamic Object Method', 'Document Order Management'],
            'correct': 0,
            'explanation': 'DOM (Document Object Model) - это программный интерфейс для HTML и XML документов.'
        },
        {
            'question': 'Какой протокол используется для передачи веб-страниц?',
            'options': ['FTP', 'HTTP', 'SMTP', 'TCP'],
            'correct': 1,
            'explanation': 'HTTP (HyperText Transfer Protocol) используется для передачи веб-страниц.'
        }
    ],
    'databases': [
        {
            'question': 'Что означает SQL?',
            'options': ['Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'System Query Language'],
            'correct': 0,
            'explanation': 'SQL расшифровывается как Structured Query Language - язык структурированных запросов.'
        },
        {
            'question': 'Какой оператор SQL используется для выборки данных?',
            'options': ['INSERT', 'UPDATE', 'SELECT', 'DELETE'],
            'correct': 2,
            'explanation': 'Оператор SELECT используется для выборки данных из таблиц.'
        },
        {
            'question': 'Что такое первичный ключ в базе данных?',
            'options': ['Ключ для шифрования', 'Уникальный идентификатор записи', 'Ключ для сортировки', 'Ключ для индексации'],
            'correct': 1,
            'explanation': 'Первичный ключ - это уникальный идентификатор записи в таблице.'
        },
        {
            'question': 'Что такое внешний ключ?',
            'options': ['Ключ для доступа', 'Ссылка на первичный ключ другой таблицы', 'Ключ для шифрования', 'Ключ для сортировки'],
            'correct': 1,
            'explanation': 'Внешний ключ - это поле, которое ссылается на первичный ключ другой таблицы.'
        },
        {
            'question': 'Что такое нормализация базы данных?',
            'options': ['Увеличение размера БД', 'Процесс организации данных для уменьшения избыточности', 'Удаление данных', 'Шифрование данных'],
            'correct': 1,
            'explanation': 'Нормализация - это процесс организации данных для уменьшения избыточности и улучшения целостности.'
        }
    ],
    'algorithms': [
        {
            'question': 'Что такое алгоритм?',
            'options': ['Программа', 'Последовательность шагов для решения задачи', 'Язык программирования', 'База данных'],
            'correct': 1,
            'explanation': 'Алгоритм - это последовательность шагов для решения определенной задачи.'
        },
        {
            'question': 'Какой алгоритм сортировки имеет сложность O(n log n)?',
            'options': ['Пузырьковая сортировка', 'Быстрая сортировка', 'Сортировка выбором', 'Сортировка вставками'],
            'correct': 1,
            'explanation': 'Быстрая сортировка (Quick Sort) имеет среднюю сложность O(n log n).'
        },
        {
            'question': 'Что означает Big O notation?',
            'options': ['Размер программы', 'Временная сложность алгоритма', 'Количество переменных', 'Размер памяти'],
            'correct': 1,
            'explanation': 'Big O notation описывает временную сложность алгоритма в худшем случае.'
        },
        {
            'question': 'Какой алгоритм используется для поиска в отсортированном массиве?',
            'options': ['Линейный поиск', 'Бинарный поиск', 'Поиск в глубину', 'Поиск в ширину'],
            'correct': 1,
            'explanation': 'Бинарный поиск эффективен для поиска в отсортированном массиве.'
        },
        {
            'question': 'Что такое рекурсия?',
            'options': ['Цикл', 'Функция, вызывающая сама себя', 'Условие', 'Переменная'],
            'correct': 1,
            'explanation': 'Рекурсия - это когда функция вызывает сама себя для решения задачи.'
        }
    ],
    'security': [
        {
            'question': 'Что такое HTTPS?',
            'options': ['HTTP с шифрованием', 'Быстрый HTTP', 'HTTP для серверов', 'HTTP для мобильных устройств'],
            'correct': 0,
            'explanation': 'HTTPS - это HTTP с шифрованием SSL/TLS для безопасной передачи данных.'
        },
        {
            'question': 'Что такое SQL инъекция?',
            'options': ['Ошибка в SQL', 'Атака через внедрение вредоносного SQL кода', 'Тип базы данных', 'Метод оптимизации'],
            'correct': 1,
            'explanation': 'SQL инъекция - это атака, при которой вредоносный SQL код внедряется в приложение.'
        },
        {
            'question': 'Что такое XSS атака?',
            'options': ['Атака на сервер', 'Внедрение вредоносного JavaScript кода', 'Атака на базу данных', 'Атака на сеть'],
            'correct': 1,
            'explanation': 'XSS (Cross-Site Scripting) - это внедрение вредоносного JavaScript кода в веб-страницы.'
        },
        {
            'question': 'Что такое хеширование паролей?',
            'options': ['Шифрование паролей', 'Преобразование пароля в необратимый хеш', 'Сжатие паролей', 'Копирование паролей'],
            'correct': 1,
            'explanation': 'Хеширование паролей - это преобразование пароля в необратимый хеш для безопасного хранения.'
        },
        {
            'question': 'Что такое двухфакторная аутентификация?',
            'options': ['Два пароля', 'Аутентификация с двумя факторами (пароль + код)', 'Два пользователя', 'Два сервера'],
            'correct': 1,
            'explanation': '2FA использует два фактора: что-то, что вы знаете (пароль) и что-то, что у вас есть (код).'
        }
    ]
}

@quiz_bp.route('/api/games/quiz/new', methods=['POST'])
@login_required
def new_quiz_game():
    """Создание новой игры IT квиз"""
    try:
        data = request.get_json()
        category = data.get('category', 'programming_basics')
        difficulty = data.get('difficulty', 'medium')  # easy, medium, hard
        questions_count = int(data.get('questions_count', 10))
        
        # Получение вопросов из выбранной категории
        available_questions = IT_QUESTIONS.get(category, IT_QUESTIONS['programming_basics'])
        
        if len(available_questions) < questions_count:
            questions_count = len(available_questions)
        
        # Выбор случайных вопросов
        selected_questions = random.sample(available_questions, questions_count)
        
        # Создание игровой сессии
        session_id = f"quiz_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        game_session = GameSession(
            user_id=current_user.id,
            session_id=session_id,
            game_type='quiz',
            game_data=json.dumps({
                'questions': selected_questions,
                'category': category,
                'difficulty': difficulty,
                'questions_count': questions_count,
                'start_time': datetime.utcnow().isoformat(),
                'current_question': 0,
                'answers': [],
                'score': 0,
                'game_state': 'playing',  # playing, completed
                'hints_used': 0
            })
        )
        
        db.session.add(game_session)
        db.session.commit()
        
        # Подготовка первого вопроса
        first_question = prepare_question(selected_questions[0], 0)
        
        return jsonify({
            'session_id': session_id,
            'question': first_question,
            'category': category,
            'difficulty': difficulty,
            'questions_count': questions_count,
            'current_question': 1,
            'created_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при создании квиза'}), 500

@quiz_bp.route('/api/games/quiz/answer', methods=['POST'])
@login_required
def submit_quiz_answer():
    """Отправка ответа в квизе"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answer = int(data.get('answer', -1))
        
        if not session_id or answer == -1:
            return jsonify({'error': 'Необходимые параметры не указаны'}), 400
        
        # Получение игровой сессии
        game_session = GameSession.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not game_session:
            return jsonify({'error': 'Игровая сессия не найдена'}), 404
        
        game_data = game_session.get_game_data()
        
        # Проверка состояния игры
        if game_data['game_state'] != 'playing':
            return jsonify({'error': 'Игра уже завершена'}), 400
        
        # Получение текущего вопроса
        current_question = game_data['questions'][game_data['current_question']]
        
        # Проверка ответа
        is_correct = answer == current_question['correct']
        
        # Сохранение ответа
        game_data['answers'].append({
            'question_index': game_data['current_question'],
            'answer': answer,
            'correct': is_correct,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Обновление счета
        if is_correct:
            game_data['score'] += 1
        
        # Переход к следующему вопросу
        game_data['current_question'] += 1
        
        # Проверка завершения квиза
        if game_data['current_question'] >= game_data['questions_count']:
            game_data['game_state'] = 'completed'
            
            # Сохранение результата
            time_spent = calculate_game_time(game_data['start_time'])
            final_score = calculate_quiz_score(game_data, time_spent)
            
            game_score = GameScore(
                user_id=current_user.id,
                game_type='quiz',
                score=final_score,
                level=1,
                time_spent=time_spent
            )
            
            db.session.add(game_score)
            db.session.commit()
            
            # Проверка достижений
            from achievements import check_game_achievements
            check_game_achievements(current_user.id, 'quiz', final_score, time_spent)
            
            return jsonify({
                'correct': is_correct,
                'game_state': 'completed',
                'final_score': final_score,
                'correct_answers': game_data['score'],
                'total_questions': game_data['questions_count'],
                'time_spent': time_spent,
                'message': 'Квиз завершен!'
            })
        
        # Подготовка следующего вопроса
        next_question = prepare_question(
            game_data['questions'][game_data['current_question']],
            game_data['current_question']
        )
        
        # Сохранение прогресса
        game_session.set_game_data(game_data)
        db.session.commit()
        
        return jsonify({
            'correct': is_correct,
            'game_state': 'playing',
            'next_question': next_question,
            'current_question': game_data['current_question'] + 1,
            'score': game_data['score'],
            'message': 'Правильно!' if is_correct else 'Неправильно!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при отправке ответа'}), 500

@quiz_bp.route('/api/games/quiz/hint', methods=['POST'])
@login_required
def get_quiz_hint():
    """Получить подсказку в квизе"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'ID сессии не указан'}), 400
        
        # Получение игровой сессии
        game_session = GameSession.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not game_session:
            return jsonify({'error': 'Игровая сессия не найдена'}), 404
        
        game_data = game_session.get_game_data()
        
        # Проверка состояния игры
        if game_data['game_state'] != 'playing':
            return jsonify({'error': 'Игра уже завершена'}), 400
        
        # Получение текущего вопроса
        current_question = game_data['questions'][game_data['current_question']]
        
        # Генерация подсказки
        hint = generate_quiz_hint(current_question)
        
        game_data['hints_used'] += 1
        game_session.set_game_data(game_data)
        db.session.commit()
        
        return jsonify({
            'hint': hint,
            'hints_used': game_data['hints_used']
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при получении подсказки'}), 500

@quiz_bp.route('/api/games/quiz/categories', methods=['GET'])
def get_quiz_categories():
    """Получение категорий для квиза"""
    try:
        categories = {}
        for category, questions in IT_QUESTIONS.items():
            categories[category] = {
                'name': get_category_name(category),
                'description': get_category_description(category),
                'questions_count': len(questions)
            }
        
        return jsonify({'categories': categories})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении категорий'}), 500

def prepare_question(question_data, question_index):
    """Подготовка вопроса для отправки"""
    return {
        'index': question_index,
        'question': question_data['question'],
        'options': question_data['options'],
        'total_questions': len(question_data['options'])
    }

def generate_quiz_hint(question_data):
    """Генерация подсказки для вопроса"""
    hints = [
        f"Правильный ответ: {question_data['options'][question_data['correct']]}",
        f"Объяснение: {question_data['explanation']}",
        f"Это вопрос из категории {get_category_name(question_data.get('category', 'programming_basics'))}",
        "Подумайте логически о каждом варианте ответа",
        "Исключите заведомо неправильные варианты"
    ]
    
    return random.choice(hints)

def get_category_name(category):
    """Получение названия категории"""
    names = {
        'programming_basics': 'Основы программирования',
        'web_development': 'Веб-разработка',
        'databases': 'Базы данных',
        'algorithms': 'Алгоритмы',
        'security': 'Безопасность'
    }
    return names.get(category, category)

def get_category_description(category):
    """Получение описания категории"""
    descriptions = {
        'programming_basics': 'Основные концепции программирования',
        'web_development': 'Веб-технологии и разработка',
        'databases': 'Работа с базами данных',
        'algorithms': 'Алгоритмы и структуры данных',
        'security': 'Информационная безопасность'
    }
    return descriptions.get(category, '')

def calculate_game_time(start_time_str):
    """Расчет времени игры"""
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.utcnow()
    return int((end_time - start_time).total_seconds())

def calculate_quiz_score(game_data, time_spent):
    """Расчет очков за квиз"""
    base_score = game_data['score'] * 10  # 10 очков за правильный ответ
    
    # Бонус за сложность
    difficulty_bonus = {
        'easy': 0,
        'medium': 25,
        'hard': 50
    }.get(game_data['difficulty'], 0)
    
    # Бонус за быструю сдачу
    time_bonus = 0
    if time_spent < 300:  # Менее 5 минут
        time_bonus = 25
    elif time_spent < 600:  # Менее 10 минут
        time_bonus = 15
    
    # Штраф за подсказки
    hint_penalty = game_data['hints_used'] * 5
    
    # Бонус за точность
    accuracy = (game_data['score'] / game_data['questions_count']) * 100
    accuracy_bonus = accuracy * 0.5
    
    score = base_score + difficulty_bonus + time_bonus + accuracy_bonus - hint_penalty
    
    return max(0, score)

def get_quiz_statistics(user_id):
    """Получение статистики игр Квиз"""
    try:
        games = GameScore.query.filter_by(
            user_id=user_id,
            game_type='quiz'
        ).all()
        
        if not games:
            return {
                'games_played': 0,
                'average_score': 0,
                'best_score': 0,
                'total_time': 0,
                'average_time': 0,
                'average_accuracy': 0
            }
        
        total_score = sum(game.score for game in games)
        total_time = sum(game.time_spent for game in games)
        best_score = max(game.score for game in games)
        
        return {
            'games_played': len(games),
            'average_score': round(total_score / len(games), 2),
            'best_score': best_score,
            'total_time': total_time,
            'average_time': round(total_time / len(games), 2),
            'average_accuracy': round((total_score / (len(games) * 100)) * 100, 2)
        }
        
    except Exception as e:
        return {
            'games_played': 0,
            'average_score': 0,
            'best_score': 0,
            'total_time': 0,
            'average_time': 0,
            'average_accuracy': 0
        }

def get_quiz_tips():
    """Получение советов по квизу"""
    tips = [
        "Внимательно читайте вопрос перед выбором ответа",
        "Исключайте заведомо неправильные варианты",
        "Используйте логическое мышление",
        "Не спешите с ответом - подумайте",
        "Изучайте IT материалы для улучшения знаний",
        "Практикуйтесь регулярно",
        "Используйте подсказки, если не уверены",
        "Анализируйте свои ошибки для улучшения"
    ]
    
    return random.choice(tips)
