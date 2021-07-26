from django.core.management.base import BaseCommand
from django.http import QueryDict
from django.utils.module_loading import import_string

from osis_export.models import Export
from osis_export.models.enums.types import ExportTypes


class Command(BaseCommand):
    help = "Generate all the export files"

    def handle(self, *args, **options):
        for export in Export.objects.not_generated():
            # Import the base view class
            BaseClass = import_string(export.called_from_class)
            # Generate a dict from the saved querydict
            filters_dict = QueryDict(export.filters).dict()
            # Pass it to the filterset class of the base class
            filterset = BaseClass.filterset_class(data=filters_dict)
            # and finally get back the initial queryset
            initial_queryset = filterset.qs

            if export.type == ExportTypes.EXCEL.name:
                # use the Excel file generator
                pass
            elif export.type == ExportTypes.PDF.name:
                # use the PDF file generator
                pass
