from django.utils.module_loading import import_string

from osis_export.contrib.export_mixins import ExportMixin, FileExportMixin


def validate_export_mixin_inheritance(classname):
    BaseClass = import_string(classname)
    return issubclass(BaseClass, (ExportMixin, FileExportMixin))
