#!/bin/bash
# Скрипт для тестирования распознавания голоса

echo "🎤 Тестирование распознавания голоса"
echo ""

# Проверяем наличие Vosk модели
echo "1. Проверка Vosk модели..."
MODEL_DIRS=(
    "/opt/bot/vosk_models/vosk-model-small-ru-0.22"
    "/opt/bot/vosk_models/vosk-model-ru-0.42"
    "/opt/bot/vosk_models/vosk-model-small-ru-0.4"
    "vosk_models/vosk-model-small-ru-0.22"
    "vosk_models/vosk-model-ru-0.42"
)

FOUND_MODEL=""
for dir in "${MODEL_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        if [ -f "$dir/am/final.mdl" ] || [ -d "$dir/am" ]; then
            echo "   ✅ Найдена модель: $dir"
            FOUND_MODEL="$dir"
            break
        fi
    fi
done

if [ -z "$FOUND_MODEL" ]; then
    echo "   ❌ Модель Vosk не найдена!"
    echo "   💡 Установи модель:"
    echo "      cd /opt/bot"
    echo "      python install_vosk_model.py"
    exit 1
fi

# Проверяем установленные пакеты
echo ""
echo "2. Проверка установленных пакетов..."
cd /opt/bot || cd .

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 -c "import vosk; print('   ✅ vosk установлен')" 2>/dev/null || echo "   ❌ vosk не установлен: pip install vosk"
python3 -c "import gtts; print('   ✅ gtts установлен')" 2>/dev/null || echo "   ❌ gtts не установлен: pip install gtts"
python3 -c "from pydub import AudioSegment; print('   ✅ pydub установлен')" 2>/dev/null || echo "   ❌ pydub не установлен: pip install pydub"

echo ""
echo "3. Проверка структуры модели..."
if [ -d "$FOUND_MODEL" ]; then
    echo "   Содержимое модели:"
    ls -la "$FOUND_MODEL" | head -10
    echo ""
    
    if [ -d "$FOUND_MODEL/am" ]; then
        echo "   ✅ Папка am/ найдена"
    else
        echo "   ❌ Папка am/ не найдена!"
    fi
    
    if [ -d "$FOUND_MODEL/graph" ]; then
        echo "   ✅ Папка graph/ найдена"
    else
        echo "   ⚠️  Папка graph/ не найдена"
    fi
fi

echo ""
echo "4. Проверка логов бота..."
LOG_FILE=""
if [ -f "/opt/bot/bot.log" ]; then
    LOG_FILE="/opt/bot/bot.log"
elif [ -f "bot.log" ]; then
    LOG_FILE="bot.log"
fi

if [ -n "$LOG_FILE" ]; then
    echo "   Последние записи о Vosk:"
    grep -i "vosk\|модель.*загружена" "$LOG_FILE" | tail -5
else
    echo "   ⚠️  Файл логов не найден"
fi

echo ""
echo "✅ Проверка завершена"
echo ""
echo "💡 Теперь отправь голосовое сообщение боту и проверь логи:"
echo "   tail -f $LOG_FILE | grep -i 'распозна\|vosk\|голос'"

