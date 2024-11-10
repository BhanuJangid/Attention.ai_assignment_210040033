from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
import requests
from neo4j import GraphDatabase


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


def call_weather_service(city):
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            weather_info = {
                "forecast": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "advice": "Carry an umbrella!" if "rain" in data["weather"][0]["description"] else "It's going to be sunny, enjoy your trip!"
            }
            return weather_info
        else:
            return {"error": "Weather data unavailable."}
    
    except Exception as e:
        return {"error": str(e)}


uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

def update_user_memory(user_id, memory_data):
    """
    Update user preferences and memory in the graph database.
    :param user_id: The ID of the user whose memory is being updated.
    :param memory_data: A dictionary or list of data to be updated in the user's memory.
    """
    with driver.session() as session:
        session.write_transaction(_update_memory, user_id, memory_data)

def _update_memory(tx, user_id, memory_data):
    """
    A helper function to handle the update query.
    :param tx: The transaction object.
    :param user_id: The ID of the user.
    :param memory_data: The memory data to be updated.
    """
    query = """
    MERGE (u:User {id: $user_id})
    SET u.memory = $memory_data
    """
    tx.run(query, user_id=user_id, memory_data=memory_data)

# Neo4j driver connection (update the URL with your Neo4j server details)
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

def fetch_user_memory(user_id):
    """
    Fetch user memory based on the user ID from the graph database.
    :param user_id: The ID of the user whose memory is being fetched.
    :return: A dictionary or data containing the user's memory.
    """
    with driver.session() as session:
        result = session.read_transaction(_fetch_memory, user_id)
        return result

def _fetch_memory(tx, user_id):
    """
    Helper function to query the user's memory from the graph database.
    :param tx: The transaction object.
    :param user_id: The ID of the user.
    :return: The user's memory data.
    """
    query = """
    MATCH (u:User {id: $user_id})
    RETURN u.memory AS memory
    """
    result = tx.run(query, user_id=user_id)
    record = result.single()
    if record:
        return record["memory"]
    else:
        return None 

import os
from dotenv import load_dotenv
from groq import Groq
import requests

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


def get_groq_response(prompt):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9,
        stream=False
    )
    return completion.choices[0].message.content


def call_weather_service(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather_info = {
                "forecast": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "advice": "Carry an umbrella!" if "rain" in data["weather"][0]["description"] else "It's sunny, enjoy your trip!"
            }
            return weather_info
        else:
            return {"error": "Weather data unavailable."}

    except Exception as e:
        return {"error": str(e)}


def format_itinerary(itinerary):
    formatted_itinerary = ""
    
    for idx, item in enumerate(itinerary.get('stops', [])):  # Assuming 'stops' is a list
        # Check that 'name' and time keys exist in the item
        if 'name' in item and 'time' in item:
            formatted_itinerary += f"{idx + 1}. {item['name']} ({item['time']})\n"
        else:
            formatted_itinerary += f"Missing details for stop {idx + 1}.\n"

    return formatted_itinerary

