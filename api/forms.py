from django import forms

from osis_export.models import Export


class ExportForm(forms.ModelForm):
    async_task_name = forms.CharField(max_length=100, widget=forms.HiddenInput())
    async_task_description = forms.CharField(widget=forms.HiddenInput())
    async_task_ttl = forms.IntegerField(required=False, widget=forms.HiddenInput())
    next = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Export
        fields = (
            "app_label",
            "model_name",
            "filters",
            "type",
            "file_name",
        )
        widgets = {
            "app_label": forms.HiddenInput(),
            "model_name": forms.HiddenInput(),
            "filters": forms.HiddenInput(),
            "type": forms.HiddenInput(),
            "file_name": forms.HiddenInput(),
        }
