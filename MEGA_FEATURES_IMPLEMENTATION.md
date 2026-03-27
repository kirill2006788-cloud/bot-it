# 🚀 План реализации мега-фич бота

## 📋 Содержание
1. [UI Builder из Скриншотов](#1-ui-builder-из-скриншотов)
2. [AI Code Memory Bank](#2-ai-code-memory-bank)
3. [AI Pair Programmer](#3-ai-pair-programmer)

---

## 1. UI Builder из Скриншотов

### 🎯 Описание
Пользователь отправляет скриншот интерфейса → бот анализирует изображение → генерирует готовый код (React, Vue, Angular, HTML/CSS)

### 📦 Необходимые зависимости

```python
# Для обработки изображений и OCR
Pillow>=10.0.0          # Обработка изображений
opencv-python>=4.8.0    # Анализ изображений
pytesseract>=0.3.10     # OCR для текста
easyocr>=1.7.0          # Улучшенный OCR (опционально)

# Для AI анализа изображений
openai>=1.0.0           # GPT-4 Vision API
anthropic>=0.7.0        # Claude 3 Vision (если доступно)

# Для генерации кода
black>=23.0.0           # Форматирование Python
jsbeautifier>=1.14.0    # Форматирование JS/CSS
```

### 🔑 API ключи и сервисы

1. **OpenAI GPT-4 Vision API** (основной)
   - API ключ: `OPENAI_API_KEY` (уже есть в `api_keys.py`)
   - Endpoint: `https://api.openai.com/v1/chat/completions`
   - Модель: `gpt-4-vision-preview` или `gpt-4-turbo`

2. **Claude 3 Vision** (альтернатива/дополнение)
   - API ключ: `ANTHROPIC_API_KEY` (если доступно)
   - Модель: `claude-3-opus-20240229` с vision capabilities

3. **Google Cloud Vision API** (опционально, для детального анализа)
   - Service account JSON
   - Библиотека: `google-cloud-vision`

### 🏗️ Архитектура решения

```
1. Пользователь отправляет фото → Telegram получает File
2. Бот скачивает изображение
3. Предобработка изображения:
   - Ресайз для оптимизации (если слишком большое)
   - Улучшение контраста/яркости
   - Обрезка лишнего (опционально)
4. Анализ изображения через GPT-4 Vision:
   - Описание элементов UI
   - Расположение компонентов
   - Цвета, шрифты, отступы
   - Типы элементов (кнопки, формы, карточки)
5. Генерация структуры компонентов через Claude:
   - HTML структура
   - CSS стили
   - JavaScript логика (если нужно)
   - React/Vue компоненты (если указан фреймворк)
6. Форматирование и оптимизация кода
7. Отправка результата пользователю
```

### 📁 Структура файлов

```
ui_builder.py              # Основной модуль
ui_analyzer.py             # Анализ изображений
code_generator.py          # Генерация кода
image_processor.py         # Обработка изображений
frameworks/
    react_generator.py     # React компоненты
    vue_generator.py       # Vue компоненты
    html_generator.py      # Чистый HTML/CSS
```

### 🛠️ Реализация

#### Шаг 1: Создать `ui_builder.py`

```python
import io
import base64
from PIL import Image
import openai
from claude_helper import ClaudeHelper
from telegram import Update
from telegram.ext import ContextTypes

class UIBuilder:
    def __init__(self):
        self.claude = ClaudeHelper()
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def analyze_image(self, image_path: str) -> dict:
        """Анализ изображения через GPT-4 Vision"""
        with open(image_path, 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Проанализируй это UI изображение и верни JSON с описанием:
{
  "elements": [
    {
      "type": "button|input|card|text|image|etc",
      "position": {"x": 0, "y": 0, "width": 100, "height": 50},
      "properties": {
        "text": "...",
        "color": "#...",
        "fontSize": "...",
        "backgroundColor": "#...",
        "borderRadius": "..."
      }
    }
  ],
  "layout": "flex|grid|absolute",
  "colors": ["#...", "#..."],
  "typography": {
    "fonts": ["..."],
    "sizes": ["..."]
  },
  "spacing": {
    "padding": "...",
    "margin": "...",
    "gap": "..."
  }
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def generate_code(self, ui_analysis: dict, framework: str = "html") -> str:
        """Генерация кода на основе анализа"""
        
        prompt = f"""На основе этого анализа UI создай готовый код для {framework}.

Анализ UI:
{json.dumps(ui_analysis, indent=2, ensure_ascii=False)}

Требования:
1. Полностью рабочий код, готовый к использованию
2. Используй современные CSS (Flexbox/Grid)
3. Адаптивный дизайн (mobile-first)
4. Семантический HTML
5. Если {framework} == "react": используй функциональные компоненты и hooks
6. Если {framework} == "vue": используй Composition API
7. Красивые анимации и переходы
8. Комментарии в коде

Верни только код, без объяснений."""
        
        code = await self.claude.ask(prompt)
        return self.format_code(code, framework)
    
    def format_code(self, code: str, framework: str) -> str:
        """Форматирование кода"""
        if framework == "html":
            import jsbeautifier
            return jsbeautifier.beautify(code)
        elif framework in ["react", "vue", "js"]:
            # Использовать prettier или jsbeautifier
            import jsbeautifier
            return jsbeautifier.beautify(code)
        return code
```

#### Шаг 2: Добавить команды в `bot.py`

```python
from ui_builder import UIBuilder

# В __init__:
self.ui_builder = UIBuilder()

# Обработчик команды:
async def ui_from_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /uibuild"""
    if not update.message.photo:
        await update.message.reply_text(
            "📸 Отправь скриншот UI, и я создам для тебя код!\n\n"
            "Команды:\n"
            "/uibuild html - HTML/CSS код\n"
            "/uibuild react - React компонент\n"
            "/uibuild vue - Vue компонент"
        )
        return
    
    framework = context.args[0] if context.args else "html"
    if framework not in ["html", "react", "vue"]:
        framework = "html"
    
    await update.message.reply_text("🔄 Анализирую изображение...")
    
    # Скачать фото
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_path = f"temp_ui_{update.effective_user.id}.jpg"
    await file.download_to_drive(image_path)
    
    try:
        # Анализ
        ui_analysis = await self.ui_builder.analyze_image(image_path)
        
        # Генерация кода
        code = await self.ui_builder.generate_code(ui_analysis, framework)
        
        # Отправка результата
        await update.message.reply_text(
            f"✅ Готово! Вот твой {framework.upper()} код:\n\n"
            f"```{framework if framework != 'html' else 'html'}\n{code}\n```",
            parse_mode='Markdown'
        )
        
        # Отправка файла для удобства
        code_file = io.BytesIO(code.encode('utf-8'))
        code_file.name = f"ui_component.{framework if framework != 'html' else 'html'}"
        await update.message.reply_document(code_file)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    finally:
        # Удалить временный файл
        if os.path.exists(image_path):
            os.remove(image_path)
```

### 🎨 Дополнительные улучшения

1. **Множественные скриншоты**: Анализ нескольких экранов для создания полного приложения
2. **Детализация**: Возможность кликнуть на элемент и получить его отдельный код
3. **Стиль-гайд**: Автоматическое создание дизайн-системы из скриншотов
4. **Экспорт в Figma**: Обратный процесс - код → Figma дизайн

---

## 2. AI Code Memory Bank

### 🎯 Описание
Бот запоминает стиль кода, паттерны, библиотеки пользователя и автоматически применяет их в новых проектах.

### 📦 Необходимые зависимости

```python
# База данных для хранения памяти
sqlite3                  # Встроенная в Python
# или
peewee>=3.17.0          # ORM для SQLite (удобнее)
# или
sqlalchemy>=2.0.0       # Более мощная ORM

# Для анализа кода
ast>=0.1                # Парсинг Python кода (встроен)
tree-sitter-python      # Парсинг различных языков
tree-sitter-javascript
tree-sitter-typescript

# Для векторного поиска (если нужно)
sentence-transformers>=2.2.0  # Семантический поиск
numpy>=1.24.0

# Для сжатия и хранения
pickle                  # Встроен
joblib>=1.3.0           # Для больших данных
```

### 🏗️ Архитектура решения

```
1. Анализ кода пользователя:
   - Парсинг структуры (функции, классы, импорты)
   - Извлечение паттернов (naming conventions, структура)
   - Анализ используемых библиотек
   - Стиль форматирования

2. Сохранение в базу данных:
   - User ID → Style Profile
   - Кэширование часто используемых паттернов
   - Версионирование стилей (эволюция)

3. Применение при генерации:
   - Поиск похожих паттернов из памяти
   - Автоматическое применение стиля
   - Адаптация под контекст проекта
```

### 📁 Структура файлов

```
code_memory/
    __init__.py
    memory_bank.py          # Основной класс
    code_analyzer.py        # Анализ кода
    style_extractor.py      # Извлечение стиля
    pattern_matcher.py      # Поиск паттернов
    database.py             # Работа с БД
    models.py               # Модели данных
```

### 🗄️ Схема базы данных

```sql
CREATE TABLE user_code_style (
    user_id INTEGER PRIMARY KEY,
    language TEXT NOT NULL,           -- python, javascript, etc
    naming_convention TEXT,           -- snake_case, camelCase, etc
    indentation INTEGER,              -- 2, 4 spaces, tabs
    max_line_length INTEGER,          -- 80, 100, 120
    quote_style TEXT,                 -- single, double
    import_order TEXT,                -- alphabetical, by type
    style_json TEXT,                  -- JSON с деталями стиля
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE code_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    pattern_type TEXT,                -- function, class, import, etc
    pattern_code TEXT,                -- Пример кода
    frequency INTEGER DEFAULT 1,      -- Как часто используется
    language TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_code_style(user_id)
);

CREATE TABLE user_libraries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    language TEXT,
    library_name TEXT,
    frequency INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES user_code_style(user_id)
);

CREATE TABLE code_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    code_hash TEXT,                   -- Для дедупликации
    code_snippet TEXT,
    language TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_code_style(user_id)
);
```

### 🛠️ Реализация

#### Шаг 1: Создать `code_memory/memory_bank.py`

```python
import ast
import sqlite3
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import re

class CodeMemoryBank:
    def __init__(self, db_path: str = "code_memory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создание таблиц
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_code_style (
                user_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL,
                naming_convention TEXT,
                indentation INTEGER,
                max_line_length INTEGER,
                quote_style TEXT,
                import_order TEXT,
                style_json TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pattern_type TEXT,
                pattern_code TEXT,
                frequency INTEGER DEFAULT 1,
                language TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_code_style(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_libraries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                language TEXT,
                library_name TEXT,
                frequency INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES user_code_style(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                code_hash TEXT,
                code_snippet TEXT,
                language TEXT,
                timestamp TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def analyze_code(self, code: str, language: str = "python") -> dict:
        """Анализ кода и извлечение стиля"""
        if language == "python":
            return self._analyze_python(code)
        elif language in ["javascript", "typescript"]:
            return self._analyze_javascript(code)
        else:
            return self._analyze_generic(code, language)
    
    def _analyze_python(self, code: str) -> dict:
        """Анализ Python кода"""
        try:
            tree = ast.parse(code)
        except:
            return {}
        
        style = {
            "naming_convention": self._detect_naming_convention(code),
            "indentation": self._detect_indentation(code),
            "max_line_length": self._detect_max_line_length(code),
            "quote_style": self._detect_quote_style(code),
            "import_order": self._detect_import_order(tree),
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                style["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [ast.unparse(d) for d in node.decorator_list]
                })
            elif isinstance(node, ast.ClassDef):
                style["classes"].append({
                    "name": node.name,
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    style["imports"].append(node.module)
        
        return style
    
    def _detect_naming_convention(self, code: str) -> str:
        """Определение стиля именования"""
        if re.search(r'\b[a-z][a-z0-9_]*\b', code):
            return "snake_case"
        elif re.search(r'\b[a-z][a-zA-Z0-9]*\b', code):
            return "camelCase"
        elif re.search(r'\b[A-Z][a-zA-Z0-9]*\b', code):
            return "PascalCase"
        return "mixed"
    
    def _detect_indentation(self, code: str) -> int:
        """Определение отступов"""
        lines = [l for l in code.split('\n') if l.strip() and l[0] in ' \t']
        if not lines:
            return 4
        
        spaces = sum(len(l) - len(l.lstrip(' ')) for l in lines if l[0] == ' ')
        tabs = sum(1 for l in lines if l[0] == '\t')
        
        if tabs > spaces:
            return None  # Tabs
        if spaces > 0:
            return spaces // len(lines) if lines else 4
        return 4
    
    def _detect_max_line_length(self, code: str) -> int:
        """Определение максимальной длины строки"""
        lines = code.split('\n')
        lengths = [len(l) for l in lines]
        if not lengths:
            return 80
        
        max_len = max(lengths)
        # Округление до ближайшего стандарта
        if max_len <= 80:
            return 80
        elif max_len <= 100:
            return 100
        else:
            return 120
    
    def _detect_quote_style(self, code: str) -> str:
        """Определение стиля кавычек"""
        single = code.count("'")
        double = code.count('"')
        return "single" if single > double else "double"
    
    def _detect_import_order(self, tree: ast.AST) -> str:
        """Определение порядка импортов"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        if len(imports) < 2:
            return "alphabetical"
        
        # Простая проверка на алфавитный порядок
        names = []
        for imp in imports:
            if isinstance(imp, ast.Import):
                names.extend([a.name for a in imp.names])
            else:
                names.append(imp.module or "")
        
        sorted_names = sorted(names)
        return "alphabetical" if names == sorted_names else "by_type"
    
    def _analyze_javascript(self, code: str) -> dict:
        """Анализ JavaScript/TypeScript кода"""
        # Похожая логика, но для JS
        return {
            "naming_convention": self._detect_naming_convention(code),
            "indentation": self._detect_indentation(code),
            "quote_style": self._detect_quote_style(code),
            "semicolons": ";" in code[:100],  # Простая проверка
            "arrow_functions": "=>" in code,
            "const_let": "const" in code or "let" in code
        }
    
    def _analyze_generic(self, code: str, language: str) -> dict:
        """Общий анализ для других языков"""
        return {
            "language": language,
            "naming_convention": self._detect_naming_convention(code),
            "indentation": self._detect_indentation(code)
        }
    
    def save_code_style(self, user_id: int, code: str, language: str):
        """Сохранение стиля кода пользователя"""
        style = self.analyze_code(code, language)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        style_json = json.dumps(style, ensure_ascii=False)
        now = datetime.now().isoformat()
        
        # Проверка существующей записи
        cursor.execute("SELECT user_id FROM user_code_style WHERE user_id = ? AND language = ?",
                      (user_id, language))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("""
                UPDATE user_code_style 
                SET style_json = ?, updated_at = ?
                WHERE user_id = ? AND language = ?
            """, (style_json, now, user_id, language))
        else:
            cursor.execute("""
                INSERT INTO user_code_style 
                (user_id, language, style_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, language, style_json, now, now))
        
        # Сохранение паттернов
        self._save_patterns(cursor, user_id, code, language, style)
        
        # Сохранение истории
        code_hash = hashlib.md5(code.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO code_history (user_id, code_hash, code_snippet, language, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, code_hash, code[:500], language, now))
        
        conn.commit()
        conn.close()
    
    def _save_patterns(self, cursor, user_id: int, code: str, language: str, style: dict):
        """Сохранение паттернов кода"""
        # Функции
        for func in style.get("functions", []):
            pattern_code = f"def {func['name']}({', '.join(func['args'])}):"
            cursor.execute("""
                INSERT OR IGNORE INTO code_patterns 
                (user_id, pattern_type, pattern_code, frequency, language)
                VALUES (?, ?, ?, 1, ?)
            """, (user_id, "function", pattern_code, language))
            
            cursor.execute("""
                UPDATE code_patterns 
                SET frequency = frequency + 1
                WHERE user_id = ? AND pattern_code = ?
            """, (user_id, pattern_code))
    
    def get_user_style(self, user_id: int, language: str) -> Optional[dict]:
        """Получение стиля пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT style_json FROM user_code_style
            WHERE user_id = ? AND language = ?
        """, (user_id, language))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_frequent_patterns(self, user_id: int, language: str, limit: int = 10) -> List[dict]:
        """Получение частых паттернов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_type, pattern_code, frequency
            FROM code_patterns
            WHERE user_id = ? AND language = ?
            ORDER BY frequency DESC
            LIMIT ?
        """, (user_id, language, limit))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "type": row[0],
                "code": row[1],
                "frequency": row[2]
            })
        
        conn.close()
        return patterns
    
    def apply_style_to_code(self, user_id: int, generated_code: str, language: str) -> str:
        """Применение стиля пользователя к сгенерированному коду"""
        style = self.get_user_style(user_id, language)
        if not style:
            return generated_code
        
        # Применение стиля
        code = generated_code
        
        # Замена кавычек
        if style.get("quote_style") == "single":
            code = code.replace('"', "'")
        elif style.get("quote_style") == "double":
            code = code.replace("'", '"')
        
        # Форматирование отступов
        indent = style.get("indentation", 4)
        if indent:
            # Простая замена (можно использовать black/formatter)
            lines = code.split('\n')
            formatted_lines = []
            for line in lines:
                if line.strip():
                    # Подсчет текущих отступов и нормализация
                    current_indent = len(line) - len(line.lstrip())
                    normalized_indent = (current_indent // 4) * indent
                    formatted_lines.append(' ' * normalized_indent + line.lstrip())
                else:
                    formatted_lines.append(line)
            code = '\n'.join(formatted_lines)
        
        return code
```

#### Шаг 2: Интеграция в `bot.py`

```python
from code_memory.memory_bank import CodeMemoryBank

# В __init__:
self.code_memory = CodeMemoryBank()

# Команда для сохранения стиля:
async def save_code_style_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранить стиль кода"""
    code = update.message.text.replace("/savestyle", "").strip()
    if not code:
        await update.message.reply_text(
            "💾 Сохранить стиль кода\n\n"
            "Отправь код, стиль которого нужно запомнить:\n"
            "/savestyle python\n"
            "```python\n"
            "def my_function(arg1, arg2):\n"
            "    return arg1 + arg2\n"
            "```"
        )
        return
    
    language = context.args[0] if context.args else "python"
    
    self.code_memory.save_code_style(
        update.effective_user.id,
        code,
        language
    )
    
    await update.message.reply_text(
        f"✅ Стиль кода сохранен для языка: {language}\n"
        "Теперь бот будет использовать твой стиль при генерации кода!"
    )

# Автоматическое применение стиля при генерации:
async def generate_code_with_style(self, user_id: int, prompt: str, language: str) -> str:
    """Генерация кода с применением стиля пользователя"""
    # Генерация через Claude
    code = await self.claude.generate_code(prompt, language)
    
    # Применение стиля
    styled_code = self.code_memory.apply_style_to_code(user_id, code, language)
    
    return styled_code
```

---

## 3. AI Pair Programmer

### 🎯 Описание
Бот работает как живой напарник: видит код в реальном времени, подсказывает решения, объясняет концепции, помогает отлаживать.

### 📦 Необходимые зависимости

```python
# Для анализа кода в реальном времени
tree-sitter>=0.20.0      # Парсинг кода
tree-sitter-python
tree-sitter-javascript

# Для контекстного анализа
openai>=1.0.0            # GPT-4 для анализа
anthropic>=0.7.0         # Claude для объяснений

# Для работы с Git (если нужно отслеживать изменения)
GitPython>=3.1.40

# Для веб-сокетов (real-time обновления, опционально)
websockets>=12.0         # Для live updates
```

### 🏗️ Архитектура решения

```
1. Отслеживание кода:
   - Пользователь отправляет код
   - Бот анализирует структуру
   - Определяет контекст и задачу

2. Активный анализ:
   - Поиск потенциальных проблем
   - Предложение улучшений
   - Объяснение сложных частей
   - Автоматические советы

3. Интерактивный режим:
   - Вопросы о коде
   - Пошаговая отладка
   - Обучение на примерах
   - Code review в реальном времени
```

### 📁 Структура файлов

```
pair_programmer/
    __init__.py
    pair_programmer.py    # Основной класс
    code_analyzer.py      # Анализ кода
    suggestions.py        # Генерация советов
    debug_helper.py       # Помощь в отладке
    explainer.py          # Объяснение концепций
    context_manager.py    # Управление контекстом
```

### 🛠️ Реализация

#### Шаг 1: Создать `pair_programmer/pair_programmer.py`

```python
import ast
import re
from typing import Dict, List, Optional
from claude_helper import ClaudeHelper
import openai

class AIPairProgrammer:
    def __init__(self):
        self.claude = ClaudeHelper()
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.user_contexts = {}  # Контекст по пользователям
    
    async def analyze_code(self, code: str, language: str = "python", user_id: int = None) -> dict:
        """Комплексный анализ кода"""
        analysis = {
            "issues": await self._find_issues(code, language),
            "suggestions": await self._generate_suggestions(code, language, user_id),
            "complexity": self._analyze_complexity(code, language),
            "potential_bugs": await self._find_potential_bugs(code, language),
            "explanations": await self._explain_complex_parts(code, language)
        }
        return analysis
    
    async def _find_issues(self, code: str, language: str) -> List[dict]:
        """Поиск проблем в коде"""
        issues = []
        
        # Базовые проверки
        if language == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "message": str(e),
                    "line": e.lineno,
                    "severity": "error"
                })
        
        # Поиск code smells
        if len(code.split('\n')) > 100:
            issues.append({
                "type": "long_function",
                "message": "Функция слишком длинная (>100 строк). Рекомендуется разбить на части.",
                "severity": "warning"
            })
        
        # Поиск дублирования
        lines = code.split('\n')
        seen = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and len(stripped) > 10:  # Игнорируем короткие строки
                if stripped in seen:
                    issues.append({
                        "type": "duplication",
                        "message": f"Дублирование кода на строке {i+1} (похоже на строку {seen[stripped]+1})",
                        "line": i+1,
                        "severity": "info"
                    })
                seen[stripped] = i
        
        return issues
    
    async def _generate_suggestions(self, code: str, language: str, user_id: int = None) -> List[str]:
        """Генерация предложений по улучшению"""
        prompt = f"""Проанализируй этот {language} код и предложи конкретные улучшения (максимум 5):

```{language}
{code}
```

Верни только список предложений, каждое с новой строки, без нумерации."""
        
        suggestions_text = await self.claude.ask(prompt)
        suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()][:5]
        
        return suggestions
    
    def _analyze_complexity(self, code: str, language: str) -> dict:
        """Анализ сложности кода"""
        if language == "python":
            try:
                tree = ast.parse(code)
                complexity = {
                    "functions": 0,
                    "classes": 0,
                    "nested_depth": 0,
                    "cyclomatic_complexity": 0
                }
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity["functions"] += 1
                        complexity["cyclomatic_complexity"] += self._calculate_cyclomatic(node)
                    elif isinstance(node, ast.ClassDef):
                        complexity["classes"] += 1
                
                return complexity
            except:
                return {}
        return {}
    
    def _calculate_cyclomatic(self, node: ast.FunctionDef) -> int:
        """Расчет цикломатической сложности"""
        complexity = 1  # Базовая сложность
        
        for n in ast.walk(node):
            if isinstance(n, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(n, ast.BoolOp):
                complexity += len(n.values) - 1
        
        return complexity
    
    async def _find_potential_bugs(self, code: str, language: str) -> List[dict]:
        """Поиск потенциальных багов"""
        bugs = []
        
        # Проверка на common mistakes
        if language == "python":
            # Незакрытые файлы
            if re.search(r'open\([^)]+\)(?!\s*as\s+\w+)', code):
                bugs.append({
                    "type": "unclosed_file",
                    "message": "Файл открыт без 'with' statement. Используйте context manager.",
                    "severity": "warning"
                })
            
            # Неиспользуемые переменные
            if re.search(r'for\s+_+\s+in', code):
                bugs.append({
                    "type": "unused_variable",
                    "message": "Используется '_' в цикле. Убедитесь, что это намеренно.",
                    "severity": "info"
                })
            
            # Сравнение с None через ==
            if re.search(r'\w+\s*==\s*None', code):
                bugs.append({
                    "type": "none_comparison",
                    "message": "Используйте 'is None' вместо '== None' для сравнения с None.",
                    "severity": "warning"
                })
        
        return bugs
    
    async def _explain_complex_parts(self, code: str, language: str) -> Dict[str, str]:
        """Объяснение сложных частей кода"""
        prompt = f"""Найди самые сложные части этого {language} кода и объясни их простым языком:

```{language}
{code}
```

Верни JSON с объяснениями:
{{
  "complex_parts": [
    {{
      "line": номер_строки,
      "explanation": "простое объяснение"
    }}
  ]
}}"""
        
        explanation_text = await self.claude.ask(prompt)
        
        # Парсинг JSON (упрощенно)
        try:
            import json
            return json.loads(explanation_text)
        except:
            return {"complex_parts": []}
    
    async def help_debug(self, error_message: str, code: str, language: str = "python") -> str:
        """Помощь в отладке ошибки"""
        prompt = f"""Пользователь получил ошибку в {language} коде. Помоги найти и исправить проблему.

Ошибка:
{error_message}

Код:
```{language}
{code}
```

Предоставь:
1. Причину ошибки (простыми словами)
2. Где именно проблема
3. Как исправить (с примером кода)"""
        
        solution = await self.claude.ask(prompt)
        return solution
    
    async def explain_concept(self, concept: str, context: str = "") -> str:
        """Объяснение концепции программирования"""
        prompt = f"""Объясни концепцию '{concept}' простым языком для программиста.

{('Контекст: ' + context) if context else ''}

Используй:
- Простые слова
- Примеры кода
- Аналогии (если уместно)
- Практические применения"""
        
        explanation = await self.claude.ask(prompt)
        return explanation
    
    async def suggest_next_steps(self, code: str, goal: str, language: str = "python") -> List[str]:
        """Предложение следующих шагов"""
        prompt = f"""Пользователь пишет {language} код для достижения цели: '{goal}'

Текущий код:
```{language}
{code}
```

Предложи следующие 3-5 конкретных шагов для завершения задачи. Каждый шаг - одно действие."""
        
        steps_text = await self.claude.ask(prompt)
        steps = [s.strip() for s in steps_text.split('\n') if s.strip()][:5]
        return steps
    
    async def code_review(self, code: str, language: str = "python") -> dict:
        """Code review с детальным анализом"""
        analysis = await self.analyze_code(code, language)
        
        prompt = f"""Проведи детальный code review этого {language} кода:

```{language}
{code}
```

Верни JSON:
{{
  "overall_score": число_от_1_до_10,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "recommendations": ["...", "..."],
  "security_issues": ["...", "..."]
}}"""
        
        review_text = await self.claude.ask(prompt)
        
        try:
            import json
            review = json.loads(review_text)
            review["technical_analysis"] = analysis
            return review
        except:
            return {
                "overall_score": 7,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "technical_analysis": analysis
            }
```

#### Шаг 2: Интеграция в `bot.py`

```python
from pair_programmer.pair_programmer import AIPairProgrammer

# В __init__:
self.pair_programmer = AIPairProgrammer()

# Команды:
async def pair_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Режим pair programming"""
    keyboard = [
        [InlineKeyboardButton("🔍 Анализ кода", callback_data="pair_analyze")],
        [InlineKeyboardButton("🐛 Помощь с ошибкой", callback_data="pair_debug")],
        [InlineKeyboardButton("💡 Объяснить концепцию", callback_data="pair_explain")],
        [InlineKeyboardButton("📝 Code Review", callback_data="pair_review")],
        [InlineKeyboardButton("🎯 Следующие шаги", callback_data="pair_steps")]
    ]
    
    await update.message.reply_text(
        "🤝 **AI Pair Programmer режим**\n\n"
        "Я буду работать как твой напарник:\n"
        "• Анализирую твой код\n"
        "• Предлагаю улучшения\n"
        "• Помогаю отлаживать\n"
        "• Объясняю сложные концепции\n\n"
        "Отправь код для анализа или выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def analyze_code_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализ кода в реальном времени"""
    code = update.message.text.replace("/analyze", "").strip()
    if not code:
        await update.message.reply_text("📝 Отправь код для анализа")
        return
    
    await update.message.reply_text("🔍 Анализирую код...")
    
    analysis = await self.pair_programmer.analyze_code(
        code,
        language="python",
        user_id=update.effective_user.id
    )
    
    # Формирование ответа
    response = "📊 **Результаты анализа:**\n\n"
    
    if analysis["issues"]:
        response += "⚠️ **Проблемы:**\n"
        for issue in analysis["issues"][:5]:
            response += f"• {issue['message']}\n"
        response += "\n"
    
    if analysis["suggestions"]:
        response += "💡 **Предложения по улучшению:**\n"
        for suggestion in analysis["suggestions"]:
            response += f"• {suggestion}\n"
        response += "\n"
    
    if analysis["potential_bugs"]:
        response += "🐛 **Потенциальные баги:**\n"
        for bug in analysis["potential_bugs"][:3]:
            response += f"• {bug['message']}\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def debug_error_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь в отладке ошибки"""
    text = update.message.text.replace("/debug", "").strip()
    
    if not text or "```" not in text:
        await update.message.reply_text(
            "🐛 **Помощь в отладке**\n\n"
            "Отправь ошибку и код в формате:\n"
            "```\n"
            "Ошибка: ...\n"
            "```python\n"
            "твой код\n"
            "```"
        )
        return
    
    # Парсинг ошибки и кода (упрощенно)
    parts = text.split("```")
    error_msg = parts[0].replace("Ошибка:", "").strip()
    code = parts[1].replace("python", "").strip() if len(parts) > 1 else text
    
    await update.message.reply_text("🔧 Анализирую ошибку...")
    
    solution = await self.pair_programmer.help_debug(
        error_msg,
        code,
        language="python"
    )
    
    await update.message.reply_text(f"✅ **Решение:**\n\n{solution}", parse_mode='Markdown')

# Callback handlers:
async def pair_programmer_callback(self, query, action: str):
    """Обработка callback для pair programmer"""
    if action == "analyze":
        await query.answer("Отправь код для анализа командой /analyze")
    elif action == "debug":
        await query.answer("Отправь ошибку командой /debug")
    # ... и т.д.
```

---

## 📋 Общий список зависимостей для всех фич

```txt
# requirements.txt - добавить:

# UI Builder
Pillow>=10.0.0
opencv-python>=4.8.0
pytesseract>=0.3.10
easyocr>=1.7.0
jsbeautifier>=1.14.0

# Code Memory Bank
peewee>=3.17.0
sentence-transformers>=2.2.0
tree-sitter>=0.20.0
tree-sitter-python
tree-sitter-javascript
tree-sitter-typescript

# Pair Programmer
GitPython>=3.1.40
tree-sitter>=0.20.0

# Общие (если еще нет)
openai>=1.0.0
anthropic>=0.7.0
numpy>=1.24.0
```

---

## 🚀 Порядок реализации

### Этап 1: UI Builder (1-2 недели)
1. ✅ Базовая обработка изображений
2. ✅ Интеграция GPT-4 Vision
3. ✅ Генерация HTML/CSS
4. ✅ Поддержка React/Vue
5. ✅ Оптимизация и форматирование

### Этап 2: Code Memory Bank (1 неделя)
1. ✅ Создание БД
2. ✅ Анализ кода
3. ✅ Сохранение стиля
4. ✅ Применение стиля
5. ✅ Интеграция в генерацию

### Этап 3: Pair Programmer (1-2 недели)
1. ✅ Базовый анализ кода
2. ✅ Поиск проблем
3. ✅ Генерация советов
4. ✅ Помощь в отладке
5. ✅ Code review

---

## 💡 Дополнительные идеи

1. **Голосовые команды для всех фич** - управление голосом
2. **Визуализация в Telegram** - диаграммы и графики прямо в чате
3. **Сравнение версий кода** - diff прямо в Telegram
4. **Автоматические тесты** - генерация тестов на основе кода
5. **Интеграция с IDE** - плагин для VS Code/JetBrains

---

## 📝 Примечания

- Все фичи используют существующую инфраструктуру (Claude, OpenAI)
- Код модульный и легко расширяемый
- Можно реализовывать поэтапно
- Каждая фича работает независимо
