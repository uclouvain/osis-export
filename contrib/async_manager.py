import abc


class AsyncManager(abc.ABC):
    @staticmethod
    def get_pending_job_uuids():
        """Must return the pending export job uuids"""
        raise NotImplementedError
