import datetime as dt

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty


class ClockWidget(BoxLayout):
    time_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1.)

    def update_time(self, delta):
        size = 150
        text = dt.datetime.now().strftime('%H:%M:%S')
        hm = text[:5]
        secs = text[5:]
        self.time_label.text = f'[size={size}]{hm}[size={size//2}]{secs}'
