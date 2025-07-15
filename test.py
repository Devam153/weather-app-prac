import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("WEATHER_API")

def get_weather(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial"  # REMOVE UNITS AND YOU'LL GET KELVIN
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        print(f"Weather in {data['name']}, {data['sys']['country']}:")
        print(data['weather'][0]['description'].capitalize())
        print(f"Temperature: {data['main']['temp']}°F")
        print(f"Humidity: {data['main']['humidity']}%")
    else:
        print("❌ Please enter a valid city name.")

if __name__ == "__main__":
    city = input("Enter city name: ")
    get_weather(city, api_key)
