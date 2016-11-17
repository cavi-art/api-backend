"""
Celery config for api_config project.

It exposes the Celery applicatoin as a module-level variable named ``app``.

For more information on this file, see
[celery docs]
"""
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_config.settings')

app = Celery(
    'api_config',
    broker='amqp://',
    # backend='amqp://',
    # result_expires=300,
)

# Using a string here means the worker doesn't have to serialize the
# configuration object.
app.config_from_object('django.conf:settings', namespace='CELERY')

# load task modules from registered Django app configs.
app.autodiscover_tasks()


## Debug task...
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

