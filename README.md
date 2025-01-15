<div align="center">
  <h1>💬 Бот для анонимного общения</h1>
  <p>Анонимный чат в Telegram</p>

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-compose-blue?logo=docker)
![Telegram](https://img.shields.io/badge/Telegram-bot-blue?logo=telegram)

</div>

## ✨ Возможности (Features)

- 💬 Анонимный чат
- 📱 Удобный интерфейс
- 👨‍💼 Панель администратора
- 📨 Рассылка сообщений
- 🤝 Реферальная система
- 🏠 Создания анонимного групповых комнат
- 📊 Настройка рекламы
- 💳 Платежная система (PAYOK)
- 🐳 Легкое развертывание через **Docker**
- 🛡️ Безопасное хранение данных в **PostgreSQL**

## 🚀 Быстрый старт (Quickstart)

### Предварительные условия (Requirements)

- Docker и Docker Compose должны быть установлены
- Токен бота ([BotFather](https://t.me/botfather))

### Установка (Installation)

1. Клонируйте репозиторий

   ```bash
   git clone https://github.com/goldpulpy/AnonymousChatBot.git
   cd AnonymousChatBot
   ```

2. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```
3. Настройте переменные окружения:

   ```bash
    # Настройки бота (Telegram)
    BOT_TOKEN=YOUR_BOT_TOKEN # Токен бота из BotFather
    BOT_TIMEZONE=Europe/Moscow # Часовой пояс (Europe/Moscow)
    BOT_ADMINS=[00000000] # ID админов через запятую если несколько, Пример: [000,000]
    BOT_MODERS=[00000000] # ID Принимают жалобы через запятую
    BOT_USE_REDIS=False # Использовать Redis (По умолчанию False)

    # Настройки Базы данных (PostgreSQL)
    DB_HOST=db
    DB_PORT=5432
    DB_NAME=YOUR_DB_NAME # Название БД, Например anonchat
    DB_USER=YOUR_DB_USER # Пользователь, Например root
    DB_PASSWORD=YOUR_DB_PASSWORD # Пароль, Например toor

    # Настройки Redis (Если используете Redis)
    REDIS_HOST=redis
    REDIS_DB=13

    # Настройки Payments (PAYOK.IO)
    PAYMENTS_API_ID=YOUR_API_ID
    PAYMENTS_API_KEY=YOUR_API_KEY
    PAYMENTS_PROJECT_ID=YOUR_PROJECT_ID
    PAYMENTS_PROJECT_SECRET=YOUR_PROJECT_SECRET
    PAYMENTS_ENABLED=False # Установите в True на production
   ```

### 🎮 Использование (Usage)

**Запустите бот:**

```bash
docker compose up -d
```

**Остановите бот:**

```bash
docker compose down
```
