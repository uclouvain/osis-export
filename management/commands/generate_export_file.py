import sys

from django.core import signing
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from osis_document.models import Upload, Token
from osis_document.utils import calculate_md5, get_token
from osis_export.models import Export


class Command(BaseCommand):
    help = "Generate all the export files"

    def handle(self, *args, **options):
        for export in Export.objects.not_generated():
            # Import and instantiate the base view class
            base_class_instance = import_string(export.called_from_class)()
            # generate the wanted file by calling the method on mixin
            file = base_class_instance.generate_file(
                filters=export.filters,
                file_name=export.file_name,
            )
            # add this file to an Upload object in order to reuse osis_document
            md5 = calculate_md5(file)
            upload = Upload.objects.create(
                file=file,
                mimetype=base_class_instance.get_mimetype(),
                size=sys.getsizeof(file),
                metadata={"md5": md5},
            )
            # create a related token
            token = Token.objects.create(
                upload_id=upload.uuid,
                token=signing.dumps(str(upload.uuid)),
            )
            # add it and save to the FileField
            upload.tokens.add(token)
            export.file = [token.token]
            export.save()
