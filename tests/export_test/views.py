from django_filters import FilterSet
from django_filters.views import FilterView

from osis_export.contrib.export_mixins import ExcelFilterSetExportMixin
from osis_export.models import Export


class ExportFilter(FilterSet):
    class Meta:
        model = Export
        fields = [
            "called_from_class",
            "filters",
            "person",
            "job_uuid",
            "file_name",
            "type",
            "created_at",
        ]


class TestViewSearch(ExcelFilterSetExportMixin, FilterView):
    def get_header(self):
        return [
            "called_from_class",
            "filters",
            "person",
            "job_uuid",
            "file_name",
            "type",
            "created_at",
        ]

    def get_data(self):
        return [
            "called_from_class",
            "filters",
            "person",
            "job_uuid",
            "file_name",
            "type",
            "created_at",
        ]

    model = Export
    template_name = "export_test/export_search.html"
    filterset_class = ExportFilter
