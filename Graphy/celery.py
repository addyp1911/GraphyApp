import os
from celery import Celery


CELERY_BROKER_URL = 'amqp://localhost:5672'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonote.settings')
app = Celery("fundoonote", broker=CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()


if __name__ == '__main__':
    app.start()