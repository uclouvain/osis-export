from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.edit import BaseFormView
from django.utils.translation import gettext as _

from osis_async.models import AsyncTask
from osis_export.api.forms import ExportForm


class AsyncExport(BaseFormView):
    """The base class that represents an asynchronous export."""

    form_class = ExportForm

    def form_invalid(self, form):
        messages.error(
            self.request,
            "{message} : {errors}".format(
                message=_(
                    "The requested export is not valid, please contact the site "
                    "administrator "
                ),
                errors=form.errors,
            ),
            extra_tags="safe",
        )
        # redirect to the initial page
        return HttpResponseRedirect(self.request.POST.get("next", "/"))

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        person = self.request.user.person

        async_task_kwargs = {
            "name": cleaned_data.get("async_task_name"),
            "description": cleaned_data.get("async_task_description"),
            "person": person,
        }
        async_task_ttl = cleaned_data.get("async_task_ttl", None)
        if async_task_ttl is not None:
            async_task_kwargs["time_to_live"] = async_task_ttl
        async_task = AsyncTask.objects.create(**async_task_kwargs)

        export = form.save(commit=False)
        export.job_uuid = async_task.uuid
        export.person = person
        export.type = cleaned_data.get("type")
        export.file_name = cleaned_data.get("file_name")
        export.save()

        # redirect to the initial page
        return HttpResponseRedirect(self.request.POST.get("next", "/"))
