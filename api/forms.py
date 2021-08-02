from django import forms

from osis_export.models import Export
from osis_export.models.validators import validate_export_mixin_inheritance


class ExportForm(forms.ModelForm):
    async_task_name = forms.CharField(max_length=100, widget=forms.HiddenInput())
    async_task_description = forms.CharField(widget=forms.HiddenInput())
    async_task_ttl = forms.IntegerField(required=False, widget=forms.HiddenInput())
    next = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Export
        fields = (
            "called_from_class",
            "filters",
            "type",
            "file_name",
        )
        widgets = {
            "called_from_class": forms.HiddenInput(),
            "filters": forms.HiddenInput(),
            "type": forms.HiddenInput(),
            "file_name": forms.HiddenInput(),
        }

    def clean_called_from_class(self):
        called_from_class = self.cleaned_data.get("called_from_class")
        validate_export_mixin_inheritance(called_from_class)
        return called_from_class
