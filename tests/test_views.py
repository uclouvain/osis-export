from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook
from openpyxl.styles import Font

from base.tests.factories.person import PersonFactory
from osis_async.models import AsyncTask
from osis_async.models.enums import TaskStates
from osis_export.contrib.export_mixins import (
    ExcelFileExportMixin,
    ExportMixin,
    FileExportMixin,
)
from osis_export.models import Export
from osis_export.tests.export_test.models import DummyModel
from osis_export.tests.export_test.views import TestViewSearch


class TestAsyncExport(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.export_data = {
            "async_task_name": "test name",
            "async_task_description": "test description",
            "called_from_class": "osis_export.tests.export_test.views.TestViewSearch",
            "filters": "",
            "type": "EXCEL",
            "file_name": "file test name",
            "next": "/some-url",
        }
        cls.url = reverse("osis_export:export")

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    def test_async_export_view_returns_errors_message_if_no_data_given(self):
        # send a post with no data must raise an exception as their is required fields
        url = self.url
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNot(len(list(response.context["messages"])), 0)
        self.assertIn(
            "called_from_class",
            list(response.context["messages"])[0].message,
        )

    def test_async_export_view_must_redirect_to_next_parameter_if_valid(self):
        response = self.client.post(self.url, self.export_data)
        self.assertEqual(response.status_code, 302)
        # must redirect to the given 'next' parameter
        self.assertEqual(response.url, self.export_data["next"])

    def test_async_export_view_must_redirect_to_slash_if_valid_and_next_not_set(self):
        data = self.export_data.copy()
        del data["next"]
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        # must redirect to the given 'next' parameter
        self.assertEqual(response.url, "/")

    def test_async_export_view_must_redirect_to_next_parameter_if_invalid(self):
        response = self.client.post(self.url, {"next": self.export_data["next"]})
        self.assertEqual(response.status_code, 302)
        # must redirect to the given 'next' parameter
        self.assertEqual(response.url, self.export_data["next"])

    def test_async_export_view_must_redirect_to_slash_if_invalid_and_next_not_set(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 302)
        # must redirect to the given 'next' parameter
        self.assertEqual(response.url, "/")

    def test_async_export_view_set_default_ttl_if_not_given(self):
        self.assertEqual(Export.objects.count(), 0)
        self.assertEqual(AsyncTask.objects.count(), 0)

        response = self.client.post(self.url, self.export_data)
        self.assertEqual(response.status_code, 302)

        # Both Export and related AsyncTask must have been created
        self.assertEqual(Export.objects.count(), 1)
        self.assertEqual(AsyncTask.objects.count(), 1)

        # now test the values of the related async task
        async_task = AsyncTask.objects.get()
        self.assertEqual(async_task.name, self.export_data["async_task_name"])
        self.assertEqual(
            async_task.description, self.export_data["async_task_description"]
        )
        self.assertEqual(async_task.person, self.person)
        self.assertEqual(async_task.time_to_live, 5)
        self.assertEqual(async_task.state, TaskStates.PENDING.name)
        self.assertEqual(async_task.progression, 0)
        self.assertIsNotNone(async_task.created_at)
        self.assertIsNone(async_task.started_at)
        self.assertIsNone(async_task.completed_at)

        # now test the values of the related export
        export = Export.objects.get()
        self.assertEqual(
            export.called_from_class, self.export_data["called_from_class"]
        )
        self.assertEqual(export.filters, self.export_data["filters"])
        self.assertEqual(export.person, self.person)
        self.assertEqual(export.job_uuid, async_task.uuid)
        self.assertEqual(export.file, [])
        self.assertEqual(export.file_name, self.export_data["file_name"])
        self.assertEqual(export.type, self.export_data["type"])
        self.assertIsNotNone(export.created_at)

    def test_async_export_view_with_ttl(self):
        self.assertEqual(Export.objects.count(), 0)
        self.assertEqual(AsyncTask.objects.count(), 0)

        data = {**self.export_data, "async_task_ttl": 42}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        # Both Export and related AsyncTask must have been created
        self.assertEqual(Export.objects.count(), 1)
        self.assertEqual(AsyncTask.objects.count(), 1)

        # and the value of the async task ttl should be set
        async_task = AsyncTask.objects.get()
        self.assertEqual(async_task.time_to_live, 42)


class TestFileExportMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        class MyClass(FileExportMixin):
            pass

        cls.my_instance = MyClass()
        cls.MyClass = MyClass

    def test_file_export_mixin_must_specify_mimetype(self):
        with self.assertRaises(ImproperlyConfigured):
            self.my_instance.get_mimetype()

        self.MyClass.mimetype = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.assertEqual(self.my_instance.get_mimetype(), self.MyClass.mimetype)

    def test_file_export_mixin_must_specify_file_extension(self):
        with self.assertRaises(ImproperlyConfigured):
            self.my_instance.get_file_extension()

        self.MyClass.file_extension = ".xlsx"
        self.assertEqual(
            self.my_instance.get_file_extension(),
            self.MyClass.file_extension,
        )


class TestExcelFileExportMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        class MyExportableObject:
            test_param = "test"
            test_param_2 = None
            test_param_3 = "This value should not appear on Excel export"
            test_param_4 = "Some value"

        cls.my_object = MyExportableObject()

        class MyClass(ExportMixin, ExcelFileExportMixin):
            def get_export_objects(self, **kwargs):
                return [MyExportableObject() for _ in range(10)]

            def get_header(self):
                return ["test param", "test param 2", "test param 4"]

            def get_data(self):
                return ["test_param", "test_param_2", "test_param_4"]

        cls.my_class_instance = MyClass()

    def test_get_attr_returns_expected_data(self):
        my_attr = ExcelFileExportMixin.get_attr(self.my_object, "test_param")
        self.assertEqual(my_attr, self.my_object.test_param)
        my_attr = ExcelFileExportMixin.get_attr(self.my_object, "test_param_2")
        self.assertEqual(my_attr, "")

    def test_generate_file_creates_excel_file(self):
        file = self.my_class_instance.generate_file()
        self.assertEqual(type(file), bytes)
        workbook = load_workbook(ContentFile(file))
        worksheet = workbook.active
        # check if the first row is in bold style
        cells = worksheet.iter_rows("A1:C1")
        # check that we have 11 rows : 1 for the header and 10 for data
        self.assertEqual(worksheet.get_highest_row(), 11)
        for col in cells:
            for cell in col:
                self.assertEqual(cell.font, Font(bold=True))
        # check if the workbook contains the correct values
        cells = worksheet.iter_rows("A2")
        for col in cells:
            for cell in col:
                self.assertEqual(cell.value, self.my_object.test_param)
        cells = worksheet.iter_rows("B2")
        for col in cells:
            for cell in col:
                self.assertEqual(cell.value, self.my_object.test_param_2)
        cells = worksheet.iter_rows("C2")
        for col in cells:
            for cell in col:
                self.assertEqual(cell.value, self.my_object.test_param_4)


class TestFilterSetExportMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dummy_objects_count = 10
        for cpt in range(cls.dummy_objects_count):
            DummyModel.objects.create(name=f"dummy-name-{cpt}", selectable_value="A")

        cls.my_class_instance = TestViewSearch()

    def test_return_all_objects_if_no_filters_specified(self):
        qs = self.my_class_instance.get_queryset_export("")
        self.assertEqual(qs.count(), self.dummy_objects_count)
        qs = self.my_class_instance.get_export_objects(filters="")
        self.assertEqual(qs.count(), self.dummy_objects_count)

    def test_return_filtered_queryset(self):
        qs = self.my_class_instance.get_queryset_export("name=dummy-name-2")
        self.assertEqual(qs.count(), 1)
        qs = self.my_class_instance.get_export_objects(filters="name=dummy-name-2")
        self.assertEqual(qs.count(), 1)

    def test_raises_validation_error_if_filterset_is_not_valid(self):
        with self.assertRaises(ValidationError):
            self.my_class_instance.get_queryset_export("selectable_value=Z")
