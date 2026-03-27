#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для поиска информации в интернете
"""

import requests
import logging
from typing import Dict, List, Optional
from urllib.parse import quote_plus
import json
import os
from config import CLAUDE_PROXY

logger = logging.getLogger(__name__)


class WebSearchHelper:
    """Класс для поиска информации в интернете"""
    
    def __init__(self, claude_helper=None):
        # Можно использовать различные поисковые API
        # Для начала используем DuckDuckGo (бесплатный, без API ключа)
        self.search_url = "https://html.duckduckgo.com/html/"
        self.instant_answer_url = "https://api.duckduckgo.com/"
        
        # Сохраняем ссылку на ClaudeHelper для fallback (не создаем новый экземпляр!)
        self.claude_helper = claude_helper
        
        # Настройка прокси (используем тот же, что и для Claude)
        self.proxies = None
        if CLAUDE_PROXY:
            try:
                # Парсим прокси
                if CLAUDE_PROXY.startswith("socks5://"):
                    # Для SOCKS5 нужен requests[socks] или pysocks
                    try:
                        import socks
                        import socket
                        # Парсим SOCKS5 прокси
                        # Формат: socks5://user:pass@host:port
                        proxy_parts = CLAUDE_PROXY.replace('socks5://', '').split('@')
                        if len(proxy_parts) == 2:
                            auth, host_port = proxy_parts
                            user, password = auth.split(':')
                            host, port = host_port.split(':')
                        else:
                            host, port = proxy_parts[0].split(':')
                            user, password = None, None
                        
                        # Настраиваем SOCKS5 прокси
                        socks.set_default_proxy(socks.SOCKS5, host, int(port), 
                                               username=user if user else None,
                                               password=password if password else None)
                        socket.socket = socks.socksocket
                        
                        # Для requests используем обычный формат
                        self.proxies = {
                            'http': f'socks5h://{host}:{port}',
                            'https': f'socks5h://{host}:{port}'
                        }
                        logger.info("SOCKS5 прокси для поиска настроен")
                    except ImportError:
                        logger.warning("Для SOCKS5 прокси установите: pip install requests[socks] или pysocks")
                        # Пробуем без прокси
                        self.proxies = None
                    except Exception as e:
                        logger.warning(f"Не удалось настроить SOCKS5 прокси: {e}")
                        self.proxies = None
                else:
                    # HTTP/HTTPS прокси
                    self.proxies = {
                        'http': CLAUDE_PROXY,
                        'https': CLAUDE_PROXY
                    }
                logger.info("Прокси для поиска настроен")
            except Exception as e:
                logger.warning(f"Ошибка настройки прокси для поиска: {e}")
        
        # User-Agent для имитации браузера
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def search(self, query: str, max_results: int = 5) -> Dict:
        """
        Поиск информации в интернете
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            Словарь с результатами поиска
        """
        try:
            if not query.strip():
                return {'success': False, 'error': 'Пустой поисковый запрос'}
            
            # Пробуем несколько методов поиска
            # 1. DuckDuckGo Instant Answer API
            results = self._search_duckduckgo(query, max_results)
            if results.get('success') and results.get('results'):
                return results
            
            # 2. Fallback: используем Claude для поиска информации
            logger.info("DuckDuckGo не вернул результатов, используем Claude")
            return self._search_with_claude(query, max_results)
                
        except Exception as e:
            logger.error(f"Ошибка поиска в интернете: {e}")
            # Последний fallback - возвращаем ссылку на поиск
            return {
                'success': True,
                'query': query,
                'results': [{
                    'title': f'Результаты поиска: {query}',
                    'url': f'https://duckduckgo.com/?q={quote_plus(query)}',
                    'snippet': f'Нажми на ссылку для просмотра результатов поиска по запросу "{query}". DuckDuckGo может быть временно недоступен.'
                }]
            }
    
    def _search_duckduckgo(self, query: str, max_results: int) -> Dict:
        """Поиск через DuckDuckGo Instant Answer API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(
                self.instant_answer_url,
                params=params,
                timeout=15,  # Увеличили timeout
                headers=self.headers,
                proxies=self.proxies,
                verify=True
            )
            
            # 200 и 202 - успешные ответы
            if response.status_code in [200, 202]:
                data = response.json()
                
                results = {
                    'success': True,
                    'query': query,
                    'results': []
                }
                
                # Добавляем Instant Answer если есть
                if data.get('AbstractText'):
                    results['instant_answer'] = {
                        'text': data.get('AbstractText'),
                        'source': data.get('AbstractURL', ''),
                        'heading': data.get('Heading', '')
                    }
                
                # Добавляем связанные темы
                if data.get('RelatedTopics'):
                    for topic in data.get('RelatedTopics', [])[:max_results]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            results['results'].append({
                                'title': topic.get('Text', '')[:100],
                                'url': topic.get('FirstURL', ''),
                                'snippet': topic.get('Text', '')[:200]
                            })
                
                # Добавляем результаты из Answer
                if data.get('Answer'):
                    results['results'].insert(0, {
                        'title': data.get('Heading', query),
                        'url': data.get('AbstractURL', ''),
                        'snippet': data.get('Answer', '')
                    })
                
                return results
            else:
                logger.warning(f"DuckDuckGo вернул статус {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            logger.error("Timeout при подключении к DuckDuckGo")
            return {'success': False, 'error': 'Timeout - сервер не отвечает'}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка подключения к DuckDuckGo: {e}")
            return {'success': False, 'error': 'Ошибка подключения - проверьте интернет или прокси'}
        except Exception as e:
            logger.error(f"Ошибка DuckDuckGo поиска: {e}")
            return {'success': False, 'error': str(e)}
    
    def _search_with_claude(self, query: str, max_results: int) -> Dict:
        """Поиск информации через Claude AI (fallback)"""
        try:
            # Используем существующий экземпляр ClaudeHelper, если есть
            if not self.claude_helper:
                from claude_helper import ClaudeHelper
                self.claude_helper = ClaudeHelper()
            
            claude = self.claude_helper
            
            prompt = f"""Найди актуальную информацию о: {query}

Верни структурированный ответ с:
1. Краткое описание (2-3 предложения)
2. Ключевые факты (3-5 пунктов)
3. Полезные ссылки или источники (если знаешь)

Формат ответа:
**Описание:**
[краткое описание]

**Ключевые факты:**
• [факт 1]
• [факт 2]
• [факт 3]

**Источники:**
[ссылки или источники, если знаешь]"""
            
            # ask_question синхронный, но вызывается из async контекста
            # В web_search_helper это fallback, вызывается редко
            # Для оптимизации можно обернуть в asyncio.to_thread в вызывающем коде
            response = claude.ask_question(prompt)
            
            return {
                'success': True,
                'query': query,
                'results': [{
                    'title': f'Информация о: {query}',
                    'url': f'https://duckduckgo.com/?q={quote_plus(query)}',
                    'snippet': response[:500] + '...' if len(response) > 500 else response
                }],
                'claude_response': response
            }
        except Exception as e:
            logger.error(f"Ошибка поиска через Claude: {e}")
            return {'success': False, 'error': str(e)}
    
    def _search_simple(self, query: str, max_results: int) -> Dict:
        """Простой поиск через DuckDuckGo HTML (fallback)"""
        try:
            # Формируем URL для поиска
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = requests.get(
                search_url,
                timeout=15,  # Увеличили timeout
                headers=self.headers,
                proxies=self.proxies,
                verify=True
            )
            
            if response.status_code in [200, 202]:
                # Парсим HTML (упрощенный вариант)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                results = {
                    'success': True,
                    'query': query,
                    'results': []
                }
                
                # Ищем результаты поиска
                result_divs = soup.find_all('div', class_='result')[:max_results]
                
                for div in result_divs:
                    title_elem = div.find('a', class_='result__a')
                    snippet_elem = div.find('a', class_='result__snippet')
                    
                    if title_elem:
                        results['results'].append({
                            'title': title_elem.get_text(strip=True),
                            'url': title_elem.get('href', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                        })
                
                return results
            else:
                logger.warning(f"DuckDuckGo HTML вернул статус {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except ImportError:
            # BeautifulSoup не установлен, возвращаем простой результат
            logger.warning("BeautifulSoup не установлен, используем Claude")
            return self._search_with_claude(query, max_results)
        except requests.exceptions.Timeout:
            logger.error("Timeout при подключении к DuckDuckGo HTML")
            return self._search_with_claude(query, max_results)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка подключения к DuckDuckGo HTML: {e}")
            return self._search_with_claude(query, max_results)
        except Exception as e:
            logger.error(f"Ошибка простого поиска: {e}")
            return self._search_with_claude(query, max_results)
    
    def search_news(self, query: str, max_results: int = 5) -> Dict:
        """Поиск новостей"""
        try:
            # Используем DuckDuckGo для поиска новостей
            search_query = f"{query} news"
            return self.search(search_query, max_results)
        except Exception as e:
            logger.error(f"Ошибка поиска новостей: {e}")
            return {'success': False, 'error': str(e)}
    
    def format_results(self, search_results: Dict) -> str:
        """Форматировать результаты поиска для отображения"""
        if not search_results.get('success'):
            error = search_results.get('error', 'Не удалось выполнить поиск')
            # Если ошибка подключения, предлагаем использовать Claude
            if 'Timeout' in error or 'Connection' in error:
                return (
                    f"❌ **Ошибка подключения к поисковой системе**\n\n"
                    f"Ошибка: {error}\n\n"
                    f"💡 **Попробуй:**\n"
                    f"• Проверить интернет-соединение\n"
                    f"• Использовать прокси (если настроен)\n"
                    f"• Попробовать позже\n\n"
                    f"Или спроси у AI Claude напрямую через `/ai_chat`"
                )
            return f"❌ {error}"
        
        text = f"🔍 **Результаты поиска:** `{search_results.get('query', '')}`\n\n"
        
        # Если есть ответ от Claude (fallback)
        if 'claude_response' in search_results:
            text += "💡 **Информация от AI:**\n\n"
            text += search_results['claude_response']
            text += "\n\n"
            text += f"🔗 **Поиск в интернете:** https://duckduckgo.com/?q={quote_plus(search_results.get('query', ''))}\n"
            return text
        
        # Добавляем Instant Answer если есть
        if 'instant_answer' in search_results:
            ia = search_results['instant_answer']
            text += f"💡 **{ia.get('heading', 'Быстрый ответ')}**\n"
            text += f"{ia.get('text', '')}\n"
            if ia.get('source'):
                text += f"📎 {ia.get('source')}\n\n"
        
        # Добавляем результаты
        results = search_results.get('results', [])
        if results:
            for i, result in enumerate(results[:5], 1):
                title = result.get('title', 'Без названия')
                url = result.get('url', '')
                snippet = result.get('snippet', '')
                
                text += f"{i}. **{title}**\n"
                if snippet:
                    # Обрезаем слишком длинные сниппеты
                    snippet_text = snippet[:200] + '...' if len(snippet) > 200 else snippet
                    text += f"   {snippet_text}\n"
                if url:
                    text += f"   🔗 {url}\n"
                text += "\n"
        else:
            text += "📝 Результаты не найдены. Попробуйте изменить запрос."
        
        return text

