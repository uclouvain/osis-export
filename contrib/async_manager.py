import abc


class AsyncManager(abc.ABC):
    def get_pending_tasks(self):
        raise NotImplementedError
