#!/bin/bash
# Скрипт для проверки настройки ffmpeg

echo "🔍 Проверка настройки ffmpeg..."
echo ""

# Проверяем наличие ffmpeg
echo "1. Проверка ffmpeg:"
if command -v ffmpeg &> /dev/null; then
    echo "   ✅ ffmpeg найден: $(which ffmpeg)"
    ffmpeg -version | head -1
else
    echo "   ❌ ffmpeg не найден в PATH"
    if [ -f "/usr/bin/ffmpeg" ]; then
        echo "   ✅ Но найден в /usr/bin/ffmpeg"
    fi
fi

echo ""
echo "2. Проверка ffprobe:"
if command -v ffprobe &> /dev/null; then
    echo "   ✅ ffprobe найден: $(which ffprobe)"
    ffprobe -version | head -1
else
    echo "   ❌ ffprobe не найден в PATH"
    if [ -f "/usr/bin/ffprobe" ]; then
        echo "   ✅ Но найден в /usr/bin/ffprobe"
    fi
fi

echo ""
echo "3. Проверка файлов:"
if [ -f "/usr/bin/ffmpeg" ]; then
    echo "   ✅ /usr/bin/ffmpeg существует"
    ls -la /usr/bin/ffmpeg
else
    echo "   ❌ /usr/bin/ffmpeg не существует"
fi

if [ -f "/usr/bin/ffprobe" ]; then
    echo "   ✅ /usr/bin/ffprobe существует"
    ls -la /usr/bin/ffprobe
else
    echo "   ❌ /usr/bin/ffprobe не существует"
fi

echo ""
echo "4. Проверка логов бота (последние строки о ffmpeg):"
sudo journalctl -u telegram-bot.service -n 50 --no-pager | grep -i "ffmpeg\|ffprobe\|найден\|установлен" | tail -10

echo ""
echo "💡 Если в логах нет строк 'Найден ffmpeg' или 'Установлен converter',"
echo "   значит обновленный voice_helper.py еще не загружен или бот не перезапущен"

