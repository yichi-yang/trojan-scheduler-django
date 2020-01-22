from __future__ import absolute_import, unicode_literals
import itertools
from .scheduler_util import Evaluator, dfs_search, part_list_from_coursebin,\
    part_combo_to_component_list, Timetable, UncaughtSchedulerException,\
    TimeoutException, TimeFormatException
from .models import Schedule, Task
from celery import shared_task
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.db import transaction
import celery

import logging

logger = logging.getLogger('celery.tasks')


class LogErrorsTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception('Celery task raised an exception:', exc_info=exc)
        super(LogErrorsTask, self).on_failure(
            exc, task_id, args, kwargs, einfo)


@shared_task(base=LogErrorsTask, ignore_result=True)
def generate_schedule(coursebin, preference, task_id, time_limit=None):

    task_instance = Task.objects.get(id=task_id)

    end_time = datetime.now() + timedelta(seconds=time_limit) if time_limit else None

    part_combinations = itertools.product(*part_list_from_coursebin(coursebin))

    evaluator = Evaluator(preference, 20)

    try:
        task_instance.status = Task.PROCESSING
        task_instance.save()

        try:
            for combination in part_combinations:
                component_list = part_combo_to_component_list(combination)
                dfs_search(component_list, 0, list(),
                           Timetable(), evaluator, end_time)
        except TimeoutException as toe:
            task_instance.status = Task.WARNING
            task_instance.message = ("This task is terminated because it exceeds the {limit} seconds limit. " +
                                     "Generated schedules may not be optimal.").format(limit=time_limit)
        finally:
            # get schedules from the evatutor
            results = evaluator.get_results()
            # save count
            task_instance.count = evaluator.count
            # save all schedules
            with transaction.atomic():
                for result in results:
                    schedule_instance = Schedule(task=task_instance,
                                                 public=not task_instance.user,
                                                 **result.toDict())
                    schedule_instance.save()
                    schedule_instance.sections.add(*result.sections)

    except TimeFormatException as tfe:
        task_instance.status = Task.ERROR
        task_instance.message = "Invalid time format: " + str(tfe)

    except Exception as e:
        exception_id = get_random_string()

        task_instance.status = Task.EXCEPT
        task_instance.message = exception_id

        raise UncaughtSchedulerException(e, exception_id, task_id) from e
    else:
        # if the task's status is still processing, e.g. not set to warning
        if task_instance.status == Task.PROCESSING:
            task_instance.status = Task.DONE
    finally:
        task_instance.save()

    return task_instance.status
