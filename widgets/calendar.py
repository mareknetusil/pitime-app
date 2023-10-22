import calendar
import datetime as dt

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty


class CalendarWidget(BoxLayout):
    day_num = ObjectProperty(None)
    day_of_week = ObjectProperty(None)
    month = ObjectProperty(None)
    month_cal = ObjectProperty(None)

    def update_day(self):
        today = dt.date.today()
        self.day_num.text = today.strftime('%d')
        self.day_of_week.text = today.strftime('%A')
        self.month.text = today.strftime('%B %Y')
        self.month_cal.text = calendar.month(today.year, today.month).split('\n', 1)[1]


class MonthWidget(Label):
    pass
