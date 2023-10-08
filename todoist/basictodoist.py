import logging as log
import os
import typing as tp

import requests
from kivy.clock import Clock

from .interface import Todoist

if tp.TYPE_CHECKING:
    from .interface import Todos


class BasicTodoist(Todoist):
    def __init__(self, timeout: int = 3):
        self.todo_list: Todos = []
        self._subscribers: list[tp.Callable] = []
        self._clock = None
        self.timeout = timeout

    def run(self):
        self._clock = Clock.schedule_interval(self.update, 10)
        self.update()

    def stop(self):
        self._clock.cancel()

    def add_subscriber(self, subscriber: 'tp.Callable[[Todos], None]') -> None:
        self._subscribers.append(subscriber)

    def query_todo_list(self):
        try:
            data = requests.get(
                os.getenv('TODOIST_URL'),
                headers={'Authorization': f'Bearer {os.getenv("TODOIST_TOKEN")}'},
                timeout=self.timeout
            )
            new_todo_list = data.json()
        except requests.ConnectionError as e:
            log.critical('Chyba pripojeni!')
            new_todo_list = [] 
        except Exception as e:
            log.critical(e)
            new_todo_list = [] 
        if new_todo_list != self.todo_list:
            self.todo_list = sorted(new_todo_list, key=BasicTodoist.__get_date)
            return True
        else:
            return False

    def update(self, _: int = 0) -> None:
        if not self.query_todo_list():
            return

        for subscriber in self._subscribers:
            subscriber(self.todo_list)

    def close_task(self, task_id: str) -> bool:
        try:
            resp = requests.post(
                f'{os.getenv("TODOIST_URL")}/{task_id}/close',
                headers={'Authorization': f'Bearer {os.getenv("TODOIST_TOKEN")}'},
                timeout=self.timeout
            )
        except requests.ConnectionError as e:
            log.critical('Chyba pripojeni!')
            return False
        except Exception as e:
            log.critical(e)
            return False

        log.debug(f'Todoist resp: {resp.status_code}')
        return resp.status_code == 204

    # def heslo(self):
    #     for task in self.todo_list:
    #         if task['content'].lower() == 'heslo':
    #             return True
    #     else:
    #         return False

    @staticmethod
    def __get_date(task):
        try:
            return task['due']['date']
        except KeyError:
            return '' 

