from kivy.uix.boxlayout import BoxLayout

from PIL import Image, ImageDraw, ImageFont


icons_list = {u'01d':u'B',u'01n':u'C',u'02d':u'H',u'02n':u'I',u'03d':u'N',u'03n':u'N',
        u'04d':u'Y',u'04n':u'Y',u'09d':u'R',u'09n':u'R',u'10d':u'R',u'10n':u'R',u'11d':u'P',
        u'11n':u'P',u'13d':u'W',u'13n':u'W',u'50d':u'M',u'50n':u'W'}


class WeatherWidget(BoxLayout):
    def __init__(self, weather, **kwargs):
        super().__init__(**kwargs)
        self.weather = weather

    def draw(self, img, x, y):
        ### Weather line
        #img.line((x + self.scale(10), yPos + self.scale(320), 
        #          x + self.scale(230), yPos + self.scale(320)), 
        #        fill = 255) 

        current_weather = self.weather.weather['weather'][0]['main']
        current_icon = self.weather.weather['weather'][0]['icon']
        current_temp = str(int(self.weather.weather['main']['temp']) - 273) + 'C'
        forecast_weather = self.weather.forecast['list'][0]['weather'][0]['main']
        forecast_icon = self.weather.forecast['list'][0]['weather'][0]['icon']
        forecast_temp_min_max = str(int(self.weather.forecast['list'][0]['main']['temp_min']) \
                - 273) + 'C \ ' + str(int(self.weather.forecast['list'][0]['main']['temp_max'])\
                - 273) + 'C'
        
        if (len(current_weather) >= 9):
            current_weather = current_weather[0:7] + '.'
        if (len(forecast_weather) >= 9):
            forecast_weather = forecast_weather[0:7] + '.'
        
        # The placement for weather icon
        w_weather_icon,h_weather_icon = self.font_weather_icons.getsize(
                icons_list[str(current_icon)])
        #y_weather_icon = yPos + self.scale(((384 - 320) / 2)) - (h_weather_icon / 2)
        y_weather_icon = self.scale(357)
        
        # The placement for current weather string & temperature
        w_current_weather,h_current_weather = self.font_weather.getsize(current_weather)
        w_current_temp,h_current_temp = self.font_weather.getsize(current_temp)
        
        # The placement for forecast temperature string & temperatures
        x_pos = 100
        w_forecast_temp_min_max,h_forecast_temp_min_max = self.font_weather.getsize(
                forecast_temp_min_max)
        w_forecast_weather,h_forecast_weather = self.font_weather.getsize(forecast_weather)
        
        img.text((x + x_pos, y_weather_icon),icons_list[str(current_icon)], 
                font = self.font_weather_icons, fill = 0) # Diplay weather icon
        
        x_current_start = x + x_pos + w_weather_icon + self.scale(10)
        img.text((x_current_start, y_weather_icon), current_weather, 
                font = self.font_weather, fill = 0) # Display the current weather text
        img.line((x_current_start, y_weather_icon + self.scale(25),
                  x_current_start + w_current_weather, y_weather_icon + self.scale(25)), 
                  fill = 0) # Line below the current weather text
        img.text((x_current_start, y_weather_icon + self.scale(29)), current_temp, 
                font = self.font_weather, fill = 0) # The text of the current temperature
        
        x_arrow_symbol = x + x_pos + w_weather_icon + self.scale(20) \
                + w_current_weather # Location of the arrow to be displayed
        img.rectangle((x_arrow_symbol, y_weather_icon + self.scale(23), 
            x_arrow_symbol + self.scale(10), y_weather_icon + self.scale(27)), 
                fill = 0) # Rectangle of the arrow
        img.polygon([x_arrow_symbol + self.scale(10), y_weather_icon  +self.scale(19), 
            x_arrow_symbol + self.scale(16), y_weather_icon + self.scale(25), 
            x_arrow_symbol + self.scale(10), y_weather_icon + self.scale(31)], 
                fill = 0) # Triangle of the arrow

        # All forcasts to be displayed start at this position
        x_forecast_start = x_arrow_symbol + self.scale(16 + 10)
        img.text((x_forecast_start, y_weather_icon + self.scale(29)), forecast_temp_min_max, 
                font = self.font_weather, fill = 0) # The text of the forecast temperature
        # Line above the forecast weather temperature text
        img.line((x_forecast_start, y_weather_icon + self.scale(25), 
            x_forecast_start + w_forecast_temp_min_max, 
            y_weather_icon + self.scale(25)), fill = 0)
        x_forecast_weather = x_forecast_start + (w_forecast_temp_min_max - w_forecast_weather) / 2
        img.text((x_forecast_weather, y_weather_icon), forecast_weather, 
                font = self.font_weather, fill = 0) # Display the forecast weather text
        
        img.text((x_forecast_start + w_forecast_temp_min_max + self.scale(10),y_weather_icon),
                icons_list[str(forecast_icon)], 
                font = self.font_weather_icons, fill = 0) # Diplay forecast weather icon
