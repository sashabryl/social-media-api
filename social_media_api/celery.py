from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media_api.settings")

# create a Celery instance and configure it with the Django settings.
app = Celery("social_media_api")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self) -> None:
    print(f"Request: {self.request!r}")
