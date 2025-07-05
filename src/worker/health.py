"""
Health check for Worker
"""

import logging
import redis
from .config import WorkerConfig

logger = logging.getLogger(__name__)


def check_health():
    """Check worker health"""
    
    try:
        config = WorkerConfig()
        
        # Check Redis connection
        r = redis.from_url(config.REDIS_URL)
        r.ping()
        
        logger.info("Worker health check passed")
        return True
        
    except Exception as e:
        logger.error(f"Worker health check failed: {e}")
        raise 