import locale
import sys

from dotenv import load_dotenv

from kivy.app import App
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase

from globals import set_global
from todoist import TODOIST_KEY, KivyTodoist, Birthdays, ComposeTodoist
from weather import WEATHER_KEY, OpenWeather


class BlacklightDummy:
    brightness = 1


try:
    from rpi_backlight import Backlight
except (FileNotFoundError, ModuleNotFoundError):
    Blacklight = BlacklightDummy


class AppWidget(BoxLayout):
    calendar_widget = ObjectProperty(None)
    carousel_widget = ObjectProperty(None)
    try:
        backlight = ObjectProperty(Backlight())
    except FileNotFoundError:
        backlight = BlacklightDummy()


class PiTimeApp(App):
    def build(self):
        app = AppWidget()
        return app


def set_czech_locale():
    if sys.platform.startswith('win'):
        locale.setlocale(locale.LC_TIME, 'Czech_Czech Republic.1250')
    elif sys.platform.startswith('linux'):
        locale.setlocale(locale.LC_TIME, 'cs_CZ.UTF-8')


if __name__ == '__main__':
    load_dotenv()

    try:
        set_czech_locale()
    except locale.Error:
        Logger.warning('Czech locale not found')        

    LabelBase.register(name='Roboto-Black', fn_regular='fonts/Roboto-Black.ttf')
    LabelBase.register(name='Roboto-Light', fn_regular='fonts/Roboto-Light.ttf')
    LabelBase.register(name='tahoma', fn_regular='fonts/tahoma.ttf')
    LabelBase.register(name='meteocons', fn_regular='fonts/meteocons-webfont.ttf')

    todoist = ComposeTodoist(
        Birthdays('birthdays.txt'),
        KivyTodoist(timeout=3),
    )
    set_global(TODOIST_KEY, todoist)
    weather = OpenWeather()
    set_global(WEATHER_KEY, weather)
    todoist.run()
    weather.run()
    PiTimeApp().run()
