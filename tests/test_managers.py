from django.test import TestCase

from osis_async.models.enums import TaskStates
from osis_async.tests.factory import AsyncTaskFactory
from osis_export.models import Export


class TestManager(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.async_task = AsyncTaskFactory()
        Export.objects.create(
            job_uuid=cls.async_task.uuid, person=cls.async_task.person
        )
        async_task = AsyncTaskFactory(state=TaskStates.PROCESSING.name)
        Export.objects.create(
            job_uuid=async_task.uuid,
            person=async_task.person,
        )

    def test_export_manager_not_generated_function_only_returns_pending_tasks(self):
        self.assertEqual(Export.objects.count(), 2)
        self.assertEqual(Export.objects.not_generated().count(), 1)
        self.async_task.state = TaskStates.DONE.name
        self.async_task.save()
        self.assertEqual(Export.objects.not_generated().count(), 0)
