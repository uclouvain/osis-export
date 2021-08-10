from django.core.management import call_command
from django.test import TestCase

from base.tests.factories.person import PersonFactory
from osis_async.models.enums import TaskStates
from osis_async.tests.factory import AsyncTaskFactory
from osis_export.models import Export
from osis_export.tests.export_test.models import DummyModel
from osis_export.tests.factory import ExportFactory


class TestGenerateExportFile(TestCase):
    @classmethod
    def setUpTestData(cls):
        for _ in range(42):
            DummyModel.objects.create()
        cls.person = PersonFactory()
        cls.export = ExportFactory()
        cls.export_2 = ExportFactory()
        async_task = AsyncTaskFactory(state=TaskStates.DONE.name)
        cls.export_3 = ExportFactory(job_uuid=async_task.uuid)

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    def test_generate_export_file_changes_related_async_state(self):
        self.assertEqual(Export.objects.all().count(), 3)
        self.assertEqual(Export.objects.not_generated().count(), 2)
        call_command("generate_export_file")
        self.assertEqual(Export.objects.not_generated().count(), 0)

    def test_generate_export_file_creates_files(self):
        self.assertEqual(len(self.export.file), 0)
        self.assertEqual(len(self.export_2.file), 0)
        call_command("generate_export_file")
        self.export.refresh_from_db()
        self.export_2.refresh_from_db()
        self.assertEqual(len(self.export.file), 1)
        self.assertEqual(len(self.export_2.file), 1)
