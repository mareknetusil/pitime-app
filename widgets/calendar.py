import calendar
import dataclasses as dc
import datetime as dt
import typing as tp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle, Line

from todoist import TODOIST_KEY
from globals import get_global


# @dc.dataclass
# class CircleSettings:
#     center_x: float
#     center_y: float
#     radius: float

#     @classmethod
#     def from_widget(cls, widget, radius_factor=0.9):
#         return cls(
#             center_x=widget.center_x,
#             center_y=widget.center_y,
#             radius=min(widget.width, widget.height) * radius_factor / 2
#         )

#     def to_tuple(self) -> tp.Tuple[float, float, float]:
#         return self.center_x, self.center_y, self.radius

def circle_settings_from_widget(widget, radius_factor=1.):
    return (
        widget.center_x,
        widget.center_y,
        min(widget.width, widget.height) * radius_factor / 2
    )


class CalendarWidget(BoxLayout):
    day_num = ObjectProperty(None)
    day_of_week = ObjectProperty(None)
    month = ObjectProperty(None)
    month_cal = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.update, 1.)

    def update(self, delta=0):
        self._update_day()
        self._schedule_update()

    def _update_day(self):
        Logger.info('UPDATING CALENDAR ...')
        today = dt.date.today()
        self.day_num.text = today.strftime('%d')
        self.day_of_week.text = today.strftime('%A')
        self.month.text = today.strftime('%B %Y')
        self.month_cal.show_month_of_date(today)

    def _schedule_update(self):
        next_update = self._next_update()
        next_in_secs = (next_update - dt.datetime.now()).total_seconds()
        Logger.info(
            f'NEXT CALENDAR UPDATE AT {next_update} O\'CLOCK, '
            f'IN {next_in_secs} SECONDS.'
        )
        Clock.schedule_once(self.update, next_in_secs)

    @staticmethod
    def _next_update() -> dt.datetime:
        now = dt.datetime.now()
        next_update = now.replace(hour=0, minute=0, second=1) + \
                      dt.timedelta(days=1)
        return next_update


class MonthTable(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        todoist = get_global(TODOIST_KEY)
        if not todoist:
            raise ValueError('Todoist not initialized')
        todoist.add_subscriber(self.set_tasks)

    def create_header(self):
        for day in calendar.day_name:
            self.add_widget(DayLabel(
                text=day[:2],
                font_name='FreeMonoBold'
            ))

    def month_days(self, date: dt.date) -> tp.Iterator[tp.Union[dt.date, None]]:
        first_day_of_month = date.replace(day=1)
        first_day_of_week = first_day_of_month.weekday()
        days_in_month = calendar.monthrange(
            date.year,
            date.month
        )[1]
        for day in range(0, first_day_of_week):
            yield None
        for day in range(1, days_in_month + 1):
            yield dt.date(date.year, date.month, day)

    def show_month_of_date(self, date: dt.date):
        self.clear_widgets()
        self.create_header()
        for day in self.month_days(date):
            if day is None:
                self.add_widget(Label())
            else:
                self.add_widget(DayWidget(day))

    def set_tasks(self, tasks) -> None:
        remind_dates = set()
        for task in tasks:
            date = task.get('due', {}).get('date')
            if date:
                remind_dates.add(dt.datetime.strptime(date, '%Y-%m-%d').date())

        for child in self.children:
            if isinstance(child, DayWidget):
                child.task = child.date in remind_dates


class DayLabel(Label):
    pass


class DayWidget(Label):
    def __init__(self, date: dt.date, task: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.date = date
        self._task = task
        self.text = str(date.day)
        # self.font_name = 'FreeMonoBold'

        self.embellish()

        # self.bind(height=self._update_min_width)
        self.bind(size=self._update_geometry, pos=self._update_geometry)

    def embellish(self):
        self.canvas.before.clear()

        reminder_color = (1, 1, 1, 1)
        if self.date == dt.date.today():
            with self.canvas.before:
                Color(1, 1, 1, 1)
                self.rect = Rectangle(pos=self.pos, size=self.size)
                reminder_color = (1, 0, 0, 1)
            self.color = (0, 0, 0, 1)

        if self.task:
            with self.canvas.before:
                Color(*reminder_color)
                circle_settings = circle_settings_from_widget(self)
                self.circle = Line(circle=circle_settings, width=1)

    @property
    def task(self) -> bool:
        return self._task

    @task.setter
    def task(self, task: bool):
        self._task = task
        self.embellish()

    def _update_min_width(self, instance, value):
        self.width = max(self.width, value)

    def _update_geometry(self, instance, value):
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

        if hasattr(self, 'circle'):
            self.circle.circle = circle_settings_from_widget(self)
