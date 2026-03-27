#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translator Module
Модуль для перевода текста с использованием различных API
"""

import logging
import requests
import json
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class Translator:
    """Класс для перевода текста"""
    
    def __init__(self):
        self.supported_languages = {
            'ru': 'Русский',
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'ar': 'العربية',
            'hi': 'हिन्दी',
            'tr': 'Türkçe',
            'pl': 'Polski',
            'nl': 'Nederlands',
            'sv': 'Svenska',
            'da': 'Dansk',
            'no': 'Norsk',
            'fi': 'Suomi',
            'cs': 'Čeština',
            'sk': 'Slovenčina',
            'hu': 'Magyar',
            'ro': 'Română',
            'bg': 'Български',
            'hr': 'Hrvatski',
            'sl': 'Slovenščina',
            'et': 'Eesti',
            'lv': 'Latviešu',
            'lt': 'Lietuvių',
            'uk': 'Українська',
            'be': 'Беларуская',
            'ka': 'ქართული',
            'hy': 'Հայերեն',
            'az': 'Azərbaycan',
            'kk': 'Қазақ',
            'ky': 'Кыргыз',
            'uz': 'Oʻzbek',
            'tg': 'Тоҷикӣ',
            'mn': 'Монгол',
            'th': 'ไทย',
            'vi': 'Tiếng Việt',
            'id': 'Bahasa Indonesia',
            'ms': 'Bahasa Melayu',
            'tl': 'Filipino',
            'sw': 'Kiswahili',
            'am': 'አማርኛ',
            'he': 'עברית',
            'fa': 'فارسی',
            'ur': 'اردو',
            'bn': 'বাংলা',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'ml': 'മലയാളം',
            'kn': 'ಕನ್ನಡ',
            'gu': 'ગુજરાતી',
            'pa': 'ਪੰਜਾਬੀ',
            'or': 'ଓଡ଼ିଆ',
            'as': 'অসমীয়া',
            'ne': 'नेपाली',
            'si': 'සිංහල',
            'my': 'မြန်မာ',
            'km': 'ខ្មែរ',
            'lo': 'ລາວ',
            'bo': 'བོད་ཡིག',
            'dz': 'རྫོང་ཁ',
            'ti': 'ትግርኛ',
            'om': 'Afaan Oromoo',
            'so': 'Soomaali',
            'ha': 'Hausa',
            'yo': 'Yorùbá',
            'ig': 'Igbo',
            'zu': 'IsiZulu',
            'xh': 'IsiXhosa',
            'af': 'Afrikaans',
            'sq': 'Shqip',
            'eu': 'Euskera',
            'ca': 'Català',
            'gl': 'Galego',
            'cy': 'Cymraeg',
            'ga': 'Gaeilge',
            'mt': 'Malti',
            'is': 'Íslenska',
            'fo': 'Føroyskt',
            'kl': 'Kalaallisut',
            'se': 'Davvisámegiella',
            'sm': 'Gagana Samoa',
            'to': 'Lea fakatonga',
            'fj': 'Na Vosa Vakaviti',
            'haw': 'ʻŌlelo Hawaiʻi',
            'mi': 'Te Reo Māori',
            'ty': 'Reo Tahiti',
            'mg': 'Malagasy',
            'rw': 'Ikinyarwanda',
            'rn': 'Kirundi',
            'lg': 'Luganda',
            'ny': 'Chichewa',
            'sn': 'ChiShona',
            'nd': 'IsiNdebele',
            've': 'Tshivenḓa',
            'ts': 'Xitsonga',
            'ss': 'SiSwati',
            'st': 'Sesotho',
            'tn': 'Setswana',
            'nso': 'Sesotho sa Leboa',
            'zu': 'IsiZulu',
            'xh': 'IsiXhosa',
            'af': 'Afrikaans'
        }
        
        # Популярные языки для быстрого доступа
        self.popular_languages = ['ru', 'en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko']
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Определить язык текста
        
        Args:
            text: Текст для определения языка
            
        Returns:
            Код языка или None
        """
        try:
            # Простая эвристика для определения языка
            text_lower = text.lower()
            
            # Русский язык
            russian_chars = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            if any(char in russian_chars for char in text_lower):
                return 'ru'
            
            # Английский язык
            english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            if any(word in text_lower for word in english_words):
                return 'en'
            
            # Испанский язык
            spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le']
            if any(word in text_lower for word in spanish_words):
                return 'es'
            
            # Французский язык
            french_words = ['le', 'la', 'de', 'et', 'à', 'un', 'il', 'que', 'ne', 'se', 'ce', 'pas', 'pour', 'sur']
            if any(word in text_lower for word in french_words):
                return 'fr'
            
            # Немецкий язык
            german_words = ['der', 'die', 'das', 'und', 'in', 'den', 'von', 'zu', 'dem', 'mit', 'sich', 'des', 'auf', 'für']
            if any(word in text_lower for word in german_words):
                return 'de'
            
            # По умолчанию считаем английским
            return 'en'
            
        except Exception as e:
            logger.error(f"Ошибка определения языка: {e}")
            return 'en'  # По умолчанию английский
    
    def translate_with_libre_translate(self, text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
        """
        Перевод через бесплатный LibreTranslate API
        
        Args:
            text: Текст для перевода
            target_lang: Целевой язык
            source_lang: Исходный язык (auto для автоопределения)
            
        Returns:
            Переведенный текст или None
        """
        try:
            # Используем публичный LibreTranslate API
            url = "https://libretranslate.de/translate"
            
            data = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get('translatedText')
            
        except Exception as e:
            logger.error(f"Ошибка перевода через LibreTranslate: {e}")
            return None
    
    def translate_with_my_memory(self, text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
        """
        Перевод через MyMemory API
        
        Args:
            text: Текст для перевода
            target_lang: Целевой язык
            source_lang: Исходный язык
            
        Returns:
            Переведенный текст или None
        """
        try:
            url = "https://api.mymemory.translated.net/get"
            
            params = {
                'q': text,
                'langpair': f"{source_lang}|{target_lang}"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get('responseData', {}).get('translatedText')
            
        except Exception as e:
            logger.error(f"Ошибка перевода через MyMemory: {e}")
            return None
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'auto') -> Dict:
        """
        Основной метод перевода текста
        
        Args:
            text: Текст для перевода
            target_lang: Целевой язык
            source_lang: Исходный язык (auto для автоопределения)
            
        Returns:
            Словарь с результатом перевода
        """
        if not text.strip():
            return {'success': False, 'error': 'Пустой текст'}
        
        if len(text) > 5000:
            return {'success': False, 'error': 'Текст слишком длинный (максимум 5000 символов)'}
        
        # Если исходный язык не указан, определяем автоматически
        if source_lang == 'auto':
            source_lang = self.detect_language(text)
        
        # Проверяем поддерживаемые языки
        if source_lang not in self.supported_languages:
            source_lang = 'en'  # По умолчанию английский
        
        if target_lang not in self.supported_languages:
            return {'success': False, 'error': f'Неподдерживаемый язык: {target_lang}'}
        
        # Если языки одинаковые, возвращаем исходный текст
        if source_lang == target_lang:
            return {
                'success': True,
                'original_text': text,
                'translated_text': text,
                'source_language': self.supported_languages[source_lang],
                'target_language': self.supported_languages[target_lang],
                'service': 'no_translation_needed'
            }
        
        # Пробуем разные сервисы перевода
        translated_text = None
        service_used = None
        
        # Сначала пробуем LibreTranslate
        translated_text = self.translate_with_libre_translate(text, target_lang, source_lang)
        if translated_text:
            service_used = 'LibreTranslate'
        
        # Если не получилось, пробуем MyMemory
        if not translated_text:
            translated_text = self.translate_with_my_memory(text, target_lang, source_lang)
            if translated_text:
                service_used = 'MyMemory'
        
        if translated_text:
            return {
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'source_language': self.supported_languages[source_lang],
                'target_language': self.supported_languages[target_lang],
                'service': service_used
            }
        else:
            return {'success': False, 'error': 'Не удалось перевести текст'}
    
    def get_language_name(self, lang_code: str) -> str:
        """Получить название языка по коду"""
        return self.supported_languages.get(lang_code, lang_code)
    
    def get_popular_languages(self) -> List[Dict]:
        """Получить список популярных языков"""
        return [{'code': code, 'name': self.supported_languages[code]} for code in self.popular_languages]
    
    def search_languages(self, query: str) -> List[Dict]:
        """Поиск языков по названию"""
        query_lower = query.lower()
        results = []
        
        for code, name in self.supported_languages.items():
            if query_lower in name.lower() or query_lower in code.lower():
                results.append({'code': code, 'name': name})
        
        return results[:10]  # Ограничиваем результаты
    
    def get_translation_suggestions(self) -> List[str]:
        """Получить предложения для перевода"""
        return [
            "Привет, как дела?",
            "Hello, how are you?",
            "Hola, ¿cómo estás?",
            "Bonjour, comment allez-vous?",
            "Hallo, wie geht es dir?",
            "Ciao, come stai?",
            "Olá, como você está?",
            "你好，你好吗？",
            "こんにちは、元気ですか？",
            "안녕하세요, 어떻게 지내세요?",
            "مرحبا، كيف حالك؟",
            "नमस्ते, आप कैसे हैं?",
            "Merhaba, nasılsın?",
            "Cześć, jak się masz?",
            "Hoi, hoe gaat het?",
            "Hej, hur mår du?",
            "Hei, miten menee?",
            "Ahoj, jak se máš?",
            "Szia, hogy vagy?",
            "Salut, ce mai faci?"
        ]


if __name__ == "__main__":
    # Тестирование
    translator = Translator()
    print(f"Поддерживаемые языки: {len(translator.supported_languages)}")
    print(f"Популярные языки: {translator.get_popular_languages()}")
    
    # Тест перевода
    result = translator.translate_text("Hello, world!", "ru")
    if result['success']:
        print(f"Перевод: {result['translated_text']}")
    else:
        print(f"Ошибка: {result['error']}")