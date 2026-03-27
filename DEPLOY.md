# Инструкция по деплою на VPS

## Что нужно загрузить на сервер

### 1. Все файлы проекта
Залить всю папку проекта на VPS (через SCP, SFTP или Git).

### 2. Важные файлы (уже настроены):
- ✅ `config.py` - прокси уже настроен
- ✅ `requirements.txt` - httpx уже добавлен
- ✅ `claude_helper.py` - поддержка прокси уже есть

## Шаги деплоя на VPS

### 1. Подключиться к серверу
```bash
ssh user@your-vps-ip
```

### 2. Установить зависимости системы
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

### 3. Создать директорию для бота
```bash
sudo mkdir -p /opt/bot
sudo chown $USER:$USER /opt/bot
cd /opt/bot
```

### 4. Загрузить файлы проекта
**Вариант А: Через Git (рекомендуется)**
```bash
git clone <your-repo-url> .
# или
# Загрузить файлы через SCP/SFTP в /opt/bot
```

**Вариант Б: Через SCP с локальной машины**
```bash
# На локальной машине (Windows PowerShell):
scp -r "C:\Users\USER\Documents\bot it\*" user@vps-ip:/opt/bot/
```

### 5. Создать виртуальное окружение и установить зависимости
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Проверить настройки прокси
Проверить, что в `config.py` прокси настроен:
```python
CLAUDE_PROXY = os.getenv("CLAUDE_PROXY", "http://user:password@host:port")
```

### 7. Настроить systemd service
```bash
# Скопировать service файл
sudo cp telegram-bot.service /etc/systemd/system/

# Отредактировать пути (если нужно)
sudo nano /etc/systemd/system/telegram-bot.service

# Обновить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable telegram-bot.service

# Запустить бота
sudo systemctl start telegram-bot.service

# Проверить статус
sudo systemctl status telegram-bot.service
```

### 8. Просмотр логов
```bash
# Логи в реальном времени
sudo journalctl -u telegram-bot.service -f

# Последние 100 строк
sudo journalctl -u telegram-bot.service -n 100
```

## Проверка работы прокси

После запуска проверьте логи:
```bash
sudo journalctl -u telegram-bot.service -f
```

Должны увидеть, что прокси подключен. Если есть ошибки - проверьте:
1. Установлен ли `httpx`: `pip list | grep httpx`
2. Правильно ли указан прокси в `config.py`
3. Доступен ли прокси с VPS (может быть блокировка)

## Управление ботом

```bash
# Остановить
sudo systemctl stop telegram-bot.service

# Запустить
sudo systemctl start telegram-bot.service

# Перезапустить
sudo systemctl restart telegram-bot.service

# Статус
sudo systemctl status telegram-bot.service
```

## Важные замечания

1. **Прокси уже настроен** в `config.py` - менять ничего не нужно
2. **httpx** уже добавлен в `requirements.txt` - установится автоматически
3. Если нужно использовать SOCKS5 вместо HTTP, измените в `config.py`:
   ```python
   CLAUDE_PROXY = "socks5://user:password@host:port"
   ```
   И установите: `pip install httpx-socks`

## Альтернативный запуск (без systemd)

Если не используете systemd:
```bash
cd /opt/bot
source venv/bin/activate
python run_bot.py
```

Или через screen/tmux для фонового запуска:
```bash
screen -S bot
cd /opt/bot
source venv/bin/activate
python run_bot.py
# Ctrl+A, затем D для отсоединения
```

