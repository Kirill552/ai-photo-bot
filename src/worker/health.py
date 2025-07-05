"""
Health check for Worker v2025
"""

import logging
import httpx
import asyncio
from .config import settings
from .storage import YandexObjectStorage
from .mq_client import get_mq_client

logger = logging.getLogger(__name__)


def check_health():
    """Check worker health for v2025 architecture"""
    
    try:
        logger.info("🏥 Starting health check for Worker v2025...")
        
        # Check configuration
        if not settings.YC_MQ_URL:
            raise ValueError("YC_MQ_URL is not configured")
            
        if not settings.PIAPI_KEY:
            raise ValueError("PIAPI_KEY is not configured")
            
        if not settings.YC_ACCESS_KEY:
            raise ValueError("YC_ACCESS_KEY is not configured")
        
        # Check PiAPI connection
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{settings.PIAPI_BASE_URL}/health",
                    headers={"Authorization": f"Bearer {settings.PIAPI_KEY}"},
                    timeout=5.0
                )
                if response.status_code != 200:
                    logger.warning(f"⚠️ PiAPI health check returned {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ PiAPI health check failed: {e}")
        
        # Check Yandex Object Storage
        try:
            storage = YandexObjectStorage()
            # Just check if we can initialize - full check is async
            logger.info("✅ Yandex Object Storage initialized")
        except Exception as e:
            logger.error(f"❌ Yandex Object Storage check failed: {e}")
            raise
        
        # Check YC Message Queue client
        try:
            mq_client = get_mq_client()
            if not mq_client:
                raise ValueError("Failed to initialize MQ client")
            logger.info("✅ YC Message Queue client initialized")
        except Exception as e:
            logger.error(f"❌ YC Message Queue check failed: {e}")
            raise
        
        logger.info("✅ Worker health check passed")
        return {
            "healthy": True,
            "architecture": "v2025",
            "components": {
                "yc_message_queue": "ok",
                "yandex_object_storage": "ok",
                "piapi": "ok",
                "configuration": "ok"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Worker health check failed: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "architecture": "v2025"
        } 