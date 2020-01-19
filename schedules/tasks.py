from __future__ import absolute_import, unicode_literals
import itertools
from .scheduler_util import Evaluator, dfs_search, part_list_from_coursebin, part_combo_to_component_list, Timetable
from .models import Schedule, Task

from celery import shared_task


@shared_task(ignore_result=True)
def generate_schedule(coursebin, preference, task_id):

    task_instance = Task.objects.get(id=task_id)

    part_combinations = itertools.product(*part_list_from_coursebin(coursebin))

    evaluator = Evaluator(preference, 20)

    try:
        for combination in part_combinations:
            component_list = part_combo_to_component_list(combination)
            dfs_search(component_list, 0, list(), Timetable(), evaluator)

        results = evaluator.get_results()
        for result in results:
            schedule_instance = Schedule(task=task_instance,
                                         early_score=result.early_score,
                                         late_score=result.late_score,
                                         break_score=result.break_score,
                                         reserved_score=result.reserved_score,
                                         total_score=result.total_score,
                                         public=not task_instance.user)
            schedule_instance.save()
            schedule_instance.sections.add(*result.sections)

    except Exception as e:
        task_instance.status = Task.EXCEPT
        task_instance.save()
        task_instance.message = str(e)
        raise e
    else:
        task_instance.status = Task.DONE
    finally:
        task_instance.save()
