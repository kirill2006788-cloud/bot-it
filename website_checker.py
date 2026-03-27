from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import requests
import time
from urllib.parse import urlparse
import re
from datetime import datetime
import ssl
import socket

website_bp = Blueprint('website', __name__)

@website_bp.route('/api/website/check', methods=['POST'])
@login_required
def check_website():
    """Проверка сайта"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL не указан'}), 400
        
        # Добавление протокола если отсутствует
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Проверка доступности сайта
        availability = check_availability(url)
        
        # Проверка скорости загрузки
        speed = check_loading_speed(url)
        
        # Проверка SSL сертификата
        ssl_info = check_ssl_certificate(url)
        
        # Проверка SEO
        seo_info = check_seo(url)
        
        # Проверка безопасности
        security_info = check_security(url)
        
        # Проверка мобильной версии
        mobile_info = check_mobile_friendly(url)
        
        # Общая оценка
        overall_score = calculate_overall_score(availability, speed, seo_info, security_info)
        
        return jsonify({
            'url': url,
            'availability': availability,
            'speed': speed,
            'ssl': ssl_info,
            'seo': seo_info,
            'security': security_info,
            'mobile': mobile_info,
            'overall_score': overall_score,
            'checked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при проверке сайта'}), 500

@website_bp.route('/api/website/batch-check', methods=['POST'])
@login_required
def batch_check_websites():
    """Пакетная проверка сайтов"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls or len(urls) > 10:
            return jsonify({'error': 'Укажите от 1 до 10 URL'}), 400
        
        results = []
        
        for url in urls:
            try:
                # Базовая проверка доступности
                availability = check_availability(url)
                speed = check_loading_speed(url)
                
                results.append({
                    'url': url,
                    'available': availability['available'],
                    'response_time': speed['response_time'],
                    'status_code': availability['status_code']
                })
                
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'available': False
                })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'checked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при пакетной проверке'}), 500

@website_bp.route('/api/website/seo-analysis', methods=['POST'])
@login_required
def seo_analysis():
    """SEO анализ сайта"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL не указан'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Получение HTML страницы
        try:
            response = requests.get(url, timeout=10)
            html_content = response.text
        except:
            return jsonify({'error': 'Не удалось получить содержимое сайта'}), 400
        
        # Анализ SEO элементов
        seo_analysis = analyze_seo_elements(html_content, url)
        
        return jsonify({
            'url': url,
            'seo_analysis': seo_analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при SEO анализе'}), 500

@website_bp.route('/api/website/performance', methods=['POST'])
@login_required
def performance_check():
    """Проверка производительности сайта"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL не указан'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Проверка производительности
        performance_data = check_performance(url)
        
        return jsonify({
            'url': url,
            'performance': performance_data,
            'checked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при проверке производительности'}), 500

def check_availability(url):
    """Проверка доступности сайта"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10, allow_redirects=True)
        response_time = time.time() - start_time
        
        return {
            'available': True,
            'status_code': response.status_code,
            'response_time': round(response_time * 1000, 2),  # в миллисекундах
            'final_url': response.url,
            'redirects': len(response.history)
        }
        
    except requests.exceptions.Timeout:
        return {
            'available': False,
            'error': 'Timeout',
            'response_time': None
        }
    except requests.exceptions.ConnectionError:
        return {
            'available': False,
            'error': 'Connection Error',
            'response_time': None
        }
    except Exception as e:
        return {
            'available': False,
            'error': str(e),
            'response_time': None
        }

def check_loading_speed(url):
    """Проверка скорости загрузки"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        load_time = time.time() - start_time
        
        # Анализ размера контента
        content_size = len(response.content)
        
        # Оценка скорости
        if load_time < 1:
            speed_rating = 'Отлично'
        elif load_time < 3:
            speed_rating = 'Хорошо'
        elif load_time < 5:
            speed_rating = 'Удовлетворительно'
        else:
            speed_rating = 'Медленно'
        
        return {
            'load_time': round(load_time, 2),
            'content_size': content_size,
            'speed_rating': speed_rating,
            'recommendations': get_speed_recommendations(load_time, content_size)
        }
        
    except Exception as e:
        return {
            'load_time': None,
            'error': str(e)
        }

def check_ssl_certificate(url):
    """Проверка SSL сертификата"""
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        if parsed_url.scheme != 'https':
            return {
                'has_ssl': False,
                'error': 'Сайт не использует HTTPS'
            }
        
        # Проверка SSL сертификата
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Проверка срока действия
                import datetime
                not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (not_after - datetime.datetime.now()).days
                
                return {
                    'has_ssl': True,
                    'issuer': cert.get('issuer', {}),
                    'subject': cert.get('subject', {}),
                    'not_after': cert['notAfter'],
                    'days_until_expiry': days_until_expiry,
                    'is_valid': days_until_expiry > 0,
                    'ssl_rating': 'Отлично' if days_until_expiry > 30 else 'Требует внимания'
                }
        
    except Exception as e:
        return {
            'has_ssl': False,
            'error': str(e)
        }

def check_seo(url):
    """Проверка SEO"""
    try:
        response = requests.get(url, timeout=10)
        html_content = response.text
        
        seo_data = analyze_seo_elements(html_content, url)
        
        return seo_data
        
    except Exception as e:
        return {
            'error': str(e)
        }

def analyze_seo_elements(html_content, url):
    """Анализ SEO элементов"""
    seo_data = {
        'title': None,
        'description': None,
        'keywords': None,
        'h1_tags': [],
        'h2_tags': [],
        'images': [],
        'links': [],
        'score': 0
    }
    
    # Поиск title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        seo_data['title'] = title_match.group(1).strip()
    
    # Поиск meta description
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if desc_match:
        seo_data['description'] = desc_match.group(1).strip()
    
    # Поиск meta keywords
    keywords_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if keywords_match:
        seo_data['keywords'] = keywords_match.group(1).strip()
    
    # Поиск заголовков H1
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
    seo_data['h1_tags'] = [h1.strip() for h1 in h1_matches]
    
    # Поиск заголовков H2
    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', html_content, re.IGNORECASE | re.DOTALL)
    seo_data['h2_tags'] = [h2.strip() for h2 in h2_matches]
    
    # Поиск изображений
    img_matches = re.findall(r'<img[^>]*src=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    seo_data['images'] = img_matches[:10]  # Первые 10 изображений
    
    # Поиск ссылок
    link_matches = re.findall(r'<a[^>]*href=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    seo_data['links'] = link_matches[:20]  # Первые 20 ссылок
    
    # Расчет SEO оценки
    score = 0
    if seo_data['title']:
        score += 20
    if seo_data['description']:
        score += 20
    if seo_data['keywords']:
        score += 10
    if seo_data['h1_tags']:
        score += 15
    if seo_data['h2_tags']:
        score += 10
    if seo_data['images']:
        score += 10
    if seo_data['links']:
        score += 15
    
    seo_data['score'] = min(score, 100)
    
    return seo_data

def check_security(url):
    """Проверка безопасности"""
    security_data = {
        'https': url.startswith('https://'),
        'mixed_content': False,
        'security_headers': {},
        'rating': 'Неизвестно'
    }
    
    try:
        response = requests.get(url, timeout=10)
        
        # Проверка HTTPS
        security_data['https'] = url.startswith('https://')
        
        # Проверка заголовков безопасности
        security_headers = [
            'Strict-Transport-Security',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Content-Security-Policy'
        ]
        
        for header in security_headers:
            if header in response.headers:
                security_data['security_headers'][header] = response.headers[header]
        
        # Оценка безопасности
        security_score = 0
        if security_data['https']:
            security_score += 40
        if 'Strict-Transport-Security' in security_data['security_headers']:
            security_score += 20
        if 'X-Content-Type-Options' in security_data['security_headers']:
            security_score += 15
        if 'X-Frame-Options' in security_data['security_headers']:
            security_score += 15
        if 'X-XSS-Protection' in security_data['security_headers']:
            security_score += 10
        
        if security_score >= 80:
            security_data['rating'] = 'Отлично'
        elif security_score >= 60:
            security_data['rating'] = 'Хорошо'
        elif security_score >= 40:
            security_data['rating'] = 'Удовлетворительно'
        else:
            security_data['rating'] = 'Требует улучшения'
        
        security_data['score'] = security_score
        
    except Exception as e:
        security_data['error'] = str(e)
    
    return security_data

def check_mobile_friendly(url):
    """Проверка мобильной версии"""
    mobile_data = {
        'viewport_meta': False,
        'responsive_design': False,
        'mobile_rating': 'Неизвестно'
    }
    
    try:
        response = requests.get(url, timeout=10)
        html_content = response.text
        
        # Проверка viewport meta тега
        viewport_match = re.search(r'<meta[^>]*name=["\']viewport["\']', html_content, re.IGNORECASE)
        mobile_data['viewport_meta'] = bool(viewport_match)
        
        # Проверка медиа-запросов
        media_queries = re.findall(r'@media[^}]*{[^}]*}', html_content, re.IGNORECASE)
        mobile_data['responsive_design'] = len(media_queries) > 0
        
        # Оценка мобильной версии
        score = 0
        if mobile_data['viewport_meta']:
            score += 50
        if mobile_data['responsive_design']:
            score += 50
        
        if score >= 80:
            mobile_data['mobile_rating'] = 'Отлично'
        elif score >= 50:
            mobile_data['mobile_rating'] = 'Хорошо'
        else:
            mobile_data['mobile_rating'] = 'Требует улучшения'
        
        mobile_data['score'] = score
        
    except Exception as e:
        mobile_data['error'] = str(e)
    
    return mobile_data

def check_performance(url):
    """Проверка производительности"""
    performance_data = {
        'response_time': None,
        'content_size': None,
        'compression': False,
        'caching': False,
        'rating': 'Неизвестно'
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        response_time = time.time() - start_time
        
        performance_data['response_time'] = round(response_time * 1000, 2)
        performance_data['content_size'] = len(response.content)
        
        # Проверка сжатия
        if 'gzip' in response.headers.get('Content-Encoding', ''):
            performance_data['compression'] = True
        
        # Проверка кэширования
        cache_headers = ['Cache-Control', 'Expires', 'ETag', 'Last-Modified']
        for header in cache_headers:
            if header in response.headers:
                performance_data['caching'] = True
                break
        
        # Оценка производительности
        score = 0
        if performance_data['response_time'] < 1000:  # Менее 1 секунды
            score += 40
        elif performance_data['response_time'] < 3000:  # Менее 3 секунд
            score += 20
        
        if performance_data['compression']:
            score += 30
        
        if performance_data['caching']:
            score += 30
        
        if score >= 80:
            performance_data['rating'] = 'Отлично'
        elif score >= 60:
            performance_data['rating'] = 'Хорошо'
        elif score >= 40:
            performance_data['rating'] = 'Удовлетворительно'
        else:
            performance_data['rating'] = 'Требует улучшения'
        
        performance_data['score'] = score
        
    except Exception as e:
        performance_data['error'] = str(e)
    
    return performance_data

def calculate_overall_score(availability, speed, seo_info, security_info):
    """Расчет общей оценки сайта"""
    score = 0
    
    # Доступность (30%)
    if availability['available']:
        score += 30
    
    # Скорость (25%)
    if speed.get('load_time'):
        if speed['load_time'] < 1:
            score += 25
        elif speed['load_time'] < 3:
            score += 20
        elif speed['load_time'] < 5:
            score += 15
        else:
            score += 10
    
    # SEO (25%)
    if seo_info.get('score'):
        score += seo_info['score'] * 0.25
    
    # Безопасность (20%)
    if security_info.get('score'):
        score += security_info['score'] * 0.20
    
    return min(round(score), 100)

def get_speed_recommendations(load_time, content_size):
    """Рекомендации по скорости"""
    recommendations = []
    
    if load_time > 3:
        recommendations.append('Оптимизируйте изображения')
        recommendations.append('Используйте CDN')
        recommendations.append('Включите сжатие gzip')
    
    if content_size > 1024 * 1024:  # Больше 1MB
        recommendations.append('Уменьшите размер страницы')
        recommendations.append('Оптимизируйте CSS и JavaScript')
    
    if not recommendations:
        recommendations.append('Скорость загрузки в норме')
    
    return recommendations
