from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _

from base.models.person import Person
from osis_async.models import AsyncTask
from osis_document.contrib import FileField


class Export(models.Model):
    """Represent an export task. It must contains the base app label and model name,
    and the related filters to be able to recreate the desired export. It is also
    linked to an async task, representing the Export to the end user. And the result
    of the export will be store in a linked DocumentFile."""

    app_label = models.CharField(_("Called from app"), max_length=100)
    model_name = models.CharField(_("Called from model name"), max_length=100)
    filters = JSONField(_("Filters"), null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="+")
    async_task = models.ForeignKey(AsyncTask, on_delete=models.CASCADE)
    file = FileField(null=True)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
