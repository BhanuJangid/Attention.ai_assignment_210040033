import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Function to fetch weather data
def call_weather_forecast(city, target_date):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            # Loop through forecast data to find the closest match to target_date (if you need daily data)
            for forecast in data['list']:
                forecast_date = forecast['dt_txt'].split(" ")[0]  # Get date part from datetime string
                if forecast_date == target_date:
                    weather_info = {
                        "forecast": forecast["weather"][0]["description"],
                        "temperature": forecast["main"]["temp"],
                        "advice": "Carry an umbrella!" if "rain" in forecast["weather"][0]["description"] else "It's going to be sunny, enjoy your trip!"
                    }
                    return weather_info
            return {"error": "No weather data found for the specified date."}
        else:
            return {"error": f"Failed to fetch weather data: {data.get('message', 'Unknown error')}."}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
