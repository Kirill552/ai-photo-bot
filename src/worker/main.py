#!/usr/bin/env python3
"""
Worker main module for Yandex Message Queue processing
Заменяет Celery worker для архитектуры v2
"""

import asyncio
import json
import logging
import signal
import sys
import time
from typing import Dict, Any

from .config import settings
from .mq_client import get_mq_client
from .tasks import process_image_generation_task
from .health import check_health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MessageQueueWorker:
    """Worker для обработки сообщений из Yandex Message Queue"""
    
    def __init__(self):
        self.running = True
        self.mq_client = get_mq_client()
        self.processed_count = 0
        self.error_count = 0
        
        # Graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 YC Message Queue Worker initialized")
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"📨 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def start(self):
        """Запуск worker'а"""
        logger.info("🔄 Starting YC Message Queue Worker...")
        
        while self.running:
            try:
                # Получаем сообщения из очереди
                messages = self.mq_client.receive_messages(
                    max_messages=settings.WORKER_CONCURRENCY,
                    wait_time=20  # Long polling
                )
                
                if not messages:
                    logger.debug("📭 No messages in queue, waiting...")
                    continue
                
                # Обрабатываем сообщения
                for message in messages:
                    try:
                        self._process_message(message)
                        self.processed_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing message: {e}")
                        self.error_count += 1
                        # Не удаляем сообщение при ошибке, оно вернётся в очередь
                        continue
                
                # Логируем статистику
                if self.processed_count % 10 == 0:
                    logger.info(f"📊 Processed: {self.processed_count}, Errors: {self.error_count}")
                
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
                time.sleep(5)  # Пауза при ошибке
        
        logger.info("🛑 Worker stopped")
    
    def _process_message(self, message: Dict[str, Any]):
        """Обработка одного сообщения"""
        try:
            # Парсим тело сообщения
            body = json.loads(message['Body'])
            task_type = body.get('task_type')
            task_data = body.get('data', {})
            
            logger.info(f"🔄 Processing task: {task_type}")
            
            # Обрабатываем задачу по типу
            if task_type == 'generate_images':
                result = process_image_generation_task(task_data)
                
                if result.get('success'):
                    logger.info(f"✅ Task completed successfully: {task_type}")
                else:
                    logger.error(f"❌ Task failed: {result.get('error')}")
                    raise Exception(f"Task processing failed: {result.get('error')}")
            
            else:
                logger.warning(f"⚠️ Unknown task type: {task_type}")
                raise Exception(f"Unknown task type: {task_type}")
            
            # Удаляем сообщение из очереди при успешной обработке
            receipt_handle = message['ReceiptHandle']
            if self.mq_client.delete_message(receipt_handle):
                logger.info("🗑️ Message deleted from queue")
            else:
                logger.warning("⚠️ Failed to delete message from queue")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in message: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
            raise


def main():
    """Главная функция worker'а"""
    try:
        # Проверяем конфигурацию
        logger.info("🔧 Checking worker configuration...")
        
        if not settings.YC_MQ_URL:
            raise ValueError("YC_MQ_URL is required")
        
        if not settings.PIAPI_KEY:
            raise ValueError("PIAPI_KEY is required")
        
        # Проверяем здоровье компонентов
        logger.info("🏥 Checking worker health...")
        health_result = check_health()
        
        if not health_result.get('healthy', False):
            logger.error(f"❌ Health check failed: {health_result}")
            sys.exit(1)
        
        # Запускаем worker
        worker = MessageQueueWorker()
        worker.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Worker interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Worker startup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 