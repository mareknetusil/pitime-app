import dataclasses as dc
import datetime as dt
import typing as tp

from kivy.clock import Clock
from kivy.logger import Logger

from .interface import Todoist, Todos, Task, Due


class Birthdays(Todoist):
    def __init__(self, filename: str, period: int = 10):
        self._subscribers: tp.List[tp.Callable] = []
        self._filename = filename
        self._period = period
        self._clock = None

    def run(self) -> None:
        Logger.info('STARTING REGULAR BIRTHDAYS CHECKS ...')
        Logger.info(f'CHECKING EVERY {self._period} seconds.')
        self._clock = Clock.schedule_interval(self.update, self._period)
        self.update()

    def stop(self) -> None:
        Logger.info('STOPPING REGULAR BIRTHDAYS CHECKS')
        if self._clock:
            self._clock.cancel()

    def add_subscriber(self, subscriber: 'tp.Callable[[Todos], None]') -> None:
        self._subscribers.append(subscriber)

    def close_task(self, task_id: str) -> None:
        pass

    def update(self, _: int = 0) -> None:
        for subscriber in self._subscribers:
            subscriber(self._load_birthdays())

    def _load_birthdays(self) -> Todos:
        with open(self._filename) as f:
            bdays = [
                Birthday.from_string(line).to_task(idx)
                for idx, line in enumerate(f.readlines())
            ]
        Logger.info(f'BIRTHDAYS LOADED: {len(bdays)}.')        
        return bdays


@dc.dataclass
class Birthday:
    name: str
    date: dt.date

    @classmethod
    def from_string(cls, s: str) -> 'Birthday':
        name, date = s.split(' - ')
        date = dt.datetime.strptime(date.strip(), '%d.%m.').replace(year=dt.datetime.now().year)
        if date < dt.datetime.now():
            date = date.replace(year=dt.datetime.now().year + 1)
        return cls(name, date)
    
    def to_task(self, idx: int) -> Task:
        if self.date.year == dt.datetime.now().year:
            s = self.date.strftime('%d %b')
        else:
            s = self.date.strftime('%d %b %Y')

        return Task(
            id=f'bday_{idx}',
            project_id= 'bday',
            content=f'narozeniny {self.name}',
            description='',
            is_completed=False,
            labels=[],
            order=idx,
            priority=1,
            due=Due(
                string=self.date.strftime('%d %b %Y'),
                date=self.date.strftime('%Y-%m-%d'),
                is_recurring=False),
            url='',
            comment_count=0,
            created_at='',
            creator_id='',
            assignee_id=None,
            assigner_id=None,
            duration=None
        )
