from django.urls import path

from osis_export.api.views import ExcelAsyncExport

app_name = "osis_export"
urlpatterns = [
    path("excel/", ExcelAsyncExport.as_view(), name="excel"),
]
