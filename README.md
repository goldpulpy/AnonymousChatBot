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
- 🔍 Режимы поиска собеседника (M/Ж/+18)
- 👨‍💼 Панель администратора
- 👮‍♀️ Модерация
- 📨 Рассылка сообщений
- 🤝 Реферальная система
- 🏠 Создания анонимного групповых комнат
- 👥 Возможность добавлять собеседников в друзья
- 📊 Настройка рекламы
- 🐳 Легкое развертывание через **Docker**
- 🛡️ Безопасное хранение данных в **PostgreSQL**

## ⚠️ Известные проблемы (Known Issues)

- 💳 Интеграция с платежной системой PAYOK.IO в настоящее время не работает (PAYOK недоступен)
- 🔄 Требуется миграция на альтернативную платежную систему

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
    DB_HOST=db # Взято из docker-compose.yml
    DB_PORT=5432 # Взято из docker-compose.yml
    DB_NAME=YOUR_DB_NAME # Название БД, Например anonchat
    DB_USER=YOUR_DB_USER # Пользователь, Например root
    DB_PASSWORD=YOUR_DB_PASSWORD # Пароль, Например toor

    # Настройки Redis (Если не используете Redis, то оставьте как есть)
    REDIS_HOST=redis
    REDIS_DB=13

    # Настройки Payments (PAYOK.IO)
    PAYMENTS_API_ID=YOUR_API_ID # Ваш API ID
    PAYMENTS_API_KEY=YOUR_API_KEY # Ваш API KEY
    PAYMENTS_PROJECT_ID=YOUR_PROJECT_ID # Ваш Project ID
    PAYMENTS_PROJECT_SECRET=YOUR_PROJECT_SECRET # Ваш Project Secret
    PAYMENTS_ENABLED=False # Установите в True на production
   ```

`PAYMENTS_ENABLED=False` - Тестовый режим (имитация оплаты)

### Настройка цен

Откройте файл `prices.py` и измените цены на свои

### 🎮 Использование (Usage)

**Запустите бот:**

```bash
docker compose up -d
```

**Остановите бот:**

```bash
docker compose down
```
