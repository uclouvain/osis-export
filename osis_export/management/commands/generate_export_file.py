import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone, translation
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from osis_async.models.enums import TaskState
from osis_document.api.utils import get_remote_token
from osis_document.utils import save_raw_content_remotely, get_file_url
from osis_export.models import Export
from osis_notification.models import WebNotification


class Command(BaseCommand):
    help = "Generate all the export files"

    def handle(self, *args, **options):
        for export in Export.objects.not_generated():
            job_uuid = export.job_uuid
            language = export.person.language or settings.LANGUAGE_CODE
            # Update the related async task first
            task_manager = import_string(settings.OSIS_EXPORT_ASYNCHRONOUS_MANAGER_CLS)
            # Import and instantiate the base view class
            base_class_instance = import_string(export.called_from_class)()

            task_manager.update(
                job_uuid,
                progression=1,
                state=TaskState.PROCESSING,
                started_at=timezone.now(),
                **base_class_instance.get_task_started_async_manager_extra_kwargs()
            )
            # Generate the file and the notification in the person's language
            with translation.override(language):
                # generate the wanted file by calling the method on mixin
                try:
                    file = base_class_instance.generate_file(
                        person=export.person,
                        filters=export.filters,
                    )

                    # save file into an Upload object in order to reuse osis_document
                    file_extension = base_class_instance.get_file_extension()
                    file_mimetype = base_class_instance.get_mimetype()
                    file_name = "{}{}".format(export.file_name, file_extension)
                    token = save_raw_content_remotely(file, file_name, file_mimetype)
                    export.file = [token]
                    export.save()
                    read_token = get_remote_token(
                        uuid=export.file[0],
                        **base_class_instance.get_read_token_extra_kwargs(),
                    )
                    file_url = get_file_url(read_token)
                except Exception as e:
                    task_manager.update(
                        job_uuid,
                        progression=0,
                        state=TaskState.ERROR,
                        **base_class_instance.get_task_error_async_manager_extra_kwargs(e)
                    )
                    logging.getLogger(settings.DEFAULT_LOGGER).error(e)
                    raise e

                # and finally update the related async task again
                task_manager.update(
                    job_uuid,
                    progression=100,
                    state=TaskState.DONE,
                    completed_at=timezone.now(),
                    **base_class_instance.get_task_done_async_manager_extra_kwargs(file_name, file_url)
                )
                payload = format_html(
                    "{}: <a href='{}' target='_blank'>{}</a>",
                    _("Your document is available here"),
                    file_url,
                    file_name,
                )
                WebNotification.objects.create(person=export.person, payload=payload)
