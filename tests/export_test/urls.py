from django.urls import path, include

from .views import TestViewSearch

urlpatterns = [
    path("", TestViewSearch.as_view(), name="export-test-list"),
    path("export/", include("osis_export.api.urls_v1", namespace="test_export")),
]
