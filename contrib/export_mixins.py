import datetime

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import QueryDict
from openpyxl import Workbook


class ExportMixin:
    def get_export_objects(self, **kwargs):
        raise NotImplementedError


class QuerySetExportMixin(ExportMixin):
    def get_export_objects(self, **kwargs):
        return self.get_queryset_export(kwargs.get("filters"))

    def get_queryset_export(self, filters) -> QuerySet:
        raise NotImplementedError


class FilterSetExportMixin(QuerySetExportMixin):
    def get_queryset_export(self, filters) -> QuerySet:
        # Generate a dict from the saved querydict
        filters_dict = QueryDict(filters).dict()
        # Now get the filterset class and instantiate it with the filters
        filterset = self.get_filterset_class()(data=filters_dict)
        if filterset.is_valid():
            # and finally get back the initial queryset
            return filterset.qs
        raise ValidationError("The formset is not valid")


class FileExportMixin:
    def generate_file(self, filters):
        raise NotImplementedError

    def get_mimetype(self):
        raise NotImplementedError


class ExcelFileExportMixin(FileExportMixin):
    def get_mimetype(self):
        return "application/vnd.ms-excel"

    def generate_file(self, **kwargs):
        export_objects = self.get_export_objects(filters=kwargs.get("filters"))

        wb = Workbook()

        # grab the active worksheet
        ws = wb.active

        # Data can be assigned directly to cells
        ws['A1'] = 42

        # Rows can also be appended
        ws.append([1, 2, 3])

        # Python types will automatically be converted
        ws['A2'] = datetime.datetime.now()

        file_name = f"{kwargs.get('file_name')}.xlsx"
        # Save the file
        wb.save(file_name)

        return file_name


class ExcelFilterSetExportMixin(FilterSetExportMixin, ExcelFileExportMixin):
    """Excel export from a FilterSet based view"""
