from django.utils.translation import gettext_lazy as _

from base.models.utils.utils import ChoiceEnum


class ExportTypes(ChoiceEnum):
    EXCEL = _("Excel")
    PDF = _("PDF")
