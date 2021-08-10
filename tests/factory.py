import factory

from base.tests.factories.person import PersonFactory
from osis_async.tests.factory import AsyncTaskFactory
from osis_export.models import Export


class ExportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Export

    person = factory.SubFactory(PersonFactory)
    called_from_class = "osis_export.tests.export_test.views.TestViewSearch"

    @factory.lazy_attribute
    def job_uuid(self):
        return AsyncTaskFactory().uuid
