from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _

from base.models.person import Person
from osis_document.contrib import FileField
from osis_export.models.enums.types import ExportTypes


class Export(models.Model):
    """Represent an export task. It must contains the base app label and model name,
    and the related filters to be able to recreate the desired export. It is also
    linked to an async task, representing the Export to the end user. And the result
    of the export will be store in a linked DocumentFile."""

    app_label = models.CharField(_("Called from app"), max_length=100)
    model_name = models.CharField(_("Called from model name"), max_length=100)
    filters = JSONField(_("Filters"), null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="+")
    job_uuid = models.UUIDField(_("UUID of the related task job"))
    file = FileField(null=True)
    file_name = models.CharField(_("File name"), max_length=100)
    type = models.CharField(_("Type"), choices=ExportTypes.choices(), max_length=25)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
