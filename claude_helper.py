import anthropic
import requests
import os
import zipfile
import base64
from io import BytesIO
from config import (
    AI_PROVIDER,
    CLAUDE_API_KEY,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
)

class ClaudeHelper:
    """Класс для работы с Claude API от Anthropic"""
    
    def __init__(self):
        self.provider = (AI_PROVIDER or "claude").strip().lower()
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None
        self.model = "claude-3-7-sonnet-20250219"
        self.deepseek_api_key = DEEPSEEK_API_KEY
        self.deepseek_model = DEEPSEEK_MODEL or "deepseek-chat"
        self.deepseek_base_url = (DEEPSEEK_BASE_URL or "https://api.deepseek.com").rstrip("/")

    def _ask_deepseek(self, question: str, max_tokens: int = 4096, system_prompt: str = None) -> str:
        if not self.deepseek_api_key:
            raise RuntimeError("DEEPSEEK_API_KEY не задан.")
        if system_prompt is None:
            system_prompt = """Ты дружелюбный AI-ассистент.
Адаптируй длину ответа под запрос:
- если приветствие, small talk или простой вопрос: 1-3 коротких предложения;
- если запрос про код, настройку, инструкцию, сравнение или разбор ошибки: дай подробный и структурный ответ.
Пиши простым текстом без markdown-оформления (без # и *).
Не делай лишне длинные вступления."""
        url = f"{self.deepseek_base_url}/chat/completions"
        payload = {
            "model": self.deepseek_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"DeepSeek вернул пустой ответ: {data}")
        content = ((choices[0] or {}).get("message") or {}).get("content")
        if not content:
            raise RuntimeError(f"DeepSeek вернул ответ без текста: {data}")
        return content
    
    def ask_question(self, question: str, max_tokens: int = 4096, system_prompt: str = None) -> str:
        """
        Задать вопрос Claude и получить ответ
        
        Args:
            question: Вопрос или задача для Claude
            max_tokens: Максимальное количество токенов в ответе
            system_prompt: Системный промпт для настройки поведения
            
        Returns:
            Ответ от Claude
        """
        try:
            if self.provider == "deepseek":
                return self._ask_deepseek(question, max_tokens=max_tokens, system_prompt=system_prompt)
            # Базовый системный промпт - универсальный ассистент
            if system_prompt is None:
                system_prompt = """Ты дружелюбный AI-ассистент.
Адаптируй длину ответа под запрос:
- если приветствие, small talk или простой вопрос: 1-3 коротких предложения;
- если запрос про код, настройку, инструкцию, сравнение или разбор ошибки: дай подробный и структурный ответ.
Пиши простым текстом без markdown-оформления (без # и *).
Не делай лишне длинные вступления."""
            
            if not self.client:
                raise RuntimeError("CLAUDE_API_KEY не задан.")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Ошибка при обращении к AI API: {str(e)}"
    
    def ask_question_with_image(self, image_bytes: bytes, question: str = "", image_format: str = "jpeg", max_tokens: int = 4096, system_prompt: str = None) -> str:
        """
        Задать вопрос Claude с изображением
        
        Args:
            image_bytes: Байты изображения
            question: Вопрос или задача для Claude (опционально)
            image_format: Формат изображения (jpeg, png, webp, gif)
            max_tokens: Максимальное количество токенов в ответе
            system_prompt: Системный промпт для настройки поведения
            
        Returns:
            Ответ от Claude
        """
        if self.provider == "deepseek":
            return "Анализ изображений доступен только в режиме Claude."
        try:
            # Проверяем, что image_bytes это bytes
            if isinstance(image_bytes, str):
                # Если передана строка, пытаемся декодировать
                image_bytes = image_bytes.encode('utf-8')
            elif not isinstance(image_bytes, bytes):
                # Если не bytes и не str, пытаемся преобразовать
                image_bytes = bytes(image_bytes)
            
            # Определяем media_type
            media_type_map = {
                "jpeg": "image/jpeg",
                "jpg": "image/jpeg",
                "png": "image/png",
                "webp": "image/webp",
                "gif": "image/gif"
            }
            media_type = media_type_map.get(image_format.lower(), "image/jpeg")
            
            # Кодируем изображение в base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Базовый системный промпт
            if system_prompt is None:
                system_prompt = """Ты дружелюбный AI-ассистент с анализом изображений.
Адаптируй длину ответа под запрос:
- простой вопрос: коротко;
- технический или сложный вопрос: подробнее и по шагам.
Пиши простым текстом без markdown-оформления (без # и *)."""
            
            # Формируем контент с изображением и текстом
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_base64
                    }
                }
            ]
            
            # Добавляем текстовый вопрос, если он есть
            if question:
                content.append({
                    "type": "text",
                    "text": question
                })
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Ошибка при обращении к AI API: {str(e)}"
    
    def generate_code(self, language: str, description: str, complexity: str = "medium") -> str:
        """
        Генерировать код на указанном языке программирования
        
        Args:
            language: Язык программирования (python, javascript, java, etc.)
            description: Описание того, что должен делать код
            complexity: Уровень сложности (simple, medium, advanced)
            
        Returns:
            Сгенерированный код
        """
        complexity_instructions = {
            "simple": "Создай простой и понятный код для начинающих.",
            "medium": "Создай хорошо структурированный код с комментариями.",
            "advanced": "Создай профессиональный код с лучшими практиками, обработкой ошибок и документацией."
        }
        
        prompt = f"""Ты опытный программист. {complexity_instructions.get(complexity, complexity_instructions['medium'])}

Язык программирования: {language}
Задача: {description}

Напиши полный рабочий код. Не добавляй лишних объяснений, только код с необходимыми комментариями.
Код должен быть готов к использованию."""

        return self.ask_question(prompt, max_tokens=4096)
    
    def generate_multiple_files(self, project_description: str, languages: list = None) -> dict:
        """
        Генерировать несколько файлов для проекта
        
        Args:
            project_description: Описание проекта
            languages: Список языков программирования для использования
            
        Returns:
            Словарь {имя_файла: содержимое}
        """
        if languages is None:
            languages = ["python"]
        
        prompt = f"""Создай полноценный проект со следующими требованиями:

Описание проекта: {project_description}
Языки программирования: {', '.join(languages)}

Верни структуру проекта в следующем формате:
FILENAME: имя_файла_1
```
код файла 1
```

FILENAME: имя_файла_2
```
код файла 2
```

И так далее для всех необходимых файлов проекта.
Создай минимум 2-3 файла для полноценного проекта."""

        response = self.ask_question(prompt, max_tokens=8000)
        
        # Парсим ответ и извлекаем файлы
        files = {}
        lines = response.split('\n')
        current_filename = None
        current_content = []
        in_code_block = False
        
        for line in lines:
            if line.startswith('FILENAME:'):
                # Сохраняем предыдущий файл
                if current_filename and current_content:
                    files[current_filename] = '\n'.join(current_content)
                # Начинаем новый файл
                current_filename = line.replace('FILENAME:', '').strip()
                current_content = []
                in_code_block = False
            elif line.startswith('```'):
                if in_code_block:
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block and current_filename:
                current_content.append(line)
        
        # Сохраняем последний файл
        if current_filename and current_content:
            files[current_filename] = '\n'.join(current_content)
        
        # Если парсинг не удался, создаем один файл с полным ответом
        if not files:
            files['generated_code.txt'] = response
        
        return files
    
    def create_zip_from_files(self, files: dict) -> BytesIO:
        """
        Создать ZIP-архив из словаря файлов
        
        Args:
            files: Словарь {имя_файла: содержимое}
            
        Returns:
            BytesIO объект с ZIP-архивом
        """
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def explain_code(self, code: str, language: str = None) -> str:
        """
        Объяснить, что делает код
        
        Args:
            code: Код для объяснения
            language: Язык программирования (опционально)
            
        Returns:
            Объяснение кода
        """
        lang_info = f" на языке {language}" if language else ""
        
        prompt = f"""Объясни подробно, что делает этот код{lang_info}:

```
{code}
```

Объясни:
1. Общее назначение кода
2. Что делает каждая важная часть
3. Возможные улучшения или проблемы"""

        return self.ask_question(prompt)
    
    def debug_code(self, code: str, error_message: str = None, language: str = None) -> str:
        """
        Помочь отладить код
        
        Args:
            code: Код с ошибкой
            error_message: Сообщение об ошибке (опционально)
            language: Язык программирования (опционально)
            
        Returns:
            Исправленный код и объяснение
        """
        lang_info = f" на языке {language}" if language else ""
        error_info = f"\n\nСообщение об ошибке:\n{error_message}" if error_message else ""
        
        prompt = f"""Найди и исправь ошибки в этом коде{lang_info}:

```
{code}
```{error_info}

Верни:
1. Исправленный код
2. Объяснение, что было не так
3. Рекомендации для избежания подобных ошибок"""

        return self.ask_question(prompt)
    
    def optimize_code(self, code: str, language: str = None) -> str:
        """
        Оптимизировать код
        
        Args:
            code: Код для оптимизации
            language: Язык программирования (опционально)
            
        Returns:
            Оптимизированный код
        """
        lang_info = f" на языке {language}" if language else ""
        
        prompt = f"""Оптимизируй этот код{lang_info}:

```
{code}
```

Улучши:
1. Производительность
2. Читаемость
3. Следование лучшим практикам

Верни оптимизированный код с комментариями о внесенных изменениях."""

        return self.ask_question(prompt)
