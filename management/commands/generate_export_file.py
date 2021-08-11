from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from osis_async.models.enums import TaskStates
from osis_async.utils import update_task
from osis_document.utils import save_raw_upload
from osis_export.models import Export
from osis_notification.models import WebNotification


class Command(BaseCommand):
    help = "Generate all the export files"

    def handle(self, *args, **options):
        for export in Export.objects.not_generated():
            job_uuid = export.job_uuid
            # Update the related async task first
            update_task(
                job_uuid,
                progression=1,
                state=TaskStates.PROCESSING.name,
                started_at=timezone.now(),
            )
            # Import and instantiate the base view class
            base_class_instance = import_string(export.called_from_class)()
            # generate the wanted file by calling the method on mixin
            file = base_class_instance.generate_file(filters=export.filters)
            # save file into an Upload object in order to reuse osis_document
            file_extension = base_class_instance.get_file_extension()
            file_mimetype = base_class_instance.get_mimetype()
            file_name = "{}{}".format(export.file_name, file_extension)
            token = save_raw_upload(file, file_name, file_mimetype)
            export.file = [token.token]
            export.save()
            # and finally update the related async task again
            update_task(
                job_uuid,
                progression=100,
                state=TaskStates.DONE.name,
                completed_at=timezone.now(),
            )
            payload = format_html(
                "{}: <a href='{}' target='_blank'>{}</a>",
                _("Your document is available here"),
                token.upload.file.url,
                file_name,
            )
            WebNotification.objects.create(person=export.person, payload=payload)
