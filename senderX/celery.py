# senderX/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'senderX.settings')

app = Celery('senderX')

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
