import dataclasses as dc
import typing as tp


Todos = list[dict[str, tp.Any]]


class Todoist:
    def run(self):
        """
        Starts fetching data from the Todoist app.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops fetching data from the Todoist app.
        """
        raise NotImplementedError

    def add_subscriber(self, subscriber: 'tp.Callable[[Todos], None]') -> None:
        """
        Adds a subscriber to the list of subscribers.
        """
        raise NotImplementedError
