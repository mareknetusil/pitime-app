import dataclasses as dc
import uuid
import typing as tp


Todos = tp.List[tp.Dict[str, tp.Any]]


TODOIST_KEY = uuid.uuid4()


class Todoist:
    def run(self) -> None:
        """
        Starts fetching data from the Todoist app.
        """
        raise NotImplementedError

    def stop(self) -> None:
        """
        Stops fetching data from the Todoist app.
        """
        raise NotImplementedError

    def add_subscriber(self, subscriber: 'tp.Callable[[Todos], None]') -> None:
        """
        Adds a subscriber to the list of subscribers.
        """
        raise NotImplementedError

    def close_task(self, task_id: str) -> None:
        """
        Closes a task with the given id.
        """
        raise NotImplementedError
