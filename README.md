# AI Photo Bot v2025 🤖📸

Telegram-бот для создания профессиональных AI-портретов с использованием OpenAI Assistants и PiAPI

## 🎯 Обзор проекта

Современный сервис генерации AI-фотосессий через Telegram. Пользователи загружают селфи, проходят интеллектуальное интервью с AI-ассистентом, и получают профессиональные портреты в различных стилях.

### Особенности v2025
- 🎨 **8 новых стилей** (RL-01 до CSP-08) с LoRA поддержкой
- 🎬 **Видео генерация** для пакетов Стандарт/Премиум
- ✨ **Автоматический пост-процесс** для премиум пакета
- 🌈 **Инклюзивность** - поддержка клиентов любого пола
- ⚡ **Yandex Message Queue** вместо Redis/Celery
- ☁️ **Serverless архитектура** (только 2 контейнера)

### Линейка пакетов 2025
- **🎁 Пробный** - 2 фото, бесплатно
- **📱 Базовый** - 10 фото, 1500₽ 
- **🎬 Стандарт** - 25 фото + 1 видео, 3500₽
- **✨ Премиум** - 50 фото + 2 видео + пост-процесс, 8990₽

### Технологический стек v2025
- **Backend**: Python, aiogram 3.2
- **AI**: OpenAI Assistants API, PiAPI (Flux + WanX)
- **Storage**: Yandex Object Storage
- **Queue**: Yandex Message Queue (managed)
- **ML**: Video generation + Post-processing pipeline
- **Infrastructure**: Docker, Yandex Cloud

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose
- API ключи: OpenAI, PiAPI, Telegram Bot, Yandex Cloud
- VPS или Yandex Serverless Containers

### Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/YOUR_USERNAME/ai-photo-bot.git
cd нейрофотограф
```

2. **Настройте переменные окружения**
```bash
# Создайте .env с ключами (см. GETTING_STARTED.md)
nano .env
```

3. **Создайте OpenAI Assistant**
```bash
python assistant_setup.py
```

4. **Запустите сервисы**
```bash
docker compose up -d --build
```

**📖 Подробная инструкция:** [GETTING_STARTED.md](GETTING_STARTED.md)

## 📁 Структура проекта v2025

```
нейрофотограф/
├── src/
│   ├── bot/                    # Telegram Bot (aiogram)
│   │   ├── main.py            # Основной модуль бота
│   │   ├── handlers.py        # Обработчики команд и колбэков
│   │   ├── assistant.py       # OpenAI Assistant интеграция
│   │   ├── config.py, utils.py, middleware.py
│   │   └── Dockerfile, requirements.txt
│   └── worker/                 # Image Generation Worker  
│       ├── main.py            # YC Message Queue worker
│       ├── tasks.py           # Задачи обработки
│       ├── image_generator.py # PiAPI Flux генерация
│       ├── video_generator.py # WanX видео генерация
│       ├── post_processor.py  # Пост-обработка премиум
│       ├── storage.py         # Yandex Object Storage
│       ├── mq_client.py       # Message Queue клиент
│       ├── prompts.py         # Стили и промпты
│       └── Dockerfile, requirements.txt
├── .github/workflows/          # GitHub Actions CI/CD
├── assistant_setup.py         # Настройка OpenAI Assistant
├── deploy.sh                  # Скрипт деплоя v2025
├── docker-compose.yml         # Только 2 сервиса!
└── GETTING_STARTED.md         # Обновленное руководство
```

## 🔧 Конфигурация v2025

### Основные переменные (.env)
```env
# Telegram Bot
BOT_TOKEN=1234567890:ABC...
DOMAIN=your-domain.com
WEBHOOK_SECRET=generated-secret

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
YC_ENDPOINT=https://storage.yandexcloud.net

# Worker настройки
WORKER_CONCURRENCY=4
```

### Новые стили v2025
- **RL-01**: Реалистичные портреты (LoRA: realism)
- **FN-02**: Fashion & Beauty портреты
- **CP-03**: Корпоративные фото
- **MJ6-04**: Художественные портреты (LoRA: mjv6)
- **CEO-05**: Деловые портреты
- **PST-06**: Пастельные тона
- **CLS-07**: Классические портреты
- **CSP-08**: Креативные портреты (LoRA: graphic-portrait)

## 🏗️ Архитектура v2025

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Telegram    │    │ Yandex Message   │    │ Image Worker    │
│ Bot         │───▶│ Queue            │───▶│ (Processing)    │
│ (webhook)   │    │ (managed)        │    │                 │
└─────────────┘    └──────────────────┘    └─────────────────┘
       │                                           │
       │            ┌──────────────────┐          │
       └───────────▶│ OpenAI          │          │
                    │ Assistant        │          │
                    │ (collect_brief)  │          │
                    └──────────────────┘          │
                                                  │
                    ┌──────────────────┐          │
                    │ Yandex Object    │◀─────────┘
                    │ Storage          │
                    │ (images/videos)  │
                    └──────────────────┘
```

**Компоненты:**
- **telegram-bot**: Webhook обработка, интервью с Assistant
- **image-worker**: Генерация изображений/видео через YC Message Queue
- **OpenAI Assistant**: Сбор технического задания
- **PiAPI**: Flux модели + WanX видео генерация
- **YC Message Queue**: Управляемая очередь (заменяет Redis/Celery)
- **YC Object Storage**: Хранение результатов

## 📊 Статус разработки v2025

### ✅ Реализовано
- ✅ Новая линейка пакетов (Пробный → Премиум)
- ✅ 8 новых стилей с LoRA поддержкой
- ✅ Видео генерация (WanX + Framepack)
- ✅ Автоматический пост-процесс (NSFW, restore, 4K upscale)
- ✅ Инклюзивные промпты (любой пол)
- ✅ YC Message Queue интеграция
- ✅ Упрощенная архитектура (2 контейнера)
- ✅ GitHub Actions CI/CD
- ✅ Обновленная документация

### 🚀 Готово к продакшену!

## 📈 Изменения в v2025

### ❌ Убрано (архитектура v1)
- ❌ OpenAI Proxy (прямые вызовы API)
- ❌ Redis + Celery (заменено на YC Message Queue)
- ❌ Caddy веб-сервер
- ❌ Сложная инфраструктура (5+ контейнеров)
- ❌ proxy/ каталог

### ✅ Добавлено (архитектура v2025)
- ✅ Yandex Message Queue (managed)
- ✅ Видео генерация
- ✅ Пост-процесс автоматизация
- ✅ Serverless-ready архитектура
- ✅ Инклюзивность
- ✅ Закрепленные версии зависимостей



## 🛠️ Поддержка

**Документация:**
- [🚀 Быстрый старт](GETTING_STARTED.md)
- [⚙️ Команды сервера](инструкция.md)
- [📋 План проекта](план%20проекта.md)

**Диагностика:**
```bash
# Health check
docker compose exec image-worker python -c "
from worker.health import check_health
print(check_health())
"

# Статус v2025
docker compose ps
docker compose logs -f
```

## 📝 Лицензия

Частный проект. Все права защищены.

---

**🎯 AI Photo Bot v2025** - современная, экономичная и масштабируемая архитектура для генерации AI-портретов