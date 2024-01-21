import typing as tp

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
        self.current_weather.temp.text = str(int(weather.main.temp) - 273) + 'C'

    def update_forecast(self, forecast: 'Forecast') -> None:
        self.forecast_1h.icon.text = icons_list[forecast.list[0].weather[0].icon]
        self.forecast_1h.temp.text = (
            f'{int(forecast.list[0].main.temp_min) - 273}C \ '
            f'{int(forecast.list[0].main.temp_max) - 273}C'
        )

        self.forecast_3h.icon.text = icons_list[forecast.list[2].weather[0].icon]
        self.forecast_3h.temp.text = (
            f'{int(forecast.list[0].main.temp_min) - 273}C \ '
            f'{int(forecast.list[0].main.temp_max) - 273}C'
        )
