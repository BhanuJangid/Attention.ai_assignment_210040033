# import datetime
from groq import Groq
from helper import get_groq_response, format_itinerary
import datetime


def create_itinerary(city, start_time, end_time, interests, budget):
    itinerary = [
        {
            "location": "Central Park",
            "start_time": str(start_time),
            "end_time": str(start_time + datetime.timedelta(hours=1)),
            "transport": "Walk",
            "cost": 0
        },
        {
            "location": "Museum of Natural History",
            "start_time": str(start_time + datetime.timedelta(hours=1.5)),
            "end_time": str(start_time + datetime.timedelta(hours=3)),
            "transport": "Taxi",
            "cost": 20
        }
    ]
    
    total_cost = sum(stop["cost"] for stop in itinerary)
    if total_cost > budget:
        for stop in itinerary:
            if stop["transport"] == "Taxi" and total_cost > budget:
                stop["transport"] = "Bus"
                stop["cost"] -= 10
                total_cost -= 10
    
    return itinerary







def generate_itinerary(city, date , start_time, end_time, interests, budget, start_location):
    prompt = (
        f"Create a one-day itinerary for a trip to {city}. "
        f"The trip starts at {start_time} and ends at {end_time}. "
        f"The user is interested in {interests} and has a budget of ${budget}. "
        f"The day starts at {start_location}. "
        "Please include suggested stops, times, transport modes, entry fees, and travel times."
    )

    # Get the response from Groq
    return get_groq_response(prompt)