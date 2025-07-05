#!/bin/bash

# 🚀 Automated Deployment Script for AI Photo Bot v2025
# Запускается автоматически через GitHub Actions или вручную

set -e

echo "🚀 Starting deployment of AI Photo Bot v2025..."

# Проверяем, что находимся в правильной папке
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Make sure you're in the project directory."
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create it from environment variables"
    exit 1
fi

echo "✅ .env file found"

# Останавливаем старые контейнеры если они есть
echo "🛑 Stopping existing containers..."
docker compose down --remove-orphans || true

# Очищаем старые образы
echo "🧹 Cleaning up old images..."
docker system prune -f || true

# Собираем новые образы
echo "🔨 Building new images..."
docker compose build --no-cache

# Запускаем сервисы
echo "🚀 Starting services..."
docker compose up -d

# Ждем запуска сервисов
echo "⏳ Waiting for services to start..."
sleep 30

# Проверяем статус сервисов
echo "🔍 Checking service status..."
docker compose ps

# Проверяем здоровье сервисов v2025
echo "❤️ Health check for v2025 architecture..."

# Проверяем Telegram Bot
if docker compose logs telegram-bot | grep -q "Bot started successfully" 2>/dev/null; then
    echo "✅ Telegram Bot is healthy"
else
    echo "⚠️  Telegram Bot status unknown (check logs)"
fi

# Проверяем Image Worker
if docker compose logs image-worker | grep -q "Worker initialized" 2>/dev/null; then
    echo "✅ Image Worker is healthy"
else
    echo "⚠️  Image Worker status unknown (check logs)"
fi

# Показываем логи последних 50 строк
echo "📋 Recent logs:"
docker compose logs --tail=50

# Показываем финальную информацию
echo ""
echo "🎉 Deployment completed!"
echo "📊 Service status:"
docker compose ps

echo ""
echo "🔗 Useful commands:"
echo "  View logs: docker compose logs -f"
echo "  Bot logs:  docker compose logs -f telegram-bot"
echo "  Worker logs: docker compose logs -f image-worker"
echo "  Restart:   docker compose restart"
echo "  Stop:      docker compose down"
echo "  Status:    docker compose ps"

echo ""
echo "🎯 Architecture v2025:"
echo "  - Telegram Bot: Handles user interactions"
echo "  - Image Worker: Processes via Yandex Message Queue"
echo "  - Storage: Yandex Object Storage"
echo "  - Queue: Yandex Message Queue (managed)"

echo ""
echo "✅ Deployment script completed successfully!" 