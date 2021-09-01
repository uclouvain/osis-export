from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from osis_export.contrib.export_mixins import ExportMixin, FileExportMixin


export_mixin_inheritance_error_msg = _(
    "Class does not inherit from ExportMixin and FileExportMixin"
)


def validate_export_mixin_inheritance(classname: str) -> None:
    """Validate the given classname inherit from ExportMixin and FileExportMixin,
    raises ValidationError if not."""
    try:
        BaseClass = import_string(classname)
    except ImportError as error:
        raise ValidationError(error)
    if not issubclass(BaseClass, (ExportMixin, FileExportMixin)):
        raise ValidationError(export_mixin_inheritance_error_msg)
