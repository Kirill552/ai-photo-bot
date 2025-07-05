"""
Worker configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class WorkerSettings(BaseSettings):
    """Настройки для worker сервиса"""
    
    # Yandex Message Queue
    YC_MQ_URL: str = Field(..., env="YC_MQ_URL", description="Yandex Message Queue URL")
    YC_MQ_QUEUE_NAME: str = Field(default="jobs", env="YC_MQ_QUEUE_NAME", description="Queue name for jobs")
    
    # PiAPI
    PIAPI_KEY: str = Field(..., env="PIAPI_KEY")
    PIAPI_BASE_URL: str = Field(default="https://api.piapi.ai", env="PIAPI_BASE_URL")
    
    # Yandex Object Storage
    YC_ACCESS_KEY: str = Field(..., env="YC_ACCESS_KEY", description="Yandex Cloud Access Key ID")
    YC_SECRET_KEY: str = Field(..., env="YC_SECRET_KEY", description="Yandex Cloud Secret Access Key")
    YC_BUCKET_NAME: str = Field(default="ai-photos", env="YC_BUCKET_NAME", description="Yandex Object Storage bucket name")
    YC_REGION: str = Field(default="ru-central1", env="YC_REGION")
    YC_ENDPOINT: str = Field(default="https://storage.yandexcloud.net", env="YC_ENDPOINT")
    
    # Telegram Bot
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    
    # Worker settings
    WORKER_CONCURRENCY: int = Field(default=4, env="WORKER_CONCURRENCY")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    RETRY_DELAY: int = Field(default=60, env="RETRY_DELAY")  # seconds
    
    # Image generation settings
    DEFAULT_IMAGE_SIZE: int = Field(default=1024, env="DEFAULT_IMAGE_SIZE")
    MAX_IMAGES_PER_SESSION: int = Field(default=100, env="MAX_IMAGES_PER_SESSION")
    
    # Video generation settings
    VIDEO_ENABLED: bool = Field(default=True, env="VIDEO_ENABLED")
    VIDEO_DEFAULT_FPS: int = Field(default=20, env="VIDEO_DEFAULT_FPS")
    VIDEO_MAX_DURATION: int = Field(default=20, env="VIDEO_MAX_DURATION")  # seconds
    VIDEO_CONCURRENT_LIMIT: int = Field(default=2, env="VIDEO_CONCURRENT_LIMIT")
    
    # Post-processing settings
    POST_PROCESS_ENABLED: bool = Field(default=True, env="POST_PROCESS_ENABLED")
    POST_PROCESS_BATCH_SIZE: int = Field(default=5, env="POST_PROCESS_BATCH_SIZE")
    POST_PROCESS_TIMEOUT: int = Field(default=300, env="POST_PROCESS_TIMEOUT")  # seconds
    NSFW_THRESHOLD: float = Field(default=0.7, env="NSFW_THRESHOLD")
    UPSCALE_TARGET_HEIGHT: int = Field(default=2160, env="UPSCALE_TARGET_HEIGHT")  # 4K
    UPSCALE_TARGET_WIDTH: int = Field(default=3840, env="UPSCALE_TARGET_WIDTH")
    
    # Package settings
    PACKAGE_TRIAL_PHOTOS: int = Field(default=2, env="PACKAGE_TRIAL_PHOTOS")
    PACKAGE_BASIC_PHOTOS: int = Field(default=10, env="PACKAGE_BASIC_PHOTOS")
    PACKAGE_STANDARD_PHOTOS: int = Field(default=25, env="PACKAGE_STANDARD_PHOTOS")
    PACKAGE_PREMIUM_PHOTOS: int = Field(default=50, env="PACKAGE_PREMIUM_PHOTOS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Development
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Глобальный экземпляр настроек
settings = WorkerSettings() 