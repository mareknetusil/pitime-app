import calendar
import datetime as dt

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.logger import Logger


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
        self.month_cal.text = calendar\
            .month(today.year, today.month)\
            .split('\n', 1)[1]

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


class MonthWidget(Label):
    pass
