import copy
import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings

from base.tests.factories.person import PersonFactory
from osis_export.models import Export


@override_settings(
    OSIS_EXPORT_ASYNCHRONOUS_MANAGER_CLS="osis_export.tests.export_test.async_manager.AsyncTaskManager",
)
class TestManager(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.async_task = {
            "person": PersonFactory(),
            "name": "An async task name",
            "description": "An async task description",
            "uuid": "2043550d-839e-4acd-b67f-2fff4ab3faea",
            "state": "PENDING",
            "created_at": datetime.datetime.now(),
        }
        Export.objects.create(
            job_uuid=cls.async_task.get("uuid"),
            person=cls.async_task.get("person"),
        )
        processing_async_task = copy.deepcopy(cls.async_task)
        processing_async_task["uuid"] = "09994869-7a16-4aa9-ae70-11ac9a32c1ea"
        processing_async_task["state"] = "PROCESSING"
        Export.objects.create(
            job_uuid=processing_async_task.get("uuid"),
            person=processing_async_task.get("person"),
        )

    @patch('osis_export.tests.export_test.async_manager.AsyncTaskManager.get_pending_job_uuids')
    def test_export_manager_not_generated_function_only_returns_pending_tasks(self, pending_job_uuids):
        pending_job_uuids.return_value = [
            "2043550d-839e-4acd-b67f-2fff4ab3faea",
            "87cb32fe-008f-4999-bd47-e7426e43006c",  # Not existing, or from another app
        ]
        self.assertEqual(Export.objects.count(), 2)
        self.assertEqual(Export.objects.not_generated().count(), 1)
        self.async_task["state"] = "DONE"
        pending_job_uuids.return_value = [
            "87cb32fe-008f-4999-bd47-e7426e43006c",  # Not existing, or from another app
        ]
        self.assertEqual(Export.objects.not_generated().count(), 0)
