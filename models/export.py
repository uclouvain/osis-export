from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from base.models.person import Person
from osis_document.contrib import FileField
from osis_export.models.enums.types import ExportTypes
from osis_export.models.validators import validate_export_mixin_inheritance


class ExportManager(models.Manager):
    def not_generated(self):
        asynchronous_manager = import_string(settings.ASYNCHRONOUS_MANAGER_CLS)()
        pending_tasks = asynchronous_manager.get_pending_tasks()
        return self.get_queryset().filter(job_uuid__in=pending_tasks)


class Export(models.Model):
    """Represent an export task. It must contains the base app label and model name,
    and the related filters to be able to recreate the desired export. It is also
    linked to an async task, representing the Export to the end user. And the result
    of the export will be store in a linked DocumentFile."""

    called_from_class = models.TextField(
        help_text=_("Export called from this class"),
        validators=[validate_export_mixin_inheritance],
    )
    filters = models.TextField(_("Filters"), blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="+")
    job_uuid = models.UUIDField(_("UUID of the related task job"))
    file = FileField(null=True)
    file_name = models.CharField(_("File name"), max_length=100)
    type = models.CharField(_("Type"), choices=ExportTypes.choices(), max_length=25)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    objects = ExportManager()
