# Нейрофотосессии (AI Photo Session Bot) v2

🤖 Telegram-бот для создания профессиональных AI-портретов с использованием OpenAI Assistants и PiAPI

## 🎯 Обзор проекта

Сервис генерации женских фотосессий (AI-портреты) через Telegram-бота. Клиентки загружают свои селфи, проходят интервью с AI-ассистентом, и получают до 100 профессиональных портретов в различных стилях.

### Особенности
- 🎨 6 профессиональных стилей фотосессий
- 🤖 Интеллектуальное интервью на русском языке
- ⚡ Быстрая генерация через Flux/GPT-4o-image
- 📦 Умная доставка результатов (альбомы/архивы)
- 🔄 Автоматическая очистка файлов
- ☁️ Serverless архитектура (Yandex Cloud)

### Технологический стек v2
- **Backend**: Python, aiogram
- **AI**: OpenAI Assistants API, PiAPI (Flux/GPT-4o-image)
- **Storage**: Yandex Object Storage
- **Queue**: Yandex Message Queue (вместо Redis/Celery)
- **Infrastructure**: Docker, Yandex Serverless Containers

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose (для локальной разработки)
- API ключи: OpenAI, PiAPI, Telegram Bot, Yandex Cloud
- Yandex Cloud аккаунт с настроенными сервисами

### Установка

1. **Клонируйте репозиторий**
```bash
git clone <repo-url>
cd нейрофотограф
```

2. **Настройте переменные окружения**
```bash
cp config.example .env
# Отредактируйте .env с вашими API ключами
```

3. **Настройте OpenAI Assistant**
```bash
python assistant_setup.py
```

4. **Локальная разработка**
```bash
docker-compose up -d --build
```

5. **Деплой в Yandex Cloud**
```bash
# Создайте Message Queue и Object Storage
# Настройте Serverless Containers
# Подробности в GETTING_STARTED.md
```

## 📁 Структура проекта v2

```
нейрофотограф/
├── src/
│   ├── bot/           # Telegram Bot (aiogram)
│   │   ├── main.py, handlers.py, assistant.py
│   │   ├── config.py, utils.py, middleware.py
│   │   └── Dockerfile, requirements.txt
│   └── worker/        # Image Generation Worker
│       ├── tasks.py, image_generator.py, mq_client.py
│       ├── prompts.py, storage.py, config.py
│       └── Dockerfile, requirements.txt
├── .github/workflows/ # CI/CD
│   └── deploy.yml
├── docker-compose.yml # Упрощенная версия (2 сервиса)
├── assistant_setup.py
├── deploy.sh
├── README.md, GETTING_STARTED.md
└── config.example     # Environment variables template
```

## 🔧 Конфигурация v2

### Основные переменные (.env)
```env
# OpenAI
OPENAI_API_KEY=sk-...
ASSISTANT_ID=asst_...

# Telegram
BOT_TOKEN=...
WEBHOOK_URL=https://yourdomain.com/webhook

# PiAPI
PIAPI_KEY=...

# Yandex Cloud
YC_ACCESS_KEY=...
YC_SECRET_KEY=...
YC_BUCKET_NAME=ai-photos
YC_MQ_URL=https://message-queue.api.cloud.yandex.net/...
YC_MQ_QUEUE_NAME=jobs
```

### Стили фотосессий
- **Studio Vogue**: Глянцевые портреты в стиле модных журналов
- **Pastel Dream**: Нежные пастельные тона
- **CEO Shot**: Деловые портреты
- **Film 90s**: Винтажная пленочная эстетика
- **Golden Hour**: Портреты в золотой час
- **Black & White Classic**: Классические черно-белые портреты

## 🏗️ Архитектура v2 (Serverless)

```
User (Telegram) → aiogram Bot → OpenAI Assistants
     │                      │  └─(tool: collect_brief)
     │                      └─▶ Yandex Message Queue
     │                             │
     │                      Worker (Serverless) → PiAPI Flux/GPT-4o-image
     │                             │
     │                      images (YC Object Storage)
     ▼                             │
Telegram album ◀── Delivery Function ◀─┘
```

## 📊 Статус разработки v2

- ✅ Основная структура проекта
- ✅ Docker настройка упрощена
- ✅ Telegram бот
- ✅ OpenAI Assistant
- ✅ Интеграция PiAPI
- ✅ Yandex Message Queue клиент
- ✅ Хранилище файлов
- ⏳ Serverless Containers деплой
- ⏳ Тестирование

## 📈 Изменения в v2

### Убрано
- ❌ OpenAI Proxy (прямые вызовы API)
- ❌ Redis + Celery (заменено на YC Message Queue)
- ❌ Caddy веб-сервер
- ❌ Сложная инфраструктура

### Добавлено
- ✅ Yandex Message Queue интеграция
- ✅ Serverless-готовая архитектура
- ✅ Упрощенная конфигурация
- ✅ Более экономичный деплой

## 💰 Экономика

| Пакет | Цена | Себестоимость | Маржа |
|-------|------|---------------|-------|
| 40 фото | 1,099₽ | ~$0.08-0.80 | 92-99% |
| 100 фото | 1,799₽ | ~$0.20-2.00 | 80-98% |

*Себестоимость снижена благодаря serverless архитектуре*

## 📝 Лицензия

Частный проект. Все права защищены.

## 🔗 Контакты

- Telegram: @your_username
- Email: your.email@example.com