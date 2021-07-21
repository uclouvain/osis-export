from django.template.defaulttags import register
from django.utils.datetime_safe import datetime
from django.utils.text import slugify
from django.utils.translation import gettext as _

from osis_export.api.forms import ExportForm
from osis_export.models.enums.types import ExportTypes


@register.inclusion_tag("osis_export/export.html", takes_context=True)
def excel_export_task(
    context,
    object_list,
    async_task_name,
    async_task_description,
    async_task_ttl=None,
    file_name=None,
):
    if hasattr(object_list, "object_list"):
        object_list = object_list.object_list.first()

    app_label = object_list._meta.app_label
    model_name = object_list.__class__.__name__
    # Then to instantiate the model from it's app just do :
    # ClassName = apps.get_model(app_label, model_name)

    if file_name is None:
        today = datetime.today().date().isoformat()
        file_name = slugify(f"export-{async_task_name}-{today}")

    return {
        "export_button_text": _("Export in Excel file"),
        "form": ExportForm(
            initial={
                "async_task_name": async_task_name,
                "async_task_description": async_task_description,
                "async_task_ttl": async_task_ttl,
                "app_label": app_label,
                "model_name": model_name,
                "filters": context.request.GET,
                # 'next' is used to redirect to the same exact result page after export
                "next": context.request.get_full_path(),
                "type": ExportTypes.EXCEL.name,
                "file_name": file_name,
            }
        ),
    }
