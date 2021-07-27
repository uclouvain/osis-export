from django_filters import FilterSet
from django_filters.views import FilterView

from osis_export.models import Export


class ExportFilter(FilterSet):
    class Meta:
        model = Export
        fields = ["job_uuid"]


class TestViewSearch(FilterView):
    model = Export
    template_name = "export_test/export_search.html"
    filterset_class = ExportFilter
