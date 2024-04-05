## Настройка
Для начало нужно переименовать `.env.example` > `.env`

```shell
cp .env.example .env
```
Заходим в `.env` и вставьте настройки

```bash
# Настройки бота
BOT__TOKEN = 'Тут ваш токен' # Токен бота
BOT__TIMEZONE = 'Europe/Moscow' # Часовой пояс
BOT__ADMINS = [00000000] # ID админов через запятую
BOT__MODERS = [00000000] # ID Принимают жалобы через запятую
BOT__USE_REDIS = False # Использовать Redis

# Настройки Базы данных postgres
DB__HOST = '127.0.0.1' # Хост от Postgres
DB__PORT = 5432 # Порт
DB__NAME = '' # Название БД
DB__USER = '' # Пользователь
DB__PASSWORD = '' # Пароль

# Настройки Redis
REDIS__HOST = 'redis'
REDIS__DB = 13

# Настройки Payments
PAYMENTS__API_ID =
PAYMENTS__API_KEY = ''
PAYMENTS__PROJECT_ID =
PAYMENTS__PROJECT_SECRET = ''
PAYMENTS__ENABLED = False

CONTAINER_NAME = 'anon'
VOLUMES_DIR = './volumes'
```

## Установка Postgres (если база данных не установлена)
Заходим в папку app/database/

Редактируем `docker-compose.yml`
```yml
POSTGRES_USER: your_user # Пользователь
POSTGRES_PASSWORD: your_password # Пароль
POSTGRES_DB: your_database # Название БД
```

Поднимаем базу данных
```shell
sudo docker-compose up -d
```


## psql.py
Управление базой данных postgres через `psql.py`
```bash
python psql.py <query>
```