from unittest import mock

from django.template import Context, Template
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.datetime_safe import datetime

import osis_export.tests.export_test.views
from base.tests.factories.user import UserFactory


@override_settings(ROOT_URLCONF="osis_export.tests.export_test.urls")
class TestTemplateTags(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.context = Context(
            {"view": osis_export.tests.export_test.views.TestViewSearch()}
        )
        cls.context.request = RequestFactory().get(reverse("export-test-list"))

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_export_template_is_rendered_with_hidden_form_fields(self):
        template_to_render = Template(
            "{% load export %}"
            "{% export_task file_type='EXCEL' name='test name' description='test description' %}"
        )
        with mock.patch(
            "django.utils.datetime_safe.datetime.now",
            return_value=datetime(2021, 7, 27, 13, 48, 42),
        ):
            rendered_template = template_to_render.render(self.context)
        self.assertInHTML(
            "<input type='hidden' name='called_from_class' value='osis_export.tests.export_test.views.TestViewSearch' id='id_called_from_class'>",
            rendered_template,
        )
        self.assertInHTML(
            "<input type='hidden' name='filters' id='id_filters'>",
            rendered_template,
        )
        self.assertInHTML(
            "<input type='hidden' name='type' value='EXCEL' id='id_type'>",
            rendered_template,
        )
        self.assertInHTML(
            "<input type='hidden' name='file_name' value='export-test-name-2021-07-27-13-48-42' id='id_file_name'>",
            rendered_template,
        )
        self.assertInHTML(
            "<input type='hidden' name='async_task_name' value='test name' id='id_async_task_name'>",
            rendered_template,
        )
        self.assertInHTML(
            "<input type='hidden' name='async_task_description' value='test description' id='id_async_task_description'>",
            rendered_template,
        )
        self.assertInHTML(
            "<input type='hidden' name='async_task_ttl' id='id_async_task_ttl'>",
            rendered_template,
        )
        self.assertInHTML(
            "<input type='hidden' name='next' value='/' id='id_next'>",
            rendered_template,
        )
        self.assertInHTML(
            "<button type='submit' class='btn btn-default'>Export in Excel file</button>",
            rendered_template,
        )

    def test_export_task_tag_raises_error_if_type_not_in_export_types(self):
        template_to_render = Template(
            "{% load export %}"
            "{% export_task file_type='JPG' name='test name' description='test description' %}"
        )
        with self.assertRaises(
            ValueError, msg="type must be in the ExportTypes values"
        ):
            template_to_render.render(self.context)

    def test_export_task_tag_with_file_name(self):
        template_to_render = Template(
            "{% load export %}"
            "{% export_task file_type='PDF' name='test name' description='test description' file_name='this file name must be slugged #é&(-èààç' %}"
        )
        rendered_template = template_to_render.render(self.context)
        # file_name must be 'slugged'
        self.assertInHTML(
            "<input type='hidden' name='file_name' value='this-file-name-must-be-slugged-e-eaac' id='id_file_name'>",
            rendered_template,
        )
