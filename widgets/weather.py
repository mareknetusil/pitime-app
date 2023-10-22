from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

# from ..weather import Weather


class WeatherWidget(BoxLayout):
    weather = ObjectProperty(None)
