import typing as tp
from statistics import mean

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from weather import InfoType

from PIL import Image, ImageDraw, ImageFont

if tp.TYPE_CHECKING:
    from weather import CurrentWeather, Forecast


icons_list = {u'01d':u'B',u'01n':u'C',u'02d':u'H',u'02n':u'I',u'03d':u'N',u'03n':u'N',
        u'04d':u'Y',u'04n':u'Y',u'09d':u'R',u'09n':u'R',u'10d':u'R',u'10n':u'R',u'11d':u'P',
        u'11n':u'P',u'13d':u'W',u'13n':u'W',u'50d':u'M',u'50n':u'W'}


class WeatherInfoWidget(BoxLayout):
    icon = ObjectProperty(None)
    temp = ObjectProperty(None)


class WeatherWidget(BoxLayout):
    current_weather = ObjectProperty(None)
    forecast_1h = ObjectProperty(None)
    forecast_3h = ObjectProperty(None)

    def __init__(self, weather, **kwargs):
        super().__init__(**kwargs)
        self.weather = weather
        self.weather.add_subscriber({
            InfoType.Weather: self.update_weather,
            InfoType.Forecast: self.update_forecast
        })

    def update_weather(self, weather: 'CurrentWeather') -> None:
        self.current_weather.icon.text = icons_list[weather.weather[0].icon]
        self.current_weather.temp.text = str(int(weather.main.temp) - 273) + '°'

    def update_forecast(self, forecast: 'Forecast') -> None:
        forecast_1h = forecast.list[0]
        self.forecast_1h.icon.text = icons_list[forecast_1h.weather[0].icon]
        temp_1h = mean([
            int(forecast_1h.main.temp_min),
            int(forecast_1h.main.temp_max)
        ])
        self.forecast_1h.temp.text = (f'{temp_1h - 273}°')

        forecast_3h = forecast.list[2]
        self.forecast_3h.icon.text = icons_list[forecast_3h.weather[0].icon]
        temp_3h = mean([
            int(forecast_3h.main.temp_min),
            int(forecast_3h.main.temp_max)
        ])
        self.forecast_3h.temp.text = (f'{temp_3h - 273}°')
