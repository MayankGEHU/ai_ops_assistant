import requests
import os
from typing import Dict, Any
import time

API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city: str, retries: int = 3) -> Dict[str, Any]:
    """Fetch current weather for city via OpenWeatherMap. Uses exponential backoff on failure."""
    if not API_KEY:
        return {"error": "WEATHER_API_KEY not configured"}
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            res = response.json()

            return {
                "city": city,
                "temperature": res["main"]["temp"],
                "condition": res["weather"][0]["description"],
                "humidity": res["main"].get("humidity"),
                "wind_speed": res.get("wind", {}).get("speed")
            }
            
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            
            error_msg = str(e)
            if response.status_code == 404:
                error_msg = f"City '{city}' not found"
            return {"error": f"Failed to fetch weather: {error_msg}"}
        except KeyError as e:
            return {"error": f"Unexpected API response format: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    return {"error": "Failed to fetch weather after retries"}
