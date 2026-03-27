#!/usr/bin/env python3
"""
IT Helper Bot - Запуск веб-приложения
Простой скрипт для запуска Flask веб-приложения
"""

import sys
import os
from web_app import app, FLASK_HOST, FLASK_PORT

if __name__ == '__main__':
    print("🌐 Запуск веб-приложения IT Helper Bot...")
    print(f"📱 Адрес: http://{FLASK_HOST}:{FLASK_PORT}")
    print("❌ Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Веб-приложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка при запуске веб-приложения: {e}")
        sys.exit(1)
