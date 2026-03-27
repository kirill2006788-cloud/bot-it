#!/bin/bash
# Скрипт для проверки запущенных экземпляров бота

echo "=== Проверка запущенных процессов бота ==="
echo ""

# Поиск процессов Python с run_bot.py
echo "Процессы run_bot.py:"
ps aux | grep "[r]un_bot.py" || echo "Не найдено"

echo ""
echo "Процессы bot.py:"
ps aux | grep "[b]ot.py" || echo "Не найдено"

echo ""
echo "Процессы python с telegram:"
ps aux | grep "[p]ython.*telegram" || echo "Не найдено"

echo ""
echo "=== Systemd статус ==="
systemctl status telegram-bot.service 2>/dev/null || echo "Service не найден или не запущен"

echo ""
echo "=== PID файлы (если есть) ==="
find /opt/bot -name "*.pid" 2>/dev/null || echo "PID файлы не найдены"

