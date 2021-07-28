from django.core.management import call_command

from backoffice.celery import app as celery_app


@celery_app.task
def run():
    """This job will launch the Django command that will generate all the Export's
    files."""

    call_command("generate_export_file")
