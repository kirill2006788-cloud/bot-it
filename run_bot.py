#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IT Helper Bot - Запуск бота
Простой скрипт для запуска Telegram бота
"""

import sys
import os

# Настройка UTF-8 для Windows консоли
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from bot import main
import signal
import atexit

# Флаг для отслеживания запущенного процесса
_process_file = None

def cleanup():
    """Очистка при выходе"""
    global _process_file
    if _process_file:
        try:
            import os
            if os.path.exists(_process_file):
                os.remove(_process_file)
        except:
            pass

def check_existing_process():
    """Проверка на уже запущенный процесс"""
    import os
    pid_file = "/opt/bot/bot.pid"
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            # Проверяем, существует ли процесс
            try:
                os.kill(old_pid, 0)  # Проверка без убийства
                print(f"[WARN] Найден запущенный процесс с PID {old_pid}")
                print("[INFO] Остановите его вручную или удалите /opt/bot/bot.pid")
                return True
            except OSError:
                # Процесс не существует, удаляем старый PID файл
                os.remove(pid_file)
                print("[INFO] Удален устаревший PID файл")
        except:
            pass
    return False

def create_pid_file():
    """Создание PID файла"""
    import os
    global _process_file
    pid_file = "/opt/bot/bot.pid"
    try:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        _process_file = pid_file
        atexit.register(cleanup)
        # Обработчик сигналов для очистки
        signal.signal(signal.SIGTERM, lambda s, f: cleanup())
        signal.signal(signal.SIGINT, lambda s, f: cleanup())
    except Exception as e:
        print(f"[WARN] Не удалось создать PID файл: {e}")

if __name__ == '__main__':
    # Настройка логирования в файл (опционально)
    import logging
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.log")
    
    # Добавляем FileHandler для записи в файл
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Получаем root logger и добавляем handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    print("Bot starting: IT Helper Bot...")
    print("Token:", "<TELEGRAM_TOKEN_FROM_ENV>")
    print("For web interface: python web_app.py")
    print("To stop: press Ctrl+C")
    print(f"📝 Логи записываются в: {log_file}")
    print("-" * 50)
    
    # Проверка на существующий процесс (только на Linux)
    if sys.platform != 'win32':
        if check_existing_process():
            print("[ERROR] Другой экземпляр бота уже запущен!")
            print("[INFO] Выполните: bash stop_all_bots.sh")
            sys.exit(1)
        create_pid_file()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting bot: {e}")
        cleanup()
        sys.exit(1)
