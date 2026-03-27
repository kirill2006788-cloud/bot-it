# IT Helper Bot - Пример конфигурации
# Скопируйте этот файл в config.py и заполните своими данными

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = "your_telegram_bot_token_here"  # Получите у @BotFather
BOT_USERNAME = "your_bot_username"

# API Keys (опционально - для реальных данных)
OPENWEATHER_API_KEY = "your_openweather_api_key"  # Получите на openweathermap.org
EXCHANGE_API_KEY = "your_exchange_api_key"  # Получите на exchangerate-api.com

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Database Configuration (SQLite для простоты)
DATABASE_URL = "sqlite:///bot_database.db"

# Bot Features Configuration
MAX_GAME_SCORE = 100
MAX_PASSWORD_LENGTH = 50
MAX_QR_TEXT_LENGTH = 1000

# Инструкции по получению API ключей:
# 1. Telegram Bot Token:
#    - Напишите @BotFather в Telegram
#    - Создайте бота командой /newbot
#    - Скопируйте полученный токен
#
# 2. OpenWeatherMap API:
#    - Зарегистрируйтесь на openweathermap.org
#    - Получите бесплатный API ключ
#
# 3. ExchangeRate API:
#    - Зарегистрируйтесь на exchangerate-api.com
#    - Получите бесплатный API ключ
