from __future__ import absolute_import

from . import models, tools
from celery import shared_task


@shared_task
def run_tool(op_id: int):
    operation = models.Operation.objects.get(pk=op_id)
    project = operation.project
    tool = operation.type
    operation = tools.default_task_queue.run_task(operation)
    return "Ended running operation %s." % operation

