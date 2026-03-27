#!/bin/bash
# Простой скрипт для просмотра логов

LOG_FILE="/opt/bot/bot.log"

echo "🔍 Проверка логов..."
echo ""

# Проверяем файл
if [ -f "$LOG_FILE" ]; then
    echo "✅ Файл найден: $LOG_FILE"
    echo "📊 Размер: $(du -h "$LOG_FILE" | cut -f1)"
    echo ""
    echo "=== Последние 50 строк ==="
    tail -50 "$LOG_FILE"
    echo ""
    echo "💡 Для просмотра в реальном времени:"
    echo "   tail -f $LOG_FILE"
else
    echo "❌ Файл $LOG_FILE не найден"
    echo ""
    echo "Пробую через journalctl..."
    echo ""
    sudo journalctl -u telegram-bot.service -n 50 --no-pager
    echo ""
    echo "💡 Для просмотра в реальном времени:"
    echo "   sudo journalctl -u telegram-bot.service -f"
fi

