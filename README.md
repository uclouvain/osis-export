# OSIS Export

`OSIS Export` is a Django application to manage asynchronous exports across OSIS plateform.


Requirements
===========

`OSIS Export` requires

- Django 2.2+
- Django REST Framework 3.12+
- Django Filters
- Celery 4+

# How to install ?

## Configuring Django

Add `osis_export` to `INSTALLED_APPS` :

```python
INSTALLED_APPS = (
    ...
    'osis_export',
    ...
)
```

## Specifying an asynchronous manager class

In order to decouple the asynchronous manager task, you must define the one you want to use like following.

### Create your interface

The manager must inherit from the interface `AsyncManager` define in `osis_export/contrib/async_manager.py` and implement all the methods :

```python
from osis_async.models import AsyncTask
from osis_async.models.enums import TaskStates
from osis_export.contrib.async_manager import AsyncManager


class AsyncTaskManager(AsyncManager):
    @staticmethod
    def get_pending_job_uuids():
        """"Must return the pending export job uuids"""
        pending_tasks = AsyncTask.objects.filter(
            state=TaskStates.PENDING.name
        ).values_list("uuid", flat=True)
        return pending_tasks
```

The example bellow uses the `osis_async` module.

### Add it to your settings

Add the full path to the asynchronous manager class in your settings :
```python
OSIS_EXPORT_ASYNCHRONOUS_MANAGER_CLS = 'backoffice.settings.osis_export.async_manager.AsyncTaskManager'
```

# Using OSIS Export

`osis_export` provides mixin views and a Django template tag to make it possible for the end user to generate exports by simply clicking on a button.

## Mixins

There is a mixin for each type of export you may want. Here is the list of export types, and their related mixins :
- Excel file : `ExcelFilterSetExportMixin`
- PDF file : `PDFFilterSetExportMixin` -> TODO

_Please see the related chapter about mixin specificities for details._

Simply add the selected mixin to the view you will be using to generate the exports and implement all the abstract methods:
```python
from osis_export.contrib.export_mixins import ExcelFilterSetExportMixin

class MyListView(ExcelFilterSetExportMixin, FilterView):
    # implement abstract methods, see related chapters below
```
+
Please note that any view using an export mixin __must__ inherit from `FilterView`.

### ExcelFilterSetExportMixin

In order to use this mixin, you must implement the following methods :
- `get_headers`: must return a list of all the headers.
- `get_row_data`: must return a list of all the row data.

example:
```python
class MyListView(ExcelFilterSetExportMixin, FilterView):
    def get_header(self):
        return [
            "name",
            "description",
            "place",
            "created at",
            "additional value",
        ]

    def get_row_data(self, row):
        return [
            row.name,
            row.description,
            str(row.place),
            row.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
            str(row.additional_value) if row.additional_value is not None else "",
        ]
```

You can change the representation of the data using `get_row_data`, like above with strftime on a date field or even with the place field calling its str representation.

Also, you may handle the representation of a `None` value by yourself, like it is done with the `additional_value`.

_Please note that all the returned values must be strings._

### PDFFilterSetExportMixin -> TODO

In order to use this mixin, you must implement the following methods :
- `get_data`: must return a list of all the data.

## Template tag

Load the export template tag at the beginning of your template and use it like this :
```html
{% load export %}
{% export_task file_type="EXCEL" name="test name" description="test description" %}
{% export_task file_type="PDF" name="test name" description="test description" ttl=42 an_optional_kwarg="i'm optional, use me if you want" %}
```

Required attributes are :
- file_type : the wanted export type ; choose between names in `osis_export.models.enums.types.ExportTypes`
- name : the name of the related asynchronous task that will be displayed to the end user.
- description : the description of the related asynchronous task that will be displayed to the end user.

Optional attributes are :
- ttl : the Time To Live of the related asynchronous task. Set to its default if not given.
- file_name : the name of the generated file. If not set, it will be something like : `export-{name}-{today}` where name if theme given in the tag and today is today's datetime.

You can also add more kwargs if you need it (`an_optional_kwarg` in the example bellow).
