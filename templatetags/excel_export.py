from django.template.defaulttags import register

from osis_export.api.forms import ExcelForm


@register.inclusion_tag("osis_export/excel.html", takes_context=True)
def excel_export_task(
    context,
    object_list,
    async_task_name,
    async_task_description,
    async_task_ttl=None,
):
    if hasattr(object_list, "object_list"):
        object_list = object_list.object_list.first()

    app_label = object_list._meta.app_label
    model_name = object_list.__class__.__name__
    # Then to instantiate the model from it's app just do :
    # ClassName = apps.get_model(app_label, model_name)

    return {
        "form": ExcelForm(
            initial={
                "async_task_name": async_task_name,
                "async_task_description": async_task_description,
                "async_task_ttl": async_task_ttl,
                "app_label": app_label,
                "model_name": model_name,
                "filters": context.request.GET,
                # 'next' is used to redirect to the same exact result page after export
                "next": context.request.get_full_path(),
            }
        ),
    }
