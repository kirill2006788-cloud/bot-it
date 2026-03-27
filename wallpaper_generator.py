#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wallpaper Generator Module
Специализированный генератор обоев для мобильных устройств
"""

import logging
from io import BytesIO
from PIL import Image, ImageOps
from image_generator import ImageGenerator, validate_prompt
from config import MAX_IMAGE_PROMPT_LENGTH

logger = logging.getLogger(__name__)


class WallpaperGenerator(ImageGenerator):
    """Класс для генерации обоев для мобильных устройств"""
    
    def __init__(self):
        super().__init__()
        self.wallpaper_presets = {
            'iphone': {'width': 1170, 'height': 2532, 'ratio': '9:19.5'},
            'android': {'width': 1080, 'height': 2340, 'ratio': '9:19.5'},
            'wide': {'width': 1440, 'height': 2560, 'ratio': '9:16'},
            'square': {'width': 1080, 'height': 1080, 'ratio': '1:1'},
            'ultrawide': {'width': 1080, 'height': 2400, 'ratio': '9:20'}
        }
    
    def enhance_wallpaper_prompt(self, user_prompt: str, claude_helper) -> str:
        """
        Улучшить промпт специально для обоев
        
        Args:
            user_prompt: Оригинальный промпт пользователя
            claude_helper: Экземпляр ClaudeHelper
            
        Returns:
            Улучшенный промпт для обоев
        """
        enhancement_request = f"""Преобразуй этот промпт в детальное описание для создания обоев на мобильный телефон на английском языке.
        
Оригинальный промпт: "{user_prompt}"

КРИТИЧЕСКИ ВАЖНО:
- ОБЯЗАТЕЛЬНО сохрани ВСЕ ключевые элементы из оригинального промпта (животные, предметы, персонажи, действия)
- НЕ заменяй и НЕ удаляй основные объекты из промпта
- НЕ добавляй новые объекты, которых нет в оригинале

Правила для обоев:
1. Переведи на английский если нужно
2. Сохрани ВСЕ ключевые слова из оригинала (животные, предметы, действия, стили)
3. Добавь детали подходящие для обоев: красивые цвета, атмосферу, композицию, но НЕ меняй основной объект
4. Учти что это будет фон экрана - избегай слишком детализированных элементов
5. Используй художественные термины для обоев
6. Добавь качественные характеристики: high resolution, wallpaper quality, mobile optimized
7. Длина: 40-80 слов
8. НЕ добавляй объяснения, только сам улучшенный промпт

Примеры хороших обоев:
- "Minimalist gradient wallpaper with soft blue to purple colors, clean design, high resolution, mobile wallpaper"
- "Abstract geometric patterns with warm colors, modern design, wallpaper quality, phone background"
- "Nature landscape with mountains and sunset, cinematic composition, high quality wallpaper"
- "Cute little elephant at sunset, anime style wallpaper, warm colors, mobile optimized, high resolution"

Твой улучшенный промпт для обоев:"""
        
        try:
            enhanced = claude_helper.ask_question(enhancement_request)
            # Убираем лишние кавычки и переносы строк
            enhanced = enhanced.strip().strip('"').strip("'").replace('\n', ' ')
            logger.info(f"Enhanced wallpaper prompt: {enhanced}")
            return enhanced
        except Exception as e:
            logger.error(f"Ошибка улучшения промпта для обоев: {e}")
            return user_prompt
    
    def generate_wallpaper_with_pollinations(self, prompt: str, device_type: str = 'android') -> BytesIO:
        """
        Генерация обоев через Pollinations.ai с оптимизацией для мобильных устройств
        
        Args:
            prompt: Текстовое описание обоев
            device_type: Тип устройства (iphone, android, wide, square, ultrawide)
            
        Returns:
            BytesIO объект с изображением обоев
        """
        import urllib.parse
        
        # Получаем размеры для устройства
        preset = self.wallpaper_presets.get(device_type, self.wallpaper_presets['android'])
        
        # URL-кодируем промпт
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Pollinations.ai URL с параметрами для обоев
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        # Параметры оптимизированные для обоев
        params = {
            "width": preset['width'],
            "height": preset['height'],
            "nologo": "true",
            "enhance": "true",
            "model": "flux",  # Используем более качественную модель
            "quality": "high"
        }
        
        try:
            logger.info(f"Generating wallpaper with Pollinations.ai: {prompt} ({device_type})")
            import requests
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            return BytesIO(response.content)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации обоев через Pollinations: {e}")
            raise Exception(f"Ошибка генерации обоев: {str(e)}")
    
    def optimize_for_wallpaper(self, image_buffer: BytesIO, device_type: str = 'android') -> BytesIO:
        """
        Оптимизировать изображение для использования в качестве обоев
        
        Args:
            image_buffer: Исходное изображение
            device_type: Тип устройства
            
        Returns:
            Оптимизированное изображение
        """
        try:
            # Открываем изображение
            image_buffer.seek(0)
            image = Image.open(image_buffer)
            
            # Получаем размеры для устройства
            preset = self.wallpaper_presets.get(device_type, self.wallpaper_presets['android'])
            target_width = preset['width']
            target_height = preset['height']
            
            # Если изображение уже нужного размера, возвращаем как есть
            if image.size == (target_width, target_height):
                image_buffer.seek(0)
                return image_buffer
            
            # Масштабируем изображение с сохранением пропорций
            image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Создаем новое изображение нужного размера
            new_image = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            
            # Центрируем изображение
            x = (target_width - image.width) // 2
            y = (target_height - image.height) // 2
            new_image.paste(image, (x, y))
            
            # Сохраняем в BytesIO
            output_buffer = BytesIO()
            new_image.save(output_buffer, format='PNG', quality=95, optimize=True)
            output_buffer.seek(0)
            
            return output_buffer
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации обоев: {e}")
            return image_buffer  # Возвращаем исходное если не удалось оптимизировать
    
    def generate_wallpaper(self, prompt: str, device_type: str = 'android', enhance_with_claude=None) -> tuple[BytesIO, str]:
        """
        Основной метод генерации обоев
        
        Args:
            prompt: Описание обоев
            device_type: Тип устройства
            enhance_with_claude: ClaudeHelper для улучшения промпта (опционально)
            
        Returns:
            Tuple (BytesIO с обоями, итоговый промпт)
        """
        # Проверяем длину промпта
        if len(prompt) > MAX_IMAGE_PROMPT_LENGTH:
            raise ValueError(f"Промпт слишком длинный! Максимум {MAX_IMAGE_PROMPT_LENGTH} символов.")
        
        # Улучшаем промпт через Claude если доступно
        final_prompt = prompt
        if enhance_with_claude:
            try:
                final_prompt = self.enhance_wallpaper_prompt(prompt, enhance_with_claude)
            except Exception as e:
                logger.warning(f"Не удалось улучшить промпт для обоев через Claude: {e}")
                final_prompt = prompt
        
        # Генерируем обои
        wallpaper_buffer = self.generate_wallpaper_with_pollinations(final_prompt, device_type)
        
        # Оптимизируем для обоев
        optimized_buffer = self.optimize_for_wallpaper(wallpaper_buffer, device_type)
        
        return optimized_buffer, final_prompt
    
    def generate_with_settings(self, prompt: str, user_id: int, enhance_with_claude=None, device_type: str = 'android') -> tuple:
        """Генерация обоев с учётом настроек пользователя"""
        settings = self.get_user_settings(user_id)
        
        # Определяем персонажа
        working_prompt, detected_char = self.detect_character(prompt)
        
        # Применяем стиль
        if settings['style']:
            working_prompt = self.apply_style(working_prompt, settings['style'])
        
        # Улучшаем через Claude если доступно (всегда, не только если нет персонажа)
        if enhance_with_claude:
            try:
                logger.info(f"Улучшаю промпт для обоев через Claude: {working_prompt[:50]}...")
                working_prompt = self.enhance_wallpaper_prompt(working_prompt, enhance_with_claude)
                logger.info(f"Улучшенный промпт для обоев: {working_prompt[:100]}...")
            except Exception as e:
                logger.warning(f"Не удалось улучшить промпт для обоев через Claude: {e}, используем оригинальный")
                # Продолжаем с оригинальным промптом
        
        # Генерируем обои
        wallpaper_buffer = self.generate_wallpaper_with_pollinations(working_prompt, device_type)
        
        # Оптимизируем для обоев
        optimized_buffer = self.optimize_for_wallpaper(wallpaper_buffer, device_type)
        
        return optimized_buffer, working_prompt, detected_char
    
    def get_device_info(self, device_type: str) -> dict:
        """Получить информацию об устройстве"""
        return self.wallpaper_presets.get(device_type, self.wallpaper_presets['android'])
    
    def get_available_devices(self) -> list:
        """Получить список доступных типов устройств"""
        return list(self.wallpaper_presets.keys())
    
    def get_wallpaper_suggestions(self) -> list:
        """Получить список предложений для обоев"""
        return [
            "минималистичный градиент",
            "абстрактные геометрические фигуры",
            "природа и пейзажи",
            "космос и звезды",
            "городской пейзаж",
            "цветочные узоры",
            "киберпанк неон",
            "водные волны",
            "горы и закат",
            "фрактальные узоры",
            "темная тема",
            "светлая тема",
            "пастельные тона",
            "яркие цвета",
            "черно-белое фото"
        ]


def validate_wallpaper_prompt(prompt: str) -> bool:
    """
    Проверить промпт обоев на допустимость
    
    Args:
        prompt: Промпт для проверки
        
    Returns:
        True если промпт допустим
    """
    if not validate_prompt(prompt):
        return False
    
    # Дополнительные проверки для обоев
    forbidden_words = ["nsfw", "nude", "naked", "explicit", "adult"]
    prompt_lower = prompt.lower()
    
    for word in forbidden_words:
        if word in prompt_lower:
            return False
    
    return True


if __name__ == "__main__":
    # Тестирование
    generator = WallpaperGenerator()
    print(f"Доступные устройства: {generator.get_available_devices()}")
    print(f"Предложения обоев: {generator.get_wallpaper_suggestions()}")
