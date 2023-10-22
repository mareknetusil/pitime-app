import locale
import typing as tp

from dotenv import load_dotenv

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase


class BlacklightDummy:
    brightness = 1


try:
    from rpi_backlight import Backlight
except (FileNotFoundError, ModuleNotFoundError):
    Blacklight = BlacklightDummy


# from weather import Weather


class WeatherWidget(BoxLayout):
    weather = ObjectProperty(None)


class CarouselWidget(Carousel):
    pass


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


if __name__ == '__main__':
    load_dotenv()

    # locale.setlocale(locale.LC_TIME, 'cs_CZ.utf8')
    LabelBase.register(name='Roboto-Black', fn_regular='fonts/Roboto-Black.ttf')
    LabelBase.register(name='Roboto-Light', fn_regular='fonts/Roboto-Light.ttf')
    LabelBase.register(name='tahoma', fn_regular='fonts/tahoma.ttf')
    LabelBase.register(name='meteocons', fn_regular='fonts/meteocons-webfont.ttf')

    PiTimeApp().run()
