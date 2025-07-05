#!/bin/bash

# 🚀 Automated Deployment Script for AI Photo Bot
# Запускается автоматически через GitHub Actions или вручную

set -e

echo "🚀 Starting deployment of AI Photo Bot..."

# Проверяем, что находимся в правильной папке
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Make sure you're in the project directory."
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create it from config.example"
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

# Проверяем здоровье сервисов
echo "❤️ Health check..."

# Проверяем OpenAI Proxy
if curl -f http://localhost:8000/health &>/dev/null; then
    echo "✅ OpenAI Proxy is healthy"
else
    echo "❌ OpenAI Proxy health check failed"
fi

# Проверяем Redis
if docker compose exec -T redis redis-cli ping &>/dev/null; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis health check failed"
fi

# Проверяем Telegram Bot
if docker compose logs telegram-bot | grep -q "Bot started successfully" 2>/dev/null; then
    echo "✅ Telegram Bot is healthy"
else
    echo "⚠️  Telegram Bot status unknown (check logs)"
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
echo "  Restart:   docker compose restart"
echo "  Stop:      docker compose down"
echo "  Status:    docker compose ps"

echo ""
echo "🌐 Your bot should be available at:"
echo "  - OpenAI Proxy: http://localhost:8000"
echo "  - Health check: http://localhost:8000/health"

echo ""
echo "✅ Deployment script completed successfully!" 