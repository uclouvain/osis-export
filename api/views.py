from django.http import HttpResponseRedirect
from django.views.generic.edit import BaseFormView

from osis_async.models import AsyncTask
from osis_export.api.forms import ExportForm


class AsyncExport(BaseFormView):
    """The base class that represents an asynchronous export."""
    form_class = ExportForm

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        person = self.request.user.person

        async_task = AsyncTask.objects.create(
            name=cleaned_data.get("async_task_name"),
            description=cleaned_data.get("async_task_description"),
            time_to_live=(
                cleaned_data.get("async_task_ttl")
                or AsyncTask._meta.get_field("time_to_live").get_default()
            ),
            person=person,
        )

        export = form.save(commit=False)
        export.async_task = async_task
        export.person = person
        export.type = cleaned_data.get("type")
        export.file_name = cleaned_data.get("file_name")
        export.save()
        # redirect to the initial page
        return HttpResponseRedirect(self.request.POST.get("next", "/"))
