import typing as tp

from kivy.logger import Logger

from .interface import Todoist, Todos



class ComposeTodoist:
    def __init__(self, *todoists: Todoist):
        self.todoists = todoists
        self._cache: tp.List[Todos] = [None] * len(todoists)
        self._subscribers: tp.List[tp.Callable] = []

        for idx, todoist in enumerate(self.todoists):
            todoist.add_subscriber(lambda t, idx=idx: self._notify_subscribers(t, idx))

    def run(self) -> None:
        for todoist in self.todoists:
            todoist.run()

    def stop(self) -> None:
        for todoist in self.todoists:
            todoist.stop()

    def add_subscriber(self, subscriber: 'tp.Callable[[Todos], None]') -> None:
        self._subscribers.append(subscriber)

    def close_task(self, task_id: str) -> None:
        for todoist in self.todoists:
            todoist.close_task(task_id)


    def _notify_subscribers(self, todos: Todos, idx: int) -> None:
        Logger.info(f'NOTIFYING SUBSCRIBERS FOR TODOIST {idx}')
        self._cache[idx] = todos
        todos = self._merge_todos()
        for subscriber in self._subscribers:
            subscriber(todos)

    def _merge_todos(self) -> Todos:
        todos = sum(filter(None, self._cache), [])
        todos.sort(key=lambda t: (t.priority, t.due))
        return todos
