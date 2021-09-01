import uuid

import factory

from base.tests.factories.person import PersonFactory
from osis_export.models import Export


class ExportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Export

    person = factory.SubFactory(PersonFactory)
    called_from_class = "osis_export.tests.export_test.views.TestViewSearch"
    job_uuid = factory.LazyFunction(uuid.uuid4)
