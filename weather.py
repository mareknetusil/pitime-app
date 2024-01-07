import uuid
import os

import requests


WEATHER_KEY = uuid.uuid4()


class Weather:
    def __init__(self):
        self.weather = None
        self.forecast = None

    def query_weather(self):
        print('-= Ping Weather API =-')
        WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
        try:
            weather = requests.get("http://api.openweathermap.org/data/2.5/weather", 
                    params={"appid":WEATHER_TOKEN, "id":'3067696'}).json()
            forecast = requests.get("http://api.openweathermap.org/data/2.5/forecast", 
                    params={"appid":WEATHER_TOKEN, "id":'3067696'}).json()

            resp = True if weather != self.weather or forecast != self.forecast else False
            self.weather = weather
            self.forecast = forecast
            return resp
        except requests.ConnectionError as e:
            print('Chyba pripojeni!')

