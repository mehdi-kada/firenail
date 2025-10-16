import os 
from dotenv import load_dotenv
from celery import Celery, Task

load_dotenv()

celery_app = Celery("thumbnail_generator",
                    broker=os.getenv("CELERY_BROKER_URL"),
                    backend=os.getenv("CELERY_RESULT_BACKEND"),
                    include=['app.celery.tasks.video_pipeline']
                        )

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    broker_connection_timeout=3,
    broker_connection_max_retries=3,
    # Ensure tasks are not run eagerly in the same process, forcing them to the queue.
    task_always_eager=False,
    task_eager_propagates=False,
    # Worker configuration for concurrent processing
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
)