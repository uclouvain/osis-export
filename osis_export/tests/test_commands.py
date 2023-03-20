import uuid
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from base.tests.factories.person import PersonFactory
from osis_export.models import Export
from osis_export.tests.export_test.models import DummyModel
from osis_export.tests.factory import ExportFactory


@override_settings(
    OSIS_EXPORT_ASYNCHRONOUS_MANAGER_CLS="osis_export.tests.export_test.async_manager.AsyncTaskManager",
)
class TestGenerateExportFile(TestCase):
    @classmethod
    def setUpTestData(cls):
        for _ in range(42):
            DummyModel.objects.create()
        cls.person = PersonFactory()
        cls.export = ExportFactory()
        cls.export_2 = ExportFactory()
        cls.export_3 = ExportFactory()

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

        # Mock documents
        patcher = patch("osis_document.api.utils.get_remote_token", return_value="foobar")
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch("osis_document.api.utils.get_remote_metadata", return_value={"name": "myfile"})
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            "osis_document.api.utils.confirm_remote_upload",
            side_effect=lambda token, upload_to: uuid.uuid4(),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    @patch('osis_export.tests.export_test.async_manager.AsyncTaskManager.get_pending_job_uuids')
    def test_generate_export_file_changes_related_async_state(self, pending_job_uuids):
        pending_job_uuids.return_value = [
            self.export.job_uuid,
            self.export_3.job_uuid,
        ]
        self.assertEqual(Export.objects.all().count(), 3)
        self.assertEqual(Export.objects.not_generated().count(), 2)
        call_command("generate_export_file")
        pending_job_uuids.return_value = []
        self.assertEqual(Export.objects.not_generated().count(), 0)

    @patch('osis_export.tests.export_test.async_manager.AsyncTaskManager.get_pending_job_uuids')
    def test_generate_export_file_creates_files(self, pending_job_uuids):
        pending_job_uuids.return_value = [
            self.export.job_uuid,
            self.export_2.job_uuid,
        ]
        self.assertEqual(len(self.export.file), 0)
        self.assertEqual(len(self.export_2.file), 0)
        call_command("generate_export_file")
        self.export.refresh_from_db()
        self.export_2.refresh_from_db()
        self.assertEqual(len(self.export.file), 1)
        self.assertEqual(len(self.export_2.file), 1)

    @patch('osis_export.tests.export_test.async_manager.AsyncTaskManager.get_pending_job_uuids')
    @patch('osis_export.tests.export_test.async_manager.AsyncTaskManager.update')
    @patch('osis_export.tests.export_test.views.TestViewSearch.generate_file')
    def test_generate_export_logs_error(self, generate_file, update, pending_job_uuids):
        pending_job_uuids.return_value = [
            self.export.job_uuid,
        ]
        generate_file.side_effect = Exception("Something went wrong")

        with self.assertRaises(Exception):
            call_command("generate_export_file")
        update.assert_called_with(self.export.job_uuid, progression=0, state='ERROR')
