import time

from celery import Celery

CELERY_BROKER_URL = "redis://redis:6379/0"

CELERY_RESULT_BACKEND = "redis://redis:6379/0"

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery_app.task
def do_nothing():
    print("сейчас отдохну")
    time.sleep(5)
    print("отдохнул")
    return "ok"