import dataclasses as dc
import datetime as dt
import uuid
import typing as tp

from pydantic import BaseModel, ConfigDict, Field, model_validator



TODOIST_KEY = uuid.uuid4()


class Due(BaseModel):
    model_config = ConfigDict(extra="allow")

    string: str
    date: str
    is_recurring: bool
    datetime: tp.Optional[str] = None
    timezone: tp.Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _split_date_and_datetime(cls, data: tp.Any) -> tp.Any:
        if not isinstance(data, dict):
            return data
        raw = data.get("date")
        if isinstance(raw, str) and "T" in raw and "datetime" not in data:
            data = {**data, "date": raw.split("T", 1)[0], "datetime": raw}
        return data

    def __lt__(self, other: 'tp.Optional[Due]') -> bool:
        if other is None:
            return False
        return self.date < other.date


class Duration(BaseModel):
    model_config = ConfigDict(extra="allow")

    amount: str
    unit: str


class Task(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: str
    project_id: str
    section_id: tp.Optional[str] = None
    content: str
    description: str
    is_completed: bool = Field(alias="checked")
    labels: tp.List[str]
    parent_id: tp.Optional[str] = None
    order: int = Field(alias="child_order")
    priority: int
    due: tp.Optional[Due] = None
    url: tp.Optional[str] = None
    comment_count: int = Field(alias="note_count")
    created_at: str = Field(alias="added_at")
    creator_id: str = Field(alias="added_by_uid")
    assignee_id: tp.Optional[str] = Field(default=None, alias="responsible_uid")
    assigner_id: tp.Optional[str] = Field(default=None, alias="assigned_by_uid")
    duration: tp.Optional[Duration] = None


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
