import datetime as dt
import typing as tp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from .clock import ClockWidget
from .weather import WeatherWidget

from todoist import TODOIST_KEY
from weather.interface import WEATHER_KEY
from globals import get_global

if tp.TYPE_CHECKING:
    from todoist import Todos

TASKS_TEXT_TEMPLATE = 'V nejbližších dnech čeká úkolů: {}'


class MainScreenWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        todoist = get_global(TODOIST_KEY)
        todoist.add_subscriber(self.update_tasks)
        self.orientation = 'vertical'
        self.tasks = Label(text='', size_hint=(1, 0.3))
        self.clock = ClockWidget(size_hint=(1, 0.3))
        self.weather = WeatherWidget(get_global(WEATHER_KEY), size_hint=(1, 0.3))
        self.add_widget(self.tasks)
        self.add_widget(self.clock)
        self.add_widget(self.weather)

    def update_tasks(self, tasks: 'Todos'):
        today = dt.date.today()
        bound = today + dt.timedelta(days=3)
        due_dates = [task.due.date for task in tasks if task.due]
        print(due_dates)
        due_dates = [
            dt.datetime.strptime(task.due.date, '%Y-%m-%d').date()
            for task in tasks if task.due
        ]
        today_tasks = sum(
            1 for due_date in due_dates
            if due_date <= bound
        )
        self.tasks.text = TASKS_TEXT_TEMPLATE.format(today_tasks) if today_tasks else ''
