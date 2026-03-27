# Проверка .env файла

## Твой .env файл выглядит правильно! ✅

Формат корректный:
```
TELEGRAM_TOKEN=<YOUR_TELEGRAM_TOKEN>
CLAUDE_API_KEY=<YOUR_CLAUDE_API_KEY>
CLAUDE_PROXY=socks5://user:password@host:port
EXCHANGE_API_KEY=<YOUR_EXCHANGE_API_KEY>
GITHUB_API_KEY=<YOUR_GITHUB_TOKEN>
```

## Важные моменты:

### 1. SOCKS5 прокси требует httpx-socks

Ты используешь SOCKS5 прокси, поэтому на сервере должен быть установлен `httpx-socks`:

```bash
pip install httpx-socks
```

Или уже есть в `requirements.txt` (добавлен ранее).

### 2. Проверка на сервере

Выполни на VPS:

```bash
cd /opt/bot
source venv/bin/activate

# Проверить установлен ли httpx-socks
pip list | grep httpx-socks

# Если нет - установить
pip install httpx-socks

# Проверить, что .env файл читается
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('CLAUDE_PROXY:', os.getenv('CLAUDE_PROXY'))"
```

### 3. Расположение .env файла

`.env` файл должен быть в корне проекта (там же, где `config.py`):

```
/opt/bot/
  ├── .env          ← здесь
  ├── config.py
  ├── bot.py
  └── ...
```

### 4. Безопасность

⚠️ **Важно**: `.env` файл содержит секретные ключи!

- НЕ коммить `.env` в Git (должен быть в `.gitignore`)
- Используй права доступа: `chmod 600 .env`
- Регулярно меняй ключи при утечке

### 5. Альтернатива: HTTP прокси

Если SOCKS5 не работает, попробуй HTTP прокси:

```env
CLAUDE_PROXY=http://user:password@host:port
```

HTTP прокси не требует `httpx-socks`, только `httpx`.

## Проверка работы

После настройки проверь:

```bash
# Перезапустить бота
sudo systemctl restart telegram-bot.service

# Проверить логи
sudo journalctl -u telegram-bot.service -f

# Должно быть:
# [INFO] Claude клиент создан с прокси: 104.166.124.19:59209
```

## Итог

Твой `.env` файл **правильный**! ✅

Просто убедись, что:
1. ✅ Файл находится в `/opt/bot/.env`
2. ✅ Установлен `httpx-socks` для SOCKS5
3. ✅ Права на файл: `chmod 600 .env`

