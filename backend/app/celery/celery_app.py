import os 
from dotenv import load_dotenv
from celery import Celery, Task

load_dotenv()

celery_app = Celery("thumbnail_generator",
                    broker=os.getenv("CELERY_BROKER_URL"),
                    backend=os.getenv("CELERY_RESULT_BACKEND"),
                    include=['app.celery.tasks']
                        )

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    task_track_started=True,
)