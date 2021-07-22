from django.template.defaulttags import register
from django.utils.datetime_safe import datetime
from django.utils.text import slugify
from django.utils.translation import gettext as _

from osis_export.api.forms import ExportForm
from osis_export.models.enums.types import ExportTypes


@register.inclusion_tag("osis_export/export.html", takes_context=True)
def excel_export_task(
    context,
    async_task_name,
    async_task_description,
    async_task_ttl=None,
    file_name=None,
):
    context_view = context['view']
    called_from_class = f"{context_view.__module__}.{context_view.__class__.__name__}"

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
                "called_from_class": called_from_class,
                "filters": context.request.GET,
                # 'next' is used to redirect to the same exact result page after export
                "next": context.request.get_full_path(),
                "type": ExportTypes.EXCEL.name,
                "file_name": file_name,
            }
        ),
    }
