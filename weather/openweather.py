import os
import typing as tp

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest

from .interface import InfoType, MODELS

if tp.TYPE_CHECKING:
    from .interface import CurrentWeather, Forecast


class OpenWeather:
    def __init__(self, timeout: int = 3, period: int = 60):
        self.weather: 'tp.Optional[CurrentWeather]' = None
        self.forecast: 'tp.Optional[Forecast]' = None
        self._subscribers = []
        self._clock = None
        self.timeout = timeout
        self.period = period

    def run(self) -> None:
        Logger.info('STARTING REGULAR WEATHER CHECKS ...')
        Logger.info(f'CHECKING EVERY {self.period} seconds.')
        self._clock = Clock.schedule_interval(self.update, self.period)
        self.update()

    def stop(self) -> None:
        Logger.info('STOPPING REGULAR WEATHER CHECKS')
        if self._clock:
            self._clock.cancel()

    def add_subscriber(self, subscriber) -> None:
        self._subscribers.append(subscriber)

    def update(self, _: int = 0) -> None:
        Logger.info('CHECKING FOR WEATHER ...')
        weather_token = os.getenv('WEATHER_TOKEN')
        req1 = UrlRequest(
            url=(
                f'http://api.openweathermap.org/data/2.5/weather'
                f'?id=3067696&appid={weather_token}'
            ),
            timeout=self.timeout,
            on_success=self._on_success_handler(InfoType.Weather),
            on_failure=self._on_error_handler(InfoType.Weather),
            on_error=self._on_error_handler(InfoType.Weather)
        )
        req2 = UrlRequest(
            url=(
                f'http://api.openweathermap.org/data/2.5/forecast'
                f'?id=3067696&appid={weather_token}'
            ),
            timeout=self.timeout,
            on_success=self._on_success_handler(InfoType.Forecast),
            on_failure=self._on_error_handler(InfoType.Forecast),
            on_error=self._on_error_handler(InfoType.Forecast)
        )

    def _on_success_handler(self, attr: InfoType) -> None:
        attr_name = attr.value
        model = MODELS[attr]
        def _on_success(req, resp) -> None:
            resp_obj = model(**resp)
            if resp_obj == getattr(self, attr_name):
                Logger.debug(f'NO CHANGE IN {attr_name.upper()}.')
                return

            Logger.info(f'CHANGE IN {attr_name.upper()}.')
            setattr(self, attr_name, resp_obj)
            for subscriber in self._subscribers:
                subscriber(attr, resp_obj)

        return _on_success

    def _on_error_handler(self, attr: InfoType) -> None:
        attr_name = attr.value
        def _on_error(req, resp) -> None:
            Logger.error(f'REQUEST TO {attr_name.upper()} FAILED!')
            Logger.error(resp)

        return _on_error


