from rest_framework import serializers

from osis_export.models import Export


class AsyncExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
        fields = [
            "called_from_class",
            "filters",
            "person",
            "created_at",
        ]
