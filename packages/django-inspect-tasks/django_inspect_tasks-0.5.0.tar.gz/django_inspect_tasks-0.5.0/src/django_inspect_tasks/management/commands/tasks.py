import argparse
import logging
from pprint import pformat

from crontask import scheduler
from django.core.management import BaseCommand, CommandError

from django_inspect_tasks import util
from django_inspect_tasks.util import all_tasks


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        task = parser.add_argument_group("Task Options")
        task.add_argument("--queue")
        task.add_argument("--backend")
        task.add_argument("--priority")
        task.add_argument("task", nargs="?")

    def handle_task(self, task: str, **options):
        try:
            task_obj = util.get_task(task)
            result = task_obj.using(
                queue_name=options["queue"],
                priority=options["priority"],
                backend=options["backend"],
            ).enqueue()
        except (ImportError, AttributeError):
            raise CommandError(f"Unknown task: {task}")
        else:
            return pformat(result)

    def handle(self, task, verbosity, **options):
        ch = logging.StreamHandler()
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        ch.setFormatter(formatter)
        match verbosity:
            case 2:
                logging.root.addHandler(ch)
                logging.root.setLevel(logging.INFO)
            case 3:
                logging.root.addHandler(ch)
                logging.root.setLevel(logging.DEBUG)

        # If we're passed a task name, we'll send that off to be executed
        if task:
            return self.handle_task(task, **options)

        # First we need to lookup all the tasks our app can see
        tasks = {t.module_path: t for t in all_tasks()}

        # Then we check the schedule
        scheduled = {}
        for job in scheduler.get_jobs():
            scheduled[job.func.__self__.module_path] = job.trigger

        # Then we format the output, showing an extra annotation
        # for scheduled tasks
        padding = max([len(k) for k in tasks])
        for task in sorted(tasks):
            if task in scheduled:
                self.stdout.write(
                    task.ljust(padding) + self.style.MIGRATE_HEADING(scheduled[task]),
                )
            else:
                self.stdout.write(task)
