import calendar
import datetime as dt
import typing as tp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle


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

    def create_header(self):
        for day in calendar.day_name:
            self.add_widget(Label(
                text=day[:2],
                font_name='FreeMonoBold'
            ))

    def month_days(self, date: dt.date) -> tp.Iterator[dt.date | None]:
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


class DayWidget(Label):
    def __init__(self, date: dt.date, **kwargs):
        super().__init__(**kwargs)
        self.date = date
        self.text = str(date.day)
        self.font_name = 'FreeMonoBold'

        if date == dt.date.today():
            self._draw_today()

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _draw_today(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.color = (0, 0, 0, 1)

    def _update_rect(self, instance, value):
        if not hasattr(self, 'rect'):
            return

        self.rect.pos = instance.pos
        self.rect.size = instance.size
