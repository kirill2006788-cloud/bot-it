#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub интеграция для Telegram бота
"""

import requests
import json
from config import GITHUB_API_KEY

class GitHubBot:
    def __init__(self):
        self.api_key = GITHUB_API_KEY
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.api_key}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def search_repositories(self, query, limit=5):
        """
        Поиск репозиториев на GitHub
        """
        try:
            url = f"{self.base_url}/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for repo in data.get('items', []):
                    repos.append({
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo['description'] or 'Нет описания',
                        'language': repo['language'] or 'Не указан',
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'url': repo['html_url'],
                        'created_at': repo['created_at'][:10],  # Только дата
                        'updated_at': repo['updated_at'][:10]
                    })
                
                return {
                    'success': True,
                    'total_count': data['total_count'],
                    'repositories': repos
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка API: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка поиска: {str(e)}'
            }

    def get_user_info(self, username):
        """
        Получение информации о пользователе GitHub
        """
        try:
            url = f"{self.base_url}/users/{username}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                
                return {
                    'success': True,
                    'username': user_data['login'],
                    'name': user_data['name'] or user_data['login'],
                    'bio': user_data['bio'] or 'Нет описания',
                    'location': user_data['location'] or 'Не указано',
                    'company': user_data['company'] or 'Не указано',
                    'blog': user_data['blog'] or 'Нет сайта',
                    'followers': user_data['followers'],
                    'following': user_data['following'],
                    'public_repos': user_data['public_repos'],
                    'public_gists': user_data['public_gists'],
                    'created_at': user_data['created_at'][:10],
                    'avatar_url': user_data['avatar_url'],
                    'html_url': user_data['html_url']
                }
            else:
                return {
                    'success': False,
                    'error': f'Пользователь не найден: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения данных: {str(e)}'
            }

    def get_user_repositories(self, username, limit=10):
        """
        Получение репозиториев пользователя
        """
        try:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                'sort': 'updated',
                'per_page': limit
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                repos = response.json()
                processed_repos = []
                
                for repo in repos:
                    processed_repos.append({
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo['description'] or 'Нет описания',
                        'language': repo['language'] or 'Не указан',
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'url': repo['html_url'],
                        'updated_at': repo['updated_at'][:10],
                        'is_private': repo['private']
                    })
                
                return {
                    'success': True,
                    'repositories': processed_repos
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения репозиториев: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка: {str(e)}'
            }

    def create_gist(self, description, filename, content, public=True):
        """
        Создание Gist на GitHub
        """
        try:
            url = f"{self.base_url}/gists"
            
            data = {
                'description': description,
                'public': public,
                'files': {
                    filename: {
                        'content': content
                    }
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                gist_data = response.json()
                
                return {
                    'success': True,
                    'url': gist_data['html_url'],
                    'id': gist_data['id'],
                    'description': gist_data['description']
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка создания Gist: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка создания Gist: {str(e)}'
            }

    def get_trending_repositories(self, language=None, since='daily'):
        """
        Получение трендовых репозиториев (через поиск)
        """
        try:
            # Формируем поисковый запрос
            query = f"stars:>100"
            if language:
                query += f" language:{language}"
            
            # Добавляем фильтр по дате
            if since == 'daily':
                query += " created:>2024-01-01"  # Примерно за последний день
            elif since == 'weekly':
                query += " created:>2024-01-01"  # Примерно за последнюю неделю
            
            url = f"{self.base_url}/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for repo in data.get('items', []):
                    repos.append({
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo['description'] or 'Нет описания',
                        'language': repo['language'] or 'Не указан',
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'url': repo['html_url'],
                        'stars_today': repo['stargazers_count']  # Примерное значение
                    })
                
                return {
                    'success': True,
                    'repositories': repos,
                    'language': language or 'Все языки',
                    'since': since
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения трендов: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения трендов: {str(e)}'
            }

    def format_repository_info(self, repo):
        """
        Форматирование информации о репозитории для Telegram
        """
        # Безопасное получение автора
        author = "Неизвестно"
        if 'full_name' in repo and repo['full_name']:
            author = repo['full_name'].split('/')[0]
        elif 'owner' in repo and repo['owner']:
            if isinstance(repo['owner'], dict):
                author = repo['owner'].get('login', 'Неизвестно')
            else:
                author = str(repo['owner'])
        
        return f"""📁 **{repo.get('name', 'Без названия')}**
👤 **Автор:** {author}
📝 **Описание:** {repo.get('description', 'Нет описания')}
💻 **Язык:** {repo.get('language', 'Не указан')}
⭐ **Звезды:** {repo.get('stars', 0)}
🍴 **Форки:** {repo.get('forks', 0)}
📅 **Обновлен:** {repo.get('updated_at', 'Неизвестно')}
🔗 **Ссылка:** {repo.get('url', '#')}"""

    def format_user_info(self, user):
        """
        Форматирование информации о пользователе для Telegram
        """
        return f"""👤 **{user['name']}** (@{user['username']})
📝 **О себе:** {user['bio']}
📍 **Местоположение:** {user['location']}
🏢 **Компания:** {user['company']}
🌐 **Сайт:** {user['blog']}
👥 **Подписчики:** {user['followers']}
👤 **Подписки:** {user['following']}
📁 **Репозитории:** {user['public_repos']}
📄 **Gists:** {user['public_gists']}
📅 **Регистрация:** {user['created_at']}
🔗 **Профиль:** {user['html_url']}"""

    def format_search_results(self, results):
        """
        Форматирование результатов поиска для Telegram
        """
        if not results['success']:
            return f"❌ Ошибка поиска: {results['error']}"
        
        if results['total_count'] == 0:
            return "🔍 Репозитории не найдены"
        
        text = f"🔍 **Найдено репозиториев:** {results['total_count']}\n\n"
        
        for i, repo in enumerate(results['repositories'], 1):
            text += f"**{i}.** {self.format_repository_info(repo)}\n\n"
        
        return text

    def search_repositories_advanced(self, query, language=None, sort='stars', order='desc', limit=10):
        """
        Расширенный поиск репозиториев с фильтрами
        """
        try:
            # Формируем расширенный запрос
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            url = f"{self.base_url}/search/repositories"
            params = {
                'q': search_query,
                'sort': sort,  # stars, forks, updated, created
                'order': order,  # asc, desc
                'per_page': limit
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for repo in data.get('items', []):
                    repos.append({
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo['description'] or 'Нет описания',
                        'language': repo['language'] or 'Не указан',
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'watchers': repo['watchers_count'],
                        'url': repo['html_url'],
                        'created_at': repo['created_at'][:10],
                        'updated_at': repo['updated_at'][:10],
                        'size': repo['size'],
                        'open_issues': repo['open_issues_count'],
                        'license': repo.get('license', {}).get('name', 'Нет лицензии') if repo.get('license') else 'Нет лицензии',
                        'topics': repo.get('topics', [])
                    })
                
                return {
                    'success': True,
                    'total_count': data['total_count'],
                    'repositories': repos,
                    'query': query,
                    'language': language,
                    'sort': sort
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка API: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка поиска: {str(e)}'
            }

    def get_repository_details(self, owner, repo_name):
        """
        Получение детальной информации о репозитории
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo_name}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                
                # Получаем языки программирования
                languages_url = f"{self.base_url}/repos/{owner}/{repo_name}/languages"
                languages_response = requests.get(languages_url, headers=self.headers, timeout=10)
                languages = {}
                if languages_response.status_code == 200:
                    languages = languages_response.json()
                
                # Получаем последние коммиты
                commits_url = f"{self.base_url}/repos/{owner}/{repo_name}/commits"
                commits_response = requests.get(commits_url, headers=self.headers, timeout=10)
                commits = []
                if commits_response.status_code == 200:
                    commits_data = commits_response.json()[:5]  # Последние 5 коммитов
                    for commit in commits_data:
                        commits.append({
                            'sha': commit['sha'][:7],
                            'message': commit['commit']['message'][:100],
                            'author': commit['commit']['author']['name'],
                            'date': commit['commit']['author']['date'][:10],
                            'url': commit['html_url']
                        })
                
                # Получаем README
                readme_url = f"{self.base_url}/repos/{owner}/{repo_name}/readme"
                readme_response = requests.get(readme_url, headers=self.headers, timeout=10)
                readme_content = None
                if readme_response.status_code == 200:
                    readme_data = readme_response.json()
                    if readme_data.get('content'):
                        import base64
                        readme_content = base64.b64decode(readme_data['content']).decode('utf-8')[:500]
                
                return {
                    'success': True,
                    'repository': {
                        'name': repo_data['name'],
                        'full_name': repo_data['full_name'],
                        'description': repo_data['description'] or 'Нет описания',
                        'language': repo_data['language'] or 'Не указан',
                        'stars': repo_data['stargazers_count'],
                        'forks': repo_data['forks_count'],
                        'watchers': repo_data['watchers_count'],
                        'size': repo_data['size'],
                        'created_at': repo_data['created_at'][:10],
                        'updated_at': repo_data['updated_at'][:10],
                        'pushed_at': repo_data['pushed_at'][:10],
                        'url': repo_data['html_url'],
                        'clone_url': repo_data['clone_url'],
                        'ssh_url': repo_data['ssh_url'],
                        'is_private': repo_data['private'],
                        'is_fork': repo_data['fork'],
                        'open_issues': repo_data['open_issues_count'],
                        'license': repo_data.get('license', {}).get('name', 'Нет лицензии') if repo_data.get('license') else 'Нет лицензии',
                        'topics': repo_data.get('topics', []),
                        'default_branch': repo_data['default_branch'],
                        'homepage': repo_data.get('homepage'),
                        'archived': repo_data['archived'],
                        'disabled': repo_data['disabled']
                    },
                    'languages': languages,
                    'commits': commits,
                    'readme': readme_content
                }
            else:
                return {
                    'success': False,
                    'error': f'Репозиторий не найден: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения репозитория: {str(e)}'
            }

    def get_repository_issues(self, owner, repo_name, state='open', limit=10):
        """
        Получение Issues репозитория
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo_name}/issues"
            params = {
                'state': state,  # open, closed, all
                'per_page': limit,
                'sort': 'updated'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                issues = response.json()
                processed_issues = []
                
                for issue in issues:
                    # Пропускаем Pull Requests (они тоже возвращаются в issues)
                    if 'pull_request' in issue:
                        continue
                        
                    processed_issues.append({
                        'number': issue['number'],
                        'title': issue['title'],
                        'body': issue['body'][:200] if issue['body'] else 'Нет описания',
                        'state': issue['state'],
                        'user': issue['user']['login'],
                        'created_at': issue['created_at'][:10],
                        'updated_at': issue['updated_at'][:10],
                        'labels': [label['name'] for label in issue['labels']],
                        'url': issue['html_url'],
                        'comments': issue['comments']
                    })
                
                return {
                    'success': True,
                    'issues': processed_issues,
                    'total': len(processed_issues)
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения Issues: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения Issues: {str(e)}'
            }

    def get_repository_pull_requests(self, owner, repo_name, state='open', limit=10):
        """
        Получение Pull Requests репозитория
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo_name}/pulls"
            params = {
                'state': state,  # open, closed, all
                'per_page': limit,
                'sort': 'updated'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                prs = response.json()
                processed_prs = []
                
                for pr in prs:
                    processed_prs.append({
                        'number': pr['number'],
                        'title': pr['title'],
                        'body': pr['body'][:200] if pr['body'] else 'Нет описания',
                        'state': pr['state'],
                        'user': pr['user']['login'],
                        'created_at': pr['created_at'][:10],
                        'updated_at': pr['updated_at'][:10],
                        'labels': [label['name'] for label in pr['labels']],
                        'url': pr['html_url'],
                        'comments': pr['comments'],
                        'review_comments': pr['review_comments'],
                        'commits': pr['commits'],
                        'additions': pr['additions'],
                        'deletions': pr['deletions'],
                        'changed_files': pr['changed_files'],
                        'head': pr['head']['ref'],
                        'base': pr['base']['ref']
                    })
                
                return {
                    'success': True,
                    'pull_requests': processed_prs,
                    'total': len(processed_prs)
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения Pull Requests: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения Pull Requests: {str(e)}'
            }

    def get_repository_stats(self, owner, repo_name):
        """
        Получение статистики репозитория
        """
        try:
            # Получаем основную информацию
            repo_result = self.get_repository_details(owner, repo_name)
            if not repo_result['success']:
                return repo_result
            
            repo = repo_result['repository']
            
            # Получаем статистику коммитов за последние недели
            stats_url = f"{self.base_url}/repos/{owner}/{repo_name}/stats/participation"
            stats_response = requests.get(stats_url, headers=self.headers, timeout=10)
            
            participation = None
            if stats_response.status_code == 200:
                participation = stats_response.json()
            
            # Получаем статистику контрибьюторов
            contrib_url = f"{self.base_url}/repos/{owner}/{repo_name}/stats/contributors"
            contrib_response = requests.get(contrib_url, headers=self.headers, timeout=10)
            
            contributors = []
            if contrib_response.status_code == 200:
                contrib_data = contrib_response.json()
                for contrib in contrib_data[:10]:  # Топ 10 контрибьюторов
                    contributors.append({
                        'author': contrib['author']['login'],
                        'total_commits': contrib['total'],
                        'avatar_url': contrib['author']['avatar_url']
                    })
            
            return {
                'success': True,
                'repository': repo,
                'languages': repo_result['languages'],
                'participation': participation,
                'top_contributors': contributors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения статистики: {str(e)}'
            }

    def format_repository_details(self, details):
        """
        Форматирование детальной информации о репозитории
        """
        if not details['success']:
            return f"❌ Ошибка: {details['error']}"
        
        repo = details['repository']
        languages = details['languages']
        commits = details['commits']
        readme = details['readme']
        
        text = f"""📁 **{repo['name']}**
👤 **Автор:** {repo['full_name'].split('/')[0]}
📝 **Описание:** {repo['description']}
💻 **Язык:** {repo['language']}
⭐ **Звезды:** {repo['stars']}
🍴 **Форки:** {repo['forks']}
👀 **Наблюдатели:** {repo['watchers']}
📊 **Размер:** {repo['size']} KB
📅 **Создан:** {repo['created_at']}
🔄 **Обновлен:** {repo['updated_at']}
📄 **Лицензия:** {repo['license']}
🏷️ **Темы:** {', '.join(repo['topics'][:5]) if repo['topics'] else 'Нет'}
🔗 **Ссылка:** {repo['url']}"""
        
        if languages:
            total_bytes = sum(languages.values())
            lang_text = "\n💻 **Языки программирования:**\n"
            for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (bytes_count / total_bytes) * 100
                lang_text += f"• {lang}: {percentage:.1f}%\n"
            text += lang_text
        
        if commits:
            text += "\n📝 **Последние коммиты:**\n"
            for commit in commits[:3]:
                text += f"• `{commit['sha']}` {commit['message']}\n"
        
        if readme:
            text += f"\n📖 **README (фрагмент):**\n```\n{readme}...\n```"
        
        return text

    def format_issues(self, issues_result):
        """
        Форматирование Issues для Telegram
        """
        if not issues_result['success']:
            return f"❌ Ошибка: {issues_result['error']}"
        
        if not issues_result['issues']:
            return "📝 Issues не найдены"
        
        text = f"📝 **Issues ({issues_result['total']}):**\n\n"
        
        for issue in issues_result['issues']:
            labels_text = f"🏷️ {', '.join(issue['labels'][:3])}" if issue['labels'] else ""
            text += f"""**#{issue['number']}** {issue['title']}
👤 {issue['user']} | 📅 {issue['updated_at']} | 💬 {issue['comments']}
{labels_text}
🔗 {issue['url']}

"""
        
        return text

    def format_pull_requests(self, prs_result):
        """
        Форматирование Pull Requests для Telegram
        """
        if not prs_result['success']:
            return f"❌ Ошибка: {prs_result['error']}"
        
        if not prs_result['pull_requests']:
            return "🔄 Pull Requests не найдены"
        
        text = f"🔄 **Pull Requests ({prs_result['total']}):**\n\n"
        
        for pr in prs_result['pull_requests']:
            labels_text = f"🏷️ {', '.join(pr['labels'][:3])}" if pr['labels'] else ""
            text += f"""**#{pr['number']}** {pr['title']}
👤 {pr['user']} | 📅 {pr['updated_at']} | 💬 {pr['comments']}
📊 +{pr['additions']}/-{pr['deletions']} | 📁 {pr['changed_files']} файлов
🔄 {pr['head']} → {pr['base']}
{labels_text}
🔗 {pr['url']}

"""
        
        return text

    def create_gist_from_file(self, file_content, filename, description="", public=True):
        """
        Создание Gist из содержимого файла
        """
        try:
            url = f"{self.base_url}/gists"
            
            data = {
                'description': description or f"Файл {filename}",
                'public': public,
                'files': {
                    filename: {
                        'content': file_content
                    }
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                gist_data = response.json()
                
                return {
                    'success': True,
                    'url': gist_data['html_url'],
                    'id': gist_data['id'],
                    'description': gist_data['description'],
                    'files': list(gist_data['files'].keys())
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка создания Gist: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка создания Gist: {str(e)}'
            }

    def detect_file_type(self, filename):
        """
        Определение типа файла по расширению
        """
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        file_types = {
            'python': ['py', 'pyw', 'pyc', 'pyo'],
            'javascript': ['js', 'jsx', 'mjs', 'ts', 'tsx'],
            'java': ['java', 'class', 'jar'],
            'c': ['c', 'h'],
            'cpp': ['cpp', 'cc', 'cxx', 'hpp', 'hxx'],
            'csharp': ['cs'],
            'go': ['go'],
            'rust': ['rs'],
            'php': ['php', 'phtml'],
            'ruby': ['rb', 'rbw'],
            'swift': ['swift'],
            'kotlin': ['kt', 'kts'],
            'html': ['html', 'htm'],
            'css': ['css', 'scss', 'sass', 'less'],
            'sql': ['sql'],
            'json': ['json'],
            'xml': ['xml'],
            'yaml': ['yaml', 'yml'],
            'markdown': ['md', 'markdown'],
            'text': ['txt', 'log', 'ini', 'cfg', 'conf'],
            'bash': ['sh', 'bash', 'zsh'],
            'powershell': ['ps1', 'psm1', 'psd1'],
            'docker': ['dockerfile'],
            'gitignore': ['gitignore'],
            'readme': ['readme']
        }
        
        for file_type, extensions in file_types.items():
            if extension in extensions:
                return file_type
        
        return 'text'

    def format_gist_result(self, gist_result):
        """
        Форматирование результата создания Gist
        """
        if not gist_result['success']:
            return f"❌ Ошибка создания Gist: {gist_result['error']}"
        
        files_text = ', '.join(gist_result['files'])
        
        return f"""✅ **Gist успешно создан!**

📄 **Описание:** {gist_result['description']}
📁 **Файлы:** {files_text}
🔗 **Ссылка:** {gist_result['url']}
🆔 **ID:** `{gist_result['id']}`

💡 **Совет:** Вы можете поделиться этой ссылкой с другими!"""

    def create_multiple_gists(self, files_data, description="", public=True):
        """
        Создание нескольких Gists из файлов
        """
        results = []
        
        for file_data in files_data:
            filename = file_data.get('filename', 'file.txt')
            content = file_data.get('content', '')
            
            if not content:
                results.append({
                    'filename': filename,
                    'success': False,
                    'error': 'Пустое содержимое файла'
                })
                continue
            
            gist_result = self.create_gist_from_file(content, filename, description, public)
            results.append({
                'filename': filename,
                'success': gist_result['success'],
                'result': gist_result
            })
        
        return results

    def format_multiple_gists_result(self, results):
        """
        Форматирование результата создания нескольких Gists
        """
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        text = f"📄 **Результат создания Gists**\n\n"
        
        if successful:
            text += f"✅ **Успешно создано:** {len(successful)}\n"
            for result in successful:
                gist_data = result['result']
                text += f"• **{result['filename']}** - {gist_data['url']}\n"
            text += "\n"
        
        if failed:
            text += f"❌ **Ошибки:** {len(failed)}\n"
            for result in failed:
                text += f"• **{result['filename']}** - {result['error']}\n"
        
        return text