#!/bin/bash
# Скрипт для поиска логов бота

echo "🔍 Поиск логов бота..."
echo ""

# Вариант 1: Проверяем стандартные места
echo "1. Проверка стандартных мест:"
for path in "/opt/bot/bot.log" "/opt/bot/logs/bot.log" "bot.log" "./bot.log" "nohup.out"; do
    if [ -f "$path" ]; then
        echo "   ✅ Найден: $path"
        echo "   Размер: $(du -h "$path" | cut -f1)"
        echo "   Последние 5 строк:"
        tail -5 "$path"
        echo ""
    fi
done

# Вариант 2: Ищем все .log файлы
echo "2. Поиск всех .log файлов в /opt/bot:"
find /opt/bot -name "*.log" -type f 2>/dev/null | head -10

# Вариант 3: Проверяем процессы бота
echo ""
echo "3. Проверка процессов бота:"
BOT_PID=$(ps aux | grep "[r]un_bot.py" | awk '{print $2}' | head -1)
if [ ! -z "$BOT_PID" ]; then
    echo "   Найден процесс с PID: $BOT_PID"
    echo "   Проверяю, куда он пишет логи..."
    
    # Проверяем открытые файлы процесса
    if command -v lsof >/dev/null 2>&1; then
        lsof -p $BOT_PID 2>/dev/null | grep -E "\.log|txt" | head -5
    fi
else
    echo "   ❌ Процесс бота не найден"
fi

# Вариант 4: Проверяем systemd
echo ""
echo "4. Проверка systemd:"
if systemctl is-active --quiet telegram-bot.service 2>/dev/null; then
    echo "   ✅ Service активен"
    echo "   Логи через journalctl:"
    echo "   sudo journalctl -u telegram-bot.service -n 10"
else
    echo "   ⚠️  Service не активен или не найден"
fi

# Вариант 5: Проверяем текущую директорию
echo ""
echo "5. Файлы в текущей директории:"
ls -la *.log 2>/dev/null || echo "   Нет .log файлов"

echo ""
echo "💡 Если логов нет, бот может писать в stdout/stderr"
echo "💡 Запусти бота с перенаправлением:"
echo "   python run_bot.py > bot.log 2>&1 &"

