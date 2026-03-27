# 📋 Команды для просмотра логов бота

## 🔍 Основные команды

### 1. Если бот пишет логи в файл `bot.log`:

```bash
# Последние 50 строк
tail -n 50 bot.log

# Последние 100 строк
tail -n 100 bot.log

# Следить за логами в реальном времени (как journalctl -f)
tail -f bot.log

# С фильтром по голосовым сообщениям
tail -f bot.log | grep -i "распозна\|vosk\|голос\|voice"

# Поиск по ключевым словам
grep -i "распозна\|vosk\|голос" bot.log | tail -20

# Все ошибки
grep -i "error\|ошибка\|failed" bot.log | tail -20
```

### 2. Если бот запущен через systemd (journalctl):

```bash
# Последние 50 строк
sudo journalctl -u telegram-bot.service -n 50

# Последние 100 строк
sudo journalctl -u telegram-bot.service -n 100

# Следить в реальном времени (аналог tail -f)
sudo journalctl -u telegram-bot.service -f

# С фильтром
sudo journalctl -u telegram-bot.service -f | grep -i "распозна\|vosk"

# За сегодня
sudo journalctl -u telegram-bot.service --since today

# За последний час
sudo journalctl -u telegram-bot.service --since "1 hour ago"
```

### 3. Если бот запущен через screen:

```bash
# Список сессий
screen -list

# Подключиться к сессии (видишь логи в реальном времени)
screen -r bot

# Или если сессия называется по-другому
screen -r <имя_сессии>
```

### 4. Если бот запущен через tmux:

```bash
# Список сессий
tmux list-sessions

# Подключиться к сессии
tmux attach -t bot
```

### 5. Если бот запущен через nohup:

```bash
# Логи в файле nohup.out
tail -f nohup.out

# Или если указан другой файл
tail -f <имя_файла>.log
```

### 6. Если бот запущен напрямую (в терминале):

Логи видны прямо в терминале, где запущен бот.

## 🎯 Быстрые команды для диагностики голоса

```bash
# 1. Последние логи о голосовых сообщениях
tail -100 bot.log | grep -i "распозна\|vosk\|голос\|voice\|pcm\|wav"

# 2. Все ошибки распознавания
grep -i "не удалось\|failed\|error.*распозна" bot.log | tail -20

# 3. Частичные результаты Vosk
grep -i "частично\|partial" bot.log | tail -20

# 4. Финальные результаты Vosk
grep -i "финальный\|final.*result" bot.log | tail -20

# 5. Информация о модели
grep -i "модель.*загружена\|model.*loaded" bot.log | tail -10
```

## 📊 Полная диагностика

```bash
# Создай файл с полной диагностикой
{
    echo "=== Последние 100 строк ==="
    tail -100 bot.log
    echo ""
    echo "=== Логи о голосе ==="
    grep -i "распозна\|vosk\|голос" bot.log | tail -50
    echo ""
    echo "=== Ошибки ==="
    grep -i "error\|ошибка\|failed" bot.log | tail -30
} > voice_diagnostics.txt

# Просмотри файл
cat voice_diagnostics.txt
```

## 🔧 Если не знаешь, где логи

```bash
# Найди все .log файлы
find /opt/bot -name "*.log" 2>/dev/null

# Найди процессы бота
ps aux | grep run_bot.py

# Проверь, куда они пишут (stdout/stderr)
lsof -p <PID> | grep -E "txt|log"
```

## 💡 Рекомендация

**Самый простой способ** - если бот пишет в `bot.log`:

```bash
# Просто следи за логами
tail -f bot.log
```

Это аналог `journalctl -f`, но для файла логов.

