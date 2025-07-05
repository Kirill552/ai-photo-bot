# Быстрый старт - AI Фотосессии

Пошаговая инструкция по запуску сервиса AI фотосессий.

## 📋 Предварительные требования

### 1. Сервисы
- **OpenAI API** - для работы Assistant
- **PiAPI** - для генерации изображений
- **Telegram Bot** - для интерфейса пользователя
- **Yandex Cloud** - для хранения файлов
- **VPS сервер** - для хостинга (Webdock, DigitalOcean, и др.)

### 2. Получение ключей

#### OpenAI API
1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Создайте аккаунт и получите API ключ
3. Пополните баланс (минимум $5)

#### PiAPI
1. Перейдите на [piapi.ai](https://piapi.ai)
2. Зарегистрируйтесь и получите API ключ
3. Пополните баланс для генерации изображений

#### Telegram Bot
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Создайте нового бота командой `/newbot`
3. Сохраните токен бота

#### Yandex Cloud
1. Зарегистрируйтесь в [Yandex Cloud](https://cloud.yandex.ru)
2. Создайте сервисный аккаунт
3. Создайте статический ключ доступа
4. Создайте S3 bucket для хранения изображений

## 🚀 Установка и настройка

### 1. Клонирование проекта

```bash
git clone <repository-url>
cd нейрофотограф
```

### 2. Настройка переменных окружения

Создайте файл `.env` с настройками:

```bash
# OpenAI API
OPENAI_KEY=sk-your-openai-key-here
ASSISTANT_ID=  # Будет заполнено автоматически

# PiAPI
PIAPI_KEY=your-piapi-key-here

# Telegram Bot
BOT_TOKEN=your-telegram-bot-token-here

# Yandex Cloud
YC_ACCESS_KEY=your-access-key
YC_SECRET_KEY=your-secret-key
YC_OBJECT_BUCKET=your-bucket-name
YC_REGION=ru-central1
YC_ENDPOINT=https://storage.yandexcloud.net

# Redis
REDIS_URL=redis://redis:6379/0

# App settings
DEBUG=True
LOG_LEVEL=INFO
RATE_LIMIT_RPS=15

# Prices (in rubles)
PRICE_40_PHOTOS=1099
PRICE_100_PHOTOS=1799
MARKETING_DISCOUNT=0.1
```

### 3. Локальная разработка

```bash
# Установите Python зависимости
pip install -r requirements.txt

# Создайте OpenAI Assistant
python assistant_setup.py

# Запустите сервисы через Docker
docker-compose up -d
```

### 4. Деплой на VPS

#### Настройка VPS
```bash
# Подключитесь к VPS
ssh root@your-vps-ip

# Установите Docker
curl -sSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Создайте директорию проекта
mkdir -p /opt/ai-studio
cd /opt/ai-studio
```

#### Загрузка проекта
```bash
# На локальной машине
# Отредактируйте deploy.sh - укажите IP вашего VPS
nano deploy.sh

# Запустите деплой
chmod +x deploy.sh
./deploy.sh
```

#### Настройка на VPS
```bash
# На VPS создайте .env файл
cd /opt/ai-studio
nano .env
# Скопируйте настройки из локального .env

# Создайте OpenAI Assistant
python assistant_setup.py

# Запустите сервисы
docker-compose up -d

# Проверьте статус
docker-compose ps
docker-compose logs -f
```

### 5. Настройка домена (опционально)

```bash
# Настройте DNS записи
# A-запись: api.photobot.ai -> IP вашего VPS
# A-запись: photobot.ai -> IP вашего VPS

# SSL сертификаты будут выданы автоматически через Caddy
```

## 🧪 Тестирование

### 1. Проверка компонентов

```bash
# Проверьте доступность сервисов
curl http://your-vps-ip/health
curl https://api.photobot.ai/health

# Проверьте OpenAI прокси
curl https://api.photobot.ai/v1/models

# Проверьте логи
docker-compose logs telegram-bot
docker-compose logs image-worker
docker-compose logs openai-proxy
```

### 2. Тестирование бота

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Проследуйте инструкциям бота
4. Загрузите тестовые фотографии
5. Ответьте на вопросы ассистента
6. Дождитесь генерации фотографий

## 📊 Мониторинг

### Логи сервисов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f telegram-bot
docker-compose logs -f image-worker
docker-compose logs -f openai-proxy
```

### Метрики Redis
```bash
# Подключитесь к Redis
docker-compose exec redis redis-cli

# Проверьте очереди
KEYS *
LLEN image_generation
```

### Статус задач Celery
```bash
# Статус worker
docker-compose exec image-worker celery -A worker.celery_app inspect active

# Статистика
docker-compose exec image-worker celery -A worker.celery_app inspect stats
```

## 🔧 Настройка под нагрузку

### Масштабирование workers
```yaml
# В docker-compose.yml
image-worker:
  # ...
  deploy:
    replicas: 4  # Увеличьте количество workers
```

### Оптимизация Redis
```bash
# Настройте Redis для производства
# Отредактируйте redis.conf
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 🛠️ Устранение неполадок

### Частые проблемы

1. **Бот не отвечает**
   - Проверьте токен бота в `.env`
   - Проверьте логи: `docker-compose logs telegram-bot`

2. **Ошибки генерации изображений**
   - Проверьте ключ PiAPI
   - Проверьте баланс PiAPI
   - Проверьте логи: `docker-compose logs image-worker`

3. **Ошибки OpenAI Assistant**
   - Проверьте ключ OpenAI
   - Проверьте ASSISTANT_ID
   - Запустите: `python assistant_setup.py`

4. **Ошибки загрузки в хранилище**
   - Проверьте ключи Yandex Cloud
   - Проверьте права доступа к bucket
   - Проверьте логи: `docker-compose logs image-worker`

### Команды диагностики
```bash
# Проверка связности
docker-compose exec telegram-bot ping redis
docker-compose exec image-worker ping redis

# Проверка дискового пространства
df -h

# Проверка памяти
free -h

# Перезапуск сервисов
docker-compose restart
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи всех сервисов
2. Убедитесь, что все ключи API действительны
3. Проверьте настройки `.env`
4. Перезапустите сервисы: `docker-compose restart`

## 🎯 Следующие шаги

После успешного запуска:

1. Протестируйте полный цикл работы
2. Настройте мониторинг и алерты
3. Настройте автоматические бэкапы
4. Создайте landing page для привлечения клиентов
5. Настройте аналитику использования 