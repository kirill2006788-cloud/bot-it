import functools
import logging

import random

import string

import qrcode
from PIL import Image

import requests

import json

import os

import re

import asyncio
from types import SimpleNamespace

from datetime import datetime

from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN, OPENWEATHER_API_KEY, EXCHANGE_API_KEY, MAX_GAME_SCORE, MAX_PASSWORD_LENGTH, MAX_QR_TEXT_LENGTH, IMAGE_GENERATION_API

from claude_helper import ClaudeHelper

from image_generator import ImageGenerator, validate_prompt

from image_menus import show_main_image_menu, show_model_menu, show_quality_menu, show_styles_menu

from characters_database import STYLES

from github_bot import GitHubBot

from file_converter import FileConverter

from presentation_generator import PresentationGenerator

from music_searcher import MusicSearcher

from wallpaper_generator import WallpaperGenerator, validate_wallpaper_prompt

from translator import Translator

from gif_generator import GifGenerator
from voice_helper import VoiceHelper
from reminder_helper import ReminderHelper
from web_search_helper import WebSearchHelper
from document_generator import DocumentGenerator



# Настройка логирования

logging.basicConfig(

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    level=logging.INFO

)

logger = logging.getLogger(__name__)



class ITHelperBot:

    def __init__(self):

        self.user_scores = {}  # Словарь для хранения очков пользователей

        self.user_games = {}   # Словарь для активных игр

        self.claude = ClaudeHelper()  # Помощник с Claude API

        self.image_gen = ImageGenerator()  # Генератор изображений

        self.wallpaper_gen = WallpaperGenerator()  # Генератор обоев

        self.translator = Translator()  # Переводчик

        self.gif_gen = GifGenerator()
        
        self.voice_helper = VoiceHelper()  # Голосовые команды
        
        self.reminder_helper = ReminderHelper()  # Напоминания и задачи
        
        self.web_search = WebSearchHelper(claude_helper=self.claude)  # Поиск в интернете
        
        self.document_generator = DocumentGenerator()  # Генератор документов Word

        self.music_searcher = MusicSearcher()  # Поиск музыки
        self.github_bot = GitHubBot()  # GitHub интеграция

        self.file_converter = FileConverter()  # Конвертер файлов

        self.presentation_generator = PresentationGenerator(
            claude_helper=self.claude,
            image_generator=self.image_gen
        )  # Генератор презентаций

        self.ai_chat_mode = {}  # Режим чата с AI для пользователей

        self.ai_chat_history = {}  # История чата с AI

        self.history_dir = "chat_history"  # Папка для хранения истории

        self.last_image_prompt = {}  # Последний промпт для перегенерации

        self.favorites = {}  # Избранные изображения
        self.input_modes = {}  # Режимы ввода после нажатия кнопок (без /команд)
        self.quick_commands = [
            ("💬 AI чат", "chat", self.start_ai_chat_command),
            ("🎨 Изображение", "image", self.generate_image_command),
            ("🖼 Обои", "wallpaper", self.generate_wallpaper_command),
            ("🔄 Переген", "imgregen", self.regenerate_image_command),
            ("🎬 GIF", "gif", self.generate_gif_command),
            ("😂 Мем", "meme", self.generate_meme_command),
            ("🤔 Thinking GIF", "thinking", self.thinking_gif_command),
            ("🌤 Погода", "weather", self.get_weather),
            ("🌐 Перевод", "translate", self.translate_command),
            ("🎵 Музыка", "music", self.music_search_command),
            ("🐙 GitHub", "github", self.github_command),
            ("💱 Валюты", "currency", self.convert_currency),
            ("💻 Код", "code", self.generate_code),
            ("⏰ Напомнить", "remind", self.remind_command),
            ("✅ Задача", "task", self.task_command),
            ("📋 Мои задачи", "tasks", self.tasks_command),
            ("🔎 Поиск", "search", self.web_search_command),
            ("📰 Новости", "news", self.news_search_command),
            ("❓ Помощь", "help", self.help_command),
        ]
        
        self.voice_response_mode = {}  # Режим голосовых ответов (True = голосом, False = только текст)
        
        self.reminder_states = {}  # Состояния диалога для добавления напоминаний/задач
        
        self.document_states = {}  # Состояния диалога для создания документов

        

        # Создаем папку для истории, если её нет

        if not os.path.exists(self.history_dir):

            os.makedirs(self.history_dir)

        

        # Загружаем сохраненные истории

        self.load_all_histories()

        

    async def run_blocking(self, func, *args, **kwargs):
        """Запуск синхронной/тяжелой функции в отдельном потоке"""
        loop = asyncio.get_running_loop()
        bound_func = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, bound_func)


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Обработчик команды /start"""

        user = update.effective_user

        welcome_text = f"""

🤖 **Добро пожаловать в IT Helper Bot с Claude AI!**



Привет, {user.first_name}! Я твой персональный IT-помощник с множеством крутых функций:



🧠 **AI-возможности (Claude):**

• 💬 Чат с AI как в ChatGPT

• 🎨 **Генерация изображений** - создавай картинки по описанию!

• 💻 Генерация профессионального кода

• 📦 **Создание целых проектов в ZIP** - готовые приложения!

• 🔍 Объяснение и отладка кода



🎬 **GIF Генератор (НОВОЕ!):**

• 🎭 Анимированный текст (wave, rainbow, pulse)

• 😂 Мемы с твоим текстом

• 🤔 Думающие GIF с эмодзи



📱 **Расширенная генерация:**

• 🖼️ **Обои для телефона** - оптимизированные для мобильных экранов!



🌍 **Полезные утилиты:**

• 🔤 **Переводчик текста** - поддержка 50+ языков

• 🎵 **Поиск музыки** - ссылки на все популярные платформы



🎮 **Игры:**

• 🎯 Угадай число

• 🧠 Викторина по программированию



🛠️ **Инструменты:**

• 🔐 Генератор паролей

• 📱 QR-код генератор

• 💱 Конвертер валют

• 🌤️ Погода



📊 Статистика: /stats

❓ Справка: /help



Используй меню ниже или команды для навигации!

        """

        

        keyboard = [

            [InlineKeyboardButton("🧠 AI Claude", callback_data="ai_menu")],

            [InlineKeyboardButton("🎮 Игры", callback_data="games")],

            [InlineKeyboardButton("🛠️ Инструменты", callback_data="tools")],

            [InlineKeyboardButton("⚡ Быстрые команды", callback_data="quick_cmds:0")],

            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],

            [InlineKeyboardButton("❓ Помощь", callback_data="help")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)



    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Обработчик команды /help"""

        help_text = """

📖 **Полная справка по командам:**



🔧 **Основные команды:**

/start - Главное меню

/help - Эта справка

/stats - Ваша статистика



🧠 **AI Claude команды:**

/chat - Начать чат с AI (общайтесь без команд!)

/ask [вопрос] - Задать вопрос Claude AI

/image [описание] - 🎨 Генерация изображений AI!

/wallpaper [описание] - 📱 Генерация обоев для телефона!

/aicode [язык] [описание] - Генерация кода через AI

/project [описание] - 📦 Создать целый проект (ZIP файл)

/explain [код] - Объяснить код

/debug [код] - Отладить код

/optimize [код] - Оптимизировать код



🎬 **GIF Генератор (НОВОЕ!):**

/gif [текст] - Анимированный текст

/gif wave [текст] - Волновая анимация

/gif rainbow [текст] - Радужная анимация

/gif pulse [текст] - Пульсирующая анимация

/meme [верх] / [низ] - Мем GIF

/thinking [emoji] - Думающий GIF



📱 **Расширенная генерация:**

/wallpaper [описание] - Обои для телефона



🌍 **Полезные утилиты:**

/translate [текст] - Переводчик текста

/music [название] - Поиск музыки



🎮 **Игры:**

/guess - Угадай число (1-100)

/quiz - Викторина по программированию



🛠️ **Инструменты:**

/password [длина] - Генератор паролей

/qr [текст] - Создать QR-код

/weather [город] - Погода

/translate [текст] - Переводчик

/music [название] - Поиск музыки

/currency [сумма] [валюта] - Конвертер валют



💡 **Примеры использования:**



**GIF команды:**

/gif Привет Мир

/gif wave Круто

/gif rainbow BOOM

/meme Когда код работает / С первого раза

/thinking 🤔



**Расширенная генерация:**

/wallpaper абстрактные волны

/wallpaper космический пейзаж



**Полезные утилиты:**

/translate Привет, как дела?

/music Imagine Dragons Thunder



**AI команды:**

/ask Как работает машинное обучение?

/image кот программист за компьютером

/aicode python веб-сервер на Flask

/project todo приложение на React

/explain def factorial(n): return 1 if n == 0 else n * factorial(n-1)



**Чат с Claude:**

Просто напиши "создай сайт портфолио" - бот автоматически вызовет /project!



💡 **Совет:** Используйте команды или кнопки для быстрого доступа к функциям!

        """

        await update.message.reply_text(help_text)



    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Обработчик нажатий на кнопки"""

        query = update.callback_query

        # Игнорировать noop кнопки (разделители)
        if query.data == "noop":
            await query.answer(cache_time=0)
            return

        # Быстрый ответ на callback (убирает задержку в UI)
        # Отвечаем сразу, без ожидания обработки
        # Используем asyncio.create_task для параллельного выполнения ответа
        answer_task = asyncio.create_task(query.answer(cache_time=0))

        if query.data == "ai_menu":

            await self.show_ai_menu(query)

        elif query.data == "ai_chat_start":

            await self.start_ai_chat(query)

        elif query.data == "ai_chat_stop":

            await self.stop_ai_chat(query)

        elif query.data == "ai_image_menu":

            await self.show_image_menu(query)
        elif query.data == "img_model_menu":
            await show_model_menu(query, self)
        elif query.data == "img_styles_menu":
            await show_styles_menu(query, self)
        elif query.data == "img_quality_menu":
            await show_quality_menu(query, self)
        elif query.data.startswith("setmodel_"):
            await self.set_model(query, query.data.replace("setmodel_", ""))
        elif query.data.startswith("setstyle_"):
            await self.set_style(query, query.data.replace("setstyle_", ""))
        elif query.data.startswith("setqual_"):
            await self.set_quality(query, query.data.replace("setqual_", ""))

        elif query.data == "regenerate_image":

            await self.handle_regenerate_image(query)

        elif query.data == "regenerate_wallpaper":

            await self.handle_regenerate_wallpaper(query)

        elif query.data == "games":

            await self.show_games_menu(query)

        elif query.data == "tools":

            await self.show_tools_menu(query)
        elif query.data.startswith("quick_cmds:"):
            page = int(query.data.split(":", 1)[1])
            await self.show_quick_commands_menu(query, page=page)
        elif query.data.startswith("quick_run:"):
            key = query.data.split(":", 1)[1]
            await self.run_quick_command(query, key)
        
        elif query.data == "toggle_voice_mode":
            await self.toggle_voice_mode(query)
        
        elif query.data == "reminders_menu":
            await self.show_reminders_menu(query)
        
        elif query.data.startswith("complete_task_"):
            task_id = int(query.data.split("_")[-1])
            await self.complete_task_handler(query, task_id)
        
        elif query.data.startswith("delete_task_"):
            task_id = int(query.data.split("_")[-1])
            await self.delete_task_handler(query, task_id)
        
        elif query.data.startswith("delete_reminder_"):
            reminder_id = int(query.data.split("_")[-1])
            await self.delete_reminder_handler(query, reminder_id)
        
        elif query.data == "add_reminder":
            await self.start_add_reminder(query)
        
        elif query.data == "add_task":
            await self.start_add_task(query)
        
        elif query.data.startswith("reminder_time_"):
            time_str = query.data.replace("reminder_time_", "")
            await self.handle_reminder_time_selection(query, time_str)
        
        elif query.data.startswith("task_priority_"):
            priority = query.data.replace("task_priority_", "")
            await self.handle_task_priority_selection(query, priority)
        
        elif query.data == "reminder_custom_time":
            await self.handle_custom_reminder_time(query)
        
        elif query.data == "web_search_menu":
            await self.show_web_search_menu(query)
        
        elif query.data == "web_search_normal":
            self.input_modes[query.from_user.id] = "search"
            await query.edit_message_text(
                "🔍 **Обычный поиск**\n\nНапишите запрос следующим сообщением.\n\nПример: `как работает ChatGPT`",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="web_search_menu")]])
            )
        
        elif query.data == "web_search_news":
            self.input_modes[query.from_user.id] = "news"
            await query.edit_message_text(
                "📰 **Поиск новостей**\n\nНапишите тему следующим сообщением.\n\nПример: `технологии 2026`",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="web_search_menu")]])
            )
        
        elif query.data == "check_more_weather":
            self.input_modes[query.from_user.id] = "weather"
            await query.edit_message_text(
                "🌤️ Напишите город следующим сообщением.\n\nПример: `Москва`",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
            )
        
        elif query.data == "translate_more":
            self.input_modes[query.from_user.id] = "translate"
            await query.edit_message_text(
                "🌐 Напишите текст для перевода следующим сообщением.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
            )

        elif query.data == "search_more_music":
            self.input_modes[query.from_user.id] = "music"
            await query.edit_message_text(
                "🎵 Напишите название трека/исполнителя следующим сообщением.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
            )
        
        elif query.data == "create_document_menu":
            await self.show_create_document_menu(query)
        
        elif query.data.startswith("doc_type_"):
            doc_type = query.data.replace("doc_type_", "")
            await self.start_create_document(query, doc_type)
        
        elif query.data == "list_reminders":
            await self.list_reminders_handler(query)
        
        elif query.data == "list_tasks":
            # Создаем временный update для tasks_command
            from telegram import Update as TGUpdate
            fake_update = TGUpdate(update_id=0, message=query.message)
            fake_context = type('Context', (), {'args': []})()
            await self.tasks_command(fake_update, fake_context)

        elif query.data == "stats":

            await self.show_stats(query)

        elif query.data == "help":

            await self.show_help(query)

        elif query.data == "guess_game":

            await self.start_guess_game(query)

        elif query.data == "quiz_game":

            await self.start_quiz_game(query)

        elif query.data == "password_gen":

            await self.show_password_menu(query)

        elif query.data == "qr_gen":

            await self.show_qr_menu(query)

        elif query.data == "weather_check":

            await self.show_weather_menu(query)

        elif query.data == "translate_text":

            await self.show_translate_menu(query)

        elif query.data == "music_search":

            await self.show_music_menu(query)

        elif query.data == "github_simple":

            await self.show_simple_github_menu(query)

        elif query.data == "file_converter":

            await self.show_file_converter_menu(query)

        elif query.data == "presentation_generator":

            await self.show_presentation_generator_menu(query)

        elif query.data.startswith("pres_"):
            await self.handle_presentation_callback(query)

        elif query.data == "converter_info":

            await self.show_converter_info(query)

        elif query.data == "pdf_converter":

            await self.show_pdf_converter_menu(query)

        elif query.data.startswith("pdf_to_"):
            await self.handle_pdf_conversion_callback(query)

        elif query.data.startswith("convert_"):
            await self.handle_conversion_callback(query)

        elif query.data == "github_search":

            await query.edit_message_text(

                "🔍 **Поиск репозиториев GitHub**\n\nВведите поисковый запрос:\n\n**Примеры:**\n• `python bot`\n• `javascript framework`\n• `machine learning`\n• `web development`",

                parse_mode='Markdown'

            )

        elif query.data == "github_user":

            await query.edit_message_text(

                "👤 **Информация о пользователе GitHub**\n\nВведите имя пользователя:\n\n**Примеры:**\n• `kirill2006788-cloud`\n• `microsoft`\n• `facebook`\n• `google`",

                parse_mode='Markdown'

            )

        elif query.data == "github_gist":

            await query.edit_message_text(

                "📄 **Создание Gist**\n\nОтправьте файл с кодом или используйте команду:\n\n`/github gist filename.py`\n\n**Пример:**\n```python\nprint('Hello, World!')\n```",

                parse_mode='Markdown'

            )

        elif query.data == "github_upload_file":

            await query.edit_message_text(

                "📁 **Загрузка файла как Gist**\n\nПросто отправьте любой текстовый файл!\n\n**Поддерживаемые типы:**\n• Python (.py)\n• JavaScript (.js, .ts)\n• HTML/CSS (.html, .css)\n• JSON (.json)\n• Markdown (.md)\n• И многие другие!\n\n**Ограничения:**\n• Максимальный размер: 1MB\n• Только текстовые файлы\n\n💡 **Совет:** Просто отправьте файл как документ!",

                parse_mode='Markdown'

            )

        elif query.data == "github_trending":

            await self.show_trending_repositories(query)

        elif query.data == "github_advanced_search":

            await query.edit_message_text(
                "🔍 **Расширенный поиск репозиториев**\n\nВведите поисковый запрос в формате:\n`запрос [язык] [сортировка]`\n\n**Примеры:**\n• `python bot stars`\n• `javascript framework updated`\n• `machine learning python forks`\n• `web development javascript created`\n\n**Сортировка:** stars, forks, updated, created\n**Языки:** python, javascript, java, c++, go, rust",
                parse_mode='Markdown'
            )

        elif query.data == "github_repo_details":

            await query.edit_message_text(
                "📁 **Детали репозитория**\n\nВведите репозиторий в формате:\n`владелец/название`\n\n**Примеры:**\n• `microsoft/vscode`\n• `facebook/react`\n• `google/tensorflow`\n• `torvalds/linux`",
                parse_mode='Markdown'
            )

        elif query.data == "github_repo_issues":

            await query.edit_message_text(
                "📝 **Issues репозитория**\n\nВведите репозиторий в формате:\n`владелец/название`\n\n**Примеры:**\n• `microsoft/vscode`\n• `facebook/react`\n• `nodejs/node`\n• `microsoft/TypeScript`",
                parse_mode='Markdown'
            )

        elif query.data == "github_repo_prs":

            await query.edit_message_text(
                "🔄 **Pull Requests репозитория**\n\nВведите репозиторий в формате:\n`владелец/название`\n\n**Примеры:**\n• `microsoft/vscode`\n• `facebook/react`\n• `nodejs/node`\n• `microsoft/TypeScript`",
                parse_mode='Markdown'
            )

        elif query.data == "github_repo_stats":

            await query.edit_message_text(
                "📊 **Статистика репозитория**\n\nВведите репозиторий в формате:\n`владелец/название`\n\n**Примеры:**\n• `microsoft/vscode`\n• `facebook/react`\n• `google/tensorflow`\n• `torvalds/linux`",
                parse_mode='Markdown'
            )

        elif query.data == "currency_conv":

            await self.show_currency_menu(query)

        elif query.data.startswith("user_repos_"):
            username = query.data[11:]  # Убираем "user_repos_"
            await self.show_user_repositories(query, username)

        elif query.data.startswith("issues_"):
            parts = query.data[7:].split("_")  # Убираем "issues_"
            if len(parts) >= 2:
                owner = parts[0]
                repo_name = "_".join(parts[1:])
                await self.show_repository_issues(query, owner, repo_name)

        elif query.data.startswith("prs_"):
            parts = query.data[4:].split("_")  # Убираем "prs_"
            if len(parts) >= 2:
                owner = parts[0]
                repo_name = "_".join(parts[1:])
                await self.show_repository_prs(query, owner, repo_name)

        elif query.data.startswith("stats_"):
            parts = query.data[6:].split("_")  # Убираем "stats_"
            if len(parts) >= 2:
                owner = parts[0]
                repo_name = "_".join(parts[1:])
                await self.show_repository_stats(query, owner, repo_name)

        elif query.data.startswith("repo_"):
            parts = query.data[5:].split("_")  # Убираем "repo_"
            if len(parts) >= 2:
                owner = parts[0]
                repo_name = "_".join(parts[1:])
                await self.show_repository_details(query, owner, repo_name)

        elif query.data == "code_gen":

            await self.show_code_menu(query)

        elif query.data == "back_to_main":

            await self.show_main_menu(query)

        



    def load_all_histories(self):

        """Загрузить все сохраненные истории чатов"""

        for filename in os.listdir(self.history_dir):

            if filename.endswith('.json'):

                user_id = int(filename.replace('.json', ''))

                try:

                    with open(os.path.join(self.history_dir, filename), 'r', encoding='utf-8') as f:

                        self.ai_chat_history[user_id] = json.load(f)

                except Exception as e:

                    logger.error(f"Ошибка загрузки истории для {user_id}: {e}")

    

    def save_history(self, user_id):

        """Сохранить историю чата пользователя"""

        if user_id in self.ai_chat_history:

            try:

                filepath = os.path.join(self.history_dir, f"{user_id}.json")

                with open(filepath, 'w', encoding='utf-8') as f:

                    json.dump(self.ai_chat_history[user_id], f, ensure_ascii=False, indent=2)

            except Exception as e:

                logger.error(f"Ошибка сохранения истории для {user_id}: {e}")



    async def show_ai_menu(self, query):

        """Показать меню AI функций"""

        keyboard = [

            [InlineKeyboardButton("💬 Начать чат с AI", callback_data="ai_chat_start")],
            
            [InlineKeyboardButton("🎤 Режим голосовых ответов", callback_data="toggle_voice_mode")],

            [InlineKeyboardButton("🎨 Генерация изображений", callback_data="ai_image_menu")],

            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        ai_info = """

🧠 **AI Claude - Твой умный собеседник!**



💬 **Начни чат с AI** - как в ChatGPT, но в Telegram!



✨ **Я могу:**

• 💭 Общаться на любые темы (не только код!)

• 🎮 Болтать о жизни, хобби, развлечениях

• 💻 Помогать с программированием

• 🎨 Создавать целые проекты

• 🖼️ **Генерировать изображения по описанию!**

• 🧠 Помнить всю историю разговора

• 😊 Просто быть интересным собеседником



🚀 **Команды:**

• **/chat** - Начать общение

• **/image** [описание] - Создать изображение

• **/project** [описание] - Создать проект в ZIP

• **/aicode** [язык] [описание] - Сгенерировать код



*Powered by Claude AI - умнее, чем кажется! 😉*

        """

        await query.edit_message_text(ai_info, parse_mode='Markdown', reply_markup=reply_markup)



    async def show_games_menu(self, query):

        """Показать меню игр"""

        keyboard = [

            [InlineKeyboardButton("🎯 Угадай число", callback_data="guess_game")],

            [InlineKeyboardButton("🧠 Викторина", callback_data="quiz_game")],

            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("🎮 **Выберите игру:**", parse_mode='Markdown', reply_markup=reply_markup)



    async def show_tools_menu(self, query):

        """Показать меню инструментов"""

        keyboard = [

            [InlineKeyboardButton("🔐 Генератор паролей", callback_data="password_gen")],

            [InlineKeyboardButton("📱 QR-код", callback_data="qr_gen")],

            [InlineKeyboardButton("🌤️ Погода", callback_data="weather_check")],

            [InlineKeyboardButton("🌐 Переводчик", callback_data="translate_text")],

            [InlineKeyboardButton("🎵 Поиск музыки", callback_data="music_search")],

            [InlineKeyboardButton("🐙 GitHub", callback_data="github_simple")],

            [InlineKeyboardButton("📄 Конвертер файлов", callback_data="file_converter")],

            [InlineKeyboardButton("🎯 Генератор презентаций", callback_data="presentation_generator")],

            [InlineKeyboardButton("💱 Валюты", callback_data="currency_conv")],

            [InlineKeyboardButton("💻 Генератор кода", callback_data="code_gen")],
            
            [InlineKeyboardButton("⏰ Напоминания и задачи", callback_data="reminders_menu")],
            
            [InlineKeyboardButton("🔍 Поиск в интернете", callback_data="web_search_menu")],
            
            [InlineKeyboardButton("📄 Создать документ Word", callback_data="create_document_menu")],

            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("🛠️ **Выберите инструмент:**", parse_mode='Markdown', reply_markup=reply_markup)



    async def show_main_menu(self, query):

        """Показать главное меню"""

        keyboard = [

            [InlineKeyboardButton("🧠 AI Claude", callback_data="ai_menu")],

            [InlineKeyboardButton("🎮 Игры", callback_data="games")],

            [InlineKeyboardButton("🛠️ Инструменты", callback_data="tools")],

            [InlineKeyboardButton("⚡ Быстрые команды", callback_data="quick_cmds:0")],

            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],

            [InlineKeyboardButton("❓ Помощь", callback_data="help")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Используем try-except для обработки ошибок при редактировании
        try:
            await query.edit_message_text("🤖 **IT Helper Bot - Главное меню**", parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            # Если не удалось отредактировать (например, сообщение не изменилось), отправляем новое
            logger.error(f"Ошибка при редактировании сообщения: {e}")
            await query.message.reply_text("🤖 **IT Helper Bot - Главное меню**", parse_mode='Markdown', reply_markup=reply_markup)



    async def show_quick_commands_menu(self, query, page: int = 0):
        per_page = 8
        total = len(self.quick_commands)
        pages = max(1, (total + per_page - 1) // per_page)
        page = max(0, min(page, pages - 1))
        start = page * per_page
        items = self.quick_commands[start:start + per_page]

        keyboard = []
        for title, key, _ in items:
            keyboard.append([InlineKeyboardButton(title, callback_data=f"quick_run:{key}")])

        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("◀️", callback_data=f"quick_cmds:{page - 1}"))
        if page < pages - 1:
            nav_row.append(InlineKeyboardButton("▶️", callback_data=f"quick_cmds:{page + 1}"))
        if nav_row:
            keyboard.append(nav_row)
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])

        text = (
            "⚡ **Быстрые команды**\n\n"
            "Запуск функций без ручного ввода `/команд`.\n"
            f"Страница {page + 1}/{pages}"
        )
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def run_quick_command(self, query, key: str):
        mode_map = {
            "weather": ("weather", "🌤️ Напишите город следующим сообщением."),
            "translate": ("translate", "🌐 Напишите текст для перевода следующим сообщением."),
            "music": ("music", "🎵 Напишите трек/исполнителя следующим сообщением."),
            "search": ("search", "🔍 Напишите поисковый запрос следующим сообщением."),
            "news": ("news", "📰 Напишите тему новостей следующим сообщением."),
            "image": ("image", "🎨 Напишите промпт для генерации изображения."),
            "wallpaper": ("wallpaper", "🖼 Напишите промпт для генерации обоев."),
            "gif": ("gif", "🎬 Напишите текст для GIF (можно: wave/pulse/rainbow/rotate + текст)."),
            "meme": ("meme", "😂 Напишите идею для мема следующим сообщением."),
            "thinking": ("thinking", "🤔 Напишите текст для thinking GIF."),
            "currency": ("currency", "💱 Напишите запрос, пример: `100 USD` или `100 USD RUB`."),
            "code": ("code", "💻 Напишите задачу для генерации кода."),
            "remind": ("remind", "⏰ Напишите напоминание, пример: `позвонить маме через 1 час`."),
            "task": ("task", "✅ Напишите задачу следующим сообщением."),
        }
        if key in mode_map:
            mode, text = mode_map[key]
            self.input_modes[query.from_user.id] = mode
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]])
            )
            await query.answer("Жду ввод", cache_time=0)
            return

        for _title, cmd_key, handler in self.quick_commands:
            if cmd_key != key:
                continue
            fake_update = Update(update_id=0, message=query.message)
            fake_context = SimpleNamespace(args=[])
            await handler(fake_update, fake_context)
            await query.answer("Открыто", cache_time=0)
            return
        await query.answer("Команда не найдена", show_alert=True)

    async def show_stats(self, query):

        """Показать статистику пользователя"""

        user_id = query.from_user.id

        score = self.user_scores.get(user_id, 0)

        

        stats_text = f"""

📊 **Ваша статистика:**



🏆 Очки: {score}

🎮 Игр сыграно: {len([g for g in self.user_games.values() if g.get('user_id') == user_id])}

🔧 Инструментов использовано: {random.randint(5, 25)}  # Заглушка



📈 Ранг: {'🥇 Мастер' if score > 50 else '🥈 Эксперт' if score > 20 else '🥉 Новичок'}

        """

        

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=reply_markup)



    async def show_help(self, query):

        """Показать справку"""

        help_text = """

❓ **Справка по командам:**



🎮 **Игры:**

• Угадай число - угадайте число от 1 до 100

• Викторина - вопросы по программированию



🛠️ **Инструменты:**

• Генератор паролей - создание безопасных паролей

• QR-код - генерация QR-кодов из текста

• Погода - актуальная погода по городам

• Конвертер валют - перевод между валютами

• Генератор кода - создание кода на разных языках



💡 **Совет:** Используйте команды или кнопки для быстрого доступа к функциям!

        """

        

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)



    # ИГРЫ

    async def start_guess_game(self, query):

        """Начать игру 'Угадай число'"""

        user_id = query.from_user.id

        secret_number = random.randint(1, 100)

        

        self.user_games[user_id] = {

            'type': 'guess',

            'secret_number': secret_number,

            'attempts': 0,

            'user_id': user_id

        }

        

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="games")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            "🎯 **Угадай число!**\n\nЯ загадал число от 1 до 100. Попробуй угадать!\n\nВведи число:",

            parse_mode='Markdown',
            reply_markup=reply_markup

        )



    async def start_quiz_game(self, query):

        """Начать викторину"""

        questions = [

            {

                'question': 'Какой язык программирования создал Гвидо ван Россум?',

                'options': ['Python', 'Java', 'C++', 'JavaScript'],

                'correct': 0

            },

            {

                'question': 'Что означает HTML?',

                'options': ['HyperText Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlink Text Management Language'],

                'correct': 0

            },

            {

                'question': 'Какой символ используется для комментариев в Python?',

                'options': ['//', '/*', '#', '--'],

                'correct': 2

            }

        ]

        

        user_id = query.from_user.id

        question = random.choice(questions)

        

        self.user_games[user_id] = {

            'type': 'quiz',

            'question': question,

            'user_id': user_id

        }

        

        keyboard = []

        for i, option in enumerate(question['options']):

            keyboard.append([InlineKeyboardButton(f"{i+1}. {option}", callback_data=f"quiz_answer_{i}")])

        # Добавляем кнопку "Назад"
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="games")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            f"🧠 **Викторина по программированию**\n\n❓ {question['question']}",

            parse_mode='Markdown',

            reply_markup=reply_markup

        )



    async def handle_quiz_answer(self, query):

        """Обработать ответ на викторину"""

        user_id = query.from_user.id

        answer_index = int(query.data.split('_')[-1])

        

        if user_id in self.user_games and self.user_games[user_id]['type'] == 'quiz':

            game = self.user_games[user_id]

            correct_index = game['question']['correct']

            

            if answer_index == correct_index:

                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 10

                result_text = "✅ **Правильно!** +10 очков"

            else:

                result_text = f"❌ **Неправильно!** Правильный ответ: {game['question']['options'][correct_index]}"

            

            del self.user_games[user_id]

            

            keyboard = [[InlineKeyboardButton("🎮 Еще викторину", callback_data="quiz_game")],

                       [InlineKeyboardButton("🔙 Меню", callback_data="games")]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            

            await query.edit_message_text(result_text, parse_mode='Markdown', reply_markup=reply_markup)



    # ИНСТРУМЕНТЫ

    async def show_password_menu(self, query):

        """Показать меню генератора паролей"""

        keyboard = [

            [InlineKeyboardButton("🔐 Сгенерировать (8 символов)", callback_data="pass_8")],

            [InlineKeyboardButton("🔐 Сгенерировать (12 символов)", callback_data="pass_12")],

            [InlineKeyboardButton("🔐 Сгенерировать (16 символов)", callback_data="pass_16")],

            [InlineKeyboardButton("🔙 Назад", callback_data="tools")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("🔐 **Генератор паролей**", parse_mode='Markdown', reply_markup=reply_markup)



    async def generate_password(self, query, length):

        """Сгенерировать пароль"""

        characters = string.ascii_letters + string.digits + "!@#$%^&*"

        password = ''.join(random.choice(characters) for _ in range(length))

        

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="password_gen")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        await query.edit_message_text(

            f"🔐 **Ваш пароль:**\n\n`{password}`\n\n💡 Скопируйте пароль и сохраните в безопасном месте!",

            parse_mode='Markdown',

            reply_markup=reply_markup

        )



    async def show_qr_menu(self, query):

        """Показать меню QR-кода"""

        self.input_modes[query.from_user.id] = "qr"
        await query.edit_message_text(
            "📱 **Генератор QR-кода**\n\nНапишите текст следующим сообщением.\n\nПример: `Hello World`",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
        )



    async def create_qr_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Создать QR-код"""

        text = ' '.join(context.args)

        

        if not text:

            await update.message.reply_text(

                "📱 **Генератор QR-кодов**\n\n"

                "Создай QR-код для любого текста или ссылки!\n\n"

                "**Примеры:**\n"

                "Hello World\n"

                "https://google.com\n"

                "Мой номер: +7-999-123-45-67\n"

                "WiFi:SSID:Password\n"

                "mailto:example@email.com\n\n"

                "**Типы QR-кодов:**\n"

                "• 📝 Текст\n"

                "• 🔗 Ссылки (URL)\n"

                "• 📧 Email\n"

                "• 📞 Телефон\n"

                "• 📍 Геолокация\n"

                "• 📶 WiFi\n"

                "• 💳 Визитка (vCard)\n\n"

                "💡 QR-код автоматически определит тип контента!",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])

            )

            return

        

        if len(text) > MAX_QR_TEXT_LENGTH:

            await update.message.reply_text(f"❌ Текст слишком длинный! Максимум {MAX_QR_TEXT_LENGTH} символов.")

            return

        

        try:

            # Показываем индикатор загрузки

            status_msg = await update.message.reply_text("📱 Создаю QR-код...")

            

            # Определяем тип контента

            content_type = self.detect_qr_content_type(text)

            

            # Создаем QR-код с улучшенными настройками

            qr = qrcode.QRCode(

                version=1,

                error_correction=qrcode.constants.ERROR_CORRECT_M,

                box_size=10,

                border=4,

            )

            qr.add_data(text)

            qr.make(fit=True)

            

            # Создаем изображение с лучшим качеством
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((400, 400), Image.Resampling.LANCZOS)
            
            # Проверяем, является ли это ссылкой на облачное хранилище
            is_cloud_link = self.is_cloud_storage_link(text)
            
            if is_cloud_link:
                # Создаем красивое изображение с QR-кодом и текстом
                img = self.create_qr_with_text_image(qr_img, text, content_type)
            else:
                img = qr_img
            
            bio = BytesIO()
            img.save(bio, 'PNG', quality=95)
            bio.seek(0)

            

            # Формируем описание

            caption = f"""

📱 **QR-код готов!**



📝 **Содержимое:** _{text}_



🏷️ **Тип:** {content_type}



💡 **Совет:** Отсканируйте QR-код камерой телефона!

            """

            

            await status_msg.delete()

            await update.message.reply_photo(photo=bio, caption=caption, parse_mode='Markdown')

            # Отправляем кнопки отдельно
            keyboard = [
                [InlineKeyboardButton("🔄 Создать еще", callback_data="create_another_qr")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💡 Что дальше?",
                reply_markup=reply_markup
            )

            

            # Добавляем очки пользователю

            user_id = update.effective_user.id

            self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 2

            

        except Exception as e:

            logger.error(f"Ошибка создания QR-кода: {e}")

            await update.message.reply_text(

                f"❌ Ошибка создания QR-кода.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте:\n"

                f"• Упростить текст\n"

                f"• Проверить корректность данных"

            )

    

    def is_cloud_storage_link(self, text: str) -> bool:
        """Проверить, является ли ссылка облачным хранилищем"""
        if not (text.startswith('http://') or text.startswith('https://')):
            return False
        
        text_lower = text.lower()
        cloud_domains = [
            'yandex.ru/disk',
            'yadi.sk',
            'disk.yandex.ru',
            'onedrive.live.com',
            '1drv.ms',
            'drive.google.com',
            'dropbox.com',
            'mega.nz',
            'icloud.com',
            'box.com',
            'pcloud.com'
        ]
        
        return any(domain in text_lower for domain in cloud_domains)
    
    def create_qr_with_text_image(self, qr_img: Image.Image, text: str, content_type: str) -> Image.Image:
        """Создать изображение с QR-кодом и текстом ссылки"""
        from PIL import ImageDraw, ImageFont
        
        # Размеры
        qr_size = 400
        padding = 40
        text_area_height = 120
        total_height = qr_size + text_area_height + padding * 2
        
        # Создаем новое изображение
        img = Image.new('RGB', (qr_size + padding * 2, total_height), color='white')
        
        # Вставляем QR-код
        img.paste(qr_img, (padding, padding))
        
        # Рисуем текст
        draw = ImageDraw.Draw(img)
        
        try:
            # Пытаемся использовать системный шрифт
            font_large = ImageFont.truetype("arial.ttf", 20) if os.name == 'nt' else ImageFont.load_default()
            font_small = ImageFont.truetype("arial.ttf", 14) if os.name == 'nt' else ImageFont.load_default()
        except:
            # Fallback на стандартный шрифт
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Обрезаем текст если слишком длинный
        display_text = text
        if len(display_text) > 60:
            display_text = display_text[:57] + "..."
        
        # Рисуем тип контента
        text_y = qr_size + padding + 20
        draw.text((padding, text_y), content_type, fill='black', font=font_large)
        
        # Рисуем ссылку
        text_y += 35
        draw.text((padding, text_y), display_text, fill='gray', font=font_small)
        
        return img
    
    def detect_qr_content_type(self, text: str) -> str:

        """Определить тип контента QR-кода"""

        text_lower = text.lower()

        

        if text.startswith('http://') or text.startswith('https://'):
            # Проверяем облачные хранилища
            if 'yandex.ru/disk' in text_lower or 'yadi.sk' in text_lower or 'disk.yandex.ru' in text_lower:
                return "☁️ Яндекс.Облако"
            elif 'onedrive.live.com' in text_lower or '1drv.ms' in text_lower:
                return "☁️ OneDrive"
            elif 'drive.google.com' in text_lower:
                return "☁️ Google Drive"
            elif 'dropbox.com' in text_lower:
                return "☁️ Dropbox"
            elif 'mega.nz' in text_lower:
                return "☁️ MEGA"
            elif 'icloud.com' in text_lower:
                return "☁️ iCloud"
            else:
                return "🔗 Ссылка (URL)"

        elif text.startswith('mailto:'):

            return "📧 Email"

        elif text.startswith('tel:'):

            return "📞 Телефон"

        elif text.startswith('geo:'):

            return "📍 Геолокация"

        elif text.startswith('wifi:'):

            return "📶 WiFi"

        elif text.startswith('vcard:'):

            return "💳 Визитка (vCard)"

        elif '@' in text and '.' in text:

            return "📧 Email адрес"

        elif text.startswith('+') and any(char.isdigit() for char in text):

            return "📞 Телефон"

        elif any(word in text_lower for word in ['wifi', 'ssid', 'password']):

            return "📶 WiFi данные"

        else:

            return "📝 Текст"



    async def show_weather_menu(self, query):

        """Показать меню погоды"""

        self.input_modes[query.from_user.id] = "weather"
        await query.edit_message_text(
            "🌤️ **Погода**\n\nНапишите следующим сообщением город.\n\nПример: `Москва`",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
        )



    async def show_translate_menu(self, query):

        """Показать меню переводчика"""

        self.input_modes[query.from_user.id] = "translate"
        await query.edit_message_text(
            "🌐 **Переводчик**\n\nНапишите текст для перевода следующим сообщением.\n\nПример: `Hello world`",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
        )



    async def show_music_menu(self, query):

        """Показать меню поиска музыки"""

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tools")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        self.input_modes[query.from_user.id] = "music"
        await query.edit_message_text(
            "🎵 **Поиск музыки**\n\nНапишите название трека/исполнителя следующим сообщением.\n\nПример: `Imagine Dragons Thunder`",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )



    async def get_weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Получить погоду"""

        city = ' '.join(context.args)

        if not city:

            await update.message.reply_text(

                "🌤️ **Погода**\n\n"

                "Узнай актуальную погоду в любом городе!\n\n"

                "**Примеры:**\n"

                "Москва\n"

                "Санкт-Петербург\n"

                "London\n"

                "New York\n"

                "Tokyo\n\n"

                "💡 Можно писать на русском или английском языке!",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])

            )

            return

        

        try:

            # Показываем индикатор загрузки

            status_msg = await update.message.reply_text("🌤️ Получаю данные о погоде...")

            

            # Получаем погоду через API

            weather_data = await self.fetch_weather_data(city)

            

            if weather_data:

                # Формируем красивое сообщение

                weather_text = f"""

🌤️ **Погода в {weather_data['city']}, {weather_data['country']}**



🌡️ **Температура:** {weather_data['temperature']}°C

☁️ **Описание:** {weather_data['description']}

🌡️ **Ощущается как:** {weather_data['feels_like']}°C

💧 **Влажность:** {weather_data['humidity']}%

💨 **Ветер:** {weather_data['wind_speed']} м/с

🌫️ **Давление:** {weather_data['pressure']} гПа

👁️ **Видимость:** {weather_data['visibility']} км



📅 **Обновлено:** {weather_data['time']}

                """

                

                keyboard = [
                    [InlineKeyboardButton("🔄 Проверить еще", callback_data="check_more_weather")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await status_msg.edit_text(weather_text, parse_mode='Markdown', reply_markup=reply_markup)

                

                # Добавляем очки пользователю

                user_id = update.effective_user.id

                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 5

                

            else:

                await status_msg.edit_text(

                    f"❌ Не удалось получить данные о погоде для города '{city}'\n\n"

                    f"💡 Проверьте:\n"

                    f"• Правильность написания города\n"

                    f"• Попробуйте английское название\n"

                    f"• Убедитесь что город существует"

                )

                

        except Exception as e:

            logger.error(f"Ошибка получения погоды: {e}")

            await update.message.reply_text(

                f"❌ Ошибка получения данных о погоде.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте позже или проверьте название города"

            )

    

    async def fetch_weather_data(self, city: str) -> dict:

        """Получить данные о погоде через API"""

        try:

            import requests

            from datetime import datetime

            

            # Используем бесплатный API OpenWeatherMap

            api_key = OPENWEATHER_API_KEY

            

            if not api_key or api_key == "your_openweather_api_key":

                # Если API ключ не настроен, используем заглушку

                return self.get_mock_weather_data(city)

            

            # URL для API OpenWeatherMap

            url = "http://api.openweathermap.org/data/2.5/weather"

            

            params = {

                'q': city,

                'appid': api_key,

                'units': 'metric',

                'lang': 'ru'

            }

            

            response = requests.get(url, params=params, timeout=10)

            response.raise_for_status()

            

            data = response.json()

            

            # Формируем данные о погоде

            weather_info = {

                'city': data['name'],

                'country': data['sys']['country'],

                'temperature': round(data['main']['temp']),

                'feels_like': round(data['main']['feels_like']),

                'description': data['weather'][0]['description'].title(),

                'humidity': data['main']['humidity'],

                'pressure': data['main']['pressure'],

                'wind_speed': round(data['wind']['speed']),

                'visibility': round(data['visibility'] / 1000, 1) if 'visibility' in data else 'N/A',

                'time': datetime.now().strftime('%H:%M')

            }

            

            return weather_info

            

        except requests.exceptions.RequestException as e:

            logger.error(f"Ошибка API погоды: {e}")

            return self.get_mock_weather_data(city)

        except Exception as e:

            logger.error(f"Ошибка обработки данных погоды: {e}")

            return self.get_mock_weather_data(city)

    

    def get_mock_weather_data(self, city: str) -> dict:

        """Заглушка для демонстрации (когда API не настроен)"""

        descriptions = ['ясно', 'облачно', 'дождь', 'снег', 'туман', 'пасмурно']

        

        return {

            'city': city.title(),

            'country': 'RU',
            'temperature': random.randint(-10, 35),
            'feels_like': random.randint(-15, 40),
            'description': random.choice(descriptions),

            'humidity': random.randint(30, 90),
            'pressure': random.randint(980, 1030),

            'wind_speed': random.randint(1, 15),

            'visibility': random.randint(5, 20),

            'time': 'демо'

        }



    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для перевода текста"""

        text = ' '.join(context.args)

        

        if not text:

            await update.message.reply_text(

                "🌐 **Переводчик**\n\n"

                "Переведи текст на любой язык!\n\n"

                "**Примеры:**\n"

                "Hello world\n"

                "Привет мир\n"

                "Hola mundo\n"

                "Bonjour le monde\n\n"

                "**Поддерживаемые языки:**\n"

                "🇷🇺 Русский (ru)\n"

                "🇺🇸 English (en)\n"

                "🇪🇸 Español (es)\n"

                "🇫🇷 Français (fr)\n"

                "🇩🇪 Deutsch (de)\n"

                "🇮🇹 Italiano (it)\n"

                "🇵🇹 Português (pt)\n"

                "🇨🇳 中文 (zh)\n"

                "🇯🇵 日本語 (ja)\n"

                "🇰🇷 한국어 (ko)\n\n"

                "💡 Язык определяется автоматически!"

            )

            return

        

        try:

            # Показываем индикатор загрузки

            status_msg = await update.message.reply_text("🌐 Перевожу текст...")

            

            # Определяем целевой язык (по умолчанию русский)

            target_lang = 'ru'

            

            # Если текст на русском, переводим на английский

            detected_lang = self.translator.detect_language(text)

            if detected_lang == 'ru':

                target_lang = 'en'

            

            # Переводим текст

            result = self.translator.translate_text(text, target_lang)

            

            if result['success']:

                # Формируем красивое сообщение

                translation_text = f"""

🌐 **Перевод готов!**



📝 **Исходный текст:** _{result['original_text']}_



🔄 **Переведенный текст:** _{result['translated_text']}_



🌍 **Языки:**

• Исходный: {result['source_language']}

• Целевой: {result['target_language']}



⚙️ **Сервис:** {result['service']}

                """

                

                keyboard = [
                    [InlineKeyboardButton("🔄 Перевести еще", callback_data="translate_more")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await status_msg.edit_text(translation_text, parse_mode='Markdown', reply_markup=reply_markup)

                

                # Добавляем очки пользователю

                user_id = update.effective_user.id

                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 3

                

            else:

                await status_msg.edit_text(

                    f"❌ Ошибка перевода: {result['error']}\n\n"

                    f"💡 Попробуйте:\n"

                    f"• Проверить правильность текста\n"

                    f"• Упростить текст\n"

                    f"• Попробовать позже"

                )

                

        except Exception as e:

            logger.error(f"Ошибка перевода: {e}")

            await update.message.reply_text(

                f"❌ Ошибка перевода.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте позже"

            )



    async def music_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для поиска музыки"""

        query = ' '.join(context.args)

        

        if not query:

            await update.message.reply_text(

                "🎵 **Поиск музыки**\n\n"

                "Найди информацию о любом треке или исполнителе!\n\n"

                "**Примеры:**\n"

                "Imagine Dragons Thunder\n"

                "Ed Sheeran Shape of You\n"

                "Billie Eilish Bad Guy\n"

                "The Weeknd Blinding Lights\n\n"

                "**Популярные треки:**\n"

                "• Imagine Dragons - Thunder\n"

                "• Ed Sheeran - Shape of You\n"

                "• Billie Eilish - Bad Guy\n"

                "• The Weeknd - Blinding Lights\n"

                "• Dua Lipa - Levitating\n\n"

                "**Жанры:**\n"

                "Pop, Rock, Hip Hop, R&B, Electronic, Jazz, Classical\n\n"

                "💡 Получите ссылки для поиска на всех популярных платформах!"

            )

            return

        

        try:

            # Показываем индикатор загрузки

            status_msg = await update.message.reply_text("🎵 Ищу информацию о музыке...")

            

            # Ищем информацию о музыке

            result = await self.run_blocking(self.music_searcher.search_music_info, query)

            

            if result['success']:

                # Форматируем результат

                formatted_result = self.music_searcher.format_music_result(result)

                

                await status_msg.edit_text(formatted_result, parse_mode='Markdown')

                

                # Добавляем очки пользователю

                user_id = update.effective_user.id

                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 5

                

            else:

                await status_msg.edit_text(

                    f"❌ Не удалось найти информацию о музыке.\n\n"

                    f"Ошибка: {result['error']}\n\n"

                    f"💡 Попробуйте:\n"

                    f"• Уточнить название трека\n"

                    f"• Добавить имя исполнителя\n"

                    f"• Проверить правильность написания"

                )

                

        except Exception as e:

            logger.error(f"Ошибка поиска музыки: {e}")

            await update.message.reply_text(

                f"❌ Ошибка поиска музыки.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте позже"

            )



    async def show_simple_github_menu(self, query):

        """Улучшенное меню GitHub"""

        keyboard = [

            [InlineKeyboardButton("🔍 Поиск репозиториев", callback_data="github_search")],
            [InlineKeyboardButton("🔍 Расширенный поиск", callback_data="github_advanced_search")],
            [InlineKeyboardButton("👤 Информация о пользователе", callback_data="github_user")],
            [InlineKeyboardButton("📁 Детали репозитория", callback_data="github_repo_details")],
            [InlineKeyboardButton("📝 Issues репозитория", callback_data="github_repo_issues")],
            [InlineKeyboardButton("🔄 Pull Requests", callback_data="github_repo_prs")],
            [InlineKeyboardButton("📊 Статистика репозитория", callback_data="github_repo_stats")],
            [InlineKeyboardButton("🔥 Трендовые репозитории", callback_data="github_trending")],
            [InlineKeyboardButton("📄 Создать Gist", callback_data="github_gist")],
            [InlineKeyboardButton("📁 Загрузить файл как Gist", callback_data="github_upload_file")],
            [InlineKeyboardButton("🔙 Назад", callback_data="tools")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            "🐙 **GitHub интеграция**\n\nВыберите действие:\n\n💡 **Новые возможности:**\n• Расширенный поиск с фильтрами\n• Детальная информация о репозиториях\n• Просмотр Issues и Pull Requests\n• Статистика и аналитика\n• Работа с Gists\n\n**Примеры команд:**\n• `/github search python bot`\n• `/github user kirill2006788-cloud`\n• `/github repo microsoft/vscode`",

            parse_mode='Markdown',

            reply_markup=reply_markup

        )

    async def show_github_menu(self, query):

        """Показать меню GitHub"""

        keyboard = [

            [InlineKeyboardButton("🔍 Поиск репозиториев", callback_data="github_search")],

            [InlineKeyboardButton("👤 Информация о пользователе", callback_data="github_user")],

            [InlineKeyboardButton("📄 Создать Gist", callback_data="github_gist")],

            [InlineKeyboardButton("🔥 Трендовые репозитории", callback_data="github_trending")],

            [InlineKeyboardButton("🔙 Назад", callback_data="tools")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            "🐙 **GitHub интеграция**\n\nВыберите действие:\n\n💡 **Примеры команд:**\n• `/github search python bot`\n• `/github user kirill2006788-cloud`\n• `/github gist test.py`",

            parse_mode='Markdown',

            reply_markup=reply_markup

        )



        """Показать меню конвертера валют"""

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tools")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            "💱 **Конвертер валют**\n\nВведите сумму и валюту для конвертации:\n\nПример: /currency 100 USD",

            parse_mode='Markdown',
            reply_markup=reply_markup

        )



    async def show_trending_repositories(self, query):

        """Показать трендовые репозитории"""

        try:

            await query.edit_message_text("🔥 Получаю трендовые репозитории...")

            # Получаем трендовые репозитории

            trending_result = self.github_bot.get_trending_repositories()

            if trending_result['success']:

                text = f"🔥 **Трендовые репозитории** ({trending_result['language']})\n\n"

                for i, repo in enumerate(trending_result['repositories'], 1):

                    text += f"**{i}.** {self.github_bot.format_repository_info(repo)}\n\n"

                keyboard = [

                    [InlineKeyboardButton("🔄 Обновить", callback_data="github_trending")],

                    [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]

                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

            else:

                await query.edit_message_text(f"❌ Ошибка получения трендов: {trending_result['error']}")

        except Exception as e:

            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def show_user_repositories(self, query, username):
        """Показать репозитории пользователя"""
        try:
            await query.edit_message_text("📁 Получаю репозитории пользователя...")
            
            repos_result = self.github_bot.get_user_repositories(username)
            if repos_result['success']:
                text = f"📁 **Репозитории пользователя {username}**\n\n"
                
                for i, repo in enumerate(repos_result['repositories'], 1):
                    text += f"**{i}.** {self.github_bot.format_repository_info(repo)}\n\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Обновить", callback_data=f"user_repos_{username}")],
                    [InlineKeyboardButton("👤 Профиль", callback_data=f"user_{username}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text(f"❌ Ошибка получения репозиториев: {repos_result['error']}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def show_repository_details(self, query, owner, repo_name):
        """Показать детали репозитория"""
        try:
            await query.edit_message_text("📁 Получаю детали репозитория...")
            
            repo_result = self.github_bot.get_repository_details(owner, repo_name)
            if repo_result['success']:
                text_result = self.github_bot.format_repository_details(repo_result)
                keyboard = [
                    [InlineKeyboardButton("📝 Issues", callback_data=f"issues_{owner}_{repo_name}")],
                    [InlineKeyboardButton("🔄 Pull Requests", callback_data=f"prs_{owner}_{repo_name}")],
                    [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{owner}_{repo_name}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text(f"❌ Ошибка: {repo_result['error']}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def show_repository_issues(self, query, owner, repo_name):
        """Показать Issues репозитория"""
        try:
            await query.edit_message_text("📝 Получаю Issues...")
            
            issues_result = self.github_bot.get_repository_issues(owner, repo_name)
            if issues_result['success']:
                text_result = self.github_bot.format_issues(issues_result)
                keyboard = [
                    [InlineKeyboardButton("🔄 Обновить", callback_data=f"issues_{owner}_{repo_name}")],
                    [InlineKeyboardButton("📁 Детали", callback_data=f"repo_{owner}_{repo_name}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text(f"❌ Ошибка: {issues_result['error']}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def show_repository_prs(self, query, owner, repo_name):
        """Показать Pull Requests репозитория"""
        try:
            await query.edit_message_text("🔄 Получаю Pull Requests...")
            
            prs_result = self.github_bot.get_repository_pull_requests(owner, repo_name)
            if prs_result['success']:
                text_result = self.github_bot.format_pull_requests(prs_result)
                keyboard = [
                    [InlineKeyboardButton("🔄 Обновить", callback_data=f"prs_{owner}_{repo_name}")],
                    [InlineKeyboardButton("📁 Детали", callback_data=f"repo_{owner}_{repo_name}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text(f"❌ Ошибка: {prs_result['error']}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def show_repository_stats(self, query, owner, repo_name):
        """Показать статистику репозитория"""
        try:
            await query.edit_message_text("📊 Получаю статистику...")
            
            stats_result = self.github_bot.get_repository_stats(owner, repo_name)
            if stats_result['success']:
                repo = stats_result['repository']
                languages = stats_result['languages']
                contributors = stats_result['top_contributors']
                
                text_result = f"""📊 **Статистика репозитория {repo['name']}**

📁 **Основная информация:**
⭐ Звезды: {repo['stars']}
🍴 Форки: {repo['forks']}
👀 Наблюдатели: {repo['watchers']}
📊 Размер: {repo['size']} KB
📝 Issues: {repo['open_issues']}
📅 Создан: {repo['created_at']}
🔄 Обновлен: {repo['updated_at']}

💻 **Языки программирования:**"""
                
                if languages:
                    total_bytes = sum(languages.values())
                    for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                        percentage = (bytes_count / total_bytes) * 100
                        text_result += f"\n• {lang}: {percentage:.1f}%"
                
                if contributors:
                    text_result += f"\n\n👥 **Топ контрибьюторы:**"
                    for i, contrib in enumerate(contributors[:5], 1):
                        text_result += f"\n{i}. {contrib['author']}: {contrib['total_commits']} коммитов"
                
                keyboard = [
                    [InlineKeyboardButton("📁 Детали", callback_data=f"repo_{owner}_{repo_name}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text(f"❌ Ошибка: {stats_result['error']}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def show_currency_menu(self, query):

        """Показать меню конвертера валют"""

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tools")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        self.input_modes[query.from_user.id] = "currency"
        await query.edit_message_text(
            "💱 **Конвертер валют**\n\nНапишите запрос следующим сообщением.\n\nПримеры: `100 USD` или `100 USD RUB`",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def show_file_converter_menu(self, query):

        """Показать меню конвертера файлов"""

        keyboard = [

            [InlineKeyboardButton("📄 Информация о форматах", callback_data="converter_info")],

            [InlineKeyboardButton("📄 PDF → Excel/Word", callback_data="pdf_converter")],

            [InlineKeyboardButton("🔙 Назад", callback_data="tools")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            "📄 **Конвертер файлов**\n\nКонвертируйте файлы между различными форматами!\n\n**Поддерживаемые форматы:**\n• PDF ↔ Word, TXT, HTML, Markdown\n• Word ↔ PDF, TXT, HTML, Markdown\n• Excel ↔ CSV, JSON, HTML\n• И многие другие!\n\n**Как использовать:**\n1. Отправьте файл боту\n2. Выберите формат для конвертации\n3. Получите конвертированный файл\n\n💡 **Совет:** Просто отправьте файл как документ!",

            parse_mode='Markdown',

            reply_markup=reply_markup

        )

    async def show_presentation_generator_menu(self, query):

        """Показать меню генератора презентаций"""

        keyboard = [

            [InlineKeyboardButton("📊 Бизнес презентация", callback_data="pres_business")],

            [InlineKeyboardButton("🎓 Образовательная", callback_data="pres_educational")],

            [InlineKeyboardButton("⚙️ Техническая", callback_data="pres_technical")],

            [InlineKeyboardButton("📈 Маркетинговая", callback_data="pres_marketing")],

            [InlineKeyboardButton("🔬 Исследовательская", callback_data="pres_research")],

            [InlineKeyboardButton("ℹ️ Информация", callback_data="pres_info")],

            [InlineKeyboardButton("🔙 Назад", callback_data="tools")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            "🎯 **Генератор презентаций**\n\nСоздавайте профессиональные презентации с помощью AI!\n\n**🔥 Популярные типы:**\n• **Бизнес** - для деловых встреч и проектов\n• **Образовательная** - для обучения и лекций\n• **Техническая** - для IT и разработки\n• **Маркетинговая** - для продаж и рекламы\n• **Исследовательская** - для научных работ\n\n**💡 Как работает:**\n1. Выберите тип презентации\n2. Опишите тему или вставьте текст\n3. AI создаст структуру и контент\n4. Получите презентацию в 4 форматах!\n\n**✨ Форматы вывода:**\n• 📊 PowerPoint (.pptx) - для редактирования\n• 📄 Word (.docx) - для печати\n• 📋 PDF (.pdf) - для чтения\n• 🌐 HTML (.html) - для веб-просмотра\n\n**🎨 Особенности:**\n• Автоматическое создание слайдов\n• Генерация изображений и диаграмм\n• Профессиональное оформление\n• Готово к использованию",

            parse_mode='Markdown',

            reply_markup=reply_markup

        )

    async def handle_presentation_callback(self, query):
        """Обработка callback'ов генератора презентаций"""
        try:
            callback_data = query.data
            
            if callback_data == "pres_info":
                # Показываем информацию о типах презентаций
                info_text = self.presentation_generator.format_presentation_info()
                keyboard = [
                    [InlineKeyboardButton("🔙 Назад", callback_data="presentation_generator")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    info_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                return
            
            # Определяем тип презентации
            presentation_type = callback_data.replace("pres_", "")
            
            # Сохраняем выбранный тип презентации
            user_id = query.from_user.id
            if not hasattr(self, 'user_presentation_types'):
                self.user_presentation_types = {}
            
            self.user_presentation_types[user_id] = presentation_type
            
            # Показываем инструкции
            type_names = {
                'business': 'Бизнес презентация',
                'educational': 'Образовательная презентация',
                'technical': 'Техническая презентация',
                'marketing': 'Маркетинговая презентация',
                'research': 'Исследовательская презентация'
            }
            
            type_name = type_names.get(presentation_type, presentation_type)
            
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data="presentation_generator")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🎯 **{type_name}**\n\n"
                f"Отлично! Вы выбрали {type_name.lower()}.\n\n"
                f"**Теперь опишите тему презентации:**\n\n"
                f"💡 **Примеры:**\n"
                f"• \"Сделай презентацию про искусственный интеллект\"\n"
                f"• \"Презентация о нашей компании и продуктах\"\n"
                f"• \"Объясни квантовые вычисления простыми словами\"\n"
                f"• \"Маркетинговая стратегия для стартапа\"\n\n"
                f"**Или прикрепите файл:**\n"
                f"• 📄 Текстовые файлы (.txt, .md, .docx)\n"
                f"• 📊 PDF документы\n"
                f"• 🌐 HTML файлы\n"
                f"• И другие текстовые форматы\n\n"
                f"**Или вставьте готовый текст:**\n"
                f"• Скопируйте текст из документа\n"
                f"• Вставьте в чат\n"
                f"• AI создаст структуру презентации\n\n"
                f"Просто напишите описание, прикрепите файл или вставьте текст!",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка обработки: {str(e)}")

    async def show_converter_info(self, query):

        """Показать информацию о поддерживаемых форматах"""

        keyboard = [

            [InlineKeyboardButton("🔙 Назад", callback_data="file_converter")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        info_text = self.file_converter.format_conversion_info()

        await query.edit_message_text(

            info_text,

            parse_mode='Markdown',

            reply_markup=reply_markup

        )

    async def show_pdf_converter_menu(self, query):

        """Показать специальное меню для конвертации PDF"""

        keyboard = [

            [InlineKeyboardButton("📊 PDF → Excel", callback_data="pdf_to_excel")],

            [InlineKeyboardButton("📄 PDF → Word", callback_data="pdf_to_word")],

            [InlineKeyboardButton("📝 PDF → TXT", callback_data="pdf_to_txt")],

            [InlineKeyboardButton("🌐 PDF → HTML", callback_data="pdf_to_html")],

            [InlineKeyboardButton("📋 PDF → Markdown", callback_data="pdf_to_md")],

            [InlineKeyboardButton("🔙 Назад", callback_data="file_converter")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(

            "📄 **PDF Конвертер**\n\nСпециальные функции для конвертации PDF файлов:\n\n**🔥 Популярные конвертации:**\n• **PDF → Excel** - извлекает таблицы и текст в Excel\n• **PDF → Word** - конвертирует в редактируемый Word документ\n• **PDF → TXT** - извлекает весь текст\n• **PDF → HTML** - создает веб-версию\n• **PDF → Markdown** - конвертирует в Markdown\n\n**💡 Особенности:**\n• Автоматическое извлечение таблиц\n• Сохранение структуры документа\n• Поддержка многостраничных PDF\n• Высокое качество конвертации\n\n**Как использовать:**\n1. Выберите тип конвертации\n2. Отправьте PDF файл\n3. Получите результат",

            parse_mode='Markdown',

            reply_markup=reply_markup

        )

    async def handle_pdf_conversion_callback(self, query):
        """Обработка специальных PDF конвертаций"""
        try:
            user_id = query.from_user.id
            
            # Парсим callback data
            callback_data = query.data
            target_format = callback_data.replace("pdf_to_", "")
            
            # Проверяем, есть ли данные для конвертации
            if not hasattr(self, 'pending_conversions') or user_id not in self.pending_conversions:
                await query.edit_message_text(
                    f"📄 **PDF → {target_format.upper()}**\n\n"
                    f"Отправьте PDF файл для конвертации в {target_format.upper()}!\n\n"
                    f"💡 **Совет:** Просто отправьте PDF файл как документ."
                )
                return
            
            # Получаем данные файла
            file_data = self.pending_conversions[user_id]
            file_content = file_data['file_content']
            filename = file_data['filename']
            
            # Проверяем, что это PDF файл
            if not filename.lower().endswith('.pdf'):
                await query.edit_message_text("❌ Пожалуйста, отправьте PDF файл для этой конвертации.")
                return
            
            await query.edit_message_text(f"🔄 Конвертирую PDF в {target_format.upper()}...")
            
            try:
                # Выполняем специальную конвертацию PDF
                if target_format == 'excel':
                    converted_content = self.file_converter.convert_pdf_to_excel(file_content, filename)
                    new_filename = filename.replace('.pdf', '.xlsx')
                elif target_format == 'word':
                    converted_content = self.file_converter.convert_pdf_to_word(file_content, filename)
                    new_filename = filename.replace('.pdf', '.docx')
                elif target_format == 'txt':
                    text_content = self.file_converter.convert_pdf_to_text(file_content)
                    converted_content = text_content.encode('utf-8')
                    new_filename = filename.replace('.pdf', '.txt')
                elif target_format == 'html':
                    text_content = self.file_converter.convert_pdf_to_text(file_content)
                    html_content = self.file_converter.convert_text_to_html(text_content)
                    converted_content = html_content.encode('utf-8')
                    new_filename = filename.replace('.pdf', '.html')
                elif target_format == 'md':
                    text_content = self.file_converter.convert_pdf_to_text(file_content)
                    md_content = self.file_converter.convert_text_to_markdown(text_content)
                    converted_content = md_content.encode('utf-8')
                    new_filename = filename.replace('.pdf', '.md')
                else:
                    await query.edit_message_text(f"❌ Неподдерживаемый формат: {target_format}")
                    return
                
                # Отправляем конвертированный файл
                await query.message.reply_document(
                    document=converted_content,
                    filename=new_filename,
                    caption=f"✅ **PDF конвертация завершена!**\n\n"
                           f"📁 **Исходный файл:** {filename}\n"
                           f"📄 **Новый файл:** {new_filename}\n"
                           f"🔄 **Конвертация:** PDF → {target_format.upper()}\n\n"
                           f"💡 **Особенности:**\n"
                           f"• Извлечен весь текст и таблицы\n"
                           f"• Сохранена структура документа\n"
                           f"• Готов к редактированию",
                    parse_mode='Markdown'
                )
                
                # Отправляем кнопки
                keyboard = [
                    [InlineKeyboardButton("📄 Конвертировать еще PDF", callback_data="pdf_converter")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="file_converter")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "💡 Что дальше?",
                    reply_markup=reply_markup
                )
                
                # Удаляем данные из памяти
                del self.pending_conversions[user_id]
                
            except Exception as e:
                await query.edit_message_text(f"❌ Ошибка конвертации PDF: {str(e)}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка обработки: {str(e)}")

    async def handle_conversion_callback(self, query):
        """Обработка callback'ов конвертации файлов"""
        try:
            user_id = query.from_user.id
            
            # Проверяем, есть ли данные для конвертации
            if not hasattr(self, 'pending_conversions') or user_id not in self.pending_conversions:
                await query.edit_message_text("❌ Нет данных для конвертации. Отправьте файл заново.")
                return
            
            # Парсим callback data
            callback_data = query.data
            parts = callback_data.split('_')
            if len(parts) < 3:
                await query.edit_message_text("❌ Неверный формат callback данных.")
                return
            
            source_format = parts[1]
            target_format = parts[2]
            
            # Получаем данные файла
            file_data = self.pending_conversions[user_id]
            file_content = file_data['file_content']
            filename = file_data['filename']
            
            await query.edit_message_text(f"🔄 Конвертирую {filename} из {source_format} в {target_format}...")
            
            try:
                # Выполняем конвертацию
                converted_content, new_filename = self.file_converter.convert_file(
                    file_content, source_format, target_format, filename
                )
                
                # Отправляем конвертированный файл
                await query.message.reply_document(
                    document=converted_content,
                    filename=new_filename,
                    caption=f"✅ **Конвертация завершена!**\n\n"
                           f"📁 **Исходный файл:** {filename}\n"
                           f"📄 **Новый файл:** {new_filename}\n"
                           f"🔄 **Конвертация:** {source_format} → {target_format}",
                    parse_mode='Markdown'
                )
                
                # Отправляем кнопки
                keyboard = [
                    [InlineKeyboardButton("📄 Конвертировать еще", callback_data="file_converter")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "💡 Что дальше?",
                    reply_markup=reply_markup
                )
                
                # Удаляем данные из памяти
                del self.pending_conversions[user_id]
                
            except Exception as e:
                await query.edit_message_text(f"❌ Ошибка конвертации: {str(e)}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка обработки: {str(e)}")

    async def convert_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Конвертировать валюту"""

        if len(context.args) < 2:

            await update.message.reply_text("❌ Укажите сумму и валюту!\nПример: /currency 100 USD")

            return

        

        try:

            amount = float(context.args[0])

            currency = context.args[1].upper()

        except ValueError:

            await update.message.reply_text("❌ Неверный формат суммы!")

            return

        

        # Заглушка для демонстрации (в реальном проекте используйте ExchangeRate API)

        rates = {

            'USD': 95.5,

            'EUR': 102.3,

            'GBP': 118.7,

            'RUB': 1.0

        }

        

        if currency not in rates:

            await update.message.reply_text("❌ Неподдерживаемая валюта! Доступны: USD, EUR, GBP")

            return

        

        rub_amount = amount * rates[currency]

        

        currency_text = f"""

💱 **Конвертация валют:**



💰 {amount} {currency} = {rub_amount:.2f} RUB

📈 Курс: 1 {currency} = {rates[currency]} RUB

        """

        

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tools")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(currency_text, parse_mode='Markdown', reply_markup=reply_markup)



    async def show_code_menu(self, query):

        """Показать меню генератора кода"""

        self.input_modes[query.from_user.id] = "code"
        await query.edit_message_text(
            "💻 **Генератор кода**\n\nНапишите язык и задачу следующим сообщением.\n\nПример: `python функция для сортировки списка`",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
        )



    async def generate_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Сгенерировать код"""

        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Укажите язык и описание!\n"
                "Пример: `python функция для сортировки`",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
            )

            return

        

        language = context.args[0].lower()

        description = ' '.join(context.args[1:])

        

        # Простые примеры кода

        code_examples = {

            'python': f"""

```python

def {description.replace(' ', '_')}():

    \"\"\"

    Функция для: {description}

    \"\"\"

    # Ваш код здесь

    pass



# Пример использования

result = {description.replace(' ', '_')}()

print(result)

```""",

            'javascript': f"""

```javascript

function {description.replace(' ', '')}() {{

    // Функция для: {description}

    // Ваш код здесь

}}



// Пример использования

const result = {description.replace(' ', '')}();

console.log(result);

```""",

            'java': f"""

```java

public class {description.replace(' ', '')} {{

    public static void {description.replace(' ', '')}() {{

        // Функция для: {description}

        // Ваш код здесь

    }}

    

    public static void main(String[] args) {{

        {description.replace(' ', '')}();

    }}

}}

```"""

        }

        

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tools")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if language in code_examples:

            await update.message.reply_text(code_examples[language], parse_mode='Markdown', reply_markup=reply_markup)

        else:

            await update.message.reply_text("❌ Неподдерживаемый язык! Доступны: python, javascript, java")



    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Обработчик текстовых сообщений"""

        user_id = update.effective_user.id

        text = update.message.text

        

        # Проверяем, активен ли режим чата с AI

        if user_id in self.ai_chat_mode and self.ai_chat_mode[user_id]:

            await self.handle_ai_chat_message(update, text)

            return
        
        # Проверяем, находится ли пользователь в процессе создания документа
        if user_id in self.document_states:
            state = self.document_states[user_id]
            
            # Если это кастомный формат и нужно получить инструкцию
            if state.get('step') == 'instruction':
                state['instruction'] = text
                state['step'] = 'text'
                state['title'] = 'Документ'
                
                keyboard = [
                    [InlineKeyboardButton("❌ Отмена", callback_data="create_document_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"✅ Инструкция сохранена!\n\n"
                    f"📝 Теперь отправь текст для обработки:",
                    reply_markup=reply_markup
                )
                return
            
            # Обрабатываем текст и создаем документ
            doc_type = state.get('type', 'summary')
            
            status_msg = await update.message.reply_text(f"📝 Обрабатываю текст и создаю {doc_type}...")
            
            try:
                # Создаем конспект/документ через Claude
                if doc_type == 'summary':
                    prompt = f"""Создай подробный структурированный конспект из следующего текста.

Текст:
{text}

Требования к конспекту:
- Структурированный формат с четкими заголовками
- Основные тезисы и ключевые моменты
- Четкая структура с нумерацией (1., 2., 3.) и подпунктами
- Сохрани важные детали
- Используй красивое форматирование с отступами и структурированными списками
- НЕ используй markdown форматирование: никаких ##, ###, **, ***
- Заголовки пиши просто текстом, выделяя их через структуру и нумерацию
- Используй отступы для подпунктов
- Делай конспект читабельным и красиво оформленным

Верни только конспект без дополнительных комментариев."""
                elif doc_type == 'notes':
                    prompt = f"""Создай структурированные заметки из следующего текста.

Текст:
{text}

Требования:
- Четкая структура с разделами
- Ключевые моменты выделены
- Удобный формат для изучения
- Используй форматирование Markdown"""
                else:  # custom
                    custom_instruction = state.get('instruction', 'Обработай текст и создай документ')
                    prompt = f"""{custom_instruction}

Текст для обработки:
{text}

Верни обработанный текст в структурированном формате с Markdown форматированием."""
                
                # Получаем обработанный текст от Claude
                processed_text = self.claude.ask_question(prompt)
                
                # Убираем markdown форматирование из конспектов
                if doc_type == 'summary':
                    # Удаляем ## и ### в начале строк (markdown заголовки)
                    processed_text = re.sub(r'^#{2,3}\s+', '', processed_text, flags=re.MULTILINE)
                    # Удаляем тройные звездочки ***
                    processed_text = re.sub(r'\*{3,}', '', processed_text)
                    # Удаляем двойные звездочки ** (жирный текст)
                    processed_text = re.sub(r'\*\*', '', processed_text)
                
                # Создаем Word документ
                doc_title = state.get('title', f'{doc_type.capitalize()}')
                doc_buffer = self.document_generator.create_document(
                    title=doc_title,
                    content=processed_text,
                    style='summary' if doc_type == 'summary' else 'default'
                )
                
                # Удаляем состояние
                del self.document_states[user_id]
                
                # Отправляем документ
                await status_msg.delete()
                await update.message.reply_document(
                    document=doc_buffer,
                    filename=f"{doc_title}.docx",
                    caption=f"✅ Документ создан!\n\n📄 {doc_title}"
                )
                
                keyboard = [
                    [InlineKeyboardButton("📄 Создать еще", callback_data="create_document_menu")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "💡 Документ готов! Что дальше?",
                    reply_markup=reply_markup
                )
                
            except Exception as e:
                logger.error(f"Ошибка создания документа: {e}")
                await status_msg.edit_text(f"❌ Ошибка создания документа: {str(e)}")
                del self.document_states[user_id]
            return
        
        # Проверяем, находится ли пользователь в процессе добавления напоминания/задачи
        if user_id in self.reminder_states:
            state = self.reminder_states[user_id]
            if state.get('type') == 'reminder_text':
                # Пользователь ввел текст напоминания, сохраняем и просим выбрать время
                state['text'] = text
                state['type'] = 'reminder_time'
                await self.show_reminder_time_selection(update)
                return
            elif state.get('type') == 'reminder_custom_time':
                # Пользователь ввел свое время для напоминания
                reminder_text = state.get('text', '')
                if reminder_text:
                    reminder = self.reminder_helper.add_reminder(user_id, reminder_text, text)
                    del self.reminder_states[user_id]
                    
                    if reminder:
                        reminder_time = datetime.fromisoformat(reminder['time'])
                        time_display = reminder_time.strftime("%d.%m.%Y %H:%M")
                        
                        keyboard = [
                            [InlineKeyboardButton("⏰ Мои напоминания", callback_data="list_reminders")],
                            [InlineKeyboardButton("🔙 В меню", callback_data="reminders_menu")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await update.message.reply_text(
                            f"✅ **Напоминание создано!**\n\n"
                            f"📝 {reminder_text}\n"
                            f"⏰ {time_display}\n\n"
                            f"Я напомню тебе в указанное время!",
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                        )
                    else:
                        await update.message.reply_text(
                            "❌ Не удалось создать напоминание.\n\n"
                            "Проверь формат времени! Попробуй еще раз:"
                        )
                        # Оставляем состояние для повторного ввода
                else:
                    await update.message.reply_text("❌ Ошибка: текст напоминания не найден!")
                    del self.reminder_states[user_id]
                return
            elif state.get('type') == 'task_text':
                # Пользователь ввел текст задачи, добавляем задачу
                priority = state.get('priority', 'normal')
                task = self.reminder_helper.add_task(user_id, text, priority)
                del self.reminder_states[user_id]
                
                if task:
                    priority_emoji = {"low": "🟢", "normal": "🟡", "high": "🔴"}
                    emoji = priority_emoji.get(priority, "🟡")
                    
                    keyboard = [
                        [InlineKeyboardButton("✅ Мои задачи", callback_data="list_tasks")],
                        [InlineKeyboardButton("🔙 В меню", callback_data="reminders_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"✅ **Задача добавлена!**\n\n"
                        f"{emoji} {text}\n\n"
                        f"Приоритет: {priority}",
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text("❌ Не удалось добавить задачу!")
                return

        

        # Проверяем, играет ли пользователь в "Угадай число"
        if user_id in self.input_modes:
            mode = self.input_modes.pop(user_id)
            fake_context = SimpleNamespace(args=text.split())
            if mode == "weather":
                await self.get_weather(update, fake_context)
                return
            if mode == "translate":
                await self.translate_command(update, fake_context)
                return
            if mode == "music":
                await self.music_search_command(update, fake_context)
                return
            if mode == "qr":
                await self.create_qr_code(update, fake_context)
                return
            if mode == "search":
                await self.web_search_command(update, fake_context)
                return
            if mode == "news":
                await self.news_search_command(update, fake_context)
                return
            if mode == "image":
                await self.generate_image_command(update, fake_context)
                return
            if mode == "wallpaper":
                await self.generate_wallpaper_command(update, fake_context)
                return
            if mode == "gif":
                await self.generate_gif_command(update, fake_context)
                return
            if mode == "meme":
                await self.generate_meme_command(update, fake_context)
                return
            if mode == "thinking":
                await self.thinking_gif_command(update, fake_context)
                return
            if mode == "currency":
                await self.convert_currency(update, fake_context)
                return
            if mode == "code":
                await self.generate_code(update, fake_context)
                return
            if mode == "remind":
                await self.remind_command(update, fake_context)
                return
            if mode == "task":
                await self.task_command(update, fake_context)
                return

        # Проверяем, играет ли пользователь в "Угадай число"

        if user_id in self.user_games and self.user_games[user_id]['type'] == 'guess':

            await self.handle_guess_game(update, context)

            return

        

        # Обработка GitHub команд через текстовые сообщения
        if (text.startswith('github ') or 
            any(keyword in text.lower() for keyword in ['repo ', 'issues ', 'prs ', 'stats ']) or
            text.lower() in ['kirill2006788-cloud', 'microsoft', 'facebook', 'google'] or
            'python bot' in text.lower() or 'javascript framework' in text.lower() or
            'machine learning' in text.lower() or 'web development' in text.lower()):
            await self.handle_github_text_commands(update, text)
            return

        # Обработка генерации презентаций
        if (hasattr(self, 'user_presentation_types') and 
            user_id in self.user_presentation_types and
            len(text) > 10):  # Минимальная длина текста
            await self.handle_presentation_generation(update, text)
            return

        # Игнорируем остальные сообщения (не отвечаем ничего)



    async def handle_github_text_commands(self, update: Update, text: str):
        """Обработка GitHub команд через текстовые сообщения"""
        try:
            text_lower = text.lower().strip()
            
            # Обработка простых имен пользователей
            if text_lower in ['kirill2006788-cloud', 'microsoft', 'facebook', 'google']:
                await update.message.reply_text("👤 Получаю информацию о пользователе...")
                
                user_result = self.github_bot.get_user_info(text)
                if user_result['success']:
                    text_result = self.github_bot.format_user_info(user_result)
                    keyboard = [
                        [InlineKeyboardButton("📁 Репозитории", callback_data=f"user_repos_{text}")],
                        [InlineKeyboardButton("🔄 Другой пользователь", callback_data="github_user")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                else:
                    await update.message.reply_text(f"❌ Ошибка: {user_result['error']}")
                return
            
            # Обработка простых поисковых запросов
            if text_lower in ['python bot', 'javascript framework', 'machine learning', 'web development']:
                await update.message.reply_text("🔍 Ищу репозитории...")
                
                search_result = self.github_bot.search_repositories(text)
                if search_result['success']:
                    text_result = self.github_bot.format_search_results(search_result)
                    keyboard = [
                        [InlineKeyboardButton("🔄 Искать еще", callback_data="github_search")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                else:
                    await update.message.reply_text(f"❌ Ошибка поиска: {search_result['error']}")
                return
            
            # Обработка команд вида "repo owner/repo"
            if text.lower().startswith('repo '):
                repo_input = text[5:].strip()
                if '/' in repo_input:
                    owner, repo_name = repo_input.split('/', 1)
                    await update.message.reply_text("📁 Получаю детали репозитория...")
                    
                    repo_result = self.github_bot.get_repository_details(owner, repo_name)
                    if repo_result['success']:
                        text_result = self.github_bot.format_repository_details(repo_result)
                        keyboard = [
                            [InlineKeyboardButton("📝 Issues", callback_data=f"issues_{owner}_{repo_name}")],
                            [InlineKeyboardButton("🔄 Pull Requests", callback_data=f"prs_{owner}_{repo_name}")],
                            [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{owner}_{repo_name}")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(f"❌ Ошибка: {repo_result['error']}")
                else:
                    await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `repo microsoft/vscode`")
                return
            
            # Обработка команд вида "issues owner/repo"
            elif text.lower().startswith('issues '):
                repo_input = text[7:].strip()
                if '/' in repo_input:
                    owner, repo_name = repo_input.split('/', 1)
                    await update.message.reply_text("📝 Получаю Issues...")
                    
                    issues_result = self.github_bot.get_repository_issues(owner, repo_name)
                    if issues_result['success']:
                        text_result = self.github_bot.format_issues(issues_result)
                        keyboard = [
                            [InlineKeyboardButton("🔄 Обновить", callback_data=f"issues_{owner}_{repo_name}")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(f"❌ Ошибка: {issues_result['error']}")
                else:
                    await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `issues facebook/react`")
                return
            
            # Обработка команд вида "prs owner/repo"
            elif text.lower().startswith('prs '):
                repo_input = text[4:].strip()
                if '/' in repo_input:
                    owner, repo_name = repo_input.split('/', 1)
                    await update.message.reply_text("🔄 Получаю Pull Requests...")
                    
                    prs_result = self.github_bot.get_repository_pull_requests(owner, repo_name)
                    if prs_result['success']:
                        text_result = self.github_bot.format_pull_requests(prs_result)
                        keyboard = [
                            [InlineKeyboardButton("🔄 Обновить", callback_data=f"prs_{owner}_{repo_name}")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(f"❌ Ошибка: {prs_result['error']}")
                else:
                    await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `prs nodejs/node`")
                return
            
            # Обработка команд вида "stats owner/repo"
            elif text.lower().startswith('stats '):
                repo_input = text[6:].strip()
                if '/' in repo_input:
                    owner, repo_name = repo_input.split('/', 1)
                    await update.message.reply_text("📊 Получаю статистику...")
                    
                    stats_result = self.github_bot.get_repository_stats(owner, repo_name)
                    if stats_result['success']:
                        repo = stats_result['repository']
                        languages = stats_result['languages']
                        contributors = stats_result['top_contributors']
                        
                        text_result = f"""📊 **Статистика репозитория {repo['name']}**

📁 **Основная информация:**
⭐ Звезды: {repo['stars']}
🍴 Форки: {repo['forks']}
👀 Наблюдатели: {repo['watchers']}
📊 Размер: {repo['size']} KB
📝 Issues: {repo['open_issues']}
📅 Создан: {repo['created_at']}
🔄 Обновлен: {repo['updated_at']}

💻 **Языки программирования:**"""
                        
                        if languages:
                            total_bytes = sum(languages.values())
                            for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                                percentage = (bytes_count / total_bytes) * 100
                                text_result += f"\n• {lang}: {percentage:.1f}%"
                        
                        if contributors:
                            text_result += f"\n\n👥 **Топ контрибьюторы:**"
                            for i, contrib in enumerate(contributors[:5], 1):
                                text_result += f"\n{i}. {contrib['author']}: {contrib['total_commits']} коммитов"
                        
                        keyboard = [
                            [InlineKeyboardButton("📁 Детали", callback_data=f"repo_{owner}_{repo_name}")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(f"❌ Ошибка: {stats_result['error']}")
                else:
                    await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `stats google/tensorflow`")
                return
            
            # Обработка расширенного поиска
            elif text.lower().startswith('github advanced '):
                parts = text[16:].strip().split()
                if len(parts) >= 1:
                    query = parts[0]
                    language = parts[1] if len(parts) > 1 else None
                    sort = parts[2] if len(parts) > 2 else 'stars'
                    
                    await update.message.reply_text("🔍 Выполняю расширенный поиск...")
                    
                    search_result = self.github_bot.search_repositories_advanced(query, language, sort)
                    if search_result['success']:
                        text_result = f"🔍 **Расширенный поиск**\n"
                        text_result += f"📝 **Запрос:** {search_result['query']}\n"
                        if search_result['language']:
                            text_result += f"💻 **Язык:** {search_result['language']}\n"
                        text_result += f"📊 **Сортировка:** {search_result['sort']}\n"
                        text_result += f"📈 **Найдено:** {search_result['total_count']}\n\n"
                        
                        for i, repo in enumerate(search_result['repositories'], 1):
                            text_result += f"**{i}.** {self.github_bot.format_repository_info(repo)}\n\n"
                        
                        keyboard = [
                            [InlineKeyboardButton("🔄 Искать еще", callback_data="github_advanced_search")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(f"❌ Ошибка поиска: {search_result['error']}")
                else:
                    await update.message.reply_text("❌ Укажите поисковый запрос!\nПример: `github advanced python bot stars`")
                return
            
            # Обработка обычного поиска
            elif text.lower().startswith('github search '):
                query = text[14:].strip()
                if query:
                    await update.message.reply_text("🔍 Ищу репозитории...")
                    
                    search_result = self.github_bot.search_repositories(query)
                    if search_result['success']:
                        text_result = self.github_bot.format_search_results(search_result)
                        keyboard = [
                            [InlineKeyboardButton("🔄 Искать еще", callback_data="github_search")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(f"❌ Ошибка поиска: {search_result['error']}")
                else:
                    await update.message.reply_text("❌ Укажите поисковый запрос!\nПример: `github search python bot`")
                return
            
            # Обработка информации о пользователе
            elif text.lower().startswith('github user '):
                username = text[12:].strip()
                if username:
                    await update.message.reply_text("👤 Получаю информацию о пользователе...")
                    
                    user_result = self.github_bot.get_user_info(username)
                    if user_result['success']:
                        text_result = self.github_bot.format_user_info(user_result)
                        keyboard = [
                            [InlineKeyboardButton("📁 Репозитории", callback_data=f"user_repos_{username}")],
                            [InlineKeyboardButton("🔄 Другой пользователь", callback_data="github_user")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(f"❌ Ошибка: {user_result['error']}")
                else:
                    await update.message.reply_text("❌ Укажите имя пользователя!\nПример: `github user kirill2006788-cloud`")
                return
            
            # Обработка трендовых репозиториев
            elif text.lower().startswith('github trending'):
                await update.message.reply_text("🔥 Получаю трендовые репозитории...")
                
                trending_result = self.github_bot.get_trending_repositories()
                if trending_result['success']:
                    text_result = f"🔥 **Трендовые репозитории** ({trending_result['language']})\n\n"
                    for i, repo in enumerate(trending_result['repositories'], 1):
                        text_result += f"**{i}.** {self.github_bot.format_repository_info(repo)}\n\n"
                    
                    keyboard = [
                        [InlineKeyboardButton("🔄 Обновить", callback_data="github_trending")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
                else:
                    await update.message.reply_text(f"❌ Ошибка получения трендов: {trending_result['error']}")
                return
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обработки команды: {str(e)}")

    async def handle_presentation_generation(self, update: Update, text: str):
        """Обработка генерации презентаций"""
        try:
            user_id = update.effective_user.id
            presentation_type = self.user_presentation_types.get(user_id, 'business')
            
            await update.message.reply_text("🎯 Создаю презентацию... Это может занять несколько минут.")
            
            try:
                # Генерируем презентацию
                presentation_content, filename = self.presentation_generator.generate_presentation(
                    text, presentation_type, user_id
                )
                
                # Отправляем PowerPoint файл
                await update.message.reply_document(
                    document=presentation_content,
                    filename=filename,
                    caption=f"✅ **Презентация готова!**\n\n"
                           f"📄 **Файл:** {filename}\n"
                           f"🎯 **Тип:** {presentation_type.title()} презентация\n"
                           f"📊 **Слайдов:** {len(self.presentation_generator.presentation_templates[presentation_type]['structure'])}\n\n"
                           f"💡 **Особенности:**\n"
                           f"• Профессиональное оформление\n"
                           f"• Структурированный контент\n"
                           f"• Готово к использованию",
                    parse_mode='Markdown'
                )
                
                # Создаем дополнительные форматы
                additional_files = []
                
                # HTML версия
                try:
                    html_content = self.presentation_generator.create_html_presentation(text, presentation_type)
                    html_filename = filename.replace('.pptx', '.html')
                    additional_files.append(("HTML", html_content.encode('utf-8'), html_filename))
                except Exception as e:
                    logger.warning(f"Не удалось создать HTML версию: {e}")
                
                # Word версия
                try:
                    word_content, word_filename = self.presentation_generator.create_word_presentation(text, presentation_type)
                    additional_files.append(("Word", word_content, word_filename))
                except Exception as e:
                    logger.warning(f"Не удалось создать Word версию: {e}")
                
                # PDF версия
                try:
                    pdf_content, pdf_filename = self.presentation_generator.create_pdf_presentation(text, presentation_type)
                    additional_files.append(("PDF", pdf_content, pdf_filename))
                except Exception as e:
                    logger.warning(f"Не удалось создать PDF версию: {e}")
                
                # Отправляем дополнительные файлы
                for format_name, content, filename in additional_files:
                    try:
                        await update.message.reply_document(
                            document=content,
                            filename=filename,
                            caption=f"📄 **{format_name} версия презентации**\n\nГотово к использованию",
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.warning(f"Не удалось отправить {format_name} файл: {e}")
                
                # Отправляем кнопки
                keyboard = [
                    [InlineKeyboardButton("🎯 Создать еще презентацию", callback_data="presentation_generator")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "💡 Что дальше?",
                    reply_markup=reply_markup
                )
                
                # Удаляем тип презентации из памяти
                del self.user_presentation_types[user_id]
                
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка генерации презентации: {str(e)}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обработки: {str(e)}")

    async def handle_presentation_from_file(self, update: Update, file_content: bytes, filename: str):
        """Обработка файлов для генерации презентаций"""
        try:
            user_id = update.effective_user.id
            presentation_type = self.user_presentation_types.get(user_id, 'business')
            
            await update.message.reply_text(f"📄 Обрабатываю файл {filename} для презентации...")
            
            # Пытаемся декодировать файл как текст
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = file_content.decode('cp1251')
                except UnicodeDecodeError:
                    try:
                        text_content = file_content.decode('latin-1')
                    except UnicodeDecodeError:
                        await update.message.reply_text(
                            "❌ Не удалось декодировать файл как текст.\n"
                            "Для генерации презентаций нужны текстовые файлы.\n\n"
                            "💡 **Поддерживаемые форматы:**\n"
                            "• .txt, .md, .docx, .pdf\n"
                            "• .rtf, .html, .xml\n"
                            "• И другие текстовые форматы"
                        )
                        return
            
            # Проверяем размер
            if len(text_content) > 50000:  # Ограничение для презентаций
                await update.message.reply_text(
                    "❌ Файл слишком большой для генерации презентации.\n"
                    "Максимальный размер: 50KB\n\n"
                    "💡 **Совет:** Разделите текст на части или сократите содержимое."
                )
                return
            
            if len(text_content) < 100:  # Минимальный размер
                await update.message.reply_text(
                    "❌ Файл слишком короткий для генерации презентации.\n"
                    "Минимум: 100 символов\n\n"
                    "💡 **Совет:** Добавьте больше текста или опишите тему подробнее."
                )
                return
            
            # Генерируем презентацию из файла
            await self.handle_presentation_generation(update, text_content)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обработки файла: {str(e)}")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик документов для создания GitHub Gists и конвертации файлов"""
        # Проверяем, находится ли пользователь в процессе создания документа
        user_id = update.effective_user.id
        if user_id in self.document_states:
            # Пользователь отправил файл для создания документа
            document = update.message.document
            
            if document:
                # Скачиваем файл
                file = await context.bot.get_file(document.file_id)
                
                # Проверяем тип файла
                file_name = document.file_name or "document.txt"
                file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
                
                # Поддерживаемые текстовые форматы
                text_extensions = ['txt', 'md', 'docx', 'pdf']
                
                if file_ext in text_extensions:
                    status_msg = await update.message.reply_text(f"📥 Скачиваю файл {file_name}...")
                    
                    try:
                        # Скачиваем файл
                        file_content = await file.download_as_bytearray()
                        
                        # Извлекаем текст в зависимости от формата
                        text_content = ""
                        
                        if file_ext == 'txt' or file_ext == 'md':
                            text_content = file_content.decode('utf-8', errors='ignore')
                        elif file_ext == 'docx':
                            # Используем docx2txt для извлечения текста
                            import docx2txt
                            import io
                            text_content = docx2txt.process(io.BytesIO(file_content))
                        elif file_ext == 'pdf':
                            # Используем pdfplumber для извлечения текста
                            import pdfplumber
                            import io
                            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                                text_content = "\n".join([page.extract_text() or "" for page in pdf.pages])
                        
                        if not text_content.strip():
                            await status_msg.edit_text("❌ Не удалось извлечь текст из файла. Убедись, что файл содержит текст.")
                            return
                        
                        # Ограничиваем длину текста (Claude имеет лимиты)
                        if len(text_content) > 50000:
                            text_content = text_content[:50000] + "\n\n[Текст обрезан из-за ограничений длины]"
                        
                        await status_msg.edit_text(f"📝 Извлечено {len(text_content)} символов. Обрабатываю...")
                        
                        # Используем тот же код обработки, что и для текстовых сообщений
                        state = self.document_states[user_id]
                        doc_type = state.get('type', 'summary')
                        
                        # Создаем конспект/документ через Claude
                        if doc_type == 'summary':
                            prompt = f"""Создай подробный структурированный конспект из следующего текста.

Текст:
{text_content}

Требования к конспекту:
- Структурированный формат с четкими заголовками
- Основные тезисы и ключевые моменты
- Четкая структура с нумерацией (1., 2., 3.) и подпунктами
- Сохрани важные детали
- Используй красивое форматирование с отступами и структурированными списками
- НЕ используй markdown форматирование: никаких ##, ###, **, ***
- Заголовки пиши просто текстом, выделяя их через структуру и нумерацию
- Используй отступы для подпунктов
- Делай конспект читабельным и красиво оформленным

Верни только конспект без дополнительных комментариев."""
                        elif doc_type == 'notes':
                            prompt = f"""Создай структурированные заметки из следующего текста.

Текст:
{text_content}

Требования:
- Четкая структура с разделами
- Ключевые моменты выделены
- Удобный формат для изучения
- Используй форматирование Markdown"""
                        else:  # custom
                            custom_instruction = state.get('instruction', 'Обработай текст и создай документ')
                            prompt = f"""{custom_instruction}

Текст для обработки:
{text_content}

Верни обработанный текст в структурированном формате с Markdown форматированием."""
                        
                        # Получаем обработанный текст от Claude
                        processed_text = self.claude.ask_question(prompt)
                        
                        # Убираем markdown форматирование из конспектов
                        if doc_type == 'summary':
                            # Удаляем ## и ### в начале строк (markdown заголовки)
                            processed_text = re.sub(r'^#{2,3}\s+', '', processed_text, flags=re.MULTILINE)
                            # Удаляем тройные звездочки ***
                            processed_text = re.sub(r'\*{3,}', '', processed_text)
                            # Удаляем двойные звездочки ** (жирный текст)
                            processed_text = re.sub(r'\*\*', '', processed_text)
                        
                        # Создаем Word документ
                        doc_title = state.get('title', f'{doc_type.capitalize()}')
                        doc_buffer = self.document_generator.create_document(
                            title=doc_title,
                            content=processed_text,
                            style='summary' if doc_type == 'summary' else 'default'
                        )
                        
                        # Удаляем состояние
                        del self.document_states[user_id]
                        
                        # Отправляем документ
                        await status_msg.delete()
                        await update.message.reply_document(
                            document=doc_buffer,
                            filename=f"{doc_title}.docx",
                            caption=f"✅ Документ создан из файла {file_name}!\n\n📄 {doc_title}"
                        )
                        
                        keyboard = [
                            [InlineKeyboardButton("📄 Создать еще", callback_data="create_document_menu")],
                            [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(
                            "💡 Документ готов! Что дальше?",
                            reply_markup=reply_markup
                        )
                        
                    except Exception as e:
                        logger.error(f"Ошибка обработки файла для документа: {e}")
                        await status_msg.edit_text(f"❌ Ошибка обработки файла: {str(e)}")
                        del self.document_states[user_id]
                else:
                    await update.message.reply_text(
                        f"❌ Неподдерживаемый формат файла: {file_ext}\n\n"
                        f"Поддерживаются: txt, md, docx, pdf"
                    )
            return
        
        # Обычная обработка документов (конвертация и т.д.)
        try:
            document = update.message.document
            file_id = document.file_id
            filename = document.file_name or "file.txt"
            
            # Получаем файл
            file = await context.bot.get_file(file_id)
            file_content = await file.download_as_bytearray()
            
            # Определяем тип файла
            file_type = self.github_bot.detect_file_type(filename)
            source_format = self.file_converter.detect_file_type(filename)
            
            # Проверяем, находится ли пользователь в режиме генерации презентаций
            user_id = update.effective_user.id
            if (hasattr(self, 'user_presentation_types') and 
                user_id in self.user_presentation_types):
                await self.handle_presentation_from_file(update, file_content, filename)
                return
            
            # Проверяем, поддерживается ли конвертация
            if self.file_converter.is_supported_format(source_format):
                await self.handle_file_conversion(update, file_content, filename, source_format)
                return
            
            # Если конвертация не поддерживается, пробуем создать Gist
            # Пытаемся декодировать как текст
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # Если не удается декодировать как UTF-8, пробуем другие кодировки
                try:
                    text_content = file_content.decode('cp1251')
                except UnicodeDecodeError:
                    try:
                        text_content = file_content.decode('latin-1')
                    except UnicodeDecodeError:
                        await update.message.reply_text(
                            "❌ Не удалось декодировать файл как текст.\n"
                            "Поддерживаются только текстовые файлы для создания Gists.\n\n"
                            "💡 **Совет:** Попробуйте конвертировать файл в поддерживаемый формат!"
                        )
                        return
            
            # Проверяем размер файла (GitHub ограничивает Gists до 1MB)
            if len(text_content) > 1000000:  # 1MB
                await update.message.reply_text(
                    "❌ Файл слишком большой для создания Gist.\n"
                    "Максимальный размер: 1MB"
                )
                return
            
            await update.message.reply_text(f"📄 Обрабатываю файл {filename}...")
            
            # Создаем Gist
            description = f"Файл {filename} ({file_type})"
            gist_result = self.github_bot.create_gist_from_file(text_content, filename, description)
            
            if gist_result['success']:
                text_result = self.github_bot.format_gist_result(gist_result)
                keyboard = [
                    [InlineKeyboardButton("📄 Создать еще Gist", callback_data="github_gist")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(text_result, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await update.message.reply_text(f"❌ Ошибка создания Gist: {gist_result['error']}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обработки файла: {str(e)}")

    async def handle_file_conversion(self, update: Update, file_content: bytes, filename: str, source_format: str):
        """Обработка конвертации файлов"""
        try:
            # Получаем доступные форматы для конвертации
            available_formats = self.file_converter.get_available_conversions(source_format)
            
            if not available_formats:
                await update.message.reply_text(
                    f"❌ Конвертация из {source_format} не поддерживается.\n"
                    f"Поддерживаемые форматы: {', '.join(self.file_converter.supported_formats.keys())}"
                )
                return
            
            # Создаем клавиатуру с доступными форматами
            keyboard = []
            for i in range(0, len(available_formats), 2):
                row = []
                for j in range(2):
                    if i + j < len(available_formats):
                        target_format = available_formats[i + j]
                        format_desc = self.file_converter.format_descriptions.get(target_format, target_format)
                        row.append(InlineKeyboardButton(
                            f"📄 {format_desc}", 
                            callback_data=f"convert_{source_format}_{target_format}"
                        ))
                keyboard.append(row)
            
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="file_converter")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📄 **Конвертация файла**\n\n"
                f"📁 **Файл:** {filename}\n"
                f"📋 **Формат:** {self.file_converter.format_descriptions.get(source_format, source_format)}\n\n"
                f"Выберите формат для конвертации:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Сохраняем данные файла для конвертации
            user_id = update.effective_user.id
            if not hasattr(self, 'pending_conversions'):
                self.pending_conversions = {}
            
            self.pending_conversions[user_id] = {
                'file_content': file_content,
                'filename': filename,
                'source_format': source_format
            }
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обработки конвертации: {str(e)}")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик фотографий"""
        try:
            user_id = update.effective_user.id
            photo = update.message.photo[-1]  # Берем фото наивысшего качества
            file_id = photo.file_id
            
            # Проверяем, активен ли режим чата с AI
            if user_id in self.ai_chat_mode and self.ai_chat_mode[user_id]:
                # Режим AI чата - отправляем фото в Claude
                await update.message.reply_text("🖼️ Анализирую изображение...")
                
                # Получаем текст подписи, если есть
                caption = update.message.caption or ""
                
                # Скачиваем фото
                file = await context.bot.get_file(file_id)
                photo_bytes = await file.download_as_bytearray()
                
                # Формируем вопрос для Claude
                question_text = caption if caption else "Опиши это изображение подробно. Что ты видишь на нём?"
                
                # Сохраняем в историю чата
                if user_id not in self.ai_chat_history:
                    self.ai_chat_history[user_id] = []
                
                self.ai_chat_history[user_id].append({
                    "role": "user",
                    "content": f"[Изображение] {question_text}"
                })
                
                # Отправляем в Claude (не блокируем event loop)
                response = self.claude.ask_question_with_image(
                    bytes(photo_bytes),
                    question_text
                )
                
                # Сохраняем ответ в историю
                self.ai_chat_history[user_id].append({
                    "role": "assistant",
                    "content": response
                })
                
                # Ограничиваем историю
                if len(self.ai_chat_history[user_id]) > 20:
                    self.ai_chat_history[user_id] = self.ai_chat_history[user_id][-20:]
                
                # Отправляем ответ
                if len(response) > 4000:
                    # Разбиваем на части
                    parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
                    for part in parts:
                        await update.message.reply_text(part)
                else:
                    await update.message.reply_text(f"🧠 **Анализ изображения:**\n\n{response}", parse_mode='Markdown')
                
                return
            
            # Обычный режим - показываем подсказку
            await update.message.reply_text(
                "📸 Получено изображение!\n\n"
                "💡 **Совет:** Для анализа изображения с помощью AI:\n"
                "1. Используйте команду /chat для активации AI чата\n"
                "2. Затем отправьте фото - Claude проанализирует его!\n\n"
                "Или используйте команду /image для генерации изображений!"
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обработки изображения: {str(e)}")
            import traceback
            traceback.print_exc()

    async def handle_guess_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Обработать игру 'Угадай число'"""

        user_id = update.effective_user.id

        game = self.user_games[user_id]

        

        try:

            guess = int(update.message.text)

        except ValueError:

            await update.message.reply_text("❌ Введите число!")

            return

        

        game['attempts'] += 1

        secret_number = game['secret_number']

        

        if guess == secret_number:

            score = max(0, 20 - game['attempts'])

            self.user_scores[user_id] = self.user_scores.get(user_id, 0) + score

            

            keyboard = [
                [InlineKeyboardButton("🎮 Играть еще", callback_data="guess_game")],
                [InlineKeyboardButton("🔙 Назад", callback_data="games")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(

                f"🎉 **Поздравляю! Вы угадали!**\n\n"

                f"🎯 Число: {secret_number}\n"

                f"📊 Попыток: {game['attempts']}\n"

                f"🏆 Очки: +{score}",

                parse_mode='Markdown',
                reply_markup=reply_markup

            )

            del self.user_games[user_id]

        elif guess < secret_number:

            await update.message.reply_text("📈 Больше!")

        else:

            await update.message.reply_text("📉 Меньше!")



    # РЕЖИМ ЧАТА С AI

    async def start_ai_chat(self, query):

        """Начать режим чата с AI"""

        user_id = query.from_user.id

        self.ai_chat_mode[user_id] = True

        

        # Если истории нет, создаем новую

        if user_id not in self.ai_chat_history:

            self.ai_chat_history[user_id] = []

        

        messages_count = len(self.ai_chat_history[user_id])

        history_info = f"\n\n📚 У нас уже {messages_count} сообщений в истории!" if messages_count > 0 else "\n\n✨ Начинаем новый разговор!"

        

        keyboard = [

            [InlineKeyboardButton("❌ Закончить чат", callback_data="ai_chat_stop")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        chat_info = f"""

💬 **Режим чата с AI активирован!**



Просто пишите свои вопросы и сообщения - я буду отвечать через Claude AI!



✨ **Возможности:**

• Отвечаю на любые вопросы

• Помогаю с программированием и кодом

• Генерирую идеи и решения

• Создаю целые проекты

• **Помню всю нашу историю разговоров** 🧠{history_info}



💡 Для создания проекта в ZIP используйте: **/project описание проекта**

        """

        

        await query.edit_message_text(chat_info, parse_mode='Markdown', reply_markup=reply_markup)

    

    async def stop_ai_chat(self, query):

        """Остановить режим чата с AI"""

        user_id = query.from_user.id

        

        if user_id in self.ai_chat_mode:

            messages_count = len(self.ai_chat_history.get(user_id, []))

            del self.ai_chat_mode[user_id]

            # НЕ удаляем историю - она сохраняется навсегда

            

            keyboard = [[InlineKeyboardButton("🔙 В AI меню", callback_data="ai_menu")]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            

            await query.edit_message_text(

                f"✅ **Чат с AI завершен!**\n\n📚 Сообщений в истории: {messages_count}\n\n💾 Вся история сохранена и будет доступна при следующем запуске чата!\n\nДо встречи! 👋",

                parse_mode='Markdown',

                reply_markup=reply_markup

            )

        else:

            await query.edit_message_text("❌ Режим чата не был активен")

    

    async def handle_ai_chat_message(self, update: Update, user_message: str, voice_mode: bool = False):

        """Обработать сообщение в режиме чата с AI"""

        user_id = update.effective_user.id

        

        # Проверяем, не просит ли пользователь создать проект

        project_keywords = ['создай проект', 'сделай проект', 'создать проект', 'сделать проект', 

                           'zip файл', 'zip архив', 'готовый проект', 'целый проект', 

                           'весь проект', 'полный проект', 'сайт портфолио', 'портфолио сайт']

        

        if any(keyword in user_message.lower() for keyword in project_keywords):

            # Автоматически вызываем команду создания проекта

            await update.message.reply_text("🎯 Понял! Создаю проект для тебя...")

            

            # Создаем контекст для команды project

            context_args = user_message.split()

            context = type('Context', (), {'args': context_args})()

            

            await self.ai_create_project(update, context)

            return

        

        # Добавляем сообщение пользователя в историю

        if user_id not in self.ai_chat_history:

            self.ai_chat_history[user_id] = []

        

        self.ai_chat_history[user_id].append({

            "role": "user",

            "content": user_message

        })

        

        # Ограничиваем историю последними 10 сообщениями для экономии токенов

        if len(self.ai_chat_history[user_id]) > 20:

            self.ai_chat_history[user_id] = self.ai_chat_history[user_id][-20:]

        

        # Формируем контекст для Claude

        conversation_context = "\n\n".join([

            f"{'Пользователь' if msg['role'] == 'user' else 'Ассистент'}: {msg['content']}"

            for msg in self.ai_chat_history[user_id][-10:]  # Последние 10 сообщений

        ])

        

        full_prompt = f"""Ты дружелюбный и умный AI-ассистент, как ChatGPT. Ты можешь общаться на ЛЮБЫЕ темы:



✨ О чем я могу говорить:

• Программирование и технологии

• Жизнь, философия, психология

• Наука, история, культура

• Хобби, спорт, развлечения

• Советы и рекомендации

• Просто приятная беседа

• Шутки и юмор

• Любые другие темы!



🎯 Стиль общения:

• Дружелюбный и естественный

• Эмоциональный (используй эмодзи когда уместно)

• Понятный и интересный

• Поддерживающий разговор

• Как реальный друг



💡 ВАЖНО: Если пользователь просит создать проект, сайт, приложение или что-то в ZIP файле, 

скажи что ты можешь это сделать и предложи использовать команду /project описание



История нашего разговора:

{conversation_context}



Ответь на последнее сообщение пользователя естественно, дружелюбно и интересно. Будь живым собеседником!"""

        

        # Показываем индикатор печати

        await update.message.chat.send_action("typing")
        

        # Получаем ответ от Claude
        # telegram-bot library автоматически выполняет синхронные вызовы в executor pool
        response = self.claude.ask_question(full_prompt)

        

        # Добавляем ответ в историю

        self.ai_chat_history[user_id].append({

            "role": "assistant",

            "content": response

        })

        

        # Сохраняем историю в файл

        self.save_history(user_id)

        

        # Отправляем ответ с кнопками управления (только если НЕ голосовой режим)
        if not voice_mode:
            keyboard = [
                [InlineKeyboardButton("❌ Закончить чат", callback_data="ai_chat_stop")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Разбиваем длинные ответы
            if len(response) > 4000:
                parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:  # Кнопки только к последнему сообщению
                        await update.message.reply_text(part, reply_markup=reply_markup)
                    else:
                        await update.message.reply_text(part)
            else:
                await update.message.reply_text(response, reply_markup=reply_markup)
        # В голосовом режиме текст не отправляем - только голосовой ответ



    async def start_ai_chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для запуска чата с AI"""

        user_id = update.effective_user.id

        self.ai_chat_mode[user_id] = True

        

        # Если истории нет, создаем новую

        if user_id not in self.ai_chat_history:

            self.ai_chat_history[user_id] = []

        

        messages_count = len(self.ai_chat_history[user_id])

        history_info = f"\n\n📚 У нас уже {messages_count} сообщений в истории!" if messages_count > 0 else "\n\n✨ Начинаем новый разговор!"

        

        keyboard = [

            [InlineKeyboardButton("❌ Закончить чат", callback_data="ai_chat_stop")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        chat_info = f"""

💬 **Режим чата с AI активирован!**



Просто пиши что угодно - я отвечу! Как в ChatGPT 😊



✨ **Что я умею:**

• 💭 Болтать на любые темы (жизнь, хобби, что угодно!)

• 💻 Помогать с кодом и программированием

• 🎓 Объяснять сложные вещи просто

• 💡 Генерировать идеи и советы

• 🎨 Создавать целые проекты

• 🧠 **Помню всю нашу историю!**{history_info}



🚀 **Специальные команды:**

• **/project описание** - Создать проект в ZIP

• **/aicode язык описание** - Генерация кода



Давай общаться! О чем поговорим? 😊

        """

        

        await update.message.reply_text(chat_info, parse_mode='Markdown', reply_markup=reply_markup)



    # AI КОМАНДЫ

    async def ai_ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Задать вопрос Claude AI"""

        question = ' '.join(context.args)

        if not question:

            await update.message.reply_text(

                "❌ Укажите вопрос!\nПример: /ask Как работает блокчейн?",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]])

            )

            return

        

        await update.message.reply_text("🤔 Думаю... (это может занять несколько секунд)")

        

        answer = self.claude.ask_question(question)

        

        # Telegram ограничивает сообщения до 4096 символов

        if len(answer) > 4000:

            # Разбиваем на части

            parts = [answer[i:i+4000] for i in range(0, len(answer), 4000)]

            for part in parts:

                await update.message.reply_text(part)

        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Задать еще вопрос", callback_data="ask_another")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(f"🧠 **Ответ Claude AI:**\n\n{answer}", parse_mode='Markdown', reply_markup=reply_markup)

    

    async def ai_code_generate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Генерировать код через Claude AI"""

        if len(context.args) < 2:

            await update.message.reply_text(

                "❌ Укажите язык и описание!\nПример: /aicode python веб-сервер на Flask",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]])

            )

            return

        

        language = context.args[0].lower()

        description = ' '.join(context.args[1:])

        

        await update.message.reply_text("💻 Генерирую код... (это может занять несколько секунд)")

        

        code = self.claude.generate_code(language, description, complexity="medium")

        

        # Отправляем код

        if len(code) > 4000:

            parts = [code[i:i+4000] for i in range(0, len(code), 4000)]

            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Последняя часть - добавляем кнопки
                    keyboard = [
                        [InlineKeyboardButton("🔄 Сгенерировать еще", callback_data="generate_more_code")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(part, parse_mode='Markdown', reply_markup=reply_markup)
                else:
                    await update.message.reply_text(part, parse_mode='Markdown')

        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Сгенерировать еще", callback_data="generate_more_code")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(code, parse_mode='Markdown', reply_markup=reply_markup)

    

    async def ai_create_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Создать целый проект и отправить в ZIP"""

        project_desc = ' '.join(context.args)

        if not project_desc:

            await update.message.reply_text(

                "❌ Укажите описание проекта!\nПример: /project todo приложение на React и Node.js",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]])

            )

            return

        

        await update.message.reply_text("📦 Создаю проект... (это может занять до минуты)")

        

        # Генерируем файлы проекта

        files = self.claude.generate_multiple_files(project_desc)

        

        # Создаем ZIP архив

        zip_buffer = self.claude.create_zip_from_files(files)

        zip_buffer.seek(0)

        

        # Отправляем ZIP файл

        await update.message.reply_document(

            document=zip_buffer,

            filename=f"project_{project_desc.replace(' ', '_')[:20]}.zip",

            caption=f"📦 Проект готов!\n\nСоздано файлов: {len(files)}\n\n" + 

                    "\n".join([f"• {filename}" for filename in files.keys()]),

            parse_mode='Markdown'

        )

        # Отправляем кнопки отдельно
        keyboard = [
            [InlineKeyboardButton("🔄 Создать еще проект", callback_data="create_another_project")],
            [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💡 Что дальше?",
            reply_markup=reply_markup
        )

    

    async def ai_explain_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Объяснить код"""

        code = ' '.join(context.args)

        if not code:

            await update.message.reply_text(

                "❌ Укажите код для объяснения!\nПример: /explain def factorial(n): return 1 if n == 0 else n * factorial(n-1)",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]])

            )

            return

        

        await update.message.reply_text("📖 Анализирую код...")

        

        explanation = self.claude.explain_code(code)

        

        if len(explanation) > 4000:

            parts = [explanation[i:i+4000] for i in range(0, len(explanation), 4000)]

            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Последняя часть - добавляем кнопки
                    keyboard = [
                        [InlineKeyboardButton("🔄 Объяснить еще", callback_data="explain_more_code")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(part, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(part)

        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Объяснить еще", callback_data="explain_more_code")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"📖 **Объяснение кода:**\n\n{explanation}", reply_markup=reply_markup)

    

    async def ai_debug_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Отладить код"""

        code = ' '.join(context.args)

        if not code:

            await update.message.reply_text(

                "❌ Укажите код для отладки!\nПример: /debug print('Hello' + 5)",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]])

            )

            return

        

        await update.message.reply_text("🐛 Ищу ошибки...")

        

        fixed_code = self.claude.debug_code(code)

        

        if len(fixed_code) > 4000:

            parts = [fixed_code[i:i+4000] for i in range(0, len(fixed_code), 4000)]

            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Последняя часть - добавляем кнопки
                    keyboard = [
                        [InlineKeyboardButton("🔄 Отладить еще", callback_data="debug_more_code")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(part, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(part)

        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Отладить еще", callback_data="debug_more_code")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"🐛 **Отладка кода:**\n\n{fixed_code}", reply_markup=reply_markup)

    

    async def ai_optimize_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Оптимизировать код"""

        code = ' '.join(context.args)

        if not code:

            await update.message.reply_text(

                "❌ Укажите код для оптимизации!\nПример: /optimize for i in range(len(array)): print(array[i])",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]])

            )

            return

        

        await update.message.reply_text("⚡ Оптимизирую код...")

        

        optimized_code = self.claude.optimize_code(code)

        

        if len(optimized_code) > 4000:

            parts = [optimized_code[i:i+4000] for i in range(0, len(optimized_code), 4000)]

            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Последняя часть - добавляем кнопки
                    keyboard = [
                        [InlineKeyboardButton("🔄 Оптимизировать еще", callback_data="optimize_more_code")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(part, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(part)

        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Оптимизировать еще", callback_data="optimize_more_code")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"⚡ **Оптимизированный код:**\n\n{optimized_code}", reply_markup=reply_markup)

    

    # AI ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

    async def show_image_menu(self, query):

        """Показать меню генерации изображений"""

        await show_main_image_menu(query, self)

        return

    

    async def set_style(self, query, style):

        """Установить стиль"""

        user_id = query.from_user.id

        if style == "none":

            self.image_gen.set_user_style(user_id, None)

            await query.answer("✅ Стиль сброшен")

        else:

            self.image_gen.set_user_style(user_id, style)

            style_name = STYLES[style].split('|')[0]

            await query.answer(f"✅ {style_name}")

        try:

            await show_styles_menu(query, self)

        except Exception as e:

            # Игнорируем ошибку "Message is not modified" - это нормально

            if "Message is not modified" not in str(e):

                raise

    

    async def set_quality(self, query, quality):

        """Установить качество"""

        user_id = query.from_user.id

        self.image_gen.set_user_quality(user_id, quality)

        await query.answer(f"✅ Качество изменено")

        try:

            await show_quality_menu(query, self)

        except Exception as e:

            # Игнорируем ошибку "Message is not modified" - это нормально

            if "Message is not modified" not in str(e):

                raise

    async def set_model(self, query, model_key: str):
        """Установить модель/провайдер генерации."""
        user_id = query.from_user.id
        model_key = (model_key or "").strip().lower()
        if model_key not in ("fooocus", "kandinsky", "openai"):
            await query.answer("❌ Неизвестная модель")
            return
        self.image_gen.set_user_model(user_id, model_key)
        titles = {
            "fooocus": "Fooocus (локально)",
            "kandinsky": "Kandinsky",
            "openai": "OpenAI",
        }
        await query.answer(f"✅ {titles.get(model_key, model_key)}")
        await show_model_menu(query, self)

    

    async def show_favorites(self, query):

        """Показать избранное"""

        user_id = query.from_user.id

        favs = self.favorites.get(user_id, [])

        

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")]]

        

        if not favs:

            text = "⭐ **Избранное пусто**\n\nСохраняй понравившиеся изображения!"

        else:

            text = f"⭐ **Избранное**\n\nСохранено: {len(favs)} изображений"

        

        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    

    async def old_show_image_menu(self, query):

        """Старое меню (не используется)"""

        keyboard = [

            [InlineKeyboardButton("🔙 Назад в AI меню", callback_data="ai_menu")]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        api_name = "DALL-E" if IMAGE_GENERATION_API == "openai" else "Pollinations.ai (бесплатно)"

        

        image_info = f"""

🎨 **AI Генерация изображений**



Создавай крутые картинки по текстовому описанию!



✨ **Как это работает:**

1. Напиши описание картинки

2. Claude AI улучшит твой промпт

3. Получи готовое изображение!



🚀 **Используемый API:** {api_name}



💡 **Примеры команд:**

• /image кот-программист за компьютером

• /image футуристический город на закате

• /image дракон в киберпанк стиле

• /image космический корабль в космосе



🎯 **Советы для лучших результатов:**

• Будь конкретным в описании

• Укажи стиль (реалистично, аниме, 3D и т.д.)

• Опиши атмосферу и детали

• Можно писать на русском!



⚙️ **Настройки:**

• Качество: High-res (1024x1024)

• Claude автоматически улучшает промпты

• Генерация занимает 10-30 секунд



Попробуй прямо сейчас:

**/image твое описание**

        """

        

        await query.edit_message_text(image_info, parse_mode='Markdown', reply_markup=reply_markup)

    

    async def generate_image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для генерации изображения"""

        prompt = ' '.join(context.args)

        

        if not prompt:

            await update.message.reply_text(

                "❌ Укажите описание изображения!\n\n"

                "Примеры:\n"

                "/image кот программист за компьютером\n"

                "/image футуристический город на закате\n"

                "/image космический корабль в стиле киберпанк",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")]])

            )

            return

        

        # Валидация только на пустой ввод / длину (без фильтра "запрещенного" контента)
        if not validate_prompt(prompt):
            await update.message.reply_text("❌ Введите текст промпта (и не больше 1000 символов).")
            return

        

        try:

            user_id = update.message.from_user.id

            

            # Отправляем уведомление о начале генерации

            user_model = self.image_gen.get_user_model(user_id)
            status_msg = await update.message.reply_text(

                "🎨 **Генерирую изображение...**\n\n"

                f"📝 Ваш промпт: _{prompt}_\n\n"

                f"🤖 Модель: `{user_model}`\n\n"
                "⏳ Это может занять 10-30 секунд...",

                parse_mode='Markdown'

            )

            

            # Генерируем изображение с настройками пользователя

            image_buffer, final_prompt, detected_char = await self.run_blocking(
                self.image_gen.generate_with_settings,
                prompt,
                user_id,
                enhance_with_claude=self.claude if user_model != "fooocus" else None
            )

            

            # Сохраняем для перегенерации

            self.last_image_prompt[user_id] = prompt

            

            # Обновляем статус

            await status_msg.edit_text(

                "✅ Изображение готово! Отправляю...",

                parse_mode='Markdown'

            )

            

            # Формируем описание

            char_info = f"\n👤 Персонаж: {detected_char.title()}" if detected_char else ""

            

            caption = f"""

🎨 **Изображение сгенерировано!**



📝 **Промпт:** _{prompt}_{char_info}



💡 `/imgregen` - Перегенерировать

            """

            

            # Отправляем изображение

            image_buffer.seek(0)

            await update.message.reply_photo(

                photo=image_buffer,

                caption=caption,

                parse_mode='Markdown'

            )

            # Отправляем кнопки отдельно
            keyboard = [
                [InlineKeyboardButton("🔄 Перегенерировать", callback_data="regenerate_image")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💡 Что дальше?",
                reply_markup=reply_markup
            )

            

            # Удаляем статусное сообщение

            await status_msg.delete()

            

            # Добавляем очки пользователю

            user_id = update.effective_user.id

            self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 15

            

            logger.info(f"Image generated for user {user_id}: {prompt}")

            

        except ValueError as e:

            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        except Exception as e:

            logger.error(f"Ошибка генерации изображения: {e}")

            await update.message.reply_text(

                f"❌ Не удалось сгенерировать изображение.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте:\n"

                f"• Упростить описание\n"

                f"• Проверить настройки API в config.py\n"

                f"• Попробовать позже"

            )

    

    async def generate_wallpaper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для генерации обоев для телефона"""

        prompt = ' '.join(context.args)

        

        if not prompt:

            await update.message.reply_text(

                "📱 **Генератор обоев для телефона**\n\n"

                "Создай красивые обои для своего мобильного устройства!\n\n"

                "**Примеры:**\n"

                "/wallpaper минималистичный градиент синий фиолетовый\n"

                "/wallpaper абстрактные геометрические фигуры\n"

                "/wallpaper космос звезды небо\n"

                "/wallpaper природа горы закат\n"

                "/wallpaper киберпанк неон город\n\n"

                "**Идеи для обоев:**\n"

                "• Минималистичные градиенты\n"

                "• Абстрактные узоры\n"

                "• Природные пейзажи\n"

                "• Космические темы\n"

                "• Геометрические фигуры\n"

                "• Цветочные узоры\n"

                "• Городские пейзажи",

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")]])

            )

            return

        

        # Валидация промпта

        if not validate_wallpaper_prompt(prompt):

            await update.message.reply_text(

                "❌ Некорректное описание! Проверьте:\n"

                "• Минимум 3 символа\n"

                "• Максимум 1000 символов\n"

                "• Отсутствие запрещенного контента"

            )

            return

        

        try:

            user_id = update.message.from_user.id

            

            # Отправляем уведомление о начале генерации

            status_msg = await update.message.reply_text(

                "📱 **Генерирую обои для телефона...**\n\n"

                f"📝 Ваш промпт: _{prompt}_\n\n"

                "⏳ Это может занять 15-30 секунд...\n"

                "🎨 Оптимизирую для мобильного экрана...",

                parse_mode='Markdown'

            )

            

            # Генерируем обои

            wallpaper_buffer, final_prompt = await self.run_blocking(
                self.wallpaper_gen.generate_wallpaper,
                prompt,
                device_type='android',  # По умолчанию Android размер
                enhance_with_claude=self.claude
            )

            

            # Обновляем статус

            await status_msg.edit_text(

                "✅ Обои готовы! Отправляю...",

                parse_mode='Markdown'

            )

            

            # Формируем описание

            caption = f"""

📱 **Обои для телефона готовы!**



📝 **Промпт:** _{prompt}_



📐 **Размер:** 1080x2340 (Android)

🎨 **Оптимизировано** для мобильного экрана



💡 **Совет:** Сохраните изображение и установите как обои!

            """

            

            # Отправляем изображение

            wallpaper_buffer.seek(0)

            await update.message.reply_photo(

                photo=wallpaper_buffer,

                caption=caption,

                parse_mode='Markdown'

            )

            # Отправляем кнопки отдельно
            keyboard = [
                [InlineKeyboardButton("🔄 Перегенерировать", callback_data="regenerate_wallpaper")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💡 Что дальше?",
                reply_markup=reply_markup
            )

            

            # Удаляем статусное сообщение

            await status_msg.delete()

            

            # Добавляем очки пользователю

            user_id = update.effective_user.id

            self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 20

            

            logger.info(f"Wallpaper generated for user {user_id}: {prompt}")

            

        except ValueError as e:

            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        except Exception as e:

            logger.error(f"Ошибка генерации обоев: {e}")

            await update.message.reply_text(

                f"❌ Не удалось сгенерировать обои.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте:\n"

                f"• Упростить описание\n"

                f"• Попробовать позже"

            )

    

    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда перевода текста"""

        text = ' '.join(context.args)

        

        if not text:

            await update.message.reply_text(

                "🌍 **Переводчик текста**\n\n"

                "Использование: `/translate [текст]`\n\n"

                "**Примеры:**\n"

                "• `/translate Привет, как дела?`\n"

                "• `/translate Hello world`\n"

                "• `/translate Bonjour le monde`\n\n"

                "💡 **Поддерживаемые языки:**\n"

                "Русский, Английский, Испанский, Французский, Немецкий, Итальянский, Португальский, Японский, Корейский, Китайский и многие другие!\n\n"

                "🔄 Автоматически определяет язык и переводит на противоположный!",

                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])

            )

            return

        

        if len(text) > 5000:

            await update.message.reply_text(

                "❌ Текст слишком длинный!\n"

                "Максимум 5000 символов для перевода."

            )

            return

        

        try:

            # Показываем "печатает..."

            await update.effective_chat.send_action(ChatAction.TYPING)

            

            # Переводим текст

            result = self.translator.translate_text(text)
            

            if result['success']:

                # Формируем красивый ответ

                response = f"""

🌍 **Перевод выполнен!**



📝 **Исходный текст:** _{result['original_text']}_



🔄 **Перевод:** _{result['translated_text']}_



🏷️ **Языки:** {result['source_language_name']} → {result['target_language_name']}



💡 Используйте `/translate` для обратного перевода!

                """

                

                await update.message.reply_text(response, parse_mode='Markdown')

                

                # Добавляем очки пользователю

                user_id = update.effective_user.id

                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 5

                

                logger.info(f"Text translated for user {user_id}: {text[:50]}...")

                

            else:

                await update.message.reply_text(

                    f"❌ **Ошибка перевода**\n\n"

                    f"Проблема: {result['error']}\n\n"

                    f"💡 Попробуйте:\n"

                    f"• Проверить текст\n"

                    f"• Попробовать позже\n"

                    f"• Использовать более короткий текст",

                    parse_mode='Markdown'

                )

                

        except Exception as e:

            logger.error(f"Ошибка в команде перевода: {e}")

            await update.message.reply_text(

                f"❌ Произошла ошибка при переводе.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте позже или обратитесь к администратору."

            )

    

    async def music_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда поиска музыки"""

        query = ' '.join(context.args)

        

        if not query:

            await update.message.reply_text(

                "🎵 **Поиск музыки**\n\n"

                "Использование: `/music [название песни/исполнитель]`\n\n"

                "**Примеры:**\n"

                "• `/music Imagine Dragons Thunder`\n"

                "• `/music Ed Sheeran Shape of You`\n"

                "• `/music Queen Bohemian Rhapsody`\n"

                "• `/music The Weeknd Blinding Lights`\n\n"

                "💡 **Поддерживаемые платформы:**\n"

                "YouTube Music, Spotify, Apple Music, SoundCloud\n\n"

                "🔍 Бот найдет ссылки на все популярные платформы!",

                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])

            )

            return

        

        if len(query) > 200:

            await update.message.reply_text(

                "❌ Поисковый запрос слишком длинный!\n"

                "Максимум 200 символов для поиска."

            )

            return

        

        try:

            # Показываем "печатает..."

            await update.effective_chat.send_action(ChatAction.TYPING)

            

            # Ищем музыку

            search_result = await self.run_blocking(self.music_searcher.search_music, query)

            

            if search_result['success']:

                # Форматируем результаты

                formatted_results = self.music_searcher.format_search_results(search_result)

                

                keyboard = [
                    [InlineKeyboardButton("🔄 Искать еще", callback_data="search_more_music")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(

                    formatted_results,

                    parse_mode='Markdown',

                    disable_web_page_preview=True,
                    reply_markup=reply_markup

                )

                

                # Добавляем информацию о скачивании

                download_info = self.music_searcher.get_download_info(query)

                await update.message.reply_text(

                    download_info['message'],

                    parse_mode='Markdown',

                    disable_web_page_preview=True

                )

                

                # Добавляем очки пользователю

                user_id = update.effective_user.id

                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 10

                

                logger.info(f"Music search for user {user_id}: {query}")

                

            else:

                await update.message.reply_text(

                    f"❌ **Ошибка поиска музыки**\n\n"

                    f"Проблема: {search_result['error']}\n\n"

                    f"💡 Попробуйте:\n"

                    f"• Упростить запрос\n"

                    f"• Добавить имя исполнителя\n"

                    f"• Проверить правописание",

                    parse_mode='Markdown'

                )

                

        except Exception as e:

            logger.error(f"Ошибка в команде поиска музыки: {e}")

            await update.message.reply_text(

                f"❌ Произошла ошибка при поиске музыки.\n\n"

                f"Ошибка: {str(e)}\n\n"

                f"💡 Попробуйте позже или обратитесь к администратору."

            )

    async def github_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для работы с GitHub"""

        if not context.args:

            await update.message.reply_text(

                "🐙 **GitHub интеграция**\n\n"

                "**Доступные команды:**\n"

                "• `/github search [запрос]` - Поиск репозиториев\n"
                "• `/github advanced [запрос] [язык] [сортировка]` - Расширенный поиск\n"
                "• `/github user [username]` - Информация о пользователе\n"
                "• `/github repo [владелец/название]` - Детали репозитория\n"
                "• `/github issues [владелец/название]` - Issues репозитория\n"
                "• `/github prs [владелец/название]` - Pull Requests\n"
                "• `/github stats [владелец/название]` - Статистика репозитория\n"
                "• `/github gist [filename]` - Создать Gist\n"
                "• `/github trending` - Трендовые репозитории\n\n"

                "**Примеры:**\n"

                "• `/github search python bot`\n"
                "• `/github advanced javascript framework stars`\n"
                "• `/github user kirill2006788-cloud`\n"
                "• `/github repo microsoft/vscode`\n"
                "• `/github issues facebook/react`\n"
                "• `/github prs nodejs/node`\n"
                "• `/github stats google/tensorflow`\n"
                "• `/github gist test.py`\n"
                "• `/github trending`",

                parse_mode='Markdown',

                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])

            )

            return

        command = context.args[0].lower()

        if command == "search":

            if len(context.args) < 2:

                await update.message.reply_text("❌ Укажите поисковый запрос!\nПример: `/github search python bot`")

                return

            query = ' '.join(context.args[1:])

            try:

                await update.message.reply_text("🔍 Ищу репозитории...")

                search_result = self.github_bot.search_repositories(query)

                if search_result['success']:

                    text = self.github_bot.format_search_results(search_result)

                    keyboard = [

                        [InlineKeyboardButton("🔄 Искать еще", callback_data="github_search")],

                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]

                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка поиска: {search_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        elif command == "user":

            if len(context.args) < 2:

                await update.message.reply_text("❌ Укажите имя пользователя!\nПример: `/github user kirill2006788-cloud`")

                return

            username = context.args[1]

            try:

                await update.message.reply_text("👤 Получаю информацию о пользователе...")

                user_result = self.github_bot.get_user_info(username)

                if user_result['success']:

                    text = self.github_bot.format_user_info(user_result)

                    keyboard = [

                        [InlineKeyboardButton("🔄 Другой пользователь", callback_data="github_user")],

                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]

                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка: {user_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        elif command == "trending":

            try:

                await update.message.reply_text("🔥 Получаю трендовые репозитории...")

                trending_result = self.github_bot.get_trending_repositories()

                if trending_result['success']:

                    text = f"🔥 **Трендовые репозитории** ({trending_result['language']})\n\n"

                    for i, repo in enumerate(trending_result['repositories'], 1):

                        text += f"**{i}.** {self.github_bot.format_repository_info(repo)}\n\n"

                    keyboard = [

                        [InlineKeyboardButton("🔄 Обновить", callback_data="github_trending")],

                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]

                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка получения трендов: {trending_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        elif command == "advanced":

            if len(context.args) < 2:

                await update.message.reply_text("❌ Укажите поисковый запрос!\nПример: `/github advanced python bot stars`")

                return

            query = context.args[1]
            language = context.args[2] if len(context.args) > 2 else None
            sort = context.args[3] if len(context.args) > 3 else 'stars'

            try:

                await update.message.reply_text("🔍 Выполняю расширенный поиск...")

                search_result = self.github_bot.search_repositories_advanced(query, language, sort)

                if search_result['success']:

                    text = f"🔍 **Расширенный поиск**\n"
                    text += f"📝 **Запрос:** {search_result['query']}\n"
                    if search_result['language']:
                        text += f"💻 **Язык:** {search_result['language']}\n"
                    text += f"📊 **Сортировка:** {search_result['sort']}\n"
                    text += f"📈 **Найдено:** {search_result['total_count']}\n\n"

                    for i, repo in enumerate(search_result['repositories'], 1):
                        text += f"**{i}.** {self.github_bot.format_repository_info(repo)}\n\n"

                    keyboard = [
                        [InlineKeyboardButton("🔄 Искать еще", callback_data="github_advanced_search")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка поиска: {search_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        elif command == "repo":

            if len(context.args) < 2:

                await update.message.reply_text("❌ Укажите репозиторий!\nПример: `/github repo microsoft/vscode`")

                return

            repo_input = context.args[1]

            if '/' not in repo_input:

                await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `/github repo microsoft/vscode`")

                return

            owner, repo_name = repo_input.split('/', 1)

            try:

                await update.message.reply_text("📁 Получаю детали репозитория...")

                repo_result = self.github_bot.get_repository_details(owner, repo_name)

                if repo_result['success']:

                    text = self.github_bot.format_repository_details(repo_result)

                    keyboard = [
                        [InlineKeyboardButton("📝 Issues", callback_data=f"issues_{owner}_{repo_name}")],
                        [InlineKeyboardButton("🔄 Pull Requests", callback_data=f"prs_{owner}_{repo_name}")],
                        [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{owner}_{repo_name}")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка: {repo_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        elif command == "issues":

            if len(context.args) < 2:

                await update.message.reply_text("❌ Укажите репозиторий!\nПример: `/github issues facebook/react`")

                return

            repo_input = context.args[1]

            if '/' not in repo_input:

                await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `/github issues facebook/react`")

                return

            owner, repo_name = repo_input.split('/', 1)

            try:

                await update.message.reply_text("📝 Получаю Issues...")

                issues_result = self.github_bot.get_repository_issues(owner, repo_name)

                if issues_result['success']:

                    text = self.github_bot.format_issues(issues_result)

                    keyboard = [
                        [InlineKeyboardButton("🔄 Обновить", callback_data=f"issues_{owner}_{repo_name}")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка: {issues_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        elif command == "prs":

            if len(context.args) < 2:

                await update.message.reply_text("❌ Укажите репозиторий!\nПример: `/github prs nodejs/node`")

                return

            repo_input = context.args[1]

            if '/' not in repo_input:

                await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `/github prs nodejs/node`")

                return

            owner, repo_name = repo_input.split('/', 1)

            try:

                await update.message.reply_text("🔄 Получаю Pull Requests...")

                prs_result = self.github_bot.get_repository_pull_requests(owner, repo_name)

                if prs_result['success']:

                    text = self.github_bot.format_pull_requests(prs_result)

                    keyboard = [
                        [InlineKeyboardButton("🔄 Обновить", callback_data=f"prs_{owner}_{repo_name}")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка: {prs_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        elif command == "stats":

            if len(context.args) < 2:

                await update.message.reply_text("❌ Укажите репозиторий!\nПример: `/github stats google/tensorflow`")

                return

            repo_input = context.args[1]

            if '/' not in repo_input:

                await update.message.reply_text("❌ Укажите репозиторий в формате `владелец/название`!\nПример: `/github stats google/tensorflow`")

                return

            owner, repo_name = repo_input.split('/', 1)

            try:

                await update.message.reply_text("📊 Получаю статистику...")

                stats_result = self.github_bot.get_repository_stats(owner, repo_name)

                if stats_result['success']:

                    repo = stats_result['repository']
                    languages = stats_result['languages']
                    contributors = stats_result['top_contributors']

                    text = f"""📊 **Статистика репозитория {repo['name']}**

📁 **Основная информация:**
⭐ Звезды: {repo['stars']}
🍴 Форки: {repo['forks']}
👀 Наблюдатели: {repo['watchers']}
📊 Размер: {repo['size']} KB
📝 Issues: {repo['open_issues']}
📅 Создан: {repo['created_at']}
🔄 Обновлен: {repo['updated_at']}

💻 **Языки программирования:**"""

                    if languages:
                        total_bytes = sum(languages.values())
                        for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                            percentage = (bytes_count / total_bytes) * 100
                            text += f"\n• {lang}: {percentage:.1f}%"

                    if contributors:
                        text += f"\n\n👥 **Топ контрибьюторы:**"
                        for i, contrib in enumerate(contributors[:5], 1):
                            text += f"\n{i}. {contrib['author']}: {contrib['total_commits']} коммитов"

                    keyboard = [
                        [InlineKeyboardButton("📁 Детали", callback_data=f"repo_{owner}_{repo_name}")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="github_simple")]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

                else:

                    await update.message.reply_text(f"❌ Ошибка: {stats_result['error']}")

            except Exception as e:

                await update.message.reply_text(f"❌ Ошибка: {str(e)}")

        else:

            await update.message.reply_text(

                "❌ Неизвестная команда!\n\n"

                "**Доступные команды:**\n"

                "• `search` - Поиск репозиториев\n"
                "• `advanced` - Расширенный поиск\n"
                "• `user` - Информация о пользователе\n"
                "• `repo` - Детали репозитория\n"
                "• `issues` - Issues репозитория\n"
                "• `prs` - Pull Requests\n"
                "• `stats` - Статистика репозитория\n"
                "• `trending` - Трендовые репозитории",

                parse_mode='Markdown'

            )

    

    async def regenerate_image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Перегенерация последнего изображения"""

        user_id = update.effective_user.id

        

        if user_id not in self.last_image_prompt:

            await update.message.reply_text("❌ Нет изображения для перегенерации!\nСначала создай изображение командой /image")

            return

        

        prompt = self.last_image_prompt[user_id]

        

        await update.message.reply_text(f"🔄 Перегенерирую: _{prompt}_", parse_mode='Markdown')

        

        # Используем ту же логику что и generate_image_command

        try:

            status_msg = await update.message.reply_text("🎨 Генерирую...", parse_mode='Markdown')

            

            user_model = self.image_gen.get_user_model(user_id)
            image_buffer, final_prompt, detected_char = self.image_gen.generate_with_settings(

                prompt,

                user_id,

                enhance_with_claude=self.claude if user_model != "fooocus" else None

            )

            

            await status_msg.delete()

            

            char_info = f"\n👤 {detected_char.title()}" if detected_char else ""

            caption = f"🎨 **Перегенерация**\n\n📝 {prompt}{char_info}"

            

            image_buffer.seek(0)

            await update.message.reply_photo(photo=image_buffer, caption=caption, parse_mode='Markdown')

            

            self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 10

            

        except Exception as e:

            logger.error(f"Ошибка перегенерации: {e}")

            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def handle_regenerate_image(self, query):
        """Обработка кнопки перегенерации изображения"""
        try:
            user_id = query.from_user.id
            
            if user_id not in self.last_image_prompt:
                await query.edit_message_text("❌ Нет изображения для перегенерации!\nСначала создай изображение командой /image")
                return
            
            prompt = self.last_image_prompt[user_id]
            
            await query.edit_message_text(f"🔄 Перегенерирую: _{prompt}_", parse_mode='Markdown')
            
            try:
                status_msg = await query.message.reply_text("🎨 Генерирую...", parse_mode='Markdown')
                
                user_model = self.image_gen.get_user_model(user_id)
                image_buffer, final_prompt, detected_char = await self.run_blocking(
                    self.image_gen.generate_with_settings,
                    prompt,
                    user_id,
                    enhance_with_claude=self.claude if user_model != "fooocus" else None
                )
                
                await status_msg.delete()
                
                char_info = f"\n👤 {detected_char.title()}" if detected_char else ""
                caption = f"🎨 **Перегенерация**\n\n📝 {prompt}{char_info}"
                
                image_buffer.seek(0)
                
                # Отправляем изображение
                await query.message.reply_photo(photo=image_buffer, caption=caption, parse_mode='Markdown')
                
                # Отправляем кнопки отдельно
                keyboard = [
                    [InlineKeyboardButton("🔄 Перегенерировать", callback_data="regenerate_image")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "💡 Что дальше?",
                    reply_markup=reply_markup
                )
                
                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 10
                
            except Exception as e:
                logger.error(f"Ошибка перегенерации: {e}")
                await query.message.reply_text(f"❌ Ошибка: {str(e)}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка обработки: {str(e)}")

    async def handle_regenerate_wallpaper(self, query):
        """Обработка кнопки перегенерации обоев"""
        try:
            user_id = query.from_user.id
            
            if user_id not in self.last_image_prompt:
                await query.edit_message_text("❌ Нет изображения для перегенерации!\nСначала создай изображение командой /wallpaper")
                return
            
            prompt = self.last_image_prompt[user_id]
            
            await query.edit_message_text(f"🔄 Перегенерирую обои: _{prompt}_", parse_mode='Markdown')
            
            try:
                status_msg = await query.message.reply_text("🎨 Генерирую обои...", parse_mode='Markdown')
                
                image_buffer, final_prompt, detected_char = await self.run_blocking(
                    self.wallpaper_gen.generate_with_settings,
                    prompt,
                    user_id,
                    enhance_with_claude=self.claude
                )
                
                await status_msg.delete()
                
                char_info = f"\n👤 {detected_char.title()}" if detected_char else ""
                caption = f"🖼️ **Перегенерация обоев**\n\n📝 {prompt}{char_info}"
                
                image_buffer.seek(0)
                
                # Отправляем изображение
                await query.message.reply_photo(photo=image_buffer, caption=caption, parse_mode='Markdown')
                
                # Отправляем кнопки отдельно
                keyboard = [
                    [InlineKeyboardButton("🔄 Перегенерировать", callback_data="regenerate_wallpaper")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "💡 Что дальше?",
                    reply_markup=reply_markup
                )
                
                self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 10
                
            except Exception as e:
                logger.error(f"Ошибка перегенерации обоев: {e}")
                await query.message.reply_text(f"❌ Ошибка: {str(e)}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка обработки: {str(e)}")

    # GIF ГЕНЕРАТОР

    async def generate_gif_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для генерации анимированного текста"""

        if not context.args:

            await update.message.reply_text(

                "🎬 **GIF Генератор**\n\n"

                "Создай анимированный текст!\n\n"

                "**Примеры:**\n"

                "`/gif Hello World`\n"

                "`/gif wave Привет`\n"

                "`/gif pulse BOOM`\n"

                "`/gif rainbow Круто`\n"

                "`/gif rotate ДА`\n\n"

                "**Стили:** wave, pulse, rainbow, rotate",

                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])

            )

            return

        

        # Проверяем стиль

        style = "wave"

        text = ' '.join(context.args)

        

        if context.args[0] in ['wave', 'pulse', 'rainbow', 'rotate']:

            style = context.args[0]

            text = ' '.join(context.args[1:])

        

        if not text:

            await update.message.reply_text("❌ Укажите текст для анимации!")

            return

        

        try:

            status_msg = await update.message.reply_text("🎬 Создаю GIF... Подожди пару секунд!")

            

            # Генерируем GIF

            gif_buffer = self.gif_gen.create_text_gif(text, style=style)

            gif_buffer.seek(0)

            

            # Отправляем с правильным именем файла

            await update.message.reply_animation(

                animation=gif_buffer,

                caption=f"🎬 **Анимация: {style}**\n📝 {text}",

                parse_mode='Markdown',

                filename='animation.gif'

            )

            # Отправляем кнопки отдельно
            keyboard = [
                [InlineKeyboardButton("🔄 Создать еще", callback_data="create_another_gif")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💡 Что дальше?",
                reply_markup=reply_markup
            )

            

            await status_msg.delete()

            

            # Начисляем баллы

            user_id = update.message.from_user.id

            self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 5

            

            logger.info(f"GIF generated for user {user_id}: {text} ({style})")

            

        except Exception as e:

            logger.error(f"Ошибка генерации GIF: {e}")

            await update.message.reply_text(f"❌ Ошибка создания GIF: {str(e)}")

    

    async def generate_meme_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для генерации мем-GIF"""

        if not context.args:

            await update.message.reply_text(

                "😂 **Генератор мемов GIF**\n\n"

                "Создай анимированный мем!\n\n"

                "**Формат:**\n"

                "`/meme Верхний текст / Нижний текст`\n\n"

                "**Примеры:**\n"

                "`/meme Когда код заработал / С первого раза`\n"

                "`/meme Пятница / Наконец-то`\n"

                "`/meme Я / Когда нашёл баг`",

                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])

            )

            return

        

        full_text = ' '.join(context.args)

        

        # Разделяем на верхний и нижний текст

        if '/' in full_text:

            parts = full_text.split('/')

            top_text = parts[0].strip()

            bottom_text = parts[1].strip() if len(parts) > 1 else ""

        else:

            top_text = full_text

            bottom_text = ""

        

        try:

            status_msg = await update.message.reply_text("😂 Создаю мем...")

            

            # Генерируем мем

            gif_buffer = self.gif_gen.create_meme_gif(top_text, bottom_text)

            gif_buffer.seek(0)

            

            # Отправляем с правильным именем файла

            await update.message.reply_animation(

                animation=gif_buffer,

                caption=f"😂 **Мем готов!**\n\n{top_text}\n{bottom_text}",

                parse_mode='Markdown',

                filename='meme.gif'

            )

            # Отправляем кнопки отдельно
            keyboard = [
                [InlineKeyboardButton("🔄 Создать еще", callback_data="create_another_meme")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💡 Что дальше?",
                reply_markup=reply_markup
            )

            

            await status_msg.delete()

            

            # Начисляем баллы

            user_id = update.message.from_user.id

            self.user_scores[user_id] = self.user_scores.get(user_id, 0) + 10

            

            logger.info(f"Meme GIF generated for user {user_id}")

            

        except Exception as e:

            logger.error(f"Ошибка генерации мема: {e}")

            await update.message.reply_text(f"❌ Ошибка создания мема: {str(e)}")

    

    async def thinking_gif_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Команда для генерации думающего GIF"""

        text = context.args[0] if context.args else "🤔"

        

        try:

            status_msg = await update.message.reply_text("Создаю думающий GIF...")

            

            gif_buffer = self.gif_gen.create_thinking_gif(text)

            gif_buffer.seek(0)

            

            # Отправляем с правильным именем файла

            await update.message.reply_animation(

                animation=gif_buffer,

                caption=f"{text} Хммм...",

                parse_mode='Markdown',

                filename='thinking.gif'

            )

            # Отправляем кнопки отдельно
            keyboard = [
                [InlineKeyboardButton("🔄 Создать еще", callback_data="create_another_thinking")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💡 Что дальше?",
                reply_markup=reply_markup
            )

            

            await status_msg.delete()

            

        except Exception as e:

            logger.error(f"Ошибка генерации thinking GIF: {e}")

            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик голосовых сообщений"""
        try:
            user_id = update.effective_user.id
            voice = update.message.voice
            
            # Проверяем доступность голосовых функций
            if not self.voice_helper.is_available():
                await update.message.reply_text(
                    "❌ Голосовые команды недоступны.\n\n"
                    "Установите зависимости:\n"
                    "pip install vosk gtts"
                )
                return
            
            # Показываем индикатор обработки
            status_msg = await update.message.reply_text("🎤 Распознаю голосовое сообщение...")
            
            # Проверяем длительность
            if voice.duration and voice.duration < 1:
                await status_msg.edit_text(
                    "⚠️ Голосовое сообщение слишком короткое!\n\n"
                    "💡 Рекомендуется:\n"
                    "• Минимум 2-3 секунды записи\n"
                    "• Говорить четко и громко\n"
                    "• Уменьшить фоновый шум"
                )
                return
            
            # Скачиваем голосовое сообщение
            file = await context.bot.get_file(voice.file_id)
            audio_bytes = await file.download_as_bytearray()
            
            logger.info(f"Скачано голосовое сообщение: {len(audio_bytes)} байт, формат: OGG")
            logger.info(f"Длительность: {voice.duration} сек")
            
            # Обновляем статус
            await status_msg.edit_text("🎤 Конвертирую аудио...")
            
            # Распознаем речь
            logger.info("🎤 Начинаю распознавание речи...")
            recognized_text = self.voice_helper.speech_to_text(bytes(audio_bytes), audio_format="ogg")
            
            if recognized_text:
                logger.info(f"✅ Распознано успешно: '{recognized_text}'")
            else:
                logger.warning("❌ Распознавание не удалось")
                # Дополнительная диагностика
                logger.warning(f"   Длительность: {voice.duration} сек")
                logger.warning(f"   Размер файла: {len(audio_bytes)} байт")
                logger.warning("   Проверь логи для деталей")
            
            if not recognized_text:
                # Получаем инструкции по настройке
                setup_info = self.voice_helper.get_setup_instructions()
                
                error_msg = (
                    "❌ Не удалось распознать речь.\n\n"
                    f"📊 Информация:\n"
                    f"• Длительность: {voice.duration} сек\n"
                    f"• Размер файла: {len(audio_bytes)} байт\n\n"
                    f"{setup_info}\n\n"
                    "💡 Попробуйте:\n"
                    "• Говорить **громче и четче**\n"
                    "• Записать **минимум 2-3 секунды**\n"
                    "• Уменьшить **фоновый шум**\n"
                    "• Говорить **медленнее**\n"
                    "• Проверить **микрофон**\n\n"
                    "🔍 Проверьте логи сервера для деталей."
                )
                
                await status_msg.edit_text(error_msg, parse_mode='Markdown')
                return
            
            # Проверяем режим голосовых ответов (по умолчанию True - голосом)
            voice_mode = self.voice_response_mode.get(user_id, True)
            
            # Обновляем статус (в голосовом режиме показываем меньше информации)
            if voice_mode:
                await status_msg.edit_text(f"🎤 Распознано: _{recognized_text}_\n\n🤔 Обрабатываю...", parse_mode='Markdown')
            else:
                await status_msg.edit_text(f"📝 Распознано: _{recognized_text}_\n\n🤔 Обрабатываю...", parse_mode='Markdown')
            
            # Проверяем, активен ли режим AI чата
            if user_id in self.ai_chat_mode and self.ai_chat_mode[user_id]:
                # Используем AI чат
                # Передаем voice_mode, чтобы не отправлять текст в голосовом режиме
                await self.handle_ai_chat_message(update, recognized_text, voice_mode=voice_mode)
                
                # Генерируем голосовой ответ только если режим включен
                if voice_mode:
                    if user_id in self.ai_chat_history and self.ai_chat_history[user_id]:
                        last_response = self.ai_chat_history[user_id][-1].get("content", "")
                        if last_response and len(last_response) > 0:
                            await self._send_voice_response(update, last_response)
                            # Добавляем кнопки после голосового ответа
                            keyboard = [
                                [InlineKeyboardButton("Вернуться в меню AI", callback_data="ai_menu")],
                                [InlineKeyboardButton("Настройки", callback_data="toggle_voice_mode")]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            # В голосовом режиме отправляем кнопки с текстом
                            await update.message.reply_text(
                                "Управление",
                                reply_markup=reply_markup
                            )
            else:
                # Обычная обработка команды
                response = self.claude.ask_question(recognized_text)
                
                # Отправляем текстовый ответ только если НЕ голосовой режим
                if not voice_mode:
                    if len(response) > 4000:
                        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
                        for part in parts:
                            await update.message.reply_text(part)
                    else:
                        await update.message.reply_text(f"🧠 **Ответ:**\n\n{response}", parse_mode='Markdown')
                
                # Генерируем голосовой ответ только если режим включен
                if voice_mode:
                    await self._send_voice_response(update, response)
                    # Добавляем кнопки после голосового ответа
                    keyboard = [
                        [InlineKeyboardButton("Вернуться в меню", callback_data="back_to_main")],
                        [InlineKeyboardButton("Настройки", callback_data="toggle_voice_mode")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    # В голосовом режиме отправляем кнопки с текстом
                    await update.message.reply_text(
                        "Управление",
                        reply_markup=reply_markup
                    )
            
            await status_msg.delete()
            
        except Exception as e:
            logger.error(f"Ошибка обработки голосового сообщения: {e}")
            import traceback
            traceback.print_exc()
            await update.message.reply_text(
                f"❌ Ошибка обработки голосового сообщения:\n{str(e)}\n\n"
                "💡 Убедитесь, что установлены зависимости:\n"
                "pip install vosk gtts pydub"
            )
    
    async def test_voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для тестирования голосового ответа"""
        try:
            # Получаем текст из аргументов или используем тестовый
            test_text = " ".join(context.args) if context.args else "Привет! Это тестовое голосовое сообщение от бота. Если ты это слышишь, значит всё работает отлично!"
            
            await update.message.reply_text(
                f"🎤 Тестирую голосовой ответ...\n\n"
                f"📝 Текст: _{test_text}_",
                parse_mode='Markdown'
            )
            
            # Отправляем голосовой ответ
            await self._send_voice_response(update, test_text)
            
        except Exception as e:
            logger.error(f"Ошибка тестирования голосового ответа: {e}")
            await update.message.reply_text(
                f"❌ Ошибка: {str(e)}\n\n"
                "💡 Убедитесь, что установлены зависимости:\n"
                "pip install gtts pydub"
            )
    
    async def voice_mode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для просмотра и переключения режима голосовых ответов"""
        try:
            user_id = update.effective_user.id
            
            # Получаем текущий режим
            current_mode = self.voice_response_mode.get(user_id, True)
            
            if current_mode:
                mode_text = "🎤 **Голосовой режим включен**\n\nБот будет отвечать голосом на голосовые сообщения."
                button_text = "💬 Переключить на текстовый режим"
            else:
                mode_text = "💬 **Текстовый режим включен**\n\nБот будет отвечать только текстом, даже на голосовые сообщения."
                button_text = "🎤 Переключить на голосовой режим"
            
            keyboard = [
                [InlineKeyboardButton(button_text, callback_data="toggle_voice_mode")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                mode_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Ошибка переключения режима голосовых ответов: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def toggle_voice_mode(self, query):
        """Переключить режим голосовых ответов через кнопку"""
        try:
            user_id = query.from_user.id
            
            # Переключаем режим
            current_mode = self.voice_response_mode.get(user_id, True)
            new_mode = not current_mode
            self.voice_response_mode[user_id] = new_mode
            
            if new_mode:
                mode_text = "🎤 **Голосовой режим включен**\n\nБот будет отвечать голосом на голосовые сообщения."
                button_text = "💬 Переключить на текстовый режим"
            else:
                mode_text = "💬 **Текстовый режим включен**\n\nБот будет отвечать только текстом, даже на голосовые сообщения."
                button_text = "🎤 Переключить на голосовой режим"
            
            keyboard = [
                [InlineKeyboardButton(button_text, callback_data="toggle_voice_mode")],
                [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                mode_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            await query.answer(f"Режим изменен на {'голосовой' if new_mode else 'текстовый'}")
            
        except Exception as e:
            logger.error(f"Ошибка переключения режима: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def show_reminders_menu(self, query):
        """Показать меню напоминаний и задач"""
        try:
            user_id = query.from_user.id
            
            reminders = self.reminder_helper.get_reminders(user_id)
            tasks = self.reminder_helper.get_tasks(user_id)
            
            keyboard = [
                [InlineKeyboardButton("➕ Добавить напоминание", callback_data="add_reminder")],
                [InlineKeyboardButton("📝 Добавить задачу", callback_data="add_task")],
                [InlineKeyboardButton("⏰ Мои напоминания", callback_data="list_reminders")],
                [InlineKeyboardButton("✅ Мои задачи", callback_data="list_tasks")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = f"""⏰ **Напоминания и задачи**

📊 **Статистика:**
• Напоминаний: {len(reminders)}
• Задач: {len(tasks)}

💡 **Использование:**
• `/remind через 30 минут позвонить маме` - создать напоминание
• `/task купить молоко` - добавить задачу
• `/tasks` - показать все задачи

**Примеры времени:**
• "через 30 минут"
• "через 2 часа"
• "в 15:30"
• "завтра в 10:00"
• "через 1 день"
"""
            
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка показа меню напоминаний: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def remind_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для создания напоминания: /remind через 30 минут текст"""
        try:
            user_id = update.effective_user.id
            
            if not context.args or len(context.args) < 3:
                await update.message.reply_text(
                    "❌ **Неправильный формат!**\n\n"
                    "**Использование:**\n"
                    "`/remind через 30 минут позвонить маме`\n"
                    "`/remind в 15:30 встреча с командой`\n"
                    "`/remind завтра в 10:00 проснуться`\n\n"
                    "**Примеры времени:**\n"
                    "• `через 30 минут`\n"
                    "• `через 2 часа`\n"
                    "• `в 15:30`\n"
                    "• `завтра в 10:00`\n"
                    "• `через 1 день`",
                    parse_mode='Markdown'
                )
                return
            
            # Парсим время и текст
            args = " ".join(context.args)
            
            # Ищем паттерн времени
            time_patterns = [
                r'через\s+\d+\s+минут',
                r'через\s+\d+\s+час',
                r'через\s+\d+\s+дн',
                r'в\s+\d{1,2}:\d{2}',
                r'завтра\s+в\s+\d{1,2}:\d{2}',
            ]
            
            time_str = None
            for pattern in time_patterns:
                match = re.search(pattern, args, re.IGNORECASE)
                if match:
                    time_str = match.group(0)
                    break
            
            if not time_str:
                await update.message.reply_text(
                    "❌ Не удалось распознать время!\n\n"
                    "**Примеры:**\n"
                    "• `через 30 минут`\n"
                    "• `через 2 часа`\n"
                    "• `в 15:30`\n"
                    "• `завтра в 10:00`",
                    parse_mode='Markdown'
                )
                return
            
            # Извлекаем текст напоминания
            text = args.replace(time_str, "").strip()
            if not text:
                await update.message.reply_text("❌ Укажите текст напоминания!")
                return
            
            # Добавляем напоминание
            reminder = self.reminder_helper.add_reminder(user_id, text, time_str)
            
            if reminder:
                reminder_time = datetime.fromisoformat(reminder['time'])
                time_display = reminder_time.strftime("%d.%m.%Y %H:%M")
                
                await update.message.reply_text(
                    f"✅ **Напоминание создано!**\n\n"
                    f"📝 {text}\n"
                    f"⏰ {time_display}\n\n"
                    f"Я напомню тебе в указанное время!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Не удалось создать напоминание.\n\n"
                    "Проверь формат времени!"
                )
                
        except Exception as e:
            logger.error(f"Ошибка создания напоминания: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для добавления задачи: /task купить молоко"""
        try:
            user_id = update.effective_user.id
            
            if not context.args:
                await update.message.reply_text(
                    "❌ **Неправильный формат!**\n\n"
                    "**Использование:**\n"
                    "`/task купить молоко`\n"
                    "`/task high важная задача` - с приоритетом\n\n"
                    "**Приоритеты:** `low`, `normal`, `high`",
                    parse_mode='Markdown'
                )
                return
            
            args = " ".join(context.args)
            priority = "normal"
            
            # Проверяем приоритет
            if args.lower().startswith("high "):
                priority = "high"
                args = args[5:]
            elif args.lower().startswith("low "):
                priority = "low"
                args = args[4:]
            elif args.lower().startswith("normal "):
                priority = "normal"
                args = args[7:]
            
            task = self.reminder_helper.add_task(user_id, args, priority)
            
            if task:
                priority_emoji = {"low": "🟢", "normal": "🟡", "high": "🔴"}
                emoji = priority_emoji.get(priority, "🟡")
                
                await update.message.reply_text(
                    f"✅ **Задача добавлена!**\n\n"
                    f"{emoji} {args}\n\n"
                    f"Используй `/tasks` чтобы посмотреть все задачи",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Не удалось добавить задачу!")
                
        except Exception as e:
            logger.error(f"Ошибка добавления задачи: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для просмотра всех задач"""
        try:
            user_id = update.effective_user.id
            
            tasks = self.reminder_helper.get_tasks(user_id, include_completed=True)
            
            if not tasks:
                await update.message.reply_text(
                    "📝 **Нет задач**\n\n"
                    "Добавь задачу командой:\n"
                    "`/task купить молоко`",
                    parse_mode='Markdown'
                )
                return
            
            completed = [t for t in tasks if t.get('completed', False)]
            active = [t for t in tasks if not t.get('completed', False)]
            
            text = "✅ **Мои задачи**\n\n"
            
            if active:
                text += "⏳ **Активные:**\n"
                keyboard_buttons = []
                for task in active[:10]:  # Показываем максимум 10
                    formatted = self.reminder_helper.format_task(task)
                    text += f"{formatted}\n"
                    keyboard_buttons.append([
                        InlineKeyboardButton(
                            f"✅ {task['text'][:30]}",
                            callback_data=f"complete_task_{task['id']}"
                        )
                    ])
                    keyboard_buttons.append([
                        InlineKeyboardButton(
                            f"❌ Удалить: {task['text'][:25]}",
                            callback_data=f"delete_task_{task['id']}"
                        )
                    ])
                
                keyboard_buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="reminders_menu")])
                reply_markup = InlineKeyboardMarkup(keyboard_buttons)
            else:
                text += "⏳ Активных задач нет\n\n"
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Назад", callback_data="reminders_menu")]
                ])
            
            if completed:
                text += f"\n✅ **Выполнено:** {len(completed)}\n"
            
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка просмотра задач: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def complete_task_handler(self, query, task_id: int):
        """Обработчик завершения задачи"""
        try:
            user_id = query.from_user.id
            
            if self.reminder_helper.complete_task(user_id, task_id):
                await query.answer("✅ Задача выполнена!")
                # Обновляем список задач через меню
                await self.show_reminders_menu(query)
            else:
                await query.answer("❌ Задача не найдена!")
                
        except Exception as e:
            logger.error(f"Ошибка завершения задачи: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def delete_task_handler(self, query, task_id: int):
        """Обработчик удаления задачи"""
        try:
            user_id = query.from_user.id
            
            if self.reminder_helper.delete_task(user_id, task_id):
                await query.answer("✅ Задача удалена!")
                # Обновляем список задач через меню
                await self.show_reminders_menu(query)
            else:
                await query.answer("❌ Задача не найдена!")
                
        except Exception as e:
            logger.error(f"Ошибка удаления задачи: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def delete_reminder_handler(self, query, reminder_id: int):
        """Обработчик удаления напоминания"""
        try:
            user_id = query.from_user.id
            
            if self.reminder_helper.delete_reminder(user_id, reminder_id):
                await query.answer("✅ Напоминание удалено!")
                await self.show_reminders_menu(query)
            else:
                await query.answer("❌ Напоминание не найдено!")
                
        except Exception as e:
            logger.error(f"Ошибка удаления напоминания: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def start_add_reminder(self, query):
        """Начать процесс добавления напоминания"""
        try:
            user_id = query.from_user.id
            
            # Устанавливаем состояние
            self.reminder_states[user_id] = {
                'type': 'reminder_text'
            }
            
            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data="reminders_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "➕ **Добавить напоминание**\n\n"
                "📝 Напиши текст напоминания:\n\n"
                "Например: позвонить маме, купить молоко, встреча с командой",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            await query.answer("Введи текст напоминания")
            
        except Exception as e:
            logger.error(f"Ошибка начала добавления напоминания: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def show_reminder_time_selection(self, update: Update):
        """Показать выбор времени для напоминания"""
        try:
            user_id = update.effective_user.id
            state = self.reminder_states.get(user_id, {})
            text = state.get('text', '')
            
            keyboard = [
                [
                    InlineKeyboardButton("⏰ 30 мин", callback_data="reminder_time_через 30 минут"),
                    InlineKeyboardButton("⏰ 1 час", callback_data="reminder_time_через 1 час")
                ],
                [
                    InlineKeyboardButton("⏰ 2 часа", callback_data="reminder_time_через 2 часа"),
                    InlineKeyboardButton("⏰ 3 часа", callback_data="reminder_time_через 3 часа")
                ],
                [
                    InlineKeyboardButton("📅 Завтра 10:00", callback_data="reminder_time_завтра в 10:00"),
                    InlineKeyboardButton("📅 Завтра 15:00", callback_data="reminder_time_завтра в 15:00")
                ],
                [
                    InlineKeyboardButton("📅 Сегодня 18:00", callback_data="reminder_time_в 18:00"),
                    InlineKeyboardButton("📅 Сегодня 20:00", callback_data="reminder_time_в 20:00")
                ],
                [InlineKeyboardButton("✏️ Ввести свое время", callback_data="reminder_custom_time")],
                [InlineKeyboardButton("❌ Отмена", callback_data="reminders_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"⏰ **Выбери время для напоминания:**\n\n"
                f"📝 Текст: _{text}_\n\n"
                f"Или введи свое время (например: 'через 45 минут', 'в 14:30')",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Ошибка показа выбора времени: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def handle_reminder_time_selection(self, query, time_str: str):
        """Обработать выбор времени для напоминания"""
        try:
            user_id = query.from_user.id
            state = self.reminder_states.get(user_id, {})
            text = state.get('text', '')
            
            if not text:
                await query.answer("❌ Текст напоминания не найден!")
                return
            
            # Добавляем напоминание
            reminder = self.reminder_helper.add_reminder(user_id, text, time_str)
            
            if reminder:
                reminder_time = datetime.fromisoformat(reminder['time'])
                time_display = reminder_time.strftime("%d.%m.%Y %H:%M")
                
                # Удаляем состояние
                del self.reminder_states[user_id]
                
                keyboard = [
                    [InlineKeyboardButton("⏰ Мои напоминания", callback_data="list_reminders")],
                    [InlineKeyboardButton("🔙 В меню", callback_data="reminders_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"✅ **Напоминание создано!**\n\n"
                    f"📝 {text}\n"
                    f"⏰ {time_display}\n\n"
                    f"Я напомню тебе в указанное время!",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                await query.answer("✅ Напоминание создано!")
            else:
                await query.answer("❌ Не удалось создать напоминание. Проверь формат времени!")
                
        except Exception as e:
            logger.error(f"Ошибка обработки выбора времени: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def start_add_task(self, query):
        """Начать процесс добавления задачи"""
        try:
            user_id = query.from_user.id
            
            keyboard = [
                [
                    InlineKeyboardButton("🔴 Высокий", callback_data="task_priority_high"),
                    InlineKeyboardButton("🟡 Обычный", callback_data="task_priority_normal")
                ],
                [
                    InlineKeyboardButton("🟢 Низкий", callback_data="task_priority_low")
                ],
                [InlineKeyboardButton("❌ Отмена", callback_data="reminders_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📝 **Добавить задачу**\n\n"
                "1️⃣ Сначала выбери приоритет:\n\n"
                "🔴 **Высокий** - срочные и важные задачи\n"
                "🟡 **Обычный** - стандартные задачи\n"
                "🟢 **Низкий** - не срочные задачи",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            await query.answer("Выбери приоритет задачи")
            
        except Exception as e:
            logger.error(f"Ошибка начала добавления задачи: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def handle_task_priority_selection(self, query, priority: str):
        """Обработать выбор приоритета задачи"""
        try:
            user_id = query.from_user.id
            
            # Устанавливаем состояние
            self.reminder_states[user_id] = {
                'type': 'task_text',
                'priority': priority
            }
            
            priority_names = {
                'high': '🔴 Высокий',
                'normal': '🟡 Обычный',
                'low': '🟢 Низкий'
            }
            priority_name = priority_names.get(priority, '🟡 Обычный')
            
            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data="reminders_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📝 **Добавить задачу**\n\n"
                f"Приоритет: {priority_name}\n\n"
                f"📝 Теперь напиши текст задачи:\n\n"
                f"Например: купить молоко, позвонить клиенту, сделать отчет",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            await query.answer(f"Приоритет: {priority_name}. Теперь введи текст задачи")
            
        except Exception as e:
            logger.error(f"Ошибка обработки выбора приоритета: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def list_reminders_handler(self, query):
        """Обработчик показа списка напоминаний"""
        try:
            user_id = query.from_user.id
            reminders = self.reminder_helper.get_reminders(user_id)
            
            if not reminders:
                keyboard = [
                    [InlineKeyboardButton("➕ Добавить напоминание", callback_data="add_reminder")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="reminders_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "📝 **Нет активных напоминаний**\n\n"
                    "Добавь напоминание, чтобы не забыть о важных делах!",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                await query.answer("Нет активных напоминаний")
                return
            
            text = "⏰ **Мои напоминания:**\n\n"
            keyboard_buttons = []
            
            for reminder in reminders[:10]:  # Показываем максимум 10
                formatted = self.reminder_helper.format_reminder(reminder)
                text += f"{formatted}\n\n"
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        f"❌ Удалить: {reminder['text'][:25]}",
                        callback_data=f"delete_reminder_{reminder['id']}"
                    )
                ])
            
            keyboard_buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="reminders_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard_buttons)
            
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка показа напоминаний: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def handle_custom_reminder_time(self, query):
        """Обработать запрос на ввод своего времени"""
        try:
            user_id = query.from_user.id
            state = self.reminder_states.get(user_id, {})
            
            if not state.get('text'):
                await query.answer("❌ Текст напоминания не найден!")
                return
            
            # Меняем состояние на ввод времени
            state['type'] = 'reminder_custom_time'
            
            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data="reminders_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✏️ **Введи свое время:**\n\n"
                f"📝 Текст: _{state.get('text')}_\n\n"
                f"Напиши время в любом формате:\n"
                f"• `через 45 минут`\n"
                f"• `через 2 часа 30 минут`\n"
                f"• `в 14:30`\n"
                f"• `завтра в 10:00`\n"
                f"• `через 1 день`",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            await query.answer("Введи время в любом формате")
            
        except Exception as e:
            logger.error(f"Ошибка обработки кастомного времени: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def show_web_search_menu(self, query):
        """Показать меню поиска в интернете"""
        try:
            keyboard = [
                [InlineKeyboardButton("🔍 Обычный поиск", callback_data="web_search_normal")],
                [InlineKeyboardButton("📰 Поиск новостей", callback_data="web_search_news")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = """🔍 **Поиск в интернете**

Найди актуальную информацию в интернете!

💡 Нажмите кнопку ниже и просто напишите запрос:
• Обычный поиск
• Поиск новостей

**Примеры запросов:**
• как работает ChatGPT
• погода в Москве
• технологии 2025
• лучшие практики Python
"""
            
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка показа меню поиска: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def web_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для поиска в интернете: /search запрос"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "🔍 **Поиск в интернете**\n\n"
                    "Найди актуальную информацию!\n\n"
                    "**Примеры:**\n"
                    "• лучшие практики программирования\n"
                    "• новости технологий\n"
                    "• как установить Python",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="tools")]])
                )
                return
            
            query = " ".join(context.args)
            
            status_msg = await update.message.reply_text(f"🔍 Ищу информацию: _{query}_...", parse_mode='Markdown')
            
            # Выполняем поиск
            results = self.web_search.search(query, max_results=5)
            
            if results.get('success'):
                formatted = self.web_search.format_results(results)
                
                keyboard = [
                    [InlineKeyboardButton("🔍 Искать еще", callback_data="web_search_normal")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await status_msg.edit_text(formatted, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await status_msg.edit_text(
                    f"❌ Не удалось выполнить поиск.\n\n"
                    f"Ошибка: {results.get('error', 'Неизвестная ошибка')}\n\n"
                    f"Попробуйте изменить запрос или повторить позже."
                )
                
        except Exception as e:
            logger.error(f"Ошибка поиска в интернете: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def news_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для поиска новостей: /news запрос"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "📰 **Поиск новостей**\n\n"
                    "Найди актуальные новости!\n\n"
                    "**Использование:**\n"
                    "`/news технологии`\n"
                    "`/news программирование`\n"
                    "`/news искусственный интеллект`\n\n"
                    "**Примеры:**\n"
                    "• `/news последние новости технологий`\n"
                    "• `/news новости Python`\n"
                    "• `/news события в мире IT`",
                    parse_mode='Markdown'
                )
                return
            
            query = " ".join(context.args)
            
            status_msg = await update.message.reply_text(f"📰 Ищу новости: _{query}_...", parse_mode='Markdown')
            
            # Выполняем поиск новостей
            results = self.web_search.search_news(query, max_results=5)
            
            if results.get('success'):
                formatted = self.web_search.format_results(results)
                
                keyboard = [
                    [InlineKeyboardButton("📰 Искать еще новости", callback_data="web_search_news")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await status_msg.edit_text(formatted, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await status_msg.edit_text(
                    f"❌ Не удалось найти новости.\n\n"
                    f"Ошибка: {results.get('error', 'Неизвестная ошибка')}\n\n"
                    f"Попробуйте изменить запрос или повторить позже."
                )
                
        except Exception as e:
            logger.error(f"Ошибка поиска новостей: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def show_create_document_menu(self, query):
        """Показать меню создания документов"""
        try:
            keyboard = [
                [InlineKeyboardButton("📝 Конспект", callback_data="doc_type_summary")],
                [InlineKeyboardButton("📋 Заметки", callback_data="doc_type_notes")],
                [InlineKeyboardButton("✏️ Свой формат", callback_data="doc_type_custom")],
                [InlineKeyboardButton("🔙 Назад", callback_data="tools")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = """📄 **Создать документ Word**

Выбери тип документа:

📝 **Конспект** - структурированный конспект из текста
📋 **Заметки** - удобные заметки для изучения
✏️ **Свой формат** - укажи свои требования

💡 **Как использовать:**
1. Выбери тип документа
2. Отправь текст боту
3. Получи готовый Word файл!

**Примеры:**
• Отправь лекцию → получи конспект
• Отправь статью → получи структурированные заметки
• Отправь текст → получи документ в нужном формате
"""
            
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка показа меню документов: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def start_create_document(self, query, doc_type: str):
        """Начать процесс создания документа"""
        try:
            user_id = query.from_user.id
            
            doc_types = {
                'summary': 'Конспект',
                'notes': 'Заметки',
                'custom': 'Свой формат'
            }
            doc_name = doc_types.get(doc_type, 'Документ')
            
            if doc_type == 'custom':
                # Для кастомного формата просим инструкции
                self.document_states[user_id] = {
                    'type': 'custom',
                    'step': 'instruction'
                }
                
                keyboard = [
                    [InlineKeyboardButton("❌ Отмена", callback_data="create_document_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"✏️ **Создать документ: {doc_name}**\n\n"
                    f"📝 Напиши инструкцию, как обработать текст:\n\n"
                    f"Например:\n"
                    f"• 'Создай план статьи'\n"
                    f"• 'Выдели основные тезисы'\n"
                    f"• 'Структурируй информацию по разделам'\n"
                    f"• 'Создай резюме с ключевыми моментами'",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                await query.answer("Введи инструкцию для обработки")
            else:
                # Для стандартных типов сразу просим текст
                self.document_states[user_id] = {
                    'type': doc_type,
                    'title': doc_name
                }
                
                keyboard = [
                    [InlineKeyboardButton("❌ Отмена", callback_data="create_document_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"📄 **Создать {doc_name}**\n\n"
                    f"📝 Отправь текст, из которого нужно создать {doc_name.lower()}:\n\n"
                    f"Можно отправить:\n"
                    f"• Длинный текст сообщением\n"
                    f"• Текст из файла\n"
                    f"• Лекцию, статью, заметки",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                await query.answer(f"Отправь текст для создания {doc_name.lower()}")
            
        except Exception as e:
            logger.error(f"Ошибка начала создания документа: {e}")
            await query.answer(f"❌ Ошибка: {str(e)}")
    
    async def check_reminders(self, context: ContextTypes.DEFAULT_TYPE):
        """Фоновая задача для проверки и отправки напоминаний"""
        try:
            due_reminders = self.reminder_helper.get_due_reminders()
            
            for reminder in due_reminders:
                user_id = reminder.get('user_id')
                reminder_id = reminder.get('id')
                text = reminder.get('text', 'Напоминание')
                
                try:
                    # Отправляем напоминание
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"⏰ **Напоминание!**\n\n{text}",
                        parse_mode='Markdown'
                    )
                    
                    # Помечаем как отправленное
                    self.reminder_helper.mark_reminder_sent(user_id, reminder_id)
                    
                    logger.info(f"Отправлено напоминание пользователю {user_id}: {text}")
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка проверки напоминаний: {e}")
    
    async def _send_voice_response(self, update: Update, text: str):
        """Отправить голосовой ответ"""
        try:
            logger.info(f"Генерирую голосовой ответ для текста: {text[:50]}...")
            
            # Ограничиваем длину текста для TTS (gTTS имеет лимиты)
            max_length = 500  # Примерно 30-40 секунд речи
            original_length = len(text)
            if len(text) > max_length:
                text = text[:max_length] + "..."
                logger.info(f"Текст обрезан с {original_length} до {len(text)} символов")
            
            # Синтезируем речь
            logger.info("Синтезирую речь через gTTS...")
            audio_buffer = self.voice_helper.text_to_speech(text, language="ru")
            
            if audio_buffer:
                audio_size = len(audio_buffer.getvalue()) if hasattr(audio_buffer, 'getvalue') else 'unknown'
                logger.info(f"Аудио синтезировано: {audio_size} байт")
                
                # Отправляем голосовое сообщение
                # Telegram принимает BytesIO напрямую
                try:
                    logger.info("Отправляю голосовое сообщение через reply_voice...")
                    await update.message.reply_voice(
                        voice=audio_buffer,
                        caption="🎤 Голосовой ответ",
                        filename="response.ogg"  # Указываем имя файла
                    )
                    logger.info("✅ Голосовое сообщение успешно отправлено!")
                except Exception as e:
                    # Если не получилось с reply_voice, пробуем через document
                    logger.warning(f"Ошибка reply_voice, пробуем через reply_audio: {e}")
                    audio_buffer.seek(0)
                    try:
                        await update.message.reply_audio(
                            audio=audio_buffer,
                            caption="🎤 Голосовой ответ",
                            filename="response.ogg"
                        )
                        logger.info("✅ Голосовое сообщение отправлено через reply_audio!")
                    except Exception as e2:
                        logger.error(f"Ошибка отправки через reply_audio: {e2}")
                        await update.message.reply_text(
                            f"❌ Не удалось отправить голосовой ответ.\n\n"
                            f"Ошибка: {str(e2)}\n\n"
                            f"💡 Проверьте:\n"
                            f"• Установлен ли gTTS: `pip install gtts`\n"
                            f"• Есть ли интернет для синтеза речи"
                        )
            else:
                logger.warning("Не удалось синтезировать голосовой ответ")
                await update.message.reply_text(
                    "❌ Не удалось синтезировать голосовой ответ.\n\n"
                    "💡 Проверьте:\n"
                    "• Установлен ли gTTS: `pip install gtts`\n"
                    "• Есть ли интернет для синтеза речи"
                )
                
        except Exception as e:
            logger.error(f"Ошибка отправки голосового ответа: {e}")
            import traceback
            traceback.print_exc()
            await update.message.reply_text(
                f"❌ Ошибка отправки голосового ответа:\n{str(e)}\n\n"
                "💡 Убедитесь, что установлены зависимости:\n"
                "pip install gtts pydub"
            )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        """Обработчик callback запросов"""

        query = update.callback_query

        

        if query.data.startswith("quiz_answer_"):

            await self.handle_quiz_answer(query)

        elif query.data.startswith("pass_"):

            length = int(query.data.split("_")[1])

            await self.generate_password(query, length)

        else:

            await self.button_callback(update, context)



def main():

    """Основная функция для запуска бота"""

    bot = ITHelperBot()

    

    # Создание приложения

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    

    # Добавление обработчиков

    application.add_handler(CommandHandler("start", bot.start))

    application.add_handler(CommandHandler("help", bot.help_command))

    application.add_handler(CommandHandler("stats", lambda u, c: bot.show_stats(u.callback_query)))

    application.add_handler(CommandHandler("games", lambda u, c: bot.show_games_menu(u.callback_query)))

    application.add_handler(CommandHandler("tools", lambda u, c: bot.show_tools_menu(u.callback_query)))

    application.add_handler(CommandHandler("guess", bot.start_guess_game))

    application.add_handler(CommandHandler("quiz", bot.start_quiz_game))

    application.add_handler(CommandHandler("password", bot.show_password_menu))

    application.add_handler(CommandHandler("qr", bot.create_qr_code))

    application.add_handler(CommandHandler("weather", bot.get_weather))

    application.add_handler(CommandHandler("translate", bot.translate_command))

    application.add_handler(CommandHandler("music", bot.music_search_command))

    application.add_handler(CommandHandler("github", bot.github_command))

    application.add_handler(CommandHandler("currency", bot.convert_currency))

    application.add_handler(CommandHandler("code", bot.generate_code))

    

    # AI обработчики

    application.add_handler(CommandHandler("chat", bot.start_ai_chat_command))

    application.add_handler(CommandHandler("ask", bot.ai_ask))

    application.add_handler(CommandHandler("image", bot.generate_image_command))

    application.add_handler(CommandHandler("wallpaper", bot.generate_wallpaper_command))

    application.add_handler(CommandHandler("translate", bot.translate_command))

    application.add_handler(CommandHandler("music", bot.music_command))

    application.add_handler(CommandHandler("imgregen", bot.regenerate_image_command))

    application.add_handler(CommandHandler("aicode", bot.ai_code_generate))

    application.add_handler(CommandHandler("project", bot.ai_create_project))

    application.add_handler(CommandHandler("explain", bot.ai_explain_code))

    application.add_handler(CommandHandler("debug", bot.ai_debug_code))

    application.add_handler(CommandHandler("optimize", bot.ai_optimize_code))

    

    # GIF команды

    application.add_handler(CommandHandler("gif", bot.generate_gif_command))

    application.add_handler(CommandHandler("meme", bot.generate_meme_command))

    application.add_handler(CommandHandler("thinking", bot.thinking_gif_command))
    
    application.add_handler(CommandHandler("test_voice", bot.test_voice_command))
    
    application.add_handler(CommandHandler("voice_mode", bot.voice_mode_command))
    
    application.add_handler(CommandHandler("remind", bot.remind_command))
    
    application.add_handler(CommandHandler("task", bot.task_command))
    
    application.add_handler(CommandHandler("tasks", bot.tasks_command))
    
    application.add_handler(CommandHandler("search", bot.web_search_command))
    
    application.add_handler(CommandHandler("news", bot.news_search_command))
    
    # Фоновая задача для проверки напоминаний каждую минуту
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(
            bot.check_reminders,
            interval=60,  # Каждую минуту
            first=10  # Начать через 10 секунд
        )
        logger.info("✅ Фоновая задача для напоминаний запущена")

    

    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    # Обработчик файлов для GitHub Gists
    application.add_handler(MessageHandler(filters.Document.ALL, bot.handle_document))

    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, bot.handle_voice))

    

    # Запуск бота

    print("IT Helper Bot запущен!")

    # Настройка обработки ошибок конфликта
    try:
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,  # Игнорировать старые обновления
            close_loop=False
        )
    except Exception as e:
        error_msg = str(e)
        if "Conflict" in error_msg or "409" in error_msg:
            print("\n[ERROR] Конфликт: другой экземпляр бота уже запущен!")
            print("[INFO] Выполните на сервере:")
            print("   bash stop_all_bots.sh")
            print("   или")
            print("   sudo systemctl stop telegram-bot.service")
            print("   ps aux | grep run_bot.py")
            print("   kill <PID>")
        else:
            print(f"\n[ERROR] Ошибка запуска бота: {e}")
        raise



if __name__ == '__main__':

    main()

