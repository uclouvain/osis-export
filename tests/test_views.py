from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory
from osis_async.models import AsyncTask
from osis_async.models.enums import TaskStates
from osis_export.models import Export


class TestViews(TestCase):
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
