from django.template.defaulttags import register
from django.utils.datetime_safe import datetime
from django.utils.text import slugify
from django.utils.translation import gettext as _

from osis_export.api.forms import ExportForm
from osis_export.models.enums.types import ExportTypes


@register.inclusion_tag("osis_export/export.html", takes_context=True)
def export_task(
    context, file_type, name, description, ttl=None, file_name=None, **kwargs
):
    if file_type not in ExportTypes.get_names():
        raise ValueError("type must be in the ExportTypes values")

    context_view = context["view"]
    called_from_class = f"{context_view.__module__}.{context_view.__class__.__name__}"

    if file_name is None:
        today = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_name = f"export-{name}-{today}"

    return {
        "export_button_text": _(f"Export in {ExportTypes.get_value(file_type)} file"),
        "form": ExportForm(
            initial={
                "async_task_name": name,
                "async_task_description": description,
                "async_task_ttl": ttl,
                "called_from_class": called_from_class,
                "filters": context.request.GET.urlencode(),
                # 'next' is used to redirect to the same exact result page after export
                "next": context.request.get_full_path(),
                "type": file_type,
                "file_name": slugify(file_name),
            }
        ),
    }
