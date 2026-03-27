#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music Search Module
Модуль для поиска информации о музыке и предоставления ссылок
"""

import logging
import requests
import json
from typing import Optional, Dict, List
import urllib.parse

logger = logging.getLogger(__name__)


class MusicSearcher:
    """Класс для поиска информации о музыке"""
    
    def __init__(self):
        self.supported_platforms = {
            'spotify': 'Spotify',
            'youtube': 'YouTube',
            'apple': 'Apple Music',
            'deezer': 'Deezer',
            'soundcloud': 'SoundCloud',
            'bandcamp': 'Bandcamp'
        }
    
    def search_music_info(self, query: str) -> Dict:
        """
        Поиск информации о музыке
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Словарь с результатами поиска
        """
        if not query.strip():
            return {'success': False, 'error': 'Пустой поисковый запрос'}
        
        try:
            # Используем Last.fm API для получения информации о треках
            lastfm_results = self.search_lastfm(query)
            
            if lastfm_results['success']:
                # Дополняем результатами поиска на YouTube
                youtube_results = self.search_youtube(query)
                
                return {
                    'success': True,
                    'query': query,
                    'lastfm': lastfm_results,
                    'youtube': youtube_results,
                    'platforms': self.get_platform_links(query)
                }
            else:
                return {'success': False, 'error': 'Не удалось найти информацию о музыке'}
                
        except Exception as e:
            logger.error(f"Ошибка поиска музыки: {e}")
            return {'success': False, 'error': f'Ошибка поиска: {str(e)}'}
    
    def search_lastfm(self, query: str) -> Dict:
        """
        Поиск через Last.fm API
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Результаты поиска Last.fm
        """
        try:
            # Используем публичный API Last.fm
            url = "http://ws.audioscrobbler.com/2.0/"
            
            params = {
                'method': 'track.search',
                'track': query,
                'api_key': 'your_lastfm_api_key',  # Нужен API ключ
                'format': 'json',
                'limit': 5
            }
            
            # Если API ключ не настроен, возвращаем заглушку
            if params['api_key'] == 'your_lastfm_api_key':
                return self.get_mock_music_data(query)
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and 'trackmatches' in data['results']:
                tracks = data['results']['trackmatches']['track']
                
                if tracks:
                    # Берем первый результат
                    track = tracks[0] if isinstance(tracks, list) else tracks
                    
                    return {
                        'success': True,
                        'track_name': track.get('name', ''),
                        'artist': track.get('artist', ''),
                        'listeners': track.get('listeners', '0'),
                        'url': track.get('url', ''),
                        'image': track.get('image', [{}])[-1].get('#text', '') if track.get('image') else ''
                    }
            
            return {'success': False, 'error': 'Трек не найден'}
            
        except Exception as e:
            logger.error(f"Ошибка Last.fm API: {e}")
            return self.get_mock_music_data(query)
    
    def get_mock_music_data(self, query: str) -> Dict:
        """Заглушка для демонстрации (когда API не настроен)"""
        return {
            'success': True,
            'track_name': query.split()[-1] if query.split() else 'Track',
            'artist': ' '.join(query.split()[:-1]) if len(query.split()) > 1 else 'Artist',
            'listeners': '1,000,000+',
            'url': f'https://www.last.fm/search?q={query.replace(" ", "+")}',
            'image': ''
        }
    
    def search_youtube(self, query: str) -> Dict:
        """
        Поиск на YouTube (только ссылки, без скачивания)
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Результаты поиска YouTube
        """
        try:
            # Формируем URL для поиска на YouTube
            search_query = urllib.parse.quote_plus(query)
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            return {
                'success': True,
                'search_url': youtube_url,
                'message': 'Нажмите на ссылку для поиска на YouTube'
            }
            
        except Exception as e:
            logger.error(f"Ошибка YouTube поиска: {e}")
            return {'success': False, 'error': 'Ошибка YouTube поиска'}
    
    def get_platform_links(self, query: str) -> Dict[str, str]:
        """
        Получить ссылки для поиска на различных платформах
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Словарь с ссылками на платформы
        """
        encoded_query = urllib.parse.quote_plus(query)
        
        return {
            'spotify': f"https://open.spotify.com/search/{encoded_query}",
            'youtube': f"https://www.youtube.com/results?search_query={encoded_query}",
            'apple': f"https://music.apple.com/search?term={encoded_query}",
            'deezer': f"https://www.deezer.com/search/{encoded_query}",
            'soundcloud': f"https://soundcloud.com/search?q={encoded_query}",
            'bandcamp': f"https://bandcamp.com/search?q={encoded_query}"
        }
    
    def get_music_suggestions(self) -> List[str]:
        """Получить предложения для поиска музыки"""
        return [
            "Imagine Dragons - Thunder",
            "Ed Sheeran - Shape of You",
            "Billie Eilish - Bad Guy",
            "The Weeknd - Blinding Lights",
            "Dua Lipa - Levitating",
            "Olivia Rodrigo - Drivers License",
            "Harry Styles - Watermelon Sugar",
            "Taylor Swift - Anti-Hero",
            "Post Malone - Circles",
            "Ariana Grande - Positions",
            "Drake - God's Plan",
            "Travis Scott - SICKO MODE",
            "Kendrick Lamar - HUMBLE.",
            "Cardi B - WAP",
            "Megan Thee Stallion - Savage",
            "Doja Cat - Say So",
            "Lil Nas X - Old Town Road",
            "Roddy Ricch - The Box",
            "DaBaby - Rockstar",
            "Lil Baby - The Bigger Picture"
        ]
    
    def get_genre_suggestions(self) -> List[str]:
        """Получить предложения жанров"""
        return [
            "Pop",
            "Rock",
            "Hip Hop",
            "R&B",
            "Electronic",
            "Jazz",
            "Classical",
            "Country",
            "Reggae",
            "Blues",
            "Folk",
            "Indie",
            "Alternative",
            "Metal",
            "Punk",
            "Funk",
            "Soul",
            "Gospel",
            "World",
            "Ambient"
        ]
    
    def format_music_result(self, result: Dict) -> str:
        """
        Форматировать результат поиска музыки
        
        Args:
            result: Результат поиска
            
        Returns:
            Отформатированная строка
        """
        if not result['success']:
            return f"❌ {result['error']}"
        
        text = f"🎵 **Найдено:** {result['query']}\n\n"
        
        if result.get('lastfm', {}).get('success'):
            lastfm = result['lastfm']
            text += f"🎤 **Исполнитель:** {lastfm['artist']}\n"
            text += f"🎵 **Трек:** {lastfm['track_name']}\n"
            text += f"👥 **Слушателей:** {lastfm['listeners']}\n\n"
        
        text += "🔗 **Ссылки для поиска:**\n"
        platforms = result.get('platforms', {})
        
        for platform, url in platforms.items():
            platform_name = self.supported_platforms.get(platform, platform)
            text += f"• [{platform_name}]({url})\n"
        
        text += "\n💡 **Важно:** Используйте легальные источники для прослушивания музыки!"
        
        return text


if __name__ == "__main__":
    # Тестирование
    searcher = MusicSearcher()
    print(f"Поддерживаемые платформы: {list(searcher.supported_platforms.keys())}")
    print(f"Предложения: {searcher.get_music_suggestions()[:5]}")
    
    # Тест поиска
    result = searcher.search_music_info("Imagine Dragons Thunder")
    if result['success']:
        print(f"Результат: {searcher.format_music_result(result)}")
    else:
        print(f"Ошибка: {result['error']}")