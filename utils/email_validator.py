from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import re
import dns.resolver
import socket
from datetime import datetime

email_validator_bp = Blueprint('email_validator', __name__)

# Регулярное выражение для проверки email
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Популярные домены
POPULAR_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com',
    'aol.com', 'mail.ru', 'yandex.ru', 'rambler.ru', 'bk.ru',
    'live.com', 'msn.com', 'comcast.net', 'verizon.net', 'att.net'
]

# Временные домены
TEMPORARY_DOMAINS = [
    '10minutemail.com', 'tempmail.org', 'guerrillamail.com', 'mailinator.com',
    'throwaway.email', 'temp-mail.org', 'sharklasers.com', 'grr.la'
]

@email_validator_bp.route('/api/email/validate', methods=['POST'])
@login_required
def validate_email():
    """Валидация email адреса"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        check_dns = data.get('check_dns', False)
        check_smtp = data.get('check_smtp', False)
        
        if not email:
            return jsonify({'error': 'Email адрес не указан'}), 400
        
        # Валидация email
        validation_result = validate_email_address(email, check_dns, check_smtp)
        
        return jsonify({
            'email': email,
            'is_valid': validation_result['is_valid'],
            'validation_details': validation_result['details'],
            'suggestions': validation_result.get('suggestions', []),
            'validated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при валидации email'}), 500

@email_validator_bp.route('/api/email/batch-validate', methods=['POST'])
@login_required
def batch_validate_emails():
    """Пакетная валидация email адресов"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        check_dns = data.get('check_dns', False)
        check_smtp = data.get('check_smtp', False)
        
        if not emails or len(emails) > 100:
            return jsonify({'error': 'Укажите от 1 до 100 email адресов'}), 400
        
        results = []
        
        for email in emails:
            validation_result = validate_email_address(email, check_dns, check_smtp)
            results.append({
                'email': email,
                'is_valid': validation_result['is_valid'],
                'details': validation_result['details']
            })
        
        # Статистика
        valid_count = sum(1 for result in results if result['is_valid'])
        invalid_count = len(results) - valid_count
        
        return jsonify({
            'results': results,
            'total': len(results),
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'valid_percentage': round((valid_count / len(results)) * 100, 2),
            'validated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при пакетной валидации email'}), 500

@email_validator_bp.route('/api/email/check-domain', methods=['POST'])
@login_required
def check_domain():
    """Проверка домена email"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({'error': 'Домен не указан'}), 400
        
        # Проверка домена
        domain_result = check_domain_validity(domain)
        
        return jsonify({
            'domain': domain,
            'is_valid': domain_result['is_valid'],
            'details': domain_result['details'],
            'mx_records': domain_result.get('mx_records', []),
            'checked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при проверке домена'}), 500

@email_validator_bp.route('/api/email/suggest', methods=['POST'])
@login_required
def suggest_email():
    """Предложение исправлений для email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email адрес не указан'}), 400
        
        # Предложения исправлений
        suggestions = suggest_email_corrections(email)
        
        return jsonify({
            'email': email,
            'suggestions': suggestions,
            'suggested_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при предложении исправлений'}), 500

@email_validator_bp.route('/api/email/analyze', methods=['POST'])
@login_required
def analyze_email():
    """Анализ email адреса"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email адрес не указан'}), 400
        
        # Анализ email
        analysis = analyze_email_address(email)
        
        return jsonify({
            'email': email,
            'analysis': analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при анализе email'}), 500

@email_validator_bp.route('/api/email/domains', methods=['GET'])
def get_domain_info():
    """Получение информации о доменах"""
    try:
        domain_info = {
            'popular_domains': POPULAR_DOMAINS,
            'temporary_domains': TEMPORARY_DOMAINS,
            'total_popular': len(POPULAR_DOMAINS),
            'total_temporary': len(TEMPORARY_DOMAINS)
        }
        
        return jsonify(domain_info)
        
    except Exception as e:
        return jsonify({'error': 'Oшибка при получении информации о доменах'}), 500

def validate_email_address(email, check_dns=False, check_smtp=False):
    """Валидация email адреса"""
    details = {
        'format_valid': False,
        'domain_valid': False,
        'dns_valid': False,
        'smtp_valid': False,
        'is_temporary': False,
        'is_popular': False,
        'length_valid': False,
        'local_part_valid': False
    }
    
    suggestions = []
    
    # Проверка формата
    if EMAIL_REGEX.match(email):
        details['format_valid'] = True
    else:
        suggestions.append('Неверный формат email адреса')
        return {
            'is_valid': False,
            'details': details,
            'suggestions': suggestions
        }
    
    # Разделение на локальную часть и домен
    try:
        local_part, domain = email.split('@')
    except ValueError:
        suggestions.append('Email должен содержать символ @')
        return {
            'is_valid': False,
            'details': details,
            'suggestions': suggestions
        }
    
    # Проверка длины
    if len(email) <= 254:
        details['length_valid'] = True
    else:
        suggestions.append('Email слишком длинный (максимум 254 символа)')
    
    # Проверка локальной части
    if len(local_part) <= 64 and local_part and not local_part.startswith('.') and not local_part.endswith('.'):
        details['local_part_valid'] = True
    else:
        suggestions.append('Локальная часть email неверна')
    
    # Проверка домена
    if len(domain) <= 253 and domain and '.' in domain:
        details['domain_valid'] = True
    else:
        suggestions.append('Домен email неверен')
    
    # Проверка на временный домен
    if domain.lower() in TEMPORARY_DOMAINS:
        details['is_temporary'] = True
        suggestions.append('Этот email использует временный домен')
    
    # Проверка на популярный домен
    if domain.lower() in POPULAR_DOMAINS:
        details['is_popular'] = True
    
    # Проверка DNS
    if check_dns:
        dns_result = check_domain_validity(domain)
        details['dns_valid'] = dns_result['is_valid']
        if not dns_result['is_valid']:
            suggestions.append('Домен не существует или недоступен')
    
    # Проверка SMTP
    if check_smtp:
        smtp_result = check_smtp_validity(email)
        details['smtp_valid'] = smtp_result['is_valid']
        if not smtp_result['is_valid']:
            suggestions.append('SMTP сервер недоступен')
    
    # Общая валидность
    is_valid = (
        details['format_valid'] and
        details['domain_valid'] and
        details['length_valid'] and
        details['local_part_valid'] and
        (not check_dns or details['dns_valid']) and
        (not check_smtp or details['smtp_valid'])
    )
    
    return {
        'is_valid': is_valid,
        'details': details,
        'suggestions': suggestions
    }

def check_domain_validity(domain):
    """Проверка валидности домена"""
    try:
        # Проверка MX записей
        mx_records = []
        try:
            mx_records = [str(record) for record in dns.resolver.resolve(domain, 'MX')]
        except:
            pass
        
        # Проверка A записей
        a_records = []
        try:
            a_records = [str(record) for record in dns.resolver.resolve(domain, 'A')]
        except:
            pass
        
        # Проверка AAAA записей
        aaaa_records = []
        try:
            aaaa_records = [str(record) for record in dns.resolver.resolve(domain, 'AAAA')]
        except:
            pass
        
        is_valid = len(mx_records) > 0 or len(a_records) > 0 or len(aaaa_records) > 0
        
        return {
            'is_valid': is_valid,
            'mx_records': mx_records,
            'a_records': a_records,
            'aaaa_records': aaaa_records,
            'details': {
                'has_mx': len(mx_records) > 0,
                'has_a': len(a_records) > 0,
                'has_aaaa': len(aaaa_records) > 0
            }
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'mx_records': [],
            'a_records': [],
            'aaaa_records': [],
            'details': {
                'has_mx': False,
                'has_a': False,
                'has_aaaa': False,
                'error': str(e)
            }
        }

def check_smtp_validity(email):
    """Проверка SMTP валидности"""
    try:
        local_part, domain = email.split('@')
        
        # Получение MX записей
        mx_records = dns.resolver.resolve(domain, 'MX')
        
        for mx_record in mx_records:
            mx_host = str(mx_record).split()[-1]
            
            # Попытка подключения к SMTP серверу
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((mx_host, 25))
                sock.close()
                
                if result == 0:
                    return {
                        'is_valid': True,
                        'mx_host': mx_host,
                        'details': 'SMTP сервер доступен'
                    }
            except:
                continue
        
        return {
            'is_valid': False,
            'mx_host': None,
            'details': 'SMTP сервер недоступен'
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'mx_host': None,
            'details': f'Ошибка проверки SMTP: {str(e)}'
        }

def suggest_email_corrections(email):
    """Предложение исправлений для email"""
    suggestions = []
    
    # Проверка на типичные ошибки
    if '@' not in email:
        suggestions.append('Добавьте символ @')
        return suggestions
    
    local_part, domain = email.split('@')
    
    # Проверка на двойные точки
    if '..' in local_part:
        suggestions.append('Удалите двойные точки в локальной части')
    
    # Проверка на пробелы
    if ' ' in email:
        suggestions.append('Удалите пробелы из email')
    
    # Проверка на заглавные буквы
    if email != email.lower():
        suggestions.append('Используйте строчные буквы')
    
    # Проверка на типичные опечатки в доменах
    domain_corrections = {
        'gmial.com': 'gmail.com',
        'gmai.com': 'gmail.com',
        'gmail.co': 'gmail.com',
        'yahooo.com': 'yahoo.com',
        'hotmial.com': 'hotmail.com',
        'outlok.com': 'outlook.com'
    }
    
    if domain.lower() in domain_corrections:
        suggestions.append(f'Возможно, вы имели в виду {domain_corrections[domain.lower()]}')
    
    # Проверка на отсутствие точки в домене
    if '.' not in domain:
        suggestions.append('Домен должен содержать точку')
    
    # Проверка на популярные домены
    if domain.lower() not in POPULAR_DOMAINS:
        suggestions.append('Проверьте правильность написания домена')
    
    return suggestions

def analyze_email_address(email):
    """Анализ email адреса"""
    try:
        local_part, domain = email.split('@')
        
        analysis = {
            'email': email,
            'local_part': local_part,
            'domain': domain,
            'local_part_length': len(local_part),
            'domain_length': len(domain),
            'total_length': len(email),
            'is_popular_domain': domain.lower() in POPULAR_DOMAINS,
            'is_temporary_domain': domain.lower() in TEMPORARY_DOMAINS,
            'has_numbers': any(c.isdigit() for c in local_part),
            'has_special_chars': any(c in '._%+-' for c in local_part),
            'has_uppercase': any(c.isupper() for c in email),
            'has_lowercase': any(c.islower() for c in email),
            'domain_tld': domain.split('.')[-1] if '.' in domain else '',
            'subdomain_count': len(domain.split('.')) - 1 if '.' in domain else 0
        }
        
        # Анализ локальной части
        analysis['local_part_analysis'] = {
            'starts_with_dot': local_part.startswith('.'),
            'ends_with_dot': local_part.endswith('.'),
            'has_consecutive_dots': '..' in local_part,
            'has_spaces': ' ' in local_part,
            'char_count': len(local_part),
            'digit_count': sum(1 for c in local_part if c.isdigit()),
            'special_char_count': sum(1 for c in local_part if c in '._%+-')
        }
        
        # Анализ домена
        analysis['domain_analysis'] = {
            'has_hyphen': '-' in domain,
            'has_underscore': '_' in domain,
            'has_numbers': any(c.isdigit() for c in domain),
            'tld_length': len(domain.split('.')[-1]) if '.' in domain else 0,
            'is_ip_address': is_ip_address(domain)
        }
        
        return analysis
        
    except Exception as e:
        return {
            'email': email,
            'error': f'Ошибка анализа: {str(e)}'
        }

def is_ip_address(domain):
    """Проверка, является ли домен IP адресом"""
    try:
        # Проверка IPv4
        parts = domain.split('.')
        if len(parts) == 4:
            for part in parts:
                if not part.isdigit() or not (0 <= int(part) <= 255):
                    return False
            return True
        
        # Проверка IPv6
        if ':' in domain:
            return True
        
        return False
        
    except:
        return False

def get_email_validator_statistics(user_id):
    """Получение статистики использования валидатора email"""
    # Здесь можно добавить статистику использования
    return {
        'emails_validated': 0,
        'valid_emails': 0,
        'invalid_emails': 0,
        'most_common_domain': 'gmail.com',
        'temporary_emails_found': 0
    }

def get_email_validator_tips():
    """Получение советов по валидации email"""
    tips = [
        "Всегда проверяйте формат email перед отправкой",
        "Используйте DNS проверку для критических приложений",
        "Остерегайтесь временных email адресов",
        "Проверяйте популярные домены на опечатки",
        "Email не должен содержать пробелы",
        "Локальная часть не должна начинаться или заканчиваться точкой",
        "Домен должен содержать точку и TLD",
        "Используйте пакетную валидацию для больших списков"
    ]
    
    return tips
