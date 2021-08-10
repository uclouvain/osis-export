from django_filters import FilterSet
from django_filters.views import FilterView

from osis_export.contrib.export_mixins import ExcelFilterSetExportMixin
from osis_export.tests.export_test.models import DummyModel


class DummyFilter(FilterSet):
    class Meta:
        model = DummyModel
        fields = ["name", "selectable_value"]


class TestViewSearch(ExcelFilterSetExportMixin, FilterView):
    model = DummyModel
    template_name = "export_test/dummy_search.html"
    filterset_class = DummyFilter

    def get_header(self):
        return ["name", "selectable value"]

    def get_data(self):
        return ["name", "selectable_value"]
