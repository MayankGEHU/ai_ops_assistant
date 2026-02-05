import requests
import os

API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    return {
        "city": city,
        "temperature": res["main"]["temp"],
        "condition": res["weather"][0]["description"]
    }
