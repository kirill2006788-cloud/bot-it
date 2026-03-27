from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import random
from datetime import datetime

lorem_generator_bp = Blueprint('lorem_generator', __name__)

# Lorem Ipsum слова
LOREM_WORDS = [
    'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit',
    'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore', 'et', 'dolore',
    'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam', 'quis', 'nostrud',
    'exercitation', 'ullamco', 'laboris', 'nisi', 'aliquip', 'ex', 'ea', 'commodo',
    'consequat', 'duis', 'aute', 'irure', 'in', 'reprehenderit', 'voluptate',
    'velit', 'esse', 'cillum', 'fugiat', 'nulla', 'pariatur', 'excepteur', 'sint',
    'occaecat', 'cupidatat', 'non', 'proident', 'sunt', 'culpa', 'qui', 'officia',
    'deserunt', 'mollit', 'anim', 'id', 'est', 'laborum'
]

# IT слова для IT Lorem
IT_WORDS = [
    'algorithm', 'database', 'framework', 'javascript', 'python', 'react', 'node',
    'api', 'rest', 'graphql', 'microservices', 'docker', 'kubernetes', 'aws',
    'azure', 'gcp', 'devops', 'ci', 'cd', 'git', 'github', 'gitlab', 'jenkins',
    'terraform', 'ansible', 'monitoring', 'logging', 'metrics', 'analytics',
    'machine', 'learning', 'artificial', 'intelligence', 'blockchain', 'cryptocurrency',
    'security', 'authentication', 'authorization', 'encryption', 'hashing',
    'testing', 'unit', 'integration', 'endpoint', 'performance', 'scalability',
    'architecture', 'design', 'pattern', 'refactoring', 'optimization', 'debugging'
]

# Русские слова для русскоязычного Lorem
RUSSIAN_WORDS = [
    'программирование', 'разработка', 'приложение', 'система', 'данные', 'информация',
    'технология', 'инновация', 'решение', 'проект', 'команда', 'процесс',
    'методология', 'архитектура', 'инфраструктура', 'безопасность', 'качество',
    'производительность', 'масштабируемость', 'надежность', 'эффективность',
    'автоматизация', 'интеграция', 'тестирование', 'развертывание', 'мониторинг',
    'аналитика', 'оптимизация', 'рефакторинг', 'отладка', 'документация',
    'спецификация', 'требования', 'функциональность', 'интерфейс', 'пользователь',
    'администратор', 'разработчик', 'тестировщик', 'аналитик', 'менеджер'
]

@lorem_generator_bp.route('/api/lorem/generate', methods=['POST'])
@login_required
def generate_lorem():
    """Генерация Lorem Ipsum текста"""
    try:
        data = request.get_json()
        text_type = data.get('type', 'paragraphs')  # paragraphs, words, sentences, custom
        count = int(data.get('count', 3))
        language = data.get('language', 'latin')  # latin, english, russian, it
        start_with_lorem = data.get('start_with_lorem', True)
        min_words = int(data.get('min_words', 5))
        max_words = int(data.get('max_words', 15))
        
        if count < 1 or count > 100:
            return jsonify({'error': 'Количество должно быть от 1 до 100'}), 400
        
        # Генерация текста
        generated_text = generate_lorem_text(
            text_type, count, language, start_with_lorem, min_words, max_words
        )
        
        return jsonify({
            'text': generated_text,
            'type': text_type,
            'count': count,
            'language': language,
            'start_with_lorem': start_with_lorem,
            'word_count': len(generated_text.split()),
            'character_count': len(generated_text),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации Lorem Ipsum'}), 500

@lorem_generator_bp.route('/api/lorem/words', methods=['POST'])
@login_required
def generate_words():
    """Генерация случайных слов"""
    try:
        data = request.get_json()
        count = int(data.get('count', 10))
        language = data.get('language', 'latin')
        unique = data.get('unique', False)
        
        if count < 1 or count > 1000:
            return jsonify({'error': 'Количество должно быть от 1 до 1000'}), 400
        
        # Генерация слов
        words = generate_random_words(count, language, unique)
        
        return jsonify({
            'words': words,
            'count': len(words),
            'language': language,
            'unique': unique,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации слов'}), 500

@lorem_generator_bp.route('/api/lorem/sentences', methods=['POST'])
@login_required
def generate_sentences():
    """Генерация случайных предложений"""
    try:
        data = request.get_json()
        count = int(data.get('count', 5))
        language = data.get('language', 'latin')
        min_words = int(data.get('min_words', 5))
        max_words = int(data.get('max_words', 20))
        
        if count < 1 or count > 100:
            return jsonify({'error': 'Количество должно быть от 1 до 100'}), 400
        
        # Генерация предложений
        sentences = generate_random_sentences(count, language, min_words, max_words)
        
        return jsonify({
            'sentences': sentences,
            'count': len(sentences),
            'language': language,
            'min_words': min_words,
            'max_words': max_words,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации предложений'}), 500

@lorem_generator_bp.route('/api/lorem/paragraphs', methods=['POST'])
@login_required
def generate_paragraphs():
    """Генерация случайных абзацев"""
    try:
        data = request.get_json()
        count = int(data.get('count', 3))
        language = data.get('language', 'latin')
        min_sentences = int(data.get('min_sentences', 3))
        max_sentences = int(data.get('max_sentences', 7))
        min_words = int(data.get('min_words', 5))
        max_words = int(data.get('max_words', 20))
        
        if count < 1 or count > 50:
            return jsonify({'error': 'Количество должно быть от 1 до 50'}), 400
        
        # Генерация абзацев
        paragraphs = generate_random_paragraphs(
            count, language, min_sentences, max_sentences, min_words, max_words
        )
        
        return jsonify({
            'paragraphs': paragraphs,
            'count': len(paragraphs),
            'language': language,
            'min_sentences': min_sentences,
            'max_sentences': max_sentences,
            'min_words': min_words,
            'max_words': max_words,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации абзацев'}), 500

@lorem_generator_bp.route('/api/lorem/custom', methods=['POST'])
@login_required
def generate_custom():
    """Генерация кастомного текста"""
    try:
        data = request.get_json()
        template = data.get('template', '')
        language = data.get('language', 'latin')
        variables = data.get('variables', {})
        
        if not template:
            return jsonify({'error': 'Шаблон не указан'}), 400
        
        # Генерация кастомного текста
        custom_text = generate_custom_text(template, language, variables)
        
        return jsonify({
            'text': custom_text,
            'template': template,
            'language': language,
            'variables': variables,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации кастомного текста'}), 500

@lorem_generator_bp.route('/api/lorem/languages', methods=['GET'])
def get_languages():
    """Получение доступных языков"""
    try:
        languages = {
            'latin': {
                'name': 'Латинский (Lorem Ipsum)',
                'description': 'Классический Lorem Ipsum текст',
                'words_count': len(LOREM_WORDS)
            },
            'english': {
                'name': 'Английский',
                'description': 'Английские слова для генерации текста',
                'words_count': len(IT_WORDS)
            },
            'russian': {
                'name': 'Русский',
                'description': 'Русские слова для генерации текста',
                'words_count': len(RUSSIAN_WORDS)
            },
            'it': {
                'name': 'IT термины',
                'description': 'IT термины и технические слова',
                'words_count': len(IT_WORDS)
            }
        }
        
        return jsonify({'languages': languages})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении языков'}), 500

@lorem_generator_bp.route('/api/lorem/templates', methods=['GET'])
def get_templates():
    """Получение доступных шаблонов"""
    try:
        templates = {
            'paragraph': {
                'name': 'Абзац',
                'template': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                'description': 'Стандартный абзац Lorem Ipsum'
            },
            'sentence': {
                'name': 'Предложение',
                'template': 'Lorem ipsum dolor sit amet.',
                'description': 'Короткое предложение'
            },
            'word': {
                'name': 'Слово',
                'template': 'lorem',
                'description': 'Одно слово'
            },
            'title': {
                'name': 'Заголовок',
                'template': 'Lorem Ipsum Dolor Sit Amet',
                'description': 'Заголовок в Title Case'
            },
            'list': {
                'name': 'Список',
                'template': '• Lorem ipsum dolor\n• Sit amet consectetur\n• Adipiscing elit sed',
                'description': 'Список с маркерами'
            }
        }
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении шаблонов'}), 500

def generate_lorem_text(text_type, count, language, start_with_lorem, min_words, max_words):
    """Генерация Lorem Ipsum текста"""
    if text_type == 'paragraphs':
        return generate_random_paragraphs(count, language, 3, 7, min_words, max_words)
    elif text_type == 'sentences':
        sentences = generate_random_sentences(count, language, min_words, max_words)
        return ' '.join(sentences)
    elif text_type == 'words':
        words = generate_random_words(count, language, False)
        return ' '.join(words)
    else:
        return generate_random_paragraphs(1, language, 3, 7, min_words, max_words)

def generate_random_words(count, language, unique):
    """Генерация случайных слов"""
    word_list = get_word_list(language)
    
    if unique and count > len(word_list):
        count = len(word_list)
    
    if unique:
        words = random.sample(word_list, count)
    else:
        words = [random.choice(word_list) for _ in range(count)]
    
    return words

def generate_random_sentences(count, language, min_words, max_words):
    """Генерация случайных предложений"""
    sentences = []
    
    for _ in range(count):
        word_count = random.randint(min_words, max_words)
        words = generate_random_words(word_count, language, False)
        
        # Первая буква заглавная
        if words:
            words[0] = words[0].capitalize()
        
        sentence = ' '.join(words) + '.'
        sentences.append(sentence)
    
    return sentences

def generate_random_paragraphs(count, language, min_sentences, max_sentences, min_words, max_words):
    """Генерация случайных абзацев"""
    paragraphs = []
    
    for _ in range(count):
        sentence_count = random.randint(min_sentences, max_sentences)
        sentences = generate_random_sentences(sentence_count, language, min_words, max_words)
        paragraph = ' '.join(sentences)
        paragraphs.append(paragraph)
    
    return paragraphs

def generate_custom_text(template, language, variables):
    """Генерация кастомного текста"""
    # Замена переменных в шаблоне
    text = template
    
    for key, value in variables.items():
        text = text.replace(f'{{{key}}}', str(value))
    
    # Замена плейсхолдеров на случайные слова
    word_list = get_word_list(language)
    
    # Замена {word} на случайное слово
    while '{word}' in text:
        random_word = random.choice(word_list)
        text = text.replace('{word}', random_word, 1)
    
    # Замена {sentence} на случайное предложение
    while '{sentence}' in text:
        random_sentence = generate_random_sentences(1, language, 5, 15)[0]
        text = text.replace('{sentence}', random_sentence, 1)
    
    # Замена {paragraph} на случайный абзац
    while '{paragraph}' in text:
        random_paragraph = generate_random_paragraphs(1, language, 3, 7, 5, 20)[0]
        text = text.replace('{paragraph}', random_paragraph, 1)
    
    return text

def get_word_list(language):
    """Получение списка слов для языка"""
    if language == 'latin':
        return LOREM_WORDS
    elif language == 'english' or language == 'it':
        return IT_WORDS
    elif language == 'russian':
        return RUSSIAN_WORDS
    else:
        return LOREM_WORDS

def get_lorem_generator_statistics(user_id):
    """Получение статистики использования генератора Lorem Ipsum"""
    # Здесь можно добавить статистику использования
    return {
        'texts_generated': 0,
        'words_generated': 0,
        'most_used_language': 'latin',
        'most_used_type': 'paragraphs',
        'total_characters': 0
    }

def get_lorem_generator_tips():
    """Получение советов по использованию генератора Lorem Ipsum"""
    tips = [
        "Используйте Lorem Ipsum для заполнения макетов и прототипов",
        "Выбирайте подходящий язык для вашего проекта",
        "Настройте количество слов и предложений под ваши нужды",
        "Используйте кастомные шаблоны для специфических случаев",
        "Lorem Ipsum помогает сосредоточиться на дизайне, а не на тексте",
        "Разные языки подходят для разных типов проектов",
        "IT термины хороши для технических проектов",
        "Русский язык подходит для локализованных проектов"
    ]
    
    return tips
