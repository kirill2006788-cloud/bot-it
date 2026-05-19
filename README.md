# 🤖 bot-it

<p align="center">
  <b>Telegram Bot • Python • Automation</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/CI/CD-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="CI/CD">
</p>

---

> Production-ready Telegram bot with modern architecture.

---

## ✨ Features

- 🔗 **Telegram Bot API** integration using python-telegram-bot v20+
- 🎯 **Command handler** system
- 💬 **Inline keyboards** and callbacks
- 📊 **User management** and state tracking
- 🔄 **Async architecture** for high performance
- 🛡️ **Error handling** and logging
- ✅ **Type hints** throughout the codebase

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **Framework** | python-telegram-bot 20+ |
| **Bot API** | Telegram Bot API |
| **CI/CD** | GitHub Actions |
| **Testing** | pytest + coverage |
| **Linting** | flake8 + black |

---

## 📂 Project Structure

```
bot-it/
├── bot/                   # Main bot application
│   ├── handlers/         # Command handlers
│   ├── keyboards/        # Inline keyboards
│   ├── states/           # User states
│   └── utils/            # Utilities
│
├── tests/                 # Unit tests
├── .github/workflows/    # CI/CD
├── requirements.txt      # Dependencies
├── pyproject.toml       # Project config
└── README.md
```

---

## 🚀 Getting Started

```bash
# Clone repository
git clone https://github.com/kirill2006788-cloud/bot-it.git
cd bot-it

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your bot token

# Run bot
python -m bot.main
```

---

## 🔧 Configuration

Create `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Lint
flake8 .
black .
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p>Built with ❤️ by <a href="https://github.com/kirill2006788-cloud">Kirill</a></p>
  <p>🤖 bot-it</p>
</div>
