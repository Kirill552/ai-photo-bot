"""
Configuration for Telegram Bot
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Bot configuration"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ASSISTANT_ID: str = os.getenv("ASSISTANT_ID", "")
    
    # PiAPI
    PIAPI_KEY: str = os.getenv("PIAPI_KEY", "")
    PIAPI_BASE_URL: str = os.getenv("PIAPI_BASE_URL", "https://api.piapi.ai/v1")
    
    # Yandex Cloud
    YC_ACCESS_KEY: str = os.getenv("YC_ACCESS_KEY", "")
    YC_SECRET_KEY: str = os.getenv("YC_SECRET_KEY", "")
    YC_BUCKET_NAME: str = os.getenv("YC_BUCKET_NAME", "ai-photos")
    YC_REGION: str = os.getenv("YC_REGION", "ru-central1")
    YC_ENDPOINT: str = os.getenv("YC_ENDPOINT", "https://storage.yandexcloud.net")
    
    # Yandex Message Queue
    YC_MQ_URL: str = os.getenv("YC_MQ_URL", "")
    YC_MQ_QUEUE_NAME: str = os.getenv("YC_MQ_QUEUE_NAME", "jobs")
    
    # App settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PROXY_URL: Optional[str] = os.getenv("PROXY_URL")
    
    # Paths
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/photobot")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "/var/log/bot")
    
    # Limits
    MAX_PHOTOS_PER_SESSION: int = int(os.getenv("MAX_PHOTOS_PER_SESSION", "15"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    
    # Prices (in rubles)
    PRICE_40_PHOTOS: int = int(os.getenv("PRICE_40_PHOTOS", "1099"))
    PRICE_100_PHOTOS: int = int(os.getenv("PRICE_100_PHOTOS", "1799"))
    MARKETING_DISCOUNT: float = float(os.getenv("MARKETING_DISCOUNT", "0.1"))
    
    def __post_init__(self):
        """Validate configuration"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        if not self.ASSISTANT_ID:
            raise ValueError("ASSISTANT_ID is required")
        
        # Create directories
        os.makedirs(self.TEMP_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True) 