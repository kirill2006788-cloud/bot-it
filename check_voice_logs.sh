#!/bin/bash
# Скрипт для проверки логов распознавания голоса

echo "🔍 Проверка логов распознавания голоса..."
echo ""

# Находим файл логов
LOG_FILE=""
if [ -f "/opt/bot/bot.log" ]; then
    LOG_FILE="/opt/bot/bot.log"
elif [ -f "bot.log" ]; then
    LOG_FILE="bot.log"
elif [ -f "nohup.out" ]; then
    LOG_FILE="nohup.out"
else
    echo "❌ Файл логов не найден"
    echo "💡 Попробуй найти логи:"
    echo "   find /opt/bot -name '*.log' 2>/dev/null"
    exit 1
fi

echo "📄 Файл логов: $LOG_FILE"
echo ""

# Последние 100 строк с упоминанием голоса/Vosk
echo "=== Последние записи о голосовых сообщениях ==="
grep -i "голос\|voice\|vosk\|распозна\|pcm\|wav" "$LOG_FILE" | tail -50

echo ""
echo "=== Последние ошибки ==="
grep -i "error\|ошибка\|failed\|не удалось" "$LOG_FILE" | tail -20

echo ""
echo "=== Статус Vosk модели ==="
grep -i "vosk.*модель\|модель.*загружена\|model.*loaded" "$LOG_FILE" | tail -10

echo ""
echo "=== Последние 30 строк логов ==="
tail -30 "$LOG_FILE"

echo ""
echo "💡 Для просмотра в реальном времени:"
echo "   tail -f $LOG_FILE | grep -i 'голос\|vosk\|распозна'"

