# -*- coding: utf-8 -*-

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plamber.settings')

app = Celery('Plamber')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
