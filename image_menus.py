#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Меню для генерации изображений
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from characters_database import CHARACTERS, STYLES, QUALITY


async def show_main_image_menu(query, bot_instance):
    """Главное меню генерации изображений"""
    user_id = query.from_user.id
    current_model = bot_instance.image_gen.get_user_model(user_id)
    model_title = {
        "fooocus": "Fooocus (локально)",
        "kandinsky": "Kandinsky",
        "openai": "OpenAI",
    }.get(current_model, current_model)

    keyboard = [
        [InlineKeyboardButton("🧠 Выбрать модель", callback_data="img_model_menu")],
        [InlineKeyboardButton("🎨 Стили", callback_data="img_styles_menu")],
        [InlineKeyboardButton("⚙️ Качество", callback_data="img_quality_menu")],
        [InlineKeyboardButton("🔙 Назад", callback_data="ai_menu")]
    ]
    
    text = """
🎨 **AI Генерация изображений**

🤖 **Текущая модель:** `{model_title}`

💡 **Команды:**
`/image [описание]` - Создать изображение
`/imgregen` - Перегенерировать последнее

🎯 **Примеры:**
`/image jett valorant`
`/image дракон в фэнтези стиле`
`/image кот программист за компьютером`
`/image закат на море в аниме стиле`

📝 **Популярные персонажи:**
jett, sage, phoenix, reyna (Valorant)
hu tao, raiden, ganyu (Genshin)
naruto, goku, nezuko (Anime)
    """
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def show_model_menu(query, bot_instance):
    """Меню выбора модели генерации."""
    user_id = query.from_user.id
    current = bot_instance.image_gen.get_user_model(user_id)
    options = [
        ("fooocus", "🖼 Fooocus (локально)"),
        ("kandinsky", "🎨 Kandinsky"),
        ("openai", "☁️ OpenAI"),
    ]
    keyboard = []
    for key, title in options:
        check = "✅ " if key == current else ""
        keyboard.append([InlineKeyboardButton(f"{check}{title}", callback_data=f"setmodel_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")])
    text = (
        "🧠 **Выбор модели генерации**\n\n"
        "• `Fooocus` — локально на вашем ПК\n"
        "• `Kandinsky` — облачный API\n"
        "• `OpenAI` — DALL-E\n\n"
        "Выбор применяется для ваших следующих генераций."
    )
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def show_styles_menu(query, bot_instance):
    """Меню выбора стилей"""
    keyboard = []
    
    for style_key, style_data in STYLES.items():
        style_name = style_data.split('|')[0]
        keyboard.append([InlineKeyboardButton(style_name, callback_data=f"setstyle_{style_key}")])
    
    keyboard.append([InlineKeyboardButton("🔄 Без стиля", callback_data="setstyle_none")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")])
    
    text = """
🎨 **Выбор стиля**

Выбери художественный стиль:

📸 Реализм - фотореалистично
🎭 Аниме - японский стиль
🌃 Киберпанк - неоновая футуристика
🧙 Фэнтези - магия
🎨 Мультяшный - яркие мультики
🖼️ Масло - классическая живопись
💻 Digital Art - цифровая графика
🎮 Pixel Art - ретро пиксели
🌊 Акварель - рисунок акварелью
✏️ Эскиз - карандаш
🎲 3D Рендер - 3D графика
📚 Комикс - стиль комиксов
    """
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def show_characters_menu(query):
    """Меню персонажей"""
    keyboard = []
    
    keyboard.append([InlineKeyboardButton("━━━ Valorant ━━━", callback_data="noop")])
    for char in ["jett", "sage", "phoenix", "reyna"]:
        keyboard.append([InlineKeyboardButton(char.title(), callback_data=f"char_{char}")])
    
    keyboard.append([InlineKeyboardButton("━━━ Genshin ━━━", callback_data="noop")])
    for char in ["hu tao", "raiden", "ganyu"]:
        keyboard.append([InlineKeyboardButton(char.title(), callback_data=f"char_{char}")])
    
    keyboard.append([InlineKeyboardButton("━━━ Anime ━━━", callback_data="noop")])
    for char in ["naruto", "goku", "nezuko"]:
        keyboard.append([InlineKeyboardButton(char.title(), callback_data=f"char_{char}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")])
    
    text = """
👤 **Популярные персонажи**

Бот знает этих персонажей!
Просто напиши их имя в промпте:

`/image jett на улице токио`
`/image raiden под сакурой`
`/image naruto и sasuke`

Выбери персонажа чтобы увидеть пример ⬇️
    """
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def show_quality_menu(query, bot_instance):
    """Меню качества"""
    user_id = query.from_user.id
    current = bot_instance.image_gen.get_user_settings(user_id)['quality']
    
    keyboard = []
    for q_key, q_data in QUALITY.items():
        check = "✅ " if q_key == current else ""
        button_text = f"{check}{q_data['name']} - {q_data['time']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"setqual_{q_key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="ai_image_menu")])
    
    text = """
⚙️ **Настройки качества**

⚡ **Быстро (512x512)** - для тестов
⚙️ **Обычно (1024x1024)** - оптимально
💎 **Высокое (1024x1024)** - макс качество

Все режимы бесплатны!
    """
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def show_character_info(query, char_key):
    """Показать инфо о персонаже"""
    if char_key in CHARACTERS:
        text = f"""
👤 **Персонаж: {char_key.title()}**

📝 **Описание:**
_{CHARACTERS[char_key][:150]}..._

💡 **Использование:**
`/image {char_key} [контекст]`

🎯 **Примеры:**
`/image {char_key} на улице`
`/image {char_key} в бою`
        """
        
        keyboard = [[InlineKeyboardButton("🔙 К персонажам", callback_data="img_chars")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

