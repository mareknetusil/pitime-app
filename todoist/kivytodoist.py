import os
import typing as tp

from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest

from .interface import Todoist

if tp.TYPE_CHECKING:
    from .interface import Todos


class KivyTodoist(Todoist):
    def __init__(self, timeout: int = 3):
        self.todo_list: Todos = []
        self._subscribers: list[tp.Callable] = []
        self._clock = None
        self.timeout = timeout

    def run(self) -> None:
        self._clock = Clock.schedule_interval(self.update, 10)
        self.update()

    def stop(self) -> None:
        if self._clock:
            self._clock.cancel()

    def add_subscriber(self, subscriber: 'tp.Callable[[Todos], None]') -> None:
        self._subscribers.append(subscriber)

    def update(self, _: int = 0) -> None:
        UrlRequest(
            url=os.getenv('TODOIST_URL'),
            req_headers={'Authorization': f'Bearer {os.getenv("TODOIST_TOKEN")}'},
            timeout=self.timeout,
            on_success=self._on_success,
            on_failure=self._on_error,
            on_error=self._on_error
        )

    def _on_success(self, req, resp) -> None:
        if resp == self.todo_list:
            return

        self.todo_list = sorted(resp, key=KivyTodoist.__get_date)
        for subscriber in self._subscribers:
            subscriber(self.todo_list)

    def _on_error(self, req, resp) -> None:
        pass
    
    def close_task(self, task_id: str) -> None:
        UrlRequest(
            url=f'{os.getenv("TODOIST_URL")}/{task_id}/close',
            req_headers={'Authorization': f'Bearer {os.getenv("TODOIST_TOKEN")}'},
            timeout=self.timeout
        )

    @staticmethod
    def __get_date(task: dict[str, tp.Any]) -> str:
        try:
            return task['due']['date']
        except KeyError:
            return '' 
