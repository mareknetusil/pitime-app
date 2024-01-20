import enum
import uuid
import typing as tp

from pydantic import BaseModel


WEATHER_KEY = uuid.uuid4()


class InfoType(enum.Enum):
    Weather = 'weather'
    Forecast = 'forecast'


class Coord(BaseModel):
    lon: float
    lat: float


class Weather(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class Main(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class Wind(BaseModel):
    speed: float
    deg: int
    gust: tp.Optional[float] = None


class Clouds(BaseModel):
    all: int


class CurrSys(BaseModel):
    type: int
    id: int
    country: str
    sunrise: int
    sunset: int


class CurrentWeather(BaseModel):
    coord: Coord
    weather: list[Weather]
    base: str
    main: Main
    visibility: int
    wind: Wind
    clouds: Clouds
    dt: int
    sys: CurrSys
    timezone: int
    id: int
    name: str
    cod: int


class City(BaseModel):
    id: int
    name: str
    coord: Coord
    country: str
    population: int
    timezone: int
    sunrise: int
    sunset: int


class ForeSys(BaseModel):
    pod: str


class ForecastWeather(BaseModel):
    dt: int
    main: Main
    weather: list[Weather]
    clouds: Clouds
    wind: Wind
    visibility: int
    pop: float
    sys: ForeSys
    dt_txt: str


class Forecast(BaseModel):
    cod: str
    message: int
    cnt: int
    list: list[ForecastWeather]
    city: City

MODELS = {
    InfoType.Weather: CurrentWeather,
    InfoType.Forecast: Forecast
}
