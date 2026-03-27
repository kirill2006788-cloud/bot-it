#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIF Generator - Генерация анимированных мемов
Полностью бесплатно! Использует только Pillow
"""

import logging
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from io import BytesIO
import textwrap

logger = logging.getLogger(__name__)


class GifGenerator:
    """Генератор анимированных GIF мемов"""
    
    def __init__(self):
        self.default_font_size = 40
        self.frame_count = 10
        self.duration = 100  # миллисекунды на кадр
        
    def create_text_gif(self, text: str, bg_color="black", text_color="white", style="wave") -> BytesIO:
        """
        Создать GIF с анимированным текстом
        
        Args:
            text: Текст для анимации
            bg_color: Цвет фона
            text_color: Цвет текста
            style: Стиль анимации (wave, pulse, rainbow, rotate)
        """
        width, height = 400, 200
        frames = []
        
        # Попытка загрузить шрифт
        try:
            font = ImageFont.truetype("arial.ttf", self.default_font_size)
        except:
            font = ImageFont.load_default()
        
        if style == "wave":
            frames = self._create_wave_animation(text, width, height, bg_color, text_color, font)
        elif style == "pulse":
            frames = self._create_pulse_animation(text, width, height, bg_color, text_color, font)
        elif style == "rainbow":
            frames = self._create_rainbow_animation(text, width, height, bg_color, font)
        elif style == "rotate":
            frames = self._create_rotate_animation(text, width, height, bg_color, text_color, font)
        else:
            frames = self._create_wave_animation(text, width, height, bg_color, text_color, font)
        
        # Сохраняем в BytesIO
        output = BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=self.duration,
            loop=0
        )
        output.seek(0)
        
        logger.info(f"GIF generated: {style} style, {len(frames)} frames")
        return output
    
    def _create_wave_animation(self, text, width, height, bg_color, text_color, font):
        """Волновая анимация текста"""
        frames = []
        for i in range(self.frame_count):
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Вычисляем позицию для каждого символа с волной
            x_offset = 50
            y_base = height // 2
            
            for j, char in enumerate(text):
                offset = 20 * ((i + j) % self.frame_count) / self.frame_count
                y_pos = y_base + int(15 * ((i + j * 2) % self.frame_count) / self.frame_count - 7.5)
                
                draw.text((x_offset, y_pos), char, fill=text_color, font=font)
                x_offset += 25
            
            frames.append(img)
        
        return frames
    
    def _create_pulse_animation(self, text, width, height, bg_color, text_color, font):
        """Пульсирующая анимация"""
        frames = []
        for i in range(self.frame_count):
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Изменяем размер текста
            scale = 0.8 + 0.4 * (i / self.frame_count)
            try:
                scaled_font = ImageFont.truetype("arial.ttf", int(self.default_font_size * scale))
            except:
                scaled_font = font
            
            # Центрируем текст
            bbox = draw.textbbox((0, 0), text, font=scaled_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=text_color, font=scaled_font)
            frames.append(img)
        
        return frames
    
    def _create_rainbow_animation(self, text, width, height, bg_color, font):
        """Радужная анимация"""
        frames = []
        colors = [
            (255, 0, 0),    # Красный
            (255, 127, 0),  # Оранжевый
            (255, 255, 0),  # Жёлтый
            (0, 255, 0),    # Зелёный
            (0, 0, 255),    # Синий
            (75, 0, 130),   # Индиго
            (148, 0, 211),  # Фиолетовый
        ]
        
        for i in range(self.frame_count):
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Центрируем текст
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Выбираем цвет из радуги
            color = colors[i % len(colors)]
            draw.text((x, y), text, fill=color, font=font)
            frames.append(img)
        
        return frames
    
    def _create_rotate_animation(self, text, width, height, bg_color, text_color, font):
        """Вращающаяся анимация"""
        frames = []
        
        # Создаем базовое изображение с текстом
        temp_img = Image.new('RGBA', (width * 2, height * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp_img)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width * 2 - text_width) // 2
        y = (height * 2 - text_height) // 2
        draw.text((x, y), text, fill=text_color, font=font)
        
        # Вращаем
        for i in range(self.frame_count):
            angle = (360 / self.frame_count) * i
            rotated = temp_img.rotate(angle, expand=False)
            
            # Обрезаем до нужного размера
            final = Image.new('RGB', (width, height), bg_color)
            box = ((rotated.width - width) // 2, (rotated.height - height) // 2,
                   (rotated.width + width) // 2, (rotated.height + height) // 2)
            cropped = rotated.crop(box)
            final.paste(cropped, (0, 0), cropped if cropped.mode == 'RGBA' else None)
            
            frames.append(final.convert('RGB'))
        
        return frames
    
    def create_meme_gif(self, top_text: str = "", bottom_text: str = "", bg_type: str = "gradient") -> BytesIO:
        """
        Создать мем GIF с текстом вверху и внизу
        
        Args:
            top_text: Текст вверху
            bottom_text: Текст внизу
            bg_type: Тип фона (gradient, solid, pattern)
        """
        width, height = 500, 400
        frames = []
        
        try:
            font = ImageFont.truetype("arial.ttf", 35)
        except:
            font = ImageFont.load_default()
        
        for i in range(self.frame_count):
            # Создаем фон
            if bg_type == "gradient":
                img = self._create_gradient_bg(width, height, i)
            elif bg_type == "pattern":
                img = self._create_pattern_bg(width, height, i)
            else:
                img = Image.new('RGB', (width, height), (30, 30, 30))
            
            draw = ImageDraw.Draw(img)
            
            # Рисуем текст вверху
            if top_text:
                self._draw_outlined_text(draw, top_text, width, 30, font)
            
            # Рисуем текст внизу
            if bottom_text:
                self._draw_outlined_text(draw, bottom_text, width, height - 80, font)
            
            frames.append(img)
        
        output = BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=self.duration,
            loop=0
        )
        output.seek(0)
        
        logger.info(f"Meme GIF generated with texts: '{top_text}' / '{bottom_text}'")
        return output
    
    def _create_gradient_bg(self, width, height, frame_num):
        """Создать градиентный фон"""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Анимированный градиент
        offset = int((frame_num / self.frame_count) * 255)
        
        for y in range(height):
            r = (100 + offset + y) % 256
            g = (50 + y) % 256
            b = (200 - y) % 256
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return img
    
    def _create_pattern_bg(self, width, height, frame_num):
        """Создать паттерн фон"""
        img = Image.new('RGB', (width, height), (20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        # Анимированные круги
        offset = int((frame_num / self.frame_count) * 50)
        
        for x in range(0, width, 50):
            for y in range(0, height, 50):
                x_pos = (x + offset) % width
                y_pos = (y + offset) % height
                draw.ellipse([x_pos, y_pos, x_pos + 30, y_pos + 30], 
                           fill=(100, 100, 200), outline=(150, 150, 255))
        
        return img
    
    def _draw_outlined_text(self, draw, text, width, y_pos, font):
        """Нарисовать текст с обводкой"""
        # Разбиваем длинный текст
        wrapped_text = textwrap.fill(text, width=20)
        
        for line in wrapped_text.split('\n'):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Обводка (чёрная)
            for offset_x in [-2, -1, 0, 1, 2]:
                for offset_y in [-2, -1, 0, 1, 2]:
                    if offset_x != 0 or offset_y != 0:
                        draw.text((x + offset_x, y_pos + offset_y), line, 
                                font=font, fill=(0, 0, 0))
            
            # Основной текст (белый)
            draw.text((x, y_pos), line, font=font, fill=(255, 255, 255))
            y_pos += 40
    
    def create_thinking_gif(self, text: str = "🤔") -> BytesIO:
        """Создать думающий GIF (популярный мем)"""
        width, height = 300, 300
        frames = []
        
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        for i in range(self.frame_count):
            img = Image.new('RGB', (width, height), (255, 220, 100))
            draw = ImageDraw.Draw(img)
            
            # Анимация масштаба и поворота
            scale = 1.0 + 0.1 * (i / self.frame_count)
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = int((width - text_width * scale) // 2)
            y = int((height - text_height * scale) // 2)
            
            draw.text((x, y), text, fill=(50, 50, 50), font=font)
            frames.append(img)
        
        output = BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=150,
            loop=0
        )
        output.seek(0)
        
        return output


# Вспомогательные функции для быстрого использования
def quick_text_gif(text: str, style: str = "wave") -> BytesIO:
    """Быстрая генерация текстового GIF"""
    gen = GifGenerator()
    return gen.create_text_gif(text, style=style)


def quick_meme_gif(top: str = "", bottom: str = "") -> BytesIO:
    """Быстрая генерация мема"""
    gen = GifGenerator()
    return gen.create_meme_gif(top, bottom)

