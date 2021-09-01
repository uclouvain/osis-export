import uuid

from base.models.person import Person
from osis_export.contrib.async_manager import AsyncManager


class AsyncTaskManager(AsyncManager):
    @staticmethod
    def create(name: str, description: str, person: Person, time_to_live: int = None) -> uuid.UUID:
        pass

    @staticmethod
    def update(
        uuid,
        progression=None,
        description=None,
        state=None,
        started_at=None,
        completed_at=None
    ):
        pass

    @staticmethod
    def get_pending_job_uuids():
        return ["2043550d-839e-4acd-b67f-2fff4ab3faea"]
