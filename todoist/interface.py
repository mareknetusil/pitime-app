import dataclasses as dc
import datetime as dt
import uuid
import typing as tp

from pydantic import BaseModel



TODOIST_KEY = uuid.uuid4()


class Due(BaseModel):
    string: str
    date: str
    is_recurring: bool
    datetime: str | None = None
    timezone: str | None = None


class Duration(BaseModel):
    amount: str
    unit: str


class Task(BaseModel):
    id: str
    project_id: str
    section_id: str | None = None
    content: str
    description: str
    is_completed: bool
    labels: tp.List[str]
    parent_id: str | None = None
    order: int
    priority: int
    due: Due | None = None
    url: str
    comment_count: int
    created_at: str
    creator_id: str
    assignee_id: str | None = None
    assigner_id: str | None = None
    duration: Duration | None = None


Todos = tp.List[Task]


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
