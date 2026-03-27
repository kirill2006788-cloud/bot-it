from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import random
import string
import qrcode
import requests
from io import BytesIO
import base64
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from claude_helper import ClaudeHelper

app = Flask(__name__)
CORS(app)

# Глобальные переменные для демонстрации
user_stats = {
    'total_users': 1250,
    'active_today': 89,
    'games_played': 3420,
    'tools_used': 15680
}

class WebApp:
    def __init__(self):
        self.user_sessions = {}
        self.claude = ClaudeHelper()
        self.chat_histories = {}
        self.projects = {}
        
    def generate_password(self, length=12, include_symbols=True):
        """Генератор паролей"""
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*"
        return ''.join(random.choice(characters) for _ in range(length))
    
    def create_qr_code(self, text):
        """Создание QR-кода"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        return base64.b64encode(bio.getvalue()).decode()
    
    def get_weather_data(self, city):
        """Получение данных о погоде (заглушка)"""
        return {
            'city': city,
            'temperature': random.randint(-10, 35),
            'description': random.choice(['ясно', 'облачно', 'дождь', 'снег', 'туман']),
            'humidity': random.randint(30, 90),
            'wind_speed': random.randint(1, 15),
            'pressure': random.randint(750, 780)
        }
    
    def convert_currency(self, amount, from_currency, to_currency='RUB'):
        """Конвертация валют (заглушка)"""
        rates = {
            'USD': 95.5,
            'EUR': 102.3,
            'GBP': 118.7,
            'RUB': 1.0
        }
        
        if from_currency not in rates:
            return None
        
        rub_amount = amount * rates[from_currency]
        return {
            'amount': amount,
            'from_currency': from_currency,
            'to_currency': to_currency,
            'result': rub_amount,
            'rate': rates[from_currency]
        }
    
    def generate_code(self, language, description):
        """Генератор кода"""
        code_templates = {
            'python': f"""
def {description.replace(' ', '_')}():
    \"\"\"
    Функция для: {description}
    \"\"\"
    # Ваш код здесь
    pass

# Пример использования
result = {description.replace(' ', '_')}()
print(result)
""",
            'javascript': f"""
function {description.replace(' ', '')}() {{
    // Функция для: {description}
    // Ваш код здесь
}}

// Пример использования
const result = {description.replace(' ', '')}();
console.log(result);
""",
            'java': f"""
public class {description.replace(' ', '')} {{
    public static void {description.replace(' ', '')}() {{
        // Функция для: {description}
        // Ваш код здесь
    }}
    
    public static void main(String[] args) {{
        {description.replace(' ', '')}();
    }}
}}
""",
            'html': f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{description}</title>
</head>
<body>
    <h1>{description}</h1>
    <!-- Ваш HTML код здесь -->
</body>
</html>
""",
            'css': f"""
/* Стили для: {description} */

.{description.replace(' ', '-').lower()} {{
    /* Ваши CSS стили здесь */
}}
""",
            'sql': f"""
-- SQL запрос для: {description}

SELECT * 
FROM table_name 
WHERE condition = 'value';

-- Ваш SQL код здесь
"""
        }
        
        return code_templates.get(language.lower(), "Неподдерживаемый язык программирования")

web_app = WebApp()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', stats=user_stats)

@app.route('/api/password', methods=['POST'])
def api_password():
    """API для генерации пароля"""
    data = request.get_json()
    length = data.get('length', 12)
    include_symbols = data.get('include_symbols', True)
    
    password = web_app.generate_password(length, include_symbols)
    
    return jsonify({
        'password': password,
        'length': length,
        'include_symbols': include_symbols
    })

@app.route('/api/qr', methods=['POST'])
def api_qr():
    """API для создания QR-кода"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Текст не может быть пустым'}), 400
    
    if len(text) > 1000:
        return jsonify({'error': 'Текст слишком длинный'}), 400
    
    qr_base64 = web_app.create_qr_code(text)
    
    return jsonify({
        'qr_code': qr_base64,
        'text': text
    })

@app.route('/api/weather', methods=['POST'])
def api_weather():
    """API для получения погоды"""
    data = request.get_json()
    city = data.get('city', '')
    
    if not city:
        return jsonify({'error': 'Город не может быть пустым'}), 400
    
    weather_data = web_app.get_weather_data(city)
    
    return jsonify(weather_data)

@app.route('/api/currency', methods=['POST'])
def api_currency():
    """API для конвертации валют"""
    data = request.get_json()
    amount = data.get('amount', 0)
    from_currency = data.get('from_currency', 'USD')
    
    if amount <= 0:
        return jsonify({'error': 'Сумма должна быть больше 0'}), 400
    
    result = web_app.convert_currency(amount, from_currency)
    
    if result is None:
        return jsonify({'error': 'Неподдерживаемая валюта'}), 400
    
    return jsonify(result)

@app.route('/api/code', methods=['POST'])
def api_code():
    """API для генерации кода"""
    data = request.get_json()
    language = data.get('language', 'python')
    description = data.get('description', '')
    
    if not description:
        return jsonify({'error': 'Описание не может быть пустым'}), 400
    
    code = web_app.generate_code(language, description)
    
    return jsonify({
        'code': code,
        'language': language,
        'description': description
    })

@app.route('/api/stats')
def api_stats():
    """API для получения статистики"""
    return jsonify(user_stats)

@app.route('/api/game/guess', methods=['POST'])
def api_guess_game():
    """API для игры 'Угадай число'"""
    data = request.get_json()
    guess = data.get('guess')
    session_id = data.get('session_id')
    
    if not session_id:
        # Создаем новую игру
        secret_number = random.randint(1, 100)
        session_id = f"game_{random.randint(1000, 9999)}"
        web_app.user_sessions[session_id] = {
            'secret_number': secret_number,
            'attempts': 0,
            'game_type': 'guess'
        }
        
        return jsonify({
            'session_id': session_id,
            'message': 'Игра началась! Угадайте число от 1 до 100',
            'game_started': True
        })
    
    if session_id not in web_app.user_sessions:
        return jsonify({'error': 'Сессия не найдена'}), 400
    
    game = web_app.user_sessions[session_id]
    game['attempts'] += 1
    
    if guess == game['secret_number']:
        score = max(0, 20 - game['attempts'])
        del web_app.user_sessions[session_id]
        
        return jsonify({
            'won': True,
            'message': f'Поздравляю! Вы угадали число {game["secret_number"]} за {game["attempts"]} попыток!',
            'score': score,
            'attempts': game['attempts']
        })
    elif guess < game['secret_number']:
        return jsonify({
            'won': False,
            'message': 'Больше!',
            'attempts': game['attempts']
        })
    else:
        return jsonify({
            'won': False,
            'message': 'Меньше!',
            'attempts': game['attempts']
        })

@app.route('/api/quiz', methods=['POST'])
def api_quiz():
    """API для викторины"""
    questions = [
        {
            'question': 'Какой язык программирования создал Гвидо ван Россум?',
            'options': ['Python', 'Java', 'C++', 'JavaScript'],
            'correct': 0
        },
        {
            'question': 'Что означает HTML?',
            'options': ['HyperText Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlink Text Management Language'],
            'correct': 0
        },
        {
            'question': 'Какой символ используется для комментариев в Python?',
            'options': ['//', '/*', '#', '--'],
            'correct': 2
        },
        {
            'question': 'Что такое API?',
            'options': ['Application Programming Interface', 'Advanced Programming Interface', 'Automated Programming Interface', 'Application Process Interface'],
            'correct': 0
        },
        {
            'question': 'Какой протокол используется для веб-страниц?',
            'options': ['HTTP', 'FTP', 'SMTP', 'TCP'],
            'correct': 0
        }
    ]
    
    question = random.choice(questions)
    
    return jsonify({
        'question': question['question'],
        'options': question['options'],
        'correct': question['correct']
    })

@app.route('/api/quiz/check', methods=['POST'])
def api_quiz_check():
    """API для проверки ответа викторины"""
    data = request.get_json()
    answer = data.get('answer')
    correct_answer = data.get('correct_answer')
    
    is_correct = answer == correct_answer
    score = 10 if is_correct else 0
    
    return jsonify({
        'correct': is_correct,
        'score': score,
        'message': 'Правильно!' if is_correct else 'Неправильно!'
    })

# WebApp Routes
@app.route('/webapp')
def webapp():
    """Главная страница WebApp"""
    return send_from_directory('webapp', 'index.html')

@app.route('/webapp/<path:filename>')
def webapp_files(filename):
    """Статические файлы WebApp"""
    return send_from_directory('webapp', filename)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API для чата с AI"""
    data = request.get_json()
    user_id = data.get('user_id', 'demo')
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Сообщение пустое'}), 400
    
    # Получаем или создаем историю чата
    if user_id not in web_app.chat_histories:
        web_app.chat_histories[user_id] = []
    
    # Добавляем сообщение пользователя
    web_app.chat_histories[user_id].append({
        'role': 'user',
        'content': message
    })
    
    # Формируем контекст
    context = "\n\n".join([
        f"{'Пользователь' if msg['role'] == 'user' else 'Ассистент'}: {msg['content']}"
        for msg in web_app.chat_histories[user_id][-10:]
    ])
    
    prompt = f"""Ты дружелюбный AI-ассистент. Веди естественный разговор.

История:
{context}

Ответь на последнее сообщение пользователя."""
    
    # Получаем ответ от Claude
    response = web_app.claude.ask_question(prompt)
    
    # Добавляем ответ в историю
    web_app.chat_histories[user_id].append({
        'role': 'assistant',
        'content': response
    })
    
    return jsonify({
        'response': response,
        'message_count': len(web_app.chat_histories[user_id])
    })

@app.route('/api/ai-help', methods=['POST'])
def api_ai_help():
    """API для помощи AI с кодом"""
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    if not code:
        return jsonify({'error': 'Код пустой'}), 400
    
    # Получаем предложения от Claude
    suggestion = web_app.claude.explain_code(code, language)
    
    return jsonify({
        'suggestion': suggestion,
        'language': language
    })

@app.route('/api/generate-project', methods=['POST'])
def api_generate_project():
    """API для генерации проекта"""
    data = request.get_json()
    user_id = data.get('user_id', 'demo')
    name = data.get('name', 'MyProject')
    description = data.get('description', '')
    
    if not description:
        return jsonify({'error': 'Описание пустое'}), 400
    
    # Генерируем проект через Claude
    files = web_app.claude.generate_multiple_files(description)
    
    # Создаем ZIP
    zip_buffer = web_app.claude.create_zip_from_files(files)
    
    # Сохраняем проект
    project_id = f"{user_id}_{int(random.random() * 1000000)}"
    web_app.projects[project_id] = {
        'id': project_id,
        'name': name,
        'description': description,
        'files': files,
        'files_count': len(files),
        'zip_data': zip_buffer.getvalue()
    }
    
    return jsonify({
        'project': {
            'id': project_id,
            'name': name,
            'description': description,
            'files_count': len(files)
        },
        'files_count': len(files)
    })

@app.route('/api/download-project/<project_id>')
def api_download_project(project_id):
    """Скачать проект"""
    if project_id not in web_app.projects:
        return jsonify({'error': 'Проект не найден'}), 404
    
    project = web_app.projects[project_id]
    
    return send_file(
        BytesIO(project['zip_data']),
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{project['name']}.zip"
    )

if __name__ == '__main__':
    print("🌐 Веб-приложение IT Helper Bot запущено!")
    print(f"📱 Откройте браузер: http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
