import datetime as dt
import typing as tp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup

from todoist import TODOIST_KEY
from globals import get_global

if tp.TYPE_CHECKING:
    from todoist import Todoist, Todos, Task, Due


class TasksWidget(BoxLayout):
    pass


class TasksListWidget(RelativeLayout):
    TASK_HEIGHT = 40

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.todoist: 'Todoist' = get_global(TODOIST_KEY)
        if not self.todoist:
            raise ValueError('Todoist not initialized')
        self.todoist.add_subscriber(self.update_tasks)
        self.todoist.run()

    def update_tasks(self, tasks: 'Todos'):
        self.clear_content()
        for i, task in enumerate(tasks):
            widget = TaskWidget(
                task=task,
                pos=(0, self.height - (i + 1)*self.TASK_HEIGHT),
                size=(self.width, self.TASK_HEIGHT),
                size_hint=(None, None)
            )
            widget.bind(on_close_task=self.on_close_task)
            self.add_widget(widget)

    def clear_content(self):
        self.clear_widgets()

    def on_close_task(self, instance, value):
        self.todoist.close_task(value)


class TaskWidget(BoxLayout):
    task_text = StringProperty('')

    task_id: str

    def __init__(self, task, **kwargs):
        super().__init__(**kwargs)
        self.set_task(task)
        self.register_event_type('on_close_task')

    def set_task(self, task: 'Task'):
        task_text = task.content
        self.task_text = task_text if len(task_text) <= 55 else task_text[:55] + '...'
        self.task_id = task.id
        self.priority.text = str(task.priority)
        self.due.set_due(task.due)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        content = TaskPopup(self.task_text)
        popup = Popup(
            title='Přeješ si dokončit úkol?',
            content=content,
            size_hint=(None, None),
            size=(300, 200)
        )
        content.bind(on_answer=lambda i, v: self.popup_answer(v, popup))
        popup.open()
        return True

    def popup_answer(self, close: bool, popup: 'Popup'):
        popup.dismiss()
        if close:
            self.dispatch('on_close_task', self.task_id)

    def on_close_task(self, *args):
        pass


class TaskPopup(BoxLayout):
    COUNT = 0
    task_text = StringProperty('')

    def __init__(self, task: str, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_answer')
        self.task_text = task

    def on_answer(self, *args):
        pass


class PriorityWidget(RelativeLayout):
    text = StringProperty('0')


class DateWidget(Label):
    bg_color = ObjectProperty((0, 0, 0))

    def set_due(self, due: 'Due'):
        if due.date:
            date = dt.datetime.fromisoformat(due.date).date()
            day_diff = (date - dt.date.today()).days
            max_light = 0x88 / 256
            bg_shade = min(7, max(0, day_diff)) / 7 * max_light
            self.bg_color = (bg_shade, bg_shade, bg_shade)
        self.text = due.string
