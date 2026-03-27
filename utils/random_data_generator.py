from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import random
import string
import uuid
from datetime import datetime, timedelta
import names
import json

random_data_generator_bp = Blueprint('random_data_generator', __name__)

# Предустановленные данные
COUNTRIES = [
    'Россия', 'США', 'Китай', 'Германия', 'Япония', 'Великобритания', 'Франция',
    'Италия', 'Бразилия', 'Канада', 'Австралия', 'Индия', 'Испания', 'Мексика',
    'Нидерланды', 'Швеция', 'Норвегия', 'Дания', 'Финляндия', 'Польша'
]

CITIES = [
    'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
    'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону',
    'Нью-Йорк', 'Лос-Анджелес', 'Чикаго', 'Хьюстон', 'Финикс',
    'Лондон', 'Париж', 'Берлин', 'Мадрид', 'Рим'
]

COMPANIES = [
    'Apple Inc.', 'Microsoft Corporation', 'Google LLC', 'Amazon.com Inc.',
    'Facebook Inc.', 'Tesla Inc.', 'Netflix Inc.', 'Uber Technologies Inc.',
    'Airbnb Inc.', 'Spotify Technology S.A.', 'Twitter Inc.', 'LinkedIn Corporation',
    'Oracle Corporation', 'IBM Corporation', 'Intel Corporation', 'Cisco Systems Inc.',
    'Adobe Inc.', 'Salesforce.com Inc.', 'ServiceNow Inc.', 'Workday Inc.'
]

JOB_TITLES = [
    'Software Engineer', 'Data Scientist', 'Product Manager', 'UX Designer',
    'DevOps Engineer', 'Backend Developer', 'Frontend Developer', 'Full Stack Developer',
    'Mobile Developer', 'QA Engineer', 'System Administrator', 'Database Administrator',
    'Security Engineer', 'Cloud Architect', 'Technical Writer', 'Scrum Master',
    'Project Manager', 'Business Analyst', 'Marketing Manager', 'Sales Manager'
]

PROGRAMMING_LANGUAGES = [
    'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift',
    'Kotlin', 'PHP', 'Ruby', 'Scala', 'TypeScript', 'Dart', 'R', 'MATLAB'
]

FRAMEWORKS = [
    'React', 'Vue.js', 'Angular', 'Django', 'Flask', 'Express.js', 'Spring',
    'Laravel', 'Rails', 'ASP.NET', 'Flutter', 'Xamarin', 'Ionic', 'Cordova'
]

@random_data_generator_bp.route('/api/random/person', methods=['POST'])
@login_required
def generate_person():
    """Генерация случайного человека"""
    try:
        data = request.get_json()
        count = int(data.get('count', 1))
        gender = data.get('gender', 'random')  # male, female, random
        country = data.get('country', 'random')
        include_contact = data.get('include_contact', True)
        include_address = data.get('include_address', True)
        include_job = data.get('include_job', True)
        
        if count < 1 or count > 100:
            return jsonify({'error': 'Количество должно быть от 1 до 100'}), 400
        
        # Генерация людей
        people = []
        for _ in range(count):
            person = generate_random_person(gender, country, include_contact, include_address, include_job)
            people.append(person)
        
        return jsonify({
            'people': people,
            'count': len(people),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при генерации людей'}), 500

@random_data_generator_bp.route('/api/random/company', methods=['POST'])
@login_required
def generate_company():
    """Генерация случайной компании"""
    try:
        data = request.get_json()
        count = int(data.get('count', 1))
        include_employees = data.get('include_employees', True)
        include_revenue = data.get('include_revenue', True)
        include_contact = data.get('include_contact', True)
        
        if count < 1 or count > 100:
            return jsonify({'error': 'Количество должно быть от 1 до 100'}), 400
        
        # Генерация компаний
        companies = []
        for _ in range(count):
            company = generate_random_company(include_employees, include_revenue, include_contact)
            companies.append(company)
        
        return jsonify({
            'companies': companies,
            'count': len(companies),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при генерации компаний'}), 500

@random_data_generator_bp.route('/api/random/developer', methods=['POST'])
@login_required
def generate_developer():
    """Генерация случайного разработчика"""
    try:
        data = request.get_json()
        count = int(data.get('count', 1))
        experience_years = data.get('experience_years', 'random')  # 0-5, 5-10, 10+, random
        include_skills = data.get('include_skills', True)
        include_projects = data.get('include_projects', True)
        
        if count < 1 or count > 100:
            return jsonify({'error': 'Количество должно быть от 1 до 100'}), 400
        
        # Генерация разработчиков
        developers = []
        for _ in range(count):
            developer = generate_random_developer(experience_years, include_skills, include_projects)
            developers.append(developer)
        
        return jsonify({
            'developers': developers,
            'count': len(developers),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при генерации разработчиков'}), 500

@random_data_generator_bp.route('/api/random/project', methods=['POST'])
@login_required
def generate_project():
    """Генерация случайного проекта"""
    try:
        data = request.get_json()
        count = int(data.get('count', 1))
        project_type = data.get('type', 'random')  # web, mobile, desktop, api, random
        include_team = data.get('include_team', True)
        include_technologies = data.get('include_technologies', True)
        
        if count < 1 or count > 100:
            return jsonify({'error': 'Количество должно быть от 1 до 100'}), 400
        
        # Генерация проектов
        projects = []
        for _ in range(count):
            project = generate_random_project(project_type, include_team, include_technologies)
            projects.append(project)
        
        return jsonify({
            'projects': projects,
            'count': len(projects),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при генерации проектов'}), 500

@random_data_generator_bp.route('/api/random/data', methods=['POST'])
@login_required
def generate_custom_data():
    """Генерация кастомных данных"""
    try:
        data = request.get_json()
        template = data.get('template', {})
        count = int(data.get('count', 1))
        
        if count < 1 or count > 1000:
            return jsonify({'error': 'Количество должно быть от 1 до 1000'}), 400
        
        # Генерация кастомных данных
        custom_data = []
        for _ in range(count):
            item = generate_custom_data_item(template)
            custom_data.append(item)
        
        return jsonify({
            'data': custom_data,
            'count': len(custom_data),
            'template': template,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при генерации кастомных данных'}), 500

@random_data_generator_bp.route('/api/random/export', methods=['POST'])
@login_required
def export_random_data():
    """Экспорт случайных данных"""
    try:
        data = request.get_json()
        data_type = data.get('type', 'person')  # person, company, developer, project
        count = int(data.get('count', 10))
        format_type = data.get('format', 'json')  # json, csv, xml
        include_headers = data.get('include_headers', True)
        
        if count < 1 or count > 1000:
            return jsonify({'error': 'Количество должно быть от 1 до 1000'}), 400
        
        # Генерация данных
        generated_data = generate_data_for_export(data_type, count)
        
        # Экспорт в нужном формате
        if format_type == 'json':
            export_data = json.dumps(generated_data, ensure_ascii=False, indent=2)
        elif format_type == 'csv':
            export_data = export_to_csv(generated_data, include_headers)
        elif format_type == 'xml':
            export_data = export_to_xml(generated_data, data_type)
        else:
            export_data = json.dumps(generated_data, ensure_ascii=False, indent=2)
        
        return jsonify({
            'data': export_data,
            'format': format_type,
            'count': len(generated_data),
            'exported_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при экспорте данных'}), 500

@random_data_generator_bp.route('/api/random/templates', methods=['GET'])
def get_data_templates():
    """Получение шаблонов данных"""
    try:
        templates = {
            'person': {
                'name': 'Человек',
                'fields': ['first_name', 'last_name', 'email', 'phone', 'age', 'gender', 'country', 'city'],
                'description': 'Персональные данные человека'
            },
            'company': {
                'name': 'Компания',
                'fields': ['name', 'industry', 'size', 'revenue', 'website', 'email', 'phone', 'address'],
                'description': 'Данные компании'
            },
            'developer': {
                'name': 'Разработчик',
                'fields': ['name', 'email', 'skills', 'experience', 'languages', 'frameworks', 'projects'],
                'description': 'Профиль разработчика'
            },
            'project': {
                'name': 'Проект',
                'fields': ['name', 'description', 'type', 'technologies', 'team_size', 'duration', 'status'],
                'description': 'Информация о проекте'
            }
        }
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при получении шаблонов'}), 500

def generate_random_person(gender, country, include_contact, include_address, include_job):
    """Генерация случайного человека"""
    # Выбор пола
    if gender == 'random':
        gender = random.choice(['male', 'female'])
    
    # Генерация имени
    if gender == 'male':
        first_name = names.get_first_name(gender='male')
    else:
        first_name = names.get_first_name(gender='female')
    
    last_name = names.get_last_name()
    
    person = {
        'first_name': first_name,
        'last_name': last_name,
        'full_name': f'{first_name} {last_name}',
        'gender': gender,
        'age': random.randint(18, 80)
    }
    
    # Контактная информация
    if include_contact:
        person['email'] = generate_email(first_name, last_name)
        person['phone'] = generate_phone()
    
    # Адрес
    if include_address:
        person['country'] = country if country != 'random' else random.choice(COUNTRIES)
        person['city'] = random.choice(CITIES)
        person['address'] = generate_address()
    
    # Работа
    if include_job:
        person['job_title'] = random.choice(JOB_TITLES)
        person['company'] = random.choice(COMPANIES)
        person['salary'] = random.randint(30000, 200000)
    
    return person

def generate_random_company(include_employees, include_revenue, include_contact):
    """Генерация случайной компании"""
    company = {
        'name': generate_company_name(),
        'industry': random.choice([
            'Technology', 'Finance', 'Healthcare', 'Education', 'Retail',
            'Manufacturing', 'Consulting', 'Media', 'Transportation', 'Energy'
        ]),
        'founded_year': random.randint(1950, 2023),
        'country': random.choice(COUNTRIES),
        'city': random.choice(CITIES)
    }
    
    # Количество сотрудников
    if include_employees:
        company['employee_count'] = random.randint(10, 10000)
        company['size'] = get_company_size(company['employee_count'])
    
    # Выручка
    if include_revenue:
        company['revenue'] = random.randint(1000000, 1000000000)
        company['revenue_formatted'] = format_revenue(company['revenue'])
    
    # Контактная информация
    if include_contact:
        company['website'] = generate_website(company['name'])
        company['email'] = generate_company_email(company['name'])
        company['phone'] = generate_phone()
    
    return company

def generate_random_developer(experience_years, include_skills, include_projects):
    """Генерация случайного разработчика"""
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    
    developer = {
        'name': f'{first_name} {last_name}',
        'email': generate_email(first_name, last_name),
        'experience_years': get_experience_years(experience_years),
        'level': get_developer_level(experience_years)
    }
    
    # Навыки
    if include_skills:
        developer['languages'] = random.sample(PROGRAMMING_LANGUAGES, random.randint(2, 5))
        developer['frameworks'] = random.sample(FRAMEWORKS, random.randint(1, 3))
        developer['skills'] = random.sample([
            'Problem Solving', 'Team Work', 'Communication', 'Leadership',
            'Project Management', 'Code Review', 'Testing', 'Documentation'
        ], random.randint(3, 6))
    
    # Проекты
    if include_projects:
        developer['projects_count'] = random.randint(5, 50)
        developer['github_repos'] = random.randint(10, 100)
        developer['commits_last_year'] = random.randint(100, 2000)
    
    return developer

def generate_random_project(project_type, include_team, include_technologies):
    """Генерация случайного проекта"""
    project = {
        'name': generate_project_name(),
        'description': generate_project_description(),
        'type': project_type if project_type != 'random' else random.choice(['web', 'mobile', 'desktop', 'api']),
        'status': random.choice(['planning', 'in_progress', 'completed', 'on_hold']),
        'start_date': generate_random_date(),
        'duration_months': random.randint(1, 24)
    }
    
    # Команда
    if include_team:
        project['team_size'] = random.randint(2, 20)
        project['roles'] = random.sample(JOB_TITLES, random.randint(2, 5))
    
    # Технологии
    if include_technologies:
        project['languages'] = random.sample(PROGRAMMING_LANGUAGES, random.randint(1, 3))
        project['frameworks'] = random.sample(FRAMEWORKS, random.randint(1, 2))
        project['tools'] = random.sample([
            'Git', 'Docker', 'Kubernetes', 'Jenkins', 'AWS', 'Azure', 'GCP',
            'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch'
        ], random.randint(2, 4))
    
    return project

def generate_custom_data_item(template):
    """Генерация кастомного элемента данных"""
    item = {}
    
    for field, field_type in template.items():
        if field_type == 'name':
            item[field] = f'{names.get_first_name()} {names.get_last_name()}'
        elif field_type == 'email':
            item[field] = generate_email()
        elif field_type == 'phone':
            item[field] = generate_phone()
        elif field_type == 'company':
            item[field] = generate_company_name()
        elif field_type == 'job_title':
            item[field] = random.choice(JOB_TITLES)
        elif field_type == 'country':
            item[field] = random.choice(COUNTRIES)
        elif field_type == 'city':
            item[field] = random.choice(CITIES)
        elif field_type == 'age':
            item[field] = random.randint(18, 80)
        elif field_type == 'salary':
            item[field] = random.randint(30000, 200000)
        elif field_type == 'uuid':
            item[field] = str(uuid.uuid4())
        elif field_type == 'date':
            item[field] = generate_random_date()
        elif field_type == 'text':
            item[field] = generate_random_text()
        elif field_type == 'number':
            item[field] = random.randint(1, 1000)
        else:
            item[field] = f'Unknown type: {field_type}'
    
    return item

def generate_email(first_name=None, last_name=None):
    """Генерация email адреса"""
    if first_name and last_name:
        local_part = f'{first_name.lower()}.{last_name.lower()}'
    else:
        local_part = f'{names.get_first_name().lower()}{random.randint(1, 999)}'
    
    domain = random.choice([
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'example.com', 'test.com', 'demo.com'
    ])
    
    return f'{local_part}@{domain}'

def generate_phone():
    """Генерация номера телефона"""
    return f'+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}'

def generate_address():
    """Генерация адреса"""
    street_types = ['ул.', 'пр.', 'пер.', 'наб.', 'ш.']
    street_names = ['Ленина', 'Пушкина', 'Гагарина', 'Мира', 'Советская', 'Центральная']
    
    street_type = random.choice(street_types)
    street_name = random.choice(street_names)
    house_number = random.randint(1, 200)
    apartment = random.randint(1, 100)
    
    return f'{street_type} {street_name}, д. {house_number}, кв. {apartment}'

def generate_company_name():
    """Генерация названия компании"""
    prefixes = ['Tech', 'Digital', 'Smart', 'Global', 'Advanced', 'Innovative']
    suffixes = ['Solutions', 'Systems', 'Technologies', 'Labs', 'Works', 'Group']
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    return f'{prefix} {suffix}'

def generate_website(company_name):
    """Генерация веб-сайта"""
    domain = company_name.lower().replace(' ', '').replace('.', '')
    return f'https://www.{domain}.com'

def generate_company_email(company_name):
    """Генерация корпоративного email"""
    domain = company_name.lower().replace(' ', '').replace('.', '')
    return f'info@{domain}.com'

def generate_project_name():
    """Генерация названия проекта"""
    prefixes = ['Smart', 'Easy', 'Quick', 'Pro', 'Ultra', 'Super']
    suffixes = ['Manager', 'Tracker', 'Analyzer', 'Optimizer', 'Generator', 'Builder']
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    return f'{prefix} {suffix}'

def generate_project_description():
    """Генерация описания проекта"""
    descriptions = [
        'A modern web application for managing tasks and projects',
        'Mobile app for tracking fitness and health metrics',
        'Desktop application for data analysis and visualization',
        'RESTful API for e-commerce platform',
        'Machine learning model for predictive analytics',
        'Cloud-based solution for team collaboration'
    ]
    
    return random.choice(descriptions)

def generate_random_date():
    """Генерация случайной даты"""
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

def generate_random_text():
    """Генерация случайного текста"""
    words = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit']
    return ' '.join(random.choices(words, k=random.randint(5, 15)))

def get_company_size(employee_count):
    """Определение размера компании"""
    if employee_count < 50:
        return 'Small'
    elif employee_count < 200:
        return 'Medium'
    elif employee_count < 1000:
        return 'Large'
    else:
        return 'Enterprise'

def format_revenue(revenue):
    """Форматирование выручки"""
    if revenue >= 1000000000:
        return f'${revenue / 1000000000:.1f}B'
    elif revenue >= 1000000:
        return f'${revenue / 1000000:.1f}M'
    else:
        return f'${revenue:,}'

def get_experience_years(experience_years):
    """Получение лет опыта"""
    if experience_years == '0-5':
        return random.randint(0, 5)
    elif experience_years == '5-10':
        return random.randint(5, 10)
    elif experience_years == '10+':
        return random.randint(10, 20)
    else:
        return random.randint(0, 20)

def get_developer_level(experience_years):
    """Определение уровня разработчика"""
    years = get_experience_years(experience_years)
    
    if years < 2:
        return 'Junior'
    elif years < 5:
        return 'Middle'
    elif years < 10:
        return 'Senior'
    else:
        return 'Lead'

def generate_data_for_export(data_type, count):
    """Генерация данных для экспорта"""
    data = []
    
    for _ in range(count):
        if data_type == 'person':
            item = generate_random_person('random', 'random', True, True, True)
        elif data_type == 'company':
            item = generate_random_company(True, True, True)
        elif data_type == 'developer':
            item = generate_random_developer('random', True, True)
        elif data_type == 'project':
            item = generate_random_project('random', True, True)
        else:
            item = generate_random_person('random', 'random', True, True, True)
        
        data.append(item)
    
    return data

def export_to_csv(data, include_headers):
    """Экспорт в CSV формат"""
    if not data:
        return ''
    
    # Получение заголовков
    headers = list(data[0].keys())
    
    csv_lines = []
    
    # Добавление заголовков
    if include_headers:
        csv_lines.append(','.join(headers))
    
    # Добавление данных
    for item in data:
        row = []
        for header in headers:
            value = str(item.get(header, ''))
            # Экранирование запятых и кавычек
            if ',' in value or '"' in value:
                value = f'"{value.replace('"', '""')}"'
            row.append(value)
        csv_lines.append(','.join(row))
    
    return '\n'.join(csv_lines)

def export_to_xml(data, data_type):
    """Экспорт в XML формат"""
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append(f'<{data_type}s>')
    
    for item in data:
        xml_lines.append(f'  <{data_type}>')
        for key, value in item.items():
            xml_lines.append(f'    <{key}>{value}</{key}>')
        xml_lines.append(f'  </{data_type}>')
    
    xml_lines.append(f'</{data_type}s>')
    
    return '\n'.join(xml_lines)

def get_random_data_generator_statistics(user_id):
    """Получение статистики использования генератора случайных данных"""
    # Здесь можно добавить статистику использования
    return {
        'data_generated': 0,
        'people_generated': 0,
        'companies_generated': 0,
        'developers_generated': 0,
        'projects_generated': 0,
        'most_used_type': 'person'
    }

def get_random_data_generator_tips():
    """Получение советов по использованию генератора случайных данных"""
    tips = [
        "Используйте генератор для создания тестовых данных",
        "Настройте параметры под ваши нужды",
        "Экспортируйте данные в нужном формате",
        "Используйте кастомные шаблоны для специфических случаев",
        "Генерируйте данные в пакетном режиме для больших объемов",
        "Проверяйте качество сгенерированных данных",
        "Используйте разные типы данных для разнообразия",
        "Сохраняйте шаблоны для повторного использования"
    ]
    
    return tips
