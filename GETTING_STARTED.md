# 🚀 Руководство по запуску AI Photo Bot v2025

> **Новая архитектура v2025**: Используем Yandex Message Queue + Yandex Object Storage + PiAPI. 
> Больше никаких Redis, Celery или OpenAI Proxy!

## 📋 Системные требования

- **Docker & Docker Compose** 
- **VPS/сервер** с минимум 2GB RAM
- **Домен** (опционально)

## 🔑 Необходимые API ключи

### 1. Telegram Bot Token
```bash
# Создайте бота через @BotFather
/newbot
# Получите токен: 1234567890:ABCDefGhIjKlMnOpQrStUvWxYz
```

### 2. OpenAI API Key  
```bash
# Зайдите на https://platform.openai.com/api-keys
# Создайте новый ключ: sk-proj-...
```

### 3. PiAPI Key
```bash
# Зарегистрируйтесь на https://piapi.ai/
# Получите ключ в личном кабинете
```

### 4. Yandex Cloud
```bash
# Создайте Object Storage bucket
# Создайте Message Queue
# Создайте Service Account с ключами доступа
```

## ⚙️ Настройка переменных окружения

Создайте файл `.env` на сервере:

```bash
# Telegram Bot
BOT_TOKEN=1234567890:ABCDefGhIjKlMnOpQrStUvWxYz

# OpenAI
OPENAI_API_KEY=sk-proj-...
ASSISTANT_ID=asst_...

# PiAPI
PIAPI_KEY=your-piapi-key
PIAPI_BASE_URL=https://api.piapi.ai

# Yandex Message Queue
YC_MQ_URL=https://message-queue.api.cloud.yandex.net/...
YC_MQ_QUEUE_NAME=ai-photo-jobs

# Yandex Object Storage  
YC_ACCESS_KEY=your-access-key
YC_SECRET_KEY=your-secret-key
YC_BUCKET_NAME=ai-photos
YC_REGION=ru-central1
YC_ENDPOINT=https://storage.yandexcloud.net

# Webhook (для Telegram)
DOMAIN=your-domain.com  # или IP
WEBHOOK_SECRET=your-generated-secret
SECRET_KEY=your-app-secret

# Worker settings
WORKER_CONCURRENCY=4
DEBUG=false
LOG_LEVEL=INFO
```

## 🎯 Быстрый старт

### 1. Создание OpenAI Assistant
```bash
# Настройте OPENAI_API_KEY в .env
python assistant_setup.py
# Скопируйте ASSISTANT_ID в .env
```

### 2. Запуск через GitHub Actions (рекомендуется)

1. **Fork репозитория**
2. **Настройте Secrets** в GitHub Settings → Secrets and variables → Actions:
   ```
   BOT_TOKEN
   OPENAI_API_KEY  
   ASSISTANT_ID
   PIAPI_KEY
   YC_MQ_URL
   YC_ACCESS_KEY
   YC_SECRET_KEY
   YC_BUCKET_NAME
   DOMAIN
   WEBHOOK_SECRET
   SECRET_KEY
   ```

3. **Пуш в main** - автоматический деплой на сервер!

### 3. Ручной запуск на VPS

```bash
# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/ai-photo-bot.git
cd ai-photo-bot

# Создайте .env файл (см. выше)
nano .env

# Запустите сервисы
docker compose up -d

# Проверьте статус
docker compose ps
```

## 🏗️ Архитектура v2025

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Telegram    │    │ Yandex Message   │    │ Image Worker    │
│ Bot         │───▶│ Queue            │───▶│ (Processing)    │
│ (webhook)   │    │ (managed)        │    │                 │
└─────────────┘    └──────────────────┘    └─────────────────┘
                                                      │
                   ┌──────────────────┐              │
                   │ Yandex Object    │◀─────────────┘
                   │ Storage          │
                   │ (images)         │
                   └──────────────────┘
```

**Компоненты:**
- **telegram-bot**: Обрабатывает пользователей через webhook
- **image-worker**: Обрабатывает задачи из очереди YC Message Queue
- **Yandex Message Queue**: Управляемая очередь сообщений
- **Yandex Object Storage**: Хранение изображений

## 🧪 Тестирование

### 1. Проверка сервисов
```bash
# Статус контейнеров
docker compose ps

# Логи бота
docker compose logs -f telegram-bot

# Логи worker
docker compose logs -f image-worker

# Здоровье worker
docker compose exec image-worker python -c "from worker.health import check_health; print(check_health())"
```

### 2. Тестирование бота
1. Найдите бота в Telegram
2. Отправьте `/start`  
3. Выберите пакет фотосессии
4. Загрузите 10-15 селфи
5. Опишите желаемый стиль
6. Дождитесь генерации

## 📊 Мониторинг

### Логи v2025
```bash
# Все логи
docker compose logs -f

# Последние 50 строк
docker compose logs --tail=50

# Логи с временными метками
docker compose logs -f -t
```

### Проверка очереди
```bash
# Статистика YC Message Queue через консоль Yandex Cloud
# https://console.cloud.yandex.ru/folders/your-folder-id/message-queue
```

### Проверка хранилища
```bash
# Статистика Object Storage через консоль Yandex Cloud  
# https://console.cloud.yandex.ru/folders/your-folder-id/storage
```

## 🔧 Настройка производительности

### Worker масштабирование
```yaml
# docker-compose.yml
image-worker:
  environment:
    - WORKER_CONCURRENCY=8  # Увеличьте количество потоков
  deploy:
    replicas: 2  # Запустите несколько экземпляров
```

### Webhook оптимизация
```bash
# Используйте домен вместо IP для стабильной работы webhook
DOMAIN=your-bot-domain.com
```

## 🛠️ Устранение неполадок

### Частые проблемы

**1. Бот не отвечает**
```bash
# Проверьте токен и webhook
docker compose logs telegram-bot | grep -i error
```

**2. Worker падает**
```bash
# Проверьте API ключи
docker compose logs image-worker | grep -i "validation\|error"
```

**3. Нет генерации изображений**
```bash
# Проверьте PiAPI баланс и ключ
# Проверьте YC Message Queue конфигурацию
```

**4. Ошибки загрузки**
```bash
# Проверьте YC Object Storage права доступа
# Проверьте что bucket создан и публично доступен для чтения
```

### Команды диагностики
```bash
# Health check
docker compose exec image-worker python -c "
from worker.health import check_health
result = check_health()
print('✅ Healthy' if result.get('healthy') else f'❌ Error: {result.get(\"error\")}')
"

# Проверка конфигурации
docker compose exec telegram-bot python -c "
from bot.config import settings
print(f'Bot token: {settings.BOT_TOKEN[:10]}...')
print(f'YC MQ URL: {settings.YC_MQ_URL[:30]}...')
"

# Проверка дискового пространства
df -h

# Использование памяти
docker stats --no-stream
```

## 🎉 Готово!

После запуска ваш AI Photo Bot v2025 готов к работе:

- ✅ **Современная архитектура** без Redis/Celery
- ✅ **Managed сервисы** Yandex Cloud  
- ✅ **Автоматическое масштабирование** через Message Queue
- ✅ **Простота поддержки** - только 2 контейнера

**Полезные ссылки:**
- Yandex Cloud Console: https://console.cloud.yandex.ru
- PiAPI Dashboard: https://piapi.ai/dashboard  
- OpenAI Platform: https://platform.openai.com 