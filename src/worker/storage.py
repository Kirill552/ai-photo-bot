"""
Yandex Object Storage integration
"""

import asyncio
import logging
import os
from typing import Optional, List, Dict, Any
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
import aiofiles
import aiohttp
from urllib.parse import quote
from .config import settings

logger = logging.getLogger(__name__)


class YandexObjectStorage:
    """Класс для работы с Yandex Object Storage"""
    
    def __init__(self):
        """Инициализация клиента S3"""
        
        # Конфигурация для Yandex Cloud
        self.config = Config(
            region_name='ru-central1',
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            signature_version='s3v4'
        )
        
        # Создаем клиент S3
        self.s3_client = boto3.client(
            's3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=settings.YC_ACCESS_KEY,
            aws_secret_access_key=settings.YC_SECRET_KEY,
            config=self.config
        )
        
        self.bucket_name = settings.YC_BUCKET_NAME  # ai-photos
        
        logger.info(f"🪣 Yandex Object Storage initialized for bucket: {self.bucket_name}")
    
    async def upload_image(self, image_data: bytes, key: str, 
                          content_type: str = 'image/jpeg') -> Dict[str, Any]:
        """
        Загружает изображение в Object Storage
        
        Args:
            image_data: данные изображения
            key: ключ объекта (путь в бакете)
            content_type: MIME тип файла
            
        Returns:
            Dict с информацией о загруженном файле
        """
        
        try:
            # Создаем временный файл
            temp_file_path = f"/tmp/{key}"
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            # Записываем данные в файл
            async with aiofiles.open(temp_file_path, 'wb') as f:
                await f.write(image_data)
            
            # Загружаем в S3 синхронно (boto3 не поддерживает async)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._upload_file_sync, 
                temp_file_path, 
                key, 
                content_type
            )
            
            # Удаляем временный файл
            try:
                os.remove(temp_file_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Upload error for {key}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "key": key
            }
    
    def _upload_file_sync(self, file_path: str, key: str, content_type: str) -> Dict[str, Any]:
        """Синхронная загрузка файла"""
        
        try:
            # Загружаем файл
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # Публичный доступ для чтения
                }
            )
            
            # Формируем публичную ссылку
            public_url = f"https://storage.yandexcloud.net/{self.bucket_name}/{quote(key)}"
            
            logger.info(f"✅ File uploaded: {key}")
            
            return {
                "success": True,
                "key": key,
                "url": public_url,
                "bucket": self.bucket_name
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"❌ AWS Client error {error_code}: {e}")
            return {
                "success": False,
                "error": f"AWS error: {error_code}",
                "key": key
            }
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found")
            return {
                "success": False,
                "error": "No AWS credentials",
                "key": key
            }
        except Exception as e:
            logger.error(f"❌ Unexpected upload error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "key": key
            }
    
    async def upload_multiple_images(self, images: List[Dict[str, Any]], 
                                   session_id: str) -> List[Dict[str, Any]]:
        """
        Загружает несколько изображений
        
        Args:
            images: список изображений с данными
            session_id: ID сессии пользователя
            
        Returns:
            Список результатов загрузки
        """
        
        results = []
        
        for i, image_data in enumerate(images):
            # Генерируем ключ файла
            timestamp = image_data.get('timestamp', 'unknown')
            key = f"sessions/{session_id}/image_{i+1}_{timestamp}.jpg"
            
            # Загружаем изображение
            result = await self.upload_image(
                image_data['data'], 
                key,
                image_data.get('content_type', 'image/jpeg')
            )
            
            # Добавляем метаданные
            result.update({
                "index": i + 1,
                "session_id": session_id,
                "original_filename": image_data.get('filename', f'image_{i+1}.jpg')
            })
            
            results.append(result)
        
        successful_uploads = len([r for r in results if r["success"]])
        logger.info(f"📤 Uploaded {successful_uploads}/{len(images)} images for session {session_id}")
        
        return results
    
    def upload_file(self, file_path: str, key: str, content_type: str = None) -> str:
        """
        Загружает файл с диска в Object Storage (синхронно)
        
        Args:
            file_path: путь к файлу на диске
            key: ключ объекта в хранилище
            content_type: MIME тип файла (автоопределение по расширению)
            
        Returns:
            URL загруженного файла
        """
        
        try:
            # Автоопределение content_type
            if content_type is None:
                if key.lower().endswith('.jpg') or key.lower().endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif key.lower().endswith('.png'):
                    content_type = 'image/png'
                elif key.lower().endswith('.zip'):
                    content_type = 'application/zip'
                else:
                    content_type = 'application/octet-stream'
            
            # Загружаем файл синхронно
            result = self._upload_file_sync(file_path, key, content_type)
            
            if result['success']:
                logger.info(f"✅ File uploaded successfully: {key}")
                return result['url']
            else:
                logger.error(f"❌ File upload failed: {result['error']}")
                raise Exception(f"Upload failed: {result['error']}")
                
        except Exception as e:
            logger.error(f"❌ Upload file error for {key}: {str(e)}")
            raise e
    
    async def delete_session_files(self, session_id: str) -> Dict[str, Any]:
        """
        Удаляет все файлы сессии
        
        Args:
            session_id: ID сессии
            
        Returns:
            Результат операции
        """
        
        try:
            # Получаем список объектов с префиксом
            prefix = f"sessions/{session_id}/"
            
            loop = asyncio.get_event_loop()
            objects = await loop.run_in_executor(
                None,
                self._list_objects_sync,
                prefix
            )
            
            if not objects:
                return {"success": True, "deleted_count": 0, "message": "No files to delete"}
            
            # Удаляем объекты
            deleted_count = await loop.run_in_executor(
                None,
                self._delete_objects_sync,
                objects
            )
            
            logger.info(f"🗑️ Deleted {deleted_count} files for session {session_id}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Delete session files error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def _list_objects_sync(self, prefix: str) -> List[str]:
        """Синхронное получение списка объектов"""
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            objects = []
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
            
            return objects
            
        except Exception as e:
            logger.error(f"❌ List objects error: {str(e)}")
            return []
    
    def _delete_objects_sync(self, object_keys: List[str]) -> int:
        """Синхронное удаление объектов"""
        
        try:
            if not object_keys:
                return 0
            
            # Формируем структуру для batch delete
            delete_objects = {
                'Objects': [{'Key': key} for key in object_keys]
            }
            
            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete=delete_objects
            )
            
            deleted_count = len(response.get('Deleted', []))
            
            if 'Errors' in response:
                for error in response['Errors']:
                    logger.error(f"❌ Delete error for {error['Key']}: {error['Message']}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Batch delete error: {str(e)}")
            return 0
    
    async def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Генерирует подписанную ссылку для временного доступа
        
        Args:
            key: ключ объекта
            expiration: время жизни ссылки в секундах
            
        Returns:
            Подписанная ссылка или None
        """
        
        try:
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None,
                self._generate_presigned_url_sync,
                key,
                expiration
            )
            
            return url
            
        except Exception as e:
            logger.error(f"❌ Generate presigned URL error: {str(e)}")
            return None
    
    def _generate_presigned_url_sync(self, key: str, expiration: int) -> str:
        """Синхронная генерация подписанной ссылки"""
        
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
    
    async def check_bucket_access(self) -> Dict[str, Any]:
        """
        Проверяет доступ к бакету
        
        Returns:
            Результат проверки
        """
        
        try:
            loop = asyncio.get_event_loop()
            
            # Пробуем получить информацию о бакете
            await loop.run_in_executor(
                None,
                self.s3_client.head_bucket,
                Bucket=self.bucket_name
            )
            
            logger.info(f"✅ Bucket access verified: {self.bucket_name}")
            
            return {
                "success": True,
                "bucket": self.bucket_name,
                "message": "Bucket access verified"
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                message = f"Bucket {self.bucket_name} not found"
            elif error_code == '403':
                message = f"Access denied to bucket {self.bucket_name}"
            else:
                message = f"AWS error {error_code}: {e}"
            
            logger.error(f"❌ Bucket access check failed: {message}")
            
            return {
                "success": False,
                "error": message,
                "bucket": self.bucket_name
            }
        except Exception as e:
            logger.error(f"❌ Bucket access check error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "bucket": self.bucket_name
            }


# Глобальный экземпляр
storage = YandexObjectStorage() 