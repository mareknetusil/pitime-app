import calendar
import datetime as dt
import locale
import typing as tp

from dotenv import load_dotenv

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup


class BlacklightDummy:
    brightness = 1


try:
    from rpi_backlight import Backlight
except (FileNotFoundError, ModuleNotFoundError):
    Blacklight = BlacklightDummy


from todoist import KivyTodoist
# from weather import Weather

if tp.TYPE_CHECKING:
    from todoist import Todoist, Todos


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


class TasksWidget(BoxLayout):
    pass


class TasksListWidget(RelativeLayout):
    TASK_HEIGHT = 40

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.todoist: 'Todoist' = KivyTodoist(timeout=3)
        self.todoist.add_subscriber(self.update_tasks)
        self.todoist.run()

    def update(self, delta):
        self.todoist.update()

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

    def set_task(self, task: 'tp.Dict[str, tp.Any]'):
        task_text = task['content']
        self.task_text = task_text if len(task_text) <= 55 else task_text[:55] + '...'
        self.task_id = str(task['id'])
        self.priority.text = str(task['priority'])
        self.due.set_due(task.get('due', {}))

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

    def set_due(self, due: 'tp.Dict[str, tp.Any]'):
        if 'date' in due:
            date = dt.datetime.fromisoformat(due['date']).date()
            day_diff = (date - dt.date.today()).days
            max_light = 0x88 / 256
            bg_shade = min(7, max(0, day_diff)) / 7 * max_light
            self.bg_color = (bg_shade, bg_shade, bg_shade)
        self.text = due.get('string', '')


class WeatherWidget(BoxLayout):
    weather = ObjectProperty(None)


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


class CarouselWidget(Carousel):
    pass


class AppWidget(BoxLayout):
    calendar_widget = ObjectProperty(None)
    carousel_widget = ObjectProperty(None)
    try:
        backlight = ObjectProperty(Backlight())
    except FileNotFoundError:
        backlight = BlacklightDummy()

    def update(self, dt):
        self.calendar_widget.update_day()


class CalendarApp(App):
    def build(self):
        app = AppWidget()
        Clock.schedule_interval(app.update, 1. / 60.)
        return app


if __name__ == '__main__':
    load_dotenv()

    # locale.setlocale(locale.LC_TIME, 'cs_CZ.utf8')
    LabelBase.register(name='Roboto-Black', fn_regular='fonts/Roboto-Black.ttf')
    LabelBase.register(name='Roboto-Light', fn_regular='fonts/Roboto-Light.ttf')
    LabelBase.register(name='tahoma', fn_regular='fonts/tahoma.ttf')
    LabelBase.register(name='meteocons', fn_regular='fonts/meteocons-webfont.ttf')

    CalendarApp().run()
