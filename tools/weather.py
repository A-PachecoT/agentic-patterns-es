import requests
from typing import Optional, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def get_coordinates(city: str) -> Optional[tuple[float, float]]:
    """Get coordinates for a city using Open-Meteo Geocoding API."""
    try:
        response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            logger.warning(f"No coordinates found for city: {city}")
            return None

        result = data["results"][0]
        return (result["latitude"], result["longitude"])
    except Exception as e:
        logger.error(f"Error getting coordinates for {city}: {str(e)}")
        return None


def get_weather(city: str) -> Dict[str, Any]:
    """Get the current weather for a specific city using Open-Meteo API."""
    logger.info(f"🔧 Getting weather for: {city}")

    # Get coordinates for the city
    coords = get_coordinates(city)
    if not coords:
        return {"error": f"Could not find coordinates for {city}"}

    lat, lon = coords

    try:
        # Make API request to Open-Meteo
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code",
                "timezone": "auto",
            },
        )
        response.raise_for_status()
        data = response.json()

        # Map weather codes to conditions
        weather_codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow fall",
            73: "moderate snow fall",
            75: "heavy snow fall",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with slight hail",
            99: "thunderstorm with heavy hail",
        }

        current = data["current"]
        weather_code = current["weather_code"]
        condition = weather_codes.get(weather_code, "unknown")

        return {
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "condition": condition,
            "units": {"temperature": "°C", "humidity": "%"},
        }

    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return {"error": str(e)}


def convert_celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


if __name__ == "__main__":
    # Test the weather function with some cities
    test_cities = ["London", "New York", "Tokyo", "NonExistentCity"]

    for city in test_cities:
        print(f"\nTesting weather for {city}:")
        result = get_weather(city)

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            temp_c = result["temperature"]
            temp_f = convert_celsius_to_fahrenheit(temp_c)
            print(f"Temperature: {temp_c:.1f}°C ({temp_f:.1f}°F)")
            print(f"Humidity: {result['humidity']}%")
            print(f"Condition: {result['condition']}")
