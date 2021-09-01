from django.urls import path

from osis_export.api.views import AsyncExport

app_name = "osis_export"
urlpatterns = [
    path("", AsyncExport.as_view(), name="export"),
]
