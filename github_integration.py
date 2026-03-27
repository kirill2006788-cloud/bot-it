from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, GitHubIntegration, User
import requests
import base64
from datetime import datetime
import json

github_bp = Blueprint('github', __name__)

# GitHub API endpoints
GITHUB_API_BASE = 'https://api.github.com'
GITHUB_CLIENT_ID = 'your_github_client_id'  # Получите на GitHub
GITHUB_CLIENT_SECRET = 'your_github_client_secret'  # Получите на GitHub

@github_bp.route('/api/github/auth', methods=['POST'])
@login_required
def github_auth():
    """Авторизация через GitHub"""
    try:
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({'error': 'Код авторизации не предоставлен'}), 400
        
        # Обмен кода на токен доступа
        token_response = requests.post('https://github.com/login/oauth/access_token', {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code
        }, headers={'Accept': 'application/json'})
        
        if token_response.status_code != 200:
            return jsonify({'error': 'Ошибка при получении токена доступа'}), 400
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'Не удалось получить токен доступа'}), 400
        
        # Получение информации о пользователе GitHub
        user_response = requests.get(f'{GITHUB_API_BASE}/user', 
                                   headers={'Authorization': f'token {access_token}'})
        
        if user_response.status_code != 200:
            return jsonify({'error': 'Ошибка при получении данных пользователя GitHub'}), 400
        
        github_user = user_response.json()
        
        # Сохранение или обновление интеграции
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id).first()
        
        if integration:
            integration.github_username = github_user['login']
            integration.access_token = access_token
            integration.last_sync = datetime.utcnow()
            integration.is_active = True
        else:
            integration = GitHubIntegration(
                user_id=current_user.id,
                github_username=github_user['login'],
                access_token=access_token,
                last_sync=datetime.utcnow(),
                is_active=True
            )
            db.session.add(integration)
        
        db.session.commit()
        
        # Синхронизация данных
        sync_github_data(current_user.id)
        
        return jsonify({
            'message': 'GitHub аккаунт успешно привязан',
            'github_username': github_user['login'],
            'github_data': github_user
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при авторизации GitHub'}), 500

@github_bp.route('/api/github/profile', methods=['GET'])
@login_required
def get_github_profile():
    """Получение профиля GitHub"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not integration:
            return jsonify({'error': 'GitHub аккаунт не привязан'}), 404
        
        # Получение актуальных данных
        github_data = get_github_user_data(integration.github_username)
        
        if not github_data:
            return jsonify({'error': 'Не удалось получить данные GitHub'}), 500
        
        return jsonify({
            'integration': integration.to_dict(),
            'github_profile': github_data
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении профиля GitHub'}), 500

@github_bp.route('/api/github/repositories', methods=['GET'])
@login_required
def get_github_repositories():
    """Получение репозиториев GitHub"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not integration:
            return jsonify({'error': 'GitHub аккаунт не привязан'}), 404
        
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 30)), 100)
        sort = request.args.get('sort', 'updated')  # created, updated, pushed, full_name
        direction = request.args.get('direction', 'desc')  # asc, desc
        
        # Получение репозиториев
        repos_response = requests.get(
            f'{GITHUB_API_BASE}/users/{integration.github_username}/repos',
            params={
                'page': page,
                'per_page': per_page,
                'sort': sort,
                'direction': direction
            }
        )
        
        if repos_response.status_code != 200:
            return jsonify({'error': 'Ошибка при получении репозиториев'}), 500
        
        repositories = repos_response.json()
        
        # Обработка данных репозиториев
        processed_repos = []
        for repo in repositories:
            processed_repos.append({
                'id': repo['id'],
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo['description'],
                'language': repo['language'],
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'watchers': repo['watchers_count'],
                'size': repo['size'],
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'pushed_at': repo['pushed_at'],
                'html_url': repo['html_url'],
                'clone_url': repo['clone_url'],
                'is_private': repo['private'],
                'is_fork': repo['fork']
            })
        
        return jsonify({
            'repositories': processed_repos,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(processed_repos)
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении репозиториев'}), 500

@github_bp.route('/api/github/repository/<path:repo_name>', methods=['GET'])
@login_required
def get_github_repository(repo_name):
    """Получение информации о конкретном репозитории"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not integration:
            return jsonify({'error': 'GitHub аккаунт не привязан'}), 404
        
        # Получение информации о репозитории
        repo_response = requests.get(f'{GITHUB_API_BASE}/repos/{integration.github_username}/{repo_name}')
        
        if repo_response.status_code != 200:
            return jsonify({'error': 'Репозиторий не найден'}), 404
        
        repo_data = repo_response.json()
        
        # Получение коммитов
        commits_response = requests.get(
            f'{GITHUB_API_BASE}/repos/{integration.github_username}/{repo_name}/commits',
            params={'per_page': 10}
        )
        
        commits = []
        if commits_response.status_code == 200:
            commits_data = commits_response.json()
            for commit in commits_data:
                commits.append({
                    'sha': commit['sha'],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'html_url': commit['html_url']
                })
        
        # Получение языков программирования
        languages_response = requests.get(
            f'{GITHUB_API_BASE}/repos/{integration.github_username}/{repo_name}/languages'
        )
        
        languages = {}
        if languages_response.status_code == 200:
            languages = languages_response.json()
        
        # Получение README
        readme_response = requests.get(
            f'{GITHUB_API_BASE}/repos/{integration.github_username}/{repo_name}/readme'
        )
        
        readme_content = None
        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            if readme_data.get('content'):
                readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
        
        return jsonify({
            'repository': {
                'id': repo_data['id'],
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data['description'],
                'language': repo_data['language'],
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'watchers': repo_data['watchers_count'],
                'size': repo_data['size'],
                'created_at': repo_data['created_at'],
                'updated_at': repo_data['updated_at'],
                'pushed_at': repo_data['pushed_at'],
                'html_url': repo_data['html_url'],
                'clone_url': repo_data['clone_url'],
                'is_private': repo_data['private'],
                'is_fork': repo_data['fork'],
                'default_branch': repo_data['default_branch'],
                'topics': repo_data.get('topics', [])
            },
            'commits': commits,
            'languages': languages,
            'readme': readme_content
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении репозитория'}), 500

@github_bp.route('/api/github/activity', methods=['GET'])
@login_required
def get_github_activity():
    """Получение активности GitHub"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not integration:
            return jsonify({'error': 'GitHub аккаунт не привязан'}), 404
        
        # Получение событий активности
        events_response = requests.get(
            f'{GITHUB_API_BASE}/users/{integration.github_username}/events/public',
            params={'per_page': 30}
        )
        
        if events_response.status_code != 200:
            return jsonify({'error': 'Ошибка при получении активности'}), 500
        
        events = events_response.json()
        
        # Обработка событий
        processed_events = []
        for event in events:
            processed_events.append({
                'id': event['id'],
                'type': event['type'],
                'actor': event['actor']['login'],
                'repo': event['repo']['name'],
                'created_at': event['created_at'],
                'payload': event.get('payload', {})
            })
        
        return jsonify({
            'activity': processed_events,
            'total': len(processed_events)
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении активности GitHub'}), 500

@github_bp.route('/api/github/sync', methods=['POST'])
@login_required
def sync_github_data():
    """Синхронизация данных GitHub"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not integration:
            return jsonify({'error': 'GitHub аккаунт не привязан'}), 404
        
        # Синхронизация данных
        sync_result = sync_github_data(current_user.id)
        
        return jsonify({
            'message': 'Данные GitHub синхронизированы',
            'sync_result': sync_result
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при синхронизации данных GitHub'}), 500

@github_bp.route('/api/github/disconnect', methods=['POST'])
@login_required
def disconnect_github():
    """Отключение GitHub интеграции"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id).first()
        
        if integration:
            integration.is_active = False
            integration.access_token = None
            db.session.commit()
        
        return jsonify({'message': 'GitHub аккаунт отключен'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при отключении GitHub'}), 500

@github_bp.route('/api/github/stats', methods=['GET'])
@login_required
def get_github_stats():
    """Получение статистики GitHub"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=current_user.id, is_active=True).first()
        
        if not integration:
            return jsonify({'error': 'GitHub аккаунт не привязан'}), 404
        
        # Получение статистики
        stats_response = requests.get(f'{GITHUB_API_BASE}/users/{integration.github_username}')
        
        if stats_response.status_code != 200:
            return jsonify({'error': 'Ошибка при получении статистики'}), 500
        
        stats_data = stats_response.json()
        
        # Получение репозиториев для дополнительной статистики
        repos_response = requests.get(f'{GITHUB_API_BASE}/users/{integration.github_username}/repos')
        
        repos_stats = {
            'total_repos': 0,
            'public_repos': 0,
            'private_repos': 0,
            'total_stars': 0,
            'total_forks': 0,
            'languages': {}
        }
        
        if repos_response.status_code == 200:
            repos = repos_response.json()
            repos_stats['total_repos'] = len(repos)
            
            for repo in repos:
                if repo['private']:
                    repos_stats['private_repos'] += 1
                else:
                    repos_stats['public_repos'] += 1
                
                repos_stats['total_stars'] += repo['stargazers_count']
                repos_stats['total_forks'] += repo['forks_count']
                
                if repo['language']:
                    language = repo['language']
                    repos_stats['languages'][language] = repos_stats['languages'].get(language, 0) + 1
        
        return jsonify({
            'user_stats': {
                'followers': stats_data['followers'],
                'following': stats_data['following'],
                'public_repos': stats_data['public_repos'],
                'public_gists': stats_data['public_gists'],
                'created_at': stats_data['created_at']
            },
            'repos_stats': repos_stats,
            'last_sync': integration.last_sync.isoformat() if integration.last_sync else None
        })
        
    except Exception as e:
        return jsonify({'error': 'Ошибка при получении статистики GitHub'}), 500

def get_github_user_data(username):
    """Получение данных пользователя GitHub"""
    try:
        response = requests.get(f'{GITHUB_API_BASE}/users/{username}')
        
        if response.status_code == 200:
            return response.json()
        return None
        
    except Exception as e:
        print(f"Ошибка при получении данных пользователя GitHub: {e}")
        return None

def sync_github_data(user_id):
    """Синхронизация данных GitHub"""
    try:
        integration = GitHubIntegration.query.filter_by(user_id=user_id, is_active=True).first()
        
        if not integration:
            return {'error': 'Интеграция не найдена'}
        
        # Получение актуальных данных пользователя
        user_data = get_github_user_data(integration.github_username)
        
        if not user_data:
            return {'error': 'Не удалось получить данные пользователя'}
        
        # Обновление данных интеграции
        integration.followers_count = user_data['followers']
        integration.following_count = user_data['following']
        integration.repositories_count = user_data['public_repos']
        integration.last_sync = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'success': True,
            'followers': user_data['followers'],
            'following': user_data['following'],
            'repositories': user_data['public_repos'],
            'last_sync': integration.last_sync.isoformat()
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при синхронизации данных GitHub: {e}")
        return {'error': 'Ошибка при синхронизации'}

def get_github_auth_url():
    """Получение URL для авторизации GitHub"""
    return f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=user:email,repo"

def check_github_integration(user_id):
    """Проверка наличия GitHub интеграции"""
    integration = GitHubIntegration.query.filter_by(user_id=user_id, is_active=True).first()
    return integration is not None

def get_user_github_data(user_id):
    """Получение данных GitHub пользователя"""
    integration = GitHubIntegration.query.filter_by(user_id=user_id, is_active=True).first()
    
    if not integration:
        return None
    
    return {
        'username': integration.github_username,
        'followers': integration.followers_count,
        'following': integration.following_count,
        'repositories': integration.repositories_count,
        'last_sync': integration.last_sync.isoformat() if integration.last_sync else None
    }
