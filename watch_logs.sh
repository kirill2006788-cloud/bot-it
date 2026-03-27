#!/bin/bash
# Простой скрипт для просмотра логов - всегда работает

echo "🔍 Просмотр логов бота..."
echo ""

# Вариант 1: Через journalctl (всегда работает для systemd)
if systemctl is-active --quiet telegram-bot.service 2>/dev/null; then
    echo "✅ Бот запущен через systemd"
    echo "📊 Используй journalctl:"
    echo ""
    echo "   sudo journalctl -u telegram-bot.service -f"
    echo ""
    echo "Или последние 100 строк:"
    echo "   sudo journalctl -u telegram-bot.service -n 100"
    echo ""
    echo "С фильтром по голосовым сообщениям:"
    echo "   sudo journalctl -u telegram-bot.service -f | grep -i 'распозна\|vosk\|голос'"
    exit 0
fi

# Вариант 2: Проверяем файл
if [ -f "/opt/bot/bot.log" ]; then
    echo "✅ Файл найден: /opt/bot/bot.log"
    tail -f /opt/bot/bot.log
    exit 0
fi

# Вариант 3: Создаем файл и смотрим через journalctl
echo "⚠️  Файл логов не найден"
echo ""
echo "💡 Используй journalctl (всегда работает):"
echo ""
echo "   sudo journalctl -u telegram-bot.service -f"
echo ""
