from django.core.exceptions import ValidationError
from django.test import TestCase

from base.tests.factories.person import PersonFactory
from osis_export.models import Export


class TestValidators(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.export_data = {
            "called_from_class": "ThisClassDoesNotExists",
            "type": "EXCEL",
            "file_name": "file test name",
        }

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    def test_called_from_class_validation_raises_an_error_if_not_an_actual_class(self):
        export = Export(**self.export_data)

        with self.assertRaises(ValidationError):
            export.full_clean()

    def test_called_from_class_validation_raises_error_if_is_not_subclass_of_export_mixins(
        self,
    ):
        self.export_data[
            "called_from_class"
        ] = "osis_export.tests.test_validators.TestValidators"
        export = Export(**self.export_data)

        with self.assertRaises(ValidationError):
            export.full_clean()

    def test_called_from_class_must_be_a_subclass_of_export_mixins(self):
        export_data = {
            "called_from_class": "osis_export.tests.export_test.views.TestViewSearch",
            "filters": "",
            "type": "EXCEL",
            "file_name": "file test name",
            "person": self.person,
            "job_uuid": "6f9b2933-5889-4638-bc03-5b42fe26dbed",
        }
        export = Export(**export_data)
        export.full_clean()
