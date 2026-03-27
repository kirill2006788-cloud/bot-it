#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Image Generator Module
Поддержка нескольких API для генерации изображений
"""

import base64
import json
import logging
import os
import subprocess
import tempfile
import time
import urllib.parse
from io import BytesIO

import requests
from config import (
    DALLE_MODEL,
    DALLE_QUALITY,
    DALLE_SIZE,
    FOOOCUS_PATH,
    IMAGE_GENERATION_API,
    KANDINSKY_API_KEY,
    KANDINSKY_API_URL,
    KANDINSKY_SECRET_KEY,
    LOCAL_IMAGE_API_URL,
    MAX_IMAGE_PROMPT_LENGTH,
    OPENAI_API_KEY,
)
from characters_database import CHARACTERS, STYLES, QUALITY

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Класс для генерации изображений через различные AI API"""
    
    def __init__(self):
        self.api_type = IMAGE_GENERATION_API
        self.openai_api_key = OPENAI_API_KEY
        self.user_settings = {}  # Настройки пользователей
        
        # Используем общую HTTP-сессию, чтобы переиспользовать соединения
        self.session = requests.Session()
        
        # Варианты Pollinations URL (используются как запасной провайдер)
        self.pollinations_urls = [
            "https://image.pollinations.ai/prompt/{prompt}",
            "https://pollinations.ai/prompt/{prompt}",
            "https://pollinations.ai/p/{prompt}",
        ]
        
        # Инициализируем клиента Kandinsky, если настроены ключи
        self.kandinsky_client = None
        if (
            KANDINSKY_API_KEY
            and KANDINSKY_SECRET_KEY
            and KANDINSKY_API_KEY != "your_kandinsky_api_key_here"
            and KANDINSKY_SECRET_KEY != "your_kandinsky_secret_here"
        ):
            self.kandinsky_client = KandinskyClient(
                base_url=KANDINSKY_API_URL,
                api_key=KANDINSKY_API_KEY,
                secret_key=KANDINSKY_SECRET_KEY,
                session=self.session,
            )

    def _fooocus_env_python(self) -> str:
        if not FOOOCUS_PATH:
            return ""
        py = os.path.join(FOOOCUS_PATH, "fooocus_env", "Scripts", "python.exe")
        return py if os.path.isfile(py) else ""

    def _extract_paths(self, obj) -> list[str]:
        out: list[str] = []
        if obj is None:
            return out
        if isinstance(obj, str):
            if os.path.isfile(obj):
                out.append(obj)
            return out
        if isinstance(obj, dict):
            name = obj.get("name") or obj.get("path")
            if isinstance(name, str) and os.path.isfile(name):
                out.append(name)
            if "value" in obj:
                out.extend(self._extract_paths(obj.get("value")))
            return out
        if isinstance(obj, (list, tuple)):
            for x in obj:
                out.extend(self._extract_paths(x))
        return out

    def generate_with_fooocus(self, prompt: str) -> BytesIO:
        """Локальная генерация через Fooocus Gradio API."""
        url = (LOCAL_IMAGE_API_URL or "").rstrip("/")
        if not url:
            raise ValueError("LOCAL_IMAGE_API_URL не задан.")

        # 1) Предпочитаем совместимый helper через fooocus_env Python (обходит heartbeat/ws баги).
        py = self._fooocus_env_python()
        if not py:
            raise RuntimeError(
                "Не найден fooocus_env python.exe. Укажите FOOOCUS_PATH до папки Fooocus-2.5.5."
            )
        if py:
            helper_code = r"""
import json, os, sys
import requests
from gradio_client import Client

url = sys.argv[1].rstrip("/")
prompt = sys.argv[2]

cfg = requests.get(f"{url}/config", timeout=30).json()
dep = (cfg.get("dependencies") or [])[67]
comp_map = {c.get("id"): c for c in (cfg.get("components") or [])}
values = []
for cid in dep.get("inputs") or []:
    comp = comp_map.get(cid) or {}
    if comp.get("type") == "state":
        continue
    props = comp.get("props") or {}
    v = props.get("value")
    if len(values) == 1:
        v = prompt
    if props.get("label") == "Image Number":
        v = 1
    values.append(v)

def extract_paths(obj):
    out = []
    if obj is None:
        return out
    if isinstance(obj, str):
        if os.path.isfile(obj):
            out.append(obj)
        return out
    if isinstance(obj, dict):
        name = obj.get("name") or obj.get("path")
        if isinstance(name, str) and os.path.isfile(name):
            out.append(name)
        if "value" in obj:
            out.extend(extract_paths(obj.get("value")))
        return out
    if isinstance(obj, (list, tuple)):
        for x in obj:
            out.extend(extract_paths(x))
    return out

try:
    try:
        client = Client(url, serialize=False, verbose=False)
    except TypeError:
        try:
            client = Client(url, verbose=False)
        except TypeError:
            client = Client(url)
    client.predict(*values, fn_index=67)
    result = client.predict(fn_index=68)
    print(json.dumps({"ok": True, "paths": extract_paths(result)}, ensure_ascii=False))
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
"""
            temp_path = ""
            try:
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix="_fooocus_helper.py", delete=False) as tmp:
                    tmp.write(helper_code)
                    temp_path = tmp.name
                proc = subprocess.run(
                    [py, temp_path, url, prompt],
                    capture_output=True,
                    text=True,
                    timeout=240,
                    cwd=FOOOCUS_PATH or None,
                )
                out = (proc.stdout or "").strip()
                if out:
                    payload = json.loads(out.splitlines()[-1])
                    if payload.get("ok"):
                        paths = payload.get("paths") or []
                        if paths:
                            with open(paths[0], "rb") as f:
                                return BytesIO(f.read())
            except Exception as e:
                logger.warning(f"Fooocus helper fallback failed: {e}")
            finally:
                if temp_path:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass

        raise RuntimeError(
            "Fooocus helper не вернул результат. Проверьте, что Fooocus полностью загружен и FOOOCUS_PATH указан верно."
        )
        
    def enhance_prompt_with_claude(self, user_prompt: str, claude_helper) -> str:
        """
        Улучшить промпт пользователя через Claude для лучших результатов
        
        Args:
            user_prompt: Оригинальный промпт пользователя
            claude_helper: Экземпляр ClaudeHelper
            
        Returns:
            Улучшенный промпт на английском
        """
        enhancement_request = f"""Преобразуй этот промпт для генерации изображения в детальное и профессиональное описание на английском языке.
        
Оригинальный промпт: "{user_prompt}"

КРИТИЧЕСКИ ВАЖНО:
- ОБЯЗАТЕЛЬНО сохрани ВСЕ ключевые элементы из оригинального промпта (животные, предметы, персонажи, действия)
- НЕ заменяй и НЕ удаляй основные объекты из промпта
- НЕ добавляй новые объекты, которых нет в оригинале

Правила:
1. Переведи на английский если нужно
2. Сохрани ВСЕ ключевые слова из оригинала (животные, предметы, действия, стили)
3. Добавь детали: стиль, освещение, композицию, атмосферу, но НЕ меняй основной объект
4. Используй художественные термины
5. Сделай промпт максимально визуальным и конкретным
6. Длина: 50-100 слов
7. НЕ добавляй объяснения, только сам улучшенный промпт

Примеры:
Вход: "кот программист"
Выход: "A professional cat wearing glasses and a hoodie, typing on a modern laptop keyboard, sitting at a sleek desk with dual monitors, soft blue ambient lighting, cozy home office setup, digital art style, detailed fur texture, warm atmosphere, 4k quality, cinematic composition"

Вход: "миленький слоненок на закате в стиле аниме"
Выход: "A cute little elephant standing on a hill at sunset, anime style, warm orange and pink sky, soft lighting, detailed anime art, kawaii aesthetic, peaceful atmosphere, high quality, vibrant colors"

Твой улучшенный промпт:"""
        
        try:
            enhanced = claude_helper.ask_question(enhancement_request)
            # Убираем лишние кавычки и переносы строк
            enhanced = enhanced.strip().strip('"').strip("'").replace('\n', ' ')
            logger.info(f"Enhanced prompt: {enhanced}")
            return enhanced
        except Exception as e:
            logger.error(f"Ошибка улучшения промпта: {e}")
            return user_prompt  # Возвращаем оригинальный если не получилось
    
    def generate_with_openai(self, prompt: str) -> BytesIO:
        """
        Генерация изображения через OpenAI DALL-E API
        
        Args:
            prompt: Текстовое описание изображения
            
        Returns:
            BytesIO объект с изображением
        """
        if not self.openai_api_key or self.openai_api_key == "your_openai_api_key_here":
            raise ValueError("OpenAI API ключ не настроен! Установите OPENAI_API_KEY в config.py")
        
        url = "https://api.openai.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": DALLE_MODEL,
            "prompt": prompt,
            "n": 1,
            "size": DALLE_SIZE,
            "quality": DALLE_QUALITY,
            "response_format": "url"
        }
        
        try:
            logger.info(f"Generating image with OpenAI DALL-E: {prompt}")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Скачиваем изображение
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            return BytesIO(image_response.content)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при генерации изображения через OpenAI: {e}")
            raise Exception(f"Ошибка генерации: {str(e)}")
    
    def generate_with_stability(self, prompt: str, api_key: str) -> BytesIO:
        """
        Генерация изображения через Stability AI (Stable Diffusion)
        
        Args:
            prompt: Текстовое описание изображения
            api_key: API ключ Stability AI
            
        Returns:
            BytesIO объект с изображением
        """
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }
        
        try:
            logger.info(f"Generating image with Stability AI: {prompt}")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # Stability AI возвращает base64
            import base64
            image_data = base64.b64decode(result['artifacts'][0]['base64'])
            
            return BytesIO(image_data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при генерации изображения через Stability AI: {e}")
            raise Exception(f"Ошибка генерации: {str(e)}")
    
    def generate_with_pollinations(self, prompt: str) -> BytesIO:
        """
        Запасной бесплатный провайдер Pollinations.ai
        """
        encoded_prompt = urllib.parse.quote(prompt)
        params_variations = [
            {"width": 1024, "height": 1024, "nologo": "true", "enhance": "true"},
            {"width": 1024, "height": 1024, "nologo": "true", "enhance": "false"},
            {"width": 1024, "height": 1024, "nologo": "true", "model": "flux"},
            {"width": 1024, "height": 1024},
        ]
        
        last_error = None
        for base_url in self.pollinations_urls:
            url = base_url.format(prompt=encoded_prompt)
            for params in params_variations:
                try:
                    logger.info(f"Pollinations request: {url} params={params}")
                    response = self.session.get(url, params=params, timeout=45)
                    response.raise_for_status()
                    
                    content_type = response.headers.get("content-type", "")
                    if "image" not in content_type:
                        logger.warning(f"Pollinations ответил не изображением ({content_type})")
                        continue
                    
                    return BytesIO(response.content)
                except requests.exceptions.RequestException as e:
                    last_error = e
                    logger.warning(f"Pollinations attempt failed ({url}): {e}")
                    time.sleep(1)
                    continue
        
        error_message = "Pollinations.ai недоступен. Попробуйте позже или используйте другой провайдер."
        if last_error:
            error_message += f"\nТехническая информация: {last_error}"
        raise Exception(error_message)
    
    def generate_image(self, prompt: str, enhance_with_claude=None) -> tuple[BytesIO, str]:
        """
        Основной метод генерации изображения
        
        Args:
            prompt: Описание изображения
            enhance_with_claude: ClaudeHelper для улучшения промпта (опционально)
            
        Returns:
            Tuple (BytesIO с изображением, итоговый промпт)
        """
        # Проверяем длину промпта
        if len(prompt) > MAX_IMAGE_PROMPT_LENGTH:
            raise ValueError(f"Промпт слишком длинный! Максимум {MAX_IMAGE_PROMPT_LENGTH} символов.")
        
        # Улучшаем промпт через Claude если доступно
        final_prompt = prompt
        if enhance_with_claude:
            try:
                final_prompt = self.enhance_prompt_with_claude(prompt, enhance_with_claude)
            except Exception as e:
                logger.warning(f"Не удалось улучшить промпт через Claude: {e}")
                final_prompt = prompt
        
        # Генерируем изображение
        image = self._generate_by_provider(final_prompt)

        return image, final_prompt
    
    def detect_character(self, prompt: str) -> tuple:
        """Определить и заменить персонажа в промпте"""
        prompt_lower = prompt.lower()
        for char_key, char_desc in CHARACTERS.items():
            if char_key in prompt_lower:
                new_prompt = prompt_lower.replace(char_key, char_desc)
                logger.info(f"Detected character: {char_key}")
                return new_prompt, char_key
        return prompt, None
    
    def apply_style(self, prompt: str, style_key: str) -> str:
        """Применить стиль к промпту"""
        if style_key and style_key in STYLES:
            style_desc = STYLES[style_key].split('|')[1]
            return f"{prompt}, {style_desc}"
        return prompt
    
    def set_user_style(self, user_id: int, style: str):
        """Установить стиль для пользователя"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}
        self.user_settings[user_id]['style'] = style
    
    def set_user_quality(self, user_id: int, quality: str):
        """Установить качество для пользователя"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}
        self.user_settings[user_id]['quality'] = quality

    def set_user_model(self, user_id: int, model_key: str):
        """Установить модель/провайдер генерации для пользователя."""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}
        self.user_settings[user_id]['model'] = model_key

    def get_user_model(self, user_id: int) -> str:
        """Получить текущую модель пользователя."""
        data = self.user_settings.get(user_id, {})
        return data.get('model') or self.api_type
    
    def get_user_settings(self, user_id: int) -> dict:
        """Получить настройки пользователя"""
        return self.user_settings.get(user_id, {'style': None, 'quality': 'normal'})
    
    def generate_with_settings(self, prompt: str, user_id: int, enhance_with_claude=None) -> tuple:
        """Генерация с учётом настроек пользователя"""
        settings = self.get_user_settings(user_id)
        style_value = settings.get('style') if isinstance(settings, dict) else None
        
        # Определяем персонажа
        working_prompt, detected_char = self.detect_character(prompt)
        
        # Применяем стиль
        if style_value:
            working_prompt = self.apply_style(working_prompt, style_value)
        
        # Улучшаем через Claude если доступно (всегда, не только если нет персонажа)
        if enhance_with_claude and self.api_type != "fooocus":
            try:
                logger.info(f"Улучшаю промпт через Claude: {working_prompt[:50]}...")
                working_prompt = self.enhance_prompt_with_claude(working_prompt, enhance_with_claude)
                if working_prompt.lower().startswith("ошибка при обращении к claude api"):
                    logger.warning("Claude вернул ошибку как текст, используем исходный промпт.")
                    working_prompt = prompt
                logger.info(f"Улучшенный промпт: {working_prompt[:100]}...")
            except Exception as e:
                logger.warning(f"Не удалось улучшить промпт через Claude: {e}, используем оригинальный")
                # Продолжаем с оригинальным промптом
        
        # Генерируем
        image = self._generate_by_provider(
            working_prompt,
            style=settings.get('style') if isinstance(settings, dict) else None,
            provider_key=self.get_user_model(user_id),
        )
        
        return image, working_prompt, detected_char

    def _generate_by_provider(
        self,
        prompt: str,
        style: str | None = None,
        provider_key: str | None = None,
    ) -> BytesIO:
        """
        Вспомогательный метод выбора провайдера генерации
        """
        provider = (provider_key or self.api_type or "fooocus").strip().lower()
        try:
            if provider == "fooocus":
                return self.generate_with_fooocus(prompt)
            if provider == "openai":
                logger.warning("OpenAI провайдер отключен. Используем Kandinsky.")
            return self.generate_with_kandinsky(prompt, style=style)
        except Exception as primary_error:
            if provider == "fooocus":
                raise RuntimeError(f"Fooocus ошибка: {primary_error}") from primary_error
            logger.warning(f"Основной провайдер не доступен ({primary_error}). Пробуем Pollinations.")
            return self.generate_with_pollinations(prompt)

    def generate_with_kandinsky(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style: str | None = None,
        negative_prompt: str | None = None
    ) -> BytesIO:
        """Генерация изображения через Kandinsky / FusionBrain"""
        if not self.kandinsky_client:
            raise ValueError("Kandinsky API не настроен. Укажите ключи в config.py")
        
        return self.kandinsky_client.generate(
            prompt=prompt,
            width=width,
            height=height,
            style=style,
            negative_prompt=negative_prompt
        )
    
    def get_available_styles(self) -> list:
        """Получить список доступных художественных стилей"""
        return [
            "realistic photo", "digital art", "oil painting", "watercolor",
            "anime style", "cartoon", "3D render", "cyberpunk",
            "steampunk", "fantasy art", "minimalist", "abstract",
            "pixel art", "comic book", "sketch", "cinematic"
        ]
    
    def add_style_to_prompt(self, prompt: str, style: str) -> str:
        """Добавить стиль к промпту"""
        return f"{prompt}, {style} style, high quality, detailed"


# --- Kandinsky client -------------------------------------------------------

class KandinskyClient:
    """Клиент для работы с FusionBrain / Kandinsky API"""

    def __init__(self, base_url: str, api_key: str, secret_key: str, session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/") + "/"
        self.session = session or requests.Session()
        self.headers = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        }
        self.pipeline_id: str | None = None

    def ensure_pipeline(self) -> str:
        if self.pipeline_id:
            return self.pipeline_id

        response = self.session.get(self.base_url + "key/api/v1/pipelines", headers=self.headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise RuntimeError("Kandinsky API не вернул список моделей")

        pipeline = next((item for item in data if item.get("status") == "ACTIVE"), data[0])
        self.pipeline_id = pipeline.get("id") or pipeline.get("uuid")
        if not self.pipeline_id:
            raise RuntimeError("Не удалось определить pipeline_id Kandinsky")

        return self.pipeline_id

    def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style: str | None = None,
        negative_prompt: str | None = None,
    ) -> BytesIO:
        pipeline_id = self.ensure_pipeline()

        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt,
            },
        }
        if style:
            params["style"] = style
        if negative_prompt:
            params["negativePromptDecoder"] = negative_prompt

        files = {
            "pipeline_id": (None, pipeline_id),
            "params": (None, json.dumps(params), "application/json"),
        }

        response = self.session.post(
            self.base_url + "key/api/v1/pipeline/run",
            headers=self.headers,
            files=files,
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        request_id = payload.get("uuid")
        if not request_id:
            raise RuntimeError(f"Kandinsky не вернул uuid задачи: {payload}")

        return self._wait_for_result(request_id)

    def _wait_for_result(self, request_id: str, attempts: int = 30, delay: int = 4) -> BytesIO:
        status_url = self.base_url + f"key/api/v1/pipeline/status/{request_id}"

        while attempts > 0:
            resp = self.session.get(status_url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status")

            if status == "DONE":
                files = data.get("result", {}).get("files") or []
                if not files:
                    raise RuntimeError("Kandinsky вернул пустой результат")
                image_data = base64.b64decode(files[0])
                return BytesIO(image_data)

            if status == "FAIL":
                error_description = data.get("errorDescription") or "Kandinsky вернул статус FAIL"
                raise RuntimeError(error_description)

            time.sleep(delay)
            attempts -= 1

        raise TimeoutError("Превышено время ожидания ответа Kandinsky")


# Вспомогательные функции

def validate_prompt(prompt: str) -> bool:
    """
    Проверить промпт на допустимость
    
    Args:
        prompt: Промпт для проверки
        
    Returns:
        True если промпт допустим
    """
    if not prompt or not prompt.strip():
        return False
    
    if len(prompt) > MAX_IMAGE_PROMPT_LENGTH:
        return False
    
    return True


if __name__ == "__main__":
    # Тестирование
    generator = ImageGenerator()
    print(f"Используемый API: {generator.api_type}")
    print(f"Доступные стили: {generator.get_available_styles()}")

