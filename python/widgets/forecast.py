import datetime as dt
import typing as tp

import pytz

from kivy.logger import Logger
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, MeshLinePlot, exp10, log10, identity

from globals import get_global
from weather import CurrentWeather, Forecast, WEATHER_KEY, InfoType, icons_list


class ForecastInfoWidget(BoxLayout):
    def __init__(self, time: str, icon: str, temp: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text=time, font_name='Roboto-Bold', font_size=40))
        self.add_widget(Label(text=icon, font_name='meteocons', font_size=50))
        self.add_widget(Label(text=temp, font_name='Roboto-Bold', font_size=40))


class ForecastLayout(GridLayout):
    pass


class ForecastWidget(BoxLayout):
    temperatures = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.add_widget(Widget(size_hint=(1, 0.1)))  # padding
        self.add_widget(
            Label(
                text='Předpověď',
                size_hint=(1, 0.1),
                font_name='Roboto-Bold',
                font_size=50,
        ))

        self.forecast_layout = ForecastLayout(cols=3, size_hint=(1, 0.8))
        self.add_widget(self.forecast_layout)
        self.add_widget(Widget(size_hint=(1, 0.1)))  # padding

        weather_api = get_global(WEATHER_KEY)
        weather_api.add_subscriber({InfoType.Forecast: self.update_forecast})

    @staticmethod
    def get_time_label(timestamp: int) -> str:
        time: dt.datetime = dt.datetime.fromtimestamp(timestamp)
        cz_loc = pytz.timezone('Europe/Prague')
        time = pytz.utc.localize(time)
        # time = time.astimezone(cz_loc)
        return time.strftime('%H:%M')

    def update_forecast(self, forecast: Forecast):
        self.forecast_layout.clear_widgets()
        print(forecast.city.timezone)
        for weather in forecast.list[:6]:
            time = self.get_time_label(weather.dt)
            icon = icons_list[weather.weather[0].icon]
            temp = f'{int(weather.main.temp) - 273:.1f}°'
            self.forecast_layout.add_widget(
                ForecastInfoWidget(time, icon, temp, size_hint=(.33, 0.5))
            )
        # self.temperatures = [weather.main.temp for weather in forecast.list]
        # self.timestamps = [
        #     f'{self.get_time_label(weather.dt)}\n{weather.main.temp - 273:.1f}°'
        #     for weather in forecast.list
        # ]
        # self.plot.points = [
        #     (x, temp - 273)
        #     for x, temp in enumerate(self.temperatures)
        # ]
        # self.graph.timestamps = self.timestamps
        # self.graph.add_plot(self.plot)
