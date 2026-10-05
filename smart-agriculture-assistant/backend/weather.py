import requests

def get_current_weather(lat: float, lon: float):
    # Free Open-Meteo API (no key required)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,cloud_cover&hourly=temperature_2m,precipitation_probability&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "cloud_cover": current.get("cloud_cover"),
            "daily_max_temp": daily.get("temperature_2m_max", [])[0] if daily.get("temperature_2m_max") else None,
            "daily_min_temp": daily.get("temperature_2m_min", [])[0] if daily.get("temperature_2m_min") else None,
            "daily_precipitation": daily.get("precipitation_sum", [])[0] if daily.get("precipitation_sum") else None,
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None
