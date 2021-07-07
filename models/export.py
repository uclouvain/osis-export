from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext as _

from base.models.person import Person
from osis_async.models import AsyncTask
from osis_document.contrib import FileField


class Export(models.Model):
    """Represent an export task. It must contains the base class and the related
    filters to be able to recreate the desired export. It is also linked to an async
    task, representing the Export to the end user. And the result of the export will be
    store in a linked DocumentFile."""

    called_from_class = models.CharField(_("Called from class"), max_length=100)
    filters = JSONField(_("Filters"))
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="+")
    async_task = models.ForeignKey(AsyncTask, on_delete=models.CASCADE)
    file = FileField(null=True)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
