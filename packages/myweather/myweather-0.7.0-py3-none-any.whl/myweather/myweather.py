import requests
import json
import os


class MyWeather:
    def __init__(self, api_key, lat, lon, setgraddegree):
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.setgraddegree = setgraddegree
        request_url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
        response = requests.get(request_url)
        self.data = response.json()

    def description(self):
        weather_describtion = self.data["weather"][0]["description"]
        return weather_describtion

    def degreefunc(self):
        if self.setgraddegree == "Grad":
            temperature = round(self.data["main"]["temp"] - 273.15)
        if self.setgraddegree == "Fahrenheit":
            temperature = round(self.data["main"]["temp"])
        return temperature


if __name__ == "__main__":
    api_key = os.getenv("OPENWEATHER_DEV_API")
    print(api_key)
    lat = 34
    lon = lat
    weather = MyWeather(api_key=api_key, lat=lat, lon=lon, setgraddegree="Grad")
    print(weather.description())
    print(weather.degreefunc())
