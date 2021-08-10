from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from osis_async.models.enums import TaskStates
from osis_async.utils import update_task
from osis_document.utils import save_raw_upload
from osis_export.models import Export


class Command(BaseCommand):
    help = "Generate all the export files"

    def handle(self, *args, **options):
        for export in Export.objects.not_generated():
            # Import and instantiate the base view class
            base_class_instance = import_string(export.called_from_class)()
            # generate the wanted file by calling the method on mixin
            file = base_class_instance.generate_file(filters=export.filters)
            # save file into an Upload object in order to reuse osis_document
            token = save_raw_upload(
                file,
                f"{export.file_name}{base_class_instance.get_file_extension()}",
                base_class_instance.get_mimetype(),
            )
            export.file = [token.token]
            export.save()
            update_task(export.job_uuid, progression=100, state=TaskStates.DONE.name)
