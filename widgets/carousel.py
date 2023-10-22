from kivy.uix.carousel import Carousel

from .clock import ClockWidget
from .tasks import TasksWidget


class CarouselWidget(Carousel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(TasksWidget())
        self.add_widget(ClockWidget())
