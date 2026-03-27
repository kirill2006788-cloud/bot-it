#!/bin/bash
# Скрипт для проверки логов бота

echo "🔍 Проверка логов бота..."
echo ""

# Вариант 1: Если бот запущен через systemd
if systemctl is-active --quiet telegram-bot.service 2>/dev/null; then
    echo "✅ Бот запущен через systemd"
    echo "📋 Логи:"
    journalctl -u telegram-bot.service -n 50 --no-pager
    echo ""
    echo "📊 Следить за логами в реальном времени:"
    echo "   journalctl -u telegram-bot.service -f"
    exit 0
fi

# Вариант 2: Если бот запущен через screen
if screen -list | grep -q "bot"; then
    echo "✅ Найдена screen сессия с ботом"
    echo "📋 Для просмотра логов:"
    echo "   screen -r bot"
    exit 0
fi

# Вариант 3: Если бот запущен через tmux
if tmux list-sessions 2>/dev/null | grep -q "bot"; then
    echo "✅ Найдена tmux сессия с ботом"
    echo "📋 Для просмотра логов:"
    echo "   tmux attach -t bot"
    exit 0
fi

# Вариант 4: Проверяем процесс Python
BOT_PID=$(ps aux | grep "[r]un_bot.py" | awk '{print $2}')
if [ ! -z "$BOT_PID" ]; then
    echo "✅ Найден процесс бота (PID: $BOT_PID)"
    echo "📋 Логи процесса:"
    echo ""
    # Пробуем найти файл логов
    if [ -f "/opt/bot/bot.log" ]; then
        echo "📄 Файл логов: /opt/bot/bot.log"
        tail -n 50 /opt/bot/bot.log
    elif [ -f "bot.log" ]; then
        echo "📄 Файл логов: bot.log"
        tail -n 50 bot.log
    elif [ -f "nohup.out" ]; then
        echo "📄 Файл логов: nohup.out"
        tail -n 50 nohup.out
    else
        echo "⚠️ Файл логов не найден"
        echo "💡 Бот может писать логи в stdout/stderr"
        echo "💡 Проверь, как запущен бот:"
        echo "   ps aux | grep run_bot"
    fi
    exit 0
fi

# Вариант 5: Проверяем PID файл
if [ -f "/opt/bot/bot.pid" ]; then
    PID=$(cat /opt/bot/bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Найден процесс по PID файлу (PID: $PID)"
        echo "📋 Проверяю логи..."
    fi
fi

echo "❌ Бот не найден или не запущен"
echo ""
echo "💡 Попробуй:"
echo "   1. ps aux | grep run_bot"
echo "   2. ps aux | grep python"
echo "   3. screen -list"
echo "   4. tmux list-sessions"

