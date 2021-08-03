from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import QueryDict
from openpyxl import Workbook
from openpyxl.styles import Font


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

    def get_header(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    @staticmethod
    def get_attr(export, data):
        """Return str representation of `export.data`, or an empty string if None."""
        return str(getattr(export, data)) if data is not None else ""

    def generate_file(self, **kwargs):
        workbook = Workbook()

        # grab the active worksheet
        worksheet = workbook.active

        # add headers
        worksheet.append(self.get_header())
        cells = worksheet.iter_rows("A1:AAA1")
        for col in cells:
            for cell in col:
                cell.font = Font(bold=True)

        # add data
        export_objects = self.get_export_objects(filters=kwargs.get("filters"))
        sheet_datas = self.get_data()
        for export in export_objects.all():
            worksheet.append(
                [self.get_attr(export, sheet_data) for sheet_data in sheet_datas]
            )

        # Save the file
        file_name = f"{kwargs.get('file_name')}.xlsx"
        workbook.save(file_name)

        return file_name


class ExcelFilterSetExportMixin(FilterSetExportMixin, ExcelFileExportMixin):
    """Excel export from a FilterSet based view"""
