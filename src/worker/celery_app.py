"""
Celery application for image processing tasks
"""

import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis URL
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Create Celery app
app = Celery(
    'image_worker',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'worker.tasks',
        'worker.image_generator',
        'worker.storage'
    ]
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    result_expires=3600,  # 1 hour
    task_routes={
        'worker.tasks.generate_images': {'queue': 'image_generation'},
        'worker.tasks.upload_to_storage': {'queue': 'storage'},
        'worker.tasks.notify_user': {'queue': 'notifications'},
    }
)

# Optional: Register tasks
app.autodiscover_tasks(['worker'])

if __name__ == '__main__':
    app.start() 