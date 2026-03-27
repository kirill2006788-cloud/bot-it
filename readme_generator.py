from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, User
import json
from datetime import datetime

readme_bp = Blueprint('readme', __name__)

@readme_bp.route('/api/readme/generate', methods=['POST'])
@login_required
def generate_readme():
    """Генерация README.md файла"""
    try:
        data = request.get_json()
        
        # Параметры проекта
        project_name = data.get('project_name', 'My Project')
        description = data.get('description', 'A wonderful project')
        author = data.get('author', current_user.username)
        email = data.get('email', current_user.email)
        github_username = data.get('github_username', '')
        website = data.get('website', '')
        license_type = data.get('license', 'MIT')
        version = data.get('version', '1.0.0')
        
        # Технологии
        technologies = data.get('technologies', [])
        features = data.get('features', [])
        installation_steps = data.get('installation_steps', [])
        usage_examples = data.get('usage_examples', [])
        
        # Дополнительные секции
        include_contributing = data.get('include_contributing', True)
        include_license = data.get('include_license', True)
        include_badges = data.get('include_badges', True)
        include_screenshots = data.get('include_screenshots', False)
        include_api_docs = data.get('include_api_docs', False)
        
        # Генерация README
        readme_content = generate_readme_content(
            project_name=project_name,
            description=description,
            author=author,
            email=email,
            github_username=github_username,
            website=website,
            license_type=license_type,
            version=version,
            technologies=technologies,
            features=features,
            installation_steps=installation_steps,
            usage_examples=usage_examples,
            include_contributing=include_contributing,
            include_license=include_license,
            include_badges=include_badges,
            include_screenshots=include_screenshots,
            include_api_docs=include_api_docs
        )
        
        return jsonify({
            'readme_content': readme_content,
            'project_name': project_name,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при генерации README'}), 500

@readme_bp.route('/api/readme/templates', methods=['GET'])
def get_readme_templates():
    """Получение шаблонов README"""
    try:
        templates = {
            'basic': {
                'name': 'Базовый',
                'description': 'Простой README с основными секциями',
                'sections': ['title', 'description', 'installation', 'usage', 'license']
            },
            'detailed': {
                'name': 'Подробный',
                'description': 'Полный README с множеством секций',
                'sections': ['title', 'description', 'badges', 'features', 'installation', 'usage', 'api', 'contributing', 'license']
            },
            'minimal': {
                'name': 'Минимальный',
                'description': 'Минимальный README только с самым необходимым',
                'sections': ['title', 'description', 'installation']
            },
            'professional': {
                'name': 'Профессиональный',
                'description': 'Профессиональный README для корпоративных проектов',
                'sections': ['title', 'description', 'badges', 'features', 'installation', 'usage', 'api', 'tests', 'contributing', 'changelog', 'license']
            }
        }
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении шаблонов'}), 500

@readme_bp.route('/api/readme/preview', methods=['POST'])
def preview_readme():
    """Предварительный просмотр README"""
    try:
        data = request.get_json()
        readme_content = data.get('readme_content', '')
        
        # Конвертация Markdown в HTML (упрощенная версия)
        html_content = convert_markdown_to_html(readme_content)
        
        return jsonify({
            'html_content': html_content,
            'markdown_content': readme_content
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при предварительном просмотре'}), 500

def generate_readme_content(project_name, description, author, email, github_username, 
                          website, license_type, version, technologies, features, 
                          installation_steps, usage_examples, include_contributing, 
                          include_license, include_badges, include_screenshots, 
                          include_api_docs):
    """Генерация содержимого README"""
    
    readme_parts = []
    
    # Заголовок
    readme_parts.append(f"# {project_name}")
    readme_parts.append("")
    
    # Описание
    readme_parts.append(f"{description}")
    readme_parts.append("")
    
    # Бейджи
    if include_badges:
        badges = generate_badges(license_type, version, github_username, project_name)
        readme_parts.append(badges)
        readme_parts.append("")
    
    # Содержание
    readme_parts.append("## 📋 Содержание")
    readme_parts.append("")
    readme_parts.append("- [Установка](#-установка)")
    readme_parts.append("- [Использование](#-использование)")
    if features:
        readme_parts.append("- [Возможности](#-возможности)")
    if technologies:
        readme_parts.append("- [Технологии](#-технологии)")
    if include_api_docs:
        readme_parts.append("- [API](#-api)")
    if include_contributing:
        readme_parts.append("- [Вклад в проект](#-вклад-в-проект)")
    if include_license:
        readme_parts.append("- [Лицензия](#-лицензия)")
    readme_parts.append("")
    
    # Возможности
    if features:
        readme_parts.append("## ✨ Возможности")
        readme_parts.append("")
        for feature in features:
            readme_parts.append(f"- {feature}")
        readme_parts.append("")
    
    # Технологии
    if technologies:
        readme_parts.append("## 🛠️ Технологии")
        readme_parts.append("")
        tech_list = ", ".join(technologies)
        readme_parts.append(f"Проект использует следующие технологии: {tech_list}")
        readme_parts.append("")
    
    # Установка
    readme_parts.append("## 🚀 Установка")
    readme_parts.append("")
    if installation_steps:
        for i, step in enumerate(installation_steps, 1):
            readme_parts.append(f"{i}. {step}")
    else:
        readme_parts.append("1. Клонируйте репозиторий:")
        readme_parts.append("```bash")
        if github_username:
            readme_parts.append(f"git clone https://github.com/{github_username}/{project_name.lower().replace(' ', '-')}.git")
        else:
            readme_parts.append("git clone <repository-url>")
        readme_parts.append("```")
        readme_parts.append("")
        readme_parts.append("2. Перейдите в директорию проекта:")
        readme_parts.append("```bash")
        readme_parts.append(f"cd {project_name.lower().replace(' ', '-')}")
        readme_parts.append("```")
        readme_parts.append("")
        readme_parts.append("3. Установите зависимости:")
        readme_parts.append("```bash")
        readme_parts.append("pip install -r requirements.txt")
        readme_parts.append("```")
    readme_parts.append("")
    
    # Использование
    readme_parts.append("## 📖 Использование")
    readme_parts.append("")
    if usage_examples:
        for example in usage_examples:
            readme_parts.append(example)
    else:
        readme_parts.append("```python")
        readme_parts.append("from project import main")
        readme_parts.append("")
        readme_parts.append("if __name__ == '__main__':")
        readme_parts.append("    main()")
        readme_parts.append("```")
    readme_parts.append("")
    
    # API документация
    if include_api_docs:
        readme_parts.append("## 📚 API")
        readme_parts.append("")
        readme_parts.append("### Основные функции")
        readme_parts.append("")
        readme_parts.append("| Функция | Описание | Параметры | Возвращает |")
        readme_parts.append("|---------|----------|-----------|------------|")
        readme_parts.append("| `main()` | Основная функция | - | None |")
        readme_parts.append("| `init()` | Инициализация | config | bool |")
        readme_parts.append("")
    
    # Скриншоты
    if include_screenshots:
        readme_parts.append("## 📸 Скриншоты")
        readme_parts.append("")
        readme_parts.append("![Скриншот 1](screenshots/screenshot1.png)")
        readme_parts.append("")
        readme_parts.append("*Описание скриншота*")
        readme_parts.append("")
    
    # Вклад в проект
    if include_contributing:
        readme_parts.append("## 🤝 Вклад в проект")
        readme_parts.append("")
        readme_parts.append("Мы приветствуем вклад в развитие проекта!")
        readme_parts.append("")
        readme_parts.append("1. Форкните репозиторий")
        readme_parts.append("2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)")
        readme_parts.append("3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)")
        readme_parts.append("4. Отправьте в ветку (`git push origin feature/AmazingFeature`)")
        readme_parts.append("5. Откройте Pull Request")
        readme_parts.append("")
    
    # Лицензия
    if include_license:
        readme_parts.append("## 📄 Лицензия")
        readme_parts.append("")
        readme_parts.append(f"Этот проект распространяется под лицензией {license_type}. См. файл `LICENSE` для подробностей.")
        readme_parts.append("")
    
    # Контакты
    readme_parts.append("## 📞 Контакты")
    readme_parts.append("")
    readme_parts.append(f"**{author}**")
    if email:
        readme_parts.append(f"- Email: {email}")
    if github_username:
        readme_parts.append(f"- GitHub: [@{github_username}](https://github.com/{github_username})")
    if website:
        readme_parts.append(f"- Website: {website}")
    readme_parts.append("")
    
    # Ссылка на проект
    if github_username:
        readme_parts.append(f"Ссылка на проект: [https://github.com/{github_username}/{project_name.lower().replace(' ', '-')}](https://github.com/{github_username}/{project_name.lower().replace(' ', '-')})")
        readme_parts.append("")
    
    return "\n".join(readme_parts)

def generate_badges(license_type, version, github_username, project_name):
    """Генерация бейджей"""
    badges = []
    
    # Лицензия
    license_badge = f"![License](https://img.shields.io/badge/license-{license_type}-blue.svg)"
    badges.append(license_badge)
    
    # Версия
    version_badge = f"![Version](https://img.shields.io/badge/version-{version}-green.svg)"
    badges.append(version_badge)
    
    # Статус сборки (заглушка)
    build_badge = "![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)"
    badges.append(build_badge)
    
    # Python версия
    python_badge = "![Python](https://img.shields.io/badge/python-3.8+-blue.svg)"
    badges.append(python_badge)
    
    # GitHub звезды
    if github_username:
        stars_badge = f"![GitHub stars](https://img.shields.io/github/stars/{github_username}/{project_name.lower().replace(' ', '-')}?style=social)"
        badges.append(stars_badge)
    
    return " ".join(badges)

def convert_markdown_to_html(markdown_content):
    """Конвертация Markdown в HTML (упрощенная версия)"""
    html = markdown_content
    
    # Заголовки
    html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
    html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
    html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
    
    # Жирный текст
    html = html.replace('**', '<strong>').replace('**', '</strong>')
    
    # Курсив
    html = html.replace('*', '<em>').replace('*', '</em>')
    
    # Код
    html = html.replace('```', '<pre><code>').replace('```', '</code></pre>')
    html = html.replace('`', '<code>').replace('`', '</code>')
    
    # Ссылки
    import re
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    html = re.sub(link_pattern, r'<a href="\2">\1</a>', html)
    
    # Списки
    html = html.replace('- ', '<li>').replace('\n- ', '</li>\n<li>')
    
    # Переносы строк
    html = html.replace('\n', '<br>\n')
    
    return html

def get_readme_templates_data():
    """Получение данных шаблонов README"""
    return {
        'technologies': [
            'Python', 'JavaScript', 'TypeScript', 'React', 'Vue.js', 'Angular',
            'Node.js', 'Express', 'Flask', 'Django', 'FastAPI', 'PostgreSQL',
            'MySQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'AWS',
            'Azure', 'Google Cloud', 'Git', 'GitHub', 'GitLab'
        ],
        'licenses': [
            'MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'ISC',
            'Unlicense', 'LGPL-3.0', 'MPL-2.0'
        ],
        'features_templates': [
            'Быстрая и легкая установка',
            'Подробная документация',
            'Поддержка множества платформ',
            'Активное сообщество',
            'Регулярные обновления',
            'Высокая производительность',
            'Безопасность',
            'Масштабируемость'
        ],
        'installation_templates': [
            'Установка через pip',
            'Установка через npm',
            'Установка через Docker',
            'Установка из исходного кода',
            'Установка через пакетный менеджер'
        ]
    }
