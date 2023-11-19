from kivy.uix.carousel import Carousel
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import NumericProperty

from .clock import ClockWidget
from .tasks import TasksWidget


class CarouselWidget(Carousel):
    return_delay = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.return_event = None
        self.clock_widget = ClockWidget()

        self.add_widget(self.clock_widget)
        self.add_widget(TasksWidget())

        self.bind(current_slide=self.on_current_slide)

    def on_current_slide(self, instance, value):
        if self.return_delay <= 0:
            return

        if self.return_event:
            self.return_event.cancel()
            self.return_event = None

        if value != self.clock_widget:
            self.schedule_return_to_clock()

    def schedule_return_to_clock(self):
        Logger.info(f'RETURNING TO CLOCK IN {self.return_delay} ...')
        self.return_event = Clock.schedule_once(self.return_to_clock, self.return_delay)

    def return_to_clock(self, dt):
        self.load_slide(self.clock_widget)
        self.return_event = None
