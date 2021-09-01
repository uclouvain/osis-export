import abc
import datetime
import uuid
from uuid import UUID

from base.models.person import Person


class AsyncManager(abc.ABC):
    @staticmethod
    def get_pending_job_uuids() -> [UUID]:
        """Must return the pending export job uuids"""
        raise NotImplementedError

    @staticmethod
    def update(
        uuid: UUID,
        progression: int = None,
        description: str = None,
        state: str = None,
        started_at: datetime.datetime = None,
        completed_at: datetime.datetime = None,
    ) -> None:
        """Update the async task with the given uuid with all the given parameters."""
        raise NotImplementedError

    @staticmethod
    def create(name: str, description: str, person: Person, time_to_live: int = None) -> uuid.UUID:
        """Create the async task with all the given parameters, must return an uuid."""
        raise NotImplementedError
