import requests

class Weather:
    def __init__(self):
        self.weather = None
        self.forecast = None

    def query_weather(self):
        WEATHER_API = '5428b8244b0584b247891402851a17ac'
        print('-= Ping Weather API =-')
        try:
            weather = requests.get("http://api.openweathermap.org/data/2.5/weather", 
                    params={"appid":WEATHER_API, "id":'3067696'}).json()
            forecast = requests.get("http://api.openweathermap.org/data/2.5/forecast", 
                    params={"appid":WEATHER_API, "id":'3067696'}).json()

            resp = True if weather != self.weather or forecast != self.forecast else False
            self.weather = weather
            self.forecast = forecast
            return resp
        except requests.ConnectionError as e:
            print('Chyba pripojeni!')

