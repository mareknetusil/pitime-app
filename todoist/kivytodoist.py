import os
import typing as tp

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest

from .interface import Todoist

if tp.TYPE_CHECKING:
    from .interface import Todos


class KivyTodoist(Todoist):
    def __init__(self, timeout: int = 3, period: int = 10):
        self.todo_list: Todos = []
        self._subscribers: list[tp.Callable] = []
        self._clock = None
        self.timeout = timeout
        self.period = period

    def run(self) -> None:
        Logger.info('STARTING REGULAR TODOIST CHECKS ...')
        Logger.info(f'CHECKING EVERY {self.period} seconds.')
        self._clock = Clock.schedule_interval(self.update, self.period)
        self.update()

    def stop(self) -> None:
        Logger.info('STOPPING REGULAR TODOIST CHECKS')
        if self._clock:
            self._clock.cancel()

    def add_subscriber(self, subscriber: 'tp.Callable[[Todos], None]') -> None:
        self._subscribers.append(subscriber)

    def update(self, _: int = 0) -> None:
        Logger.debug('CHECKING FOR TODOS ...')
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
            Logger.debug('NO CHANGE IN TODOS.')
            return

        Logger.info('CHANGE IN TODOS.')
        self.todo_list = sorted(resp, key=KivyTodoist.__get_date)
        for subscriber in self._subscribers:
            subscriber(self.todo_list)

    def _on_error(self, req, resp) -> None:
        Logger.error('REQUEST TO TODOIST FAILED!')
        Logger.error(resp)
    
    def close_task(self, task_id: str) -> None:
        Logger.info(f'CLOSING A TASK: {task_id}')
        UrlRequest(
            url=f'{os.getenv("TODOIST_URL")}/{task_id}/close',
            req_headers={'Authorization': f'Bearer {os.getenv("TODOIST_TOKEN")}'},
            req_body=b'',
            timeout=self.timeout,
            on_success=lambda _req, _resp: self.update(),
            on_failure=self._on_error,
            on_error=self._on_error
        )

    @staticmethod
    def __get_date(task: tp.Dict[str, tp.Any]) -> str:
        try:
            return task['due']['date']
        except KeyError:
            return '' 

