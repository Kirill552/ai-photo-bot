"""
Yandex Message Queue client
Заменяет Celery для работы с очередями в Serverless архитектуре
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError
from .config import settings

logger = logging.getLogger(__name__)


class YandexMessageQueue:
    """Клиент для работы с Yandex Message Queue"""
    
    def __init__(self, queue_url: str, access_key: str, secret_key: str, region: str = "ru-central1"):
        """
        Инициализация клиента
        
        Args:
            queue_url: URL очереди в Yandex Cloud
            access_key: Ключ доступа к Yandex Cloud
            secret_key: Секретный ключ Yandex Cloud
            region: Регион Yandex Cloud
        """
        self.queue_url = queue_url
        self.region = region
        
        # Создаем клиент SQS (YC MQ совместим с Amazon SQS)
        self.sqs = boto3.client(
            'sqs',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url='https://message-queue.api.cloud.yandex.net'
        )
        
        logger.info(f"Initialized YC Message Queue client for region {region}")
    
    def send_message(self, message_body: Dict[str, Any], delay_seconds: int = 0) -> bool:
        """
        Отправка сообщения в очередь
        
        Args:
            message_body: Тело сообщения (будет сериализовано в JSON)
            delay_seconds: Задержка доставки в секундах
            
        Returns:
            True если сообщение отправлено успешно
        """
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body, ensure_ascii=False),
                DelaySeconds=delay_seconds
            )
            
            message_id = response.get('MessageId')
            logger.info(f"✅ Message sent to queue: {message_id}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Error sending message to queue: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending message: {e}")
            return False
    
    def receive_messages(self, max_messages: int = 10, wait_time: int = 20) -> List[Dict[str, Any]]:
        """
        Получение сообщений из очереди
        
        Args:
            max_messages: Максимальное количество сообщений для получения
            wait_time: Время ожидания в секундах (long polling)
            
        Returns:
            Список сообщений
        """
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                AttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            logger.info(f"📨 Received {len(messages)} messages from queue")
            
            return messages
            
        except ClientError as e:
            logger.error(f"❌ Error receiving messages: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error receiving messages: {e}")
            return []
    
    def delete_message(self, receipt_handle: str) -> bool:
        """
        Удаление сообщения из очереди после обработки
        
        Args:
            receipt_handle: Идентификатор сообщения для удаления
            
        Returns:
            True если сообщение удалено успешно
        """
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            
            logger.info("✅ Message deleted from queue")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Error deleting message: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error deleting message: {e}")
            return False
    
    def get_queue_attributes(self) -> Dict[str, Any]:
        """Получение атрибутов очереди"""
        try:
            response = self.sqs.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['All']
            )
            
            return response.get('Attributes', {})
            
        except ClientError as e:
            logger.error(f"❌ Error getting queue attributes: {e}")
            return {}


class AsyncYandexMessageQueue:
    """Асинхронный клиент для работы с Yandex Message Queue"""
    
    def __init__(self, queue_url: str, access_key: str, secret_key: str, region: str = "ru-central1"):
        """
        Инициализация асинхронного клиента
        """
        self.queue_url = queue_url
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        
        # Синхронный клиент для использования в async методах
        self._sync_client = None
        
        logger.info(f"Initialized async YC Message Queue client for region {region}")
    
    def _get_client(self):
        """Получение синхронного клиента (lazy initialization)"""
        if self._sync_client is None:
            self._sync_client = boto3.client(
                'sqs',
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url='https://message-queue.api.cloud.yandex.net'
            )
        return self._sync_client
    
    async def send_message(self, message_body: Dict[str, Any], delay_seconds: int = 0) -> bool:
        """Асинхронная отправка сообщения"""
        
        def _send():
            client = self._get_client()
            return client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body, ensure_ascii=False),
                DelaySeconds=delay_seconds
            )
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, _send)
            
            message_id = response.get('MessageId')
            logger.info(f"✅ Async message sent to queue: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Async error sending message: {e}")
            return False
    
    async def receive_messages(self, max_messages: int = 10, wait_time: int = 20) -> List[Dict[str, Any]]:
        """Асинхронное получение сообщений"""
        
        def _receive():
            client = self._get_client()
            return client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                AttributeNames=['All']
            )
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, _receive)
            
            messages = response.get('Messages', [])
            logger.info(f"📨 Async received {len(messages)} messages")
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Async error receiving messages: {e}")
            return []
    
    async def delete_message(self, receipt_handle: str) -> bool:
        """Асинхронное удаление сообщения"""
        
        def _delete():
            client = self._get_client()
            return client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _delete)
            
            logger.info("✅ Async message deleted from queue")
            return True
            
        except Exception as e:
            logger.error(f"❌ Async error deleting message: {e}")
            return False


# Глобальные экземпляры для использования в проекте
mq_client = None
async_mq_client = None


def get_mq_client() -> YandexMessageQueue:
    """Получение синхронного клиента MQ"""
    global mq_client
    
    if mq_client is None:
        mq_client = YandexMessageQueue(
            queue_url=settings.YC_MQ_URL,
            access_key=settings.YC_ACCESS_KEY,
            secret_key=settings.YC_SECRET_KEY,
            region=settings.YC_REGION
        )
    
    return mq_client


def get_async_mq_client() -> AsyncYandexMessageQueue:
    """Получение асинхронного клиента MQ"""
    global async_mq_client
    
    if async_mq_client is None:
        async_mq_client = AsyncYandexMessageQueue(
            queue_url=settings.YC_MQ_URL,
            access_key=settings.YC_ACCESS_KEY,
            secret_key=settings.YC_SECRET_KEY,
            region=settings.YC_REGION
        )
    
    return async_mq_client 