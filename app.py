import os
import streamlit as st
from groq import Groq
import datetime
from dotenv import load_dotenv
from helper import get_groq_response, format_itinerary
from itinerary_service import generate_itinerary
from memory_service import MemoryService
from helper import call_weather_service
from weather_service import call_weather_forecast

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
memory_service = MemoryService("bolt://localhost:7687", "neo4j", "password")

st.set_page_config(page_title="One-Day Trip Planner", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    .user-message, .ai-message {
        display: flex;
        margin-bottom: 10px;
    }
    .user-message p, .ai-message p {
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
    }
    .user-message {
        justify-content: flex-end;
    }
    .user-message p {
        background-color: #DCF8C6;
        text-align: right;
    }
    .ai-message {
        justify-content: flex-start;
    }
    .ai-message p {
        background-color: #F1F1F1;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)


st.header("Plan Your One-Day Trip")

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

if 'trip_details' not in st.session_state:
    st.session_state['trip_details'] = {}

if 'final_itinerary' not in st.session_state:
    st.session_state['final_itinerary'] = None

def display_chat():
    for msg in st.session_state['conversation_history']:
        if isinstance(msg, dict) and 'role' in msg and 'text' in msg:
            if msg['role'] == 'user':
                st.markdown(
                    f"<div style='text-align: right;'><p style='background-color: #DCF8C6; display: inline-block; padding: 10px; border-radius: 10px;'>{msg['text']}</p></div>",
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div style='text-align: left;'><p style='background-color: #F1F1F1; display: inline-block; padding: 10px; border-radius: 10px;'>{msg['text']}</p></div>",
                    unsafe_allow_html=True)

with st.form(key="chat_form"):
    user_input = st.text_input("You: ", key="user_input")
    submit_button = st.form_submit_button("Send")

if submit_button:
    if user_input:
        st.session_state['conversation_history'].append({'role': 'user', 'text': user_input})

        # Collect trip details
        if 'city' not in st.session_state['trip_details']:
            st.session_state['trip_details']['city'] = user_input
            response = "Great! What day are you planning for?"
        elif 'date' not in st.session_state['trip_details']:
            try:
                datetime.datetime.strptime(user_input, "%d %B %Y")  # Validate date format
                st.session_state['trip_details']['date'] = user_input
                response = "What time would you like to start and end your day?"
            except ValueError:
                response = "Please provide a valid date in the format '10 November 2024'."
        elif 'start_time' not in st.session_state['trip_details']:
            try:
                times = user_input.split(' to ')
                if len(times) == 2:
                    st.session_state['trip_details']['start_time'] = times[0].strip()
                    st.session_state['trip_details']['end_time'] = times[1].strip()
                    response = "Could you tell me your interests? Historical sites, food, or relaxing spots?"
                else:
                    raise ValueError("Invalid format. Please use '8 AM to 5 PM'.")
            except ValueError as e:
                response = f"Invalid input. {str(e)}"
        elif 'interests' not in st.session_state['trip_details']:
            st.session_state['trip_details']['interests'] = user_input
            response = "What's your budget for the day?"
        elif 'budget' not in st.session_state['trip_details']:
            st.session_state['trip_details']['budget'] = user_input
            response = "Where would you like to start your day? Provide your hotel or starting point."
        elif 'start_location' not in st.session_state['trip_details']:
            st.session_state['trip_details']['start_location'] = user_input
            response = "Generating your itinerary..."
            
            # Now use Groq to generate the itinerary and directly return the raw response
            itinerary = generate_itinerary(**st.session_state['trip_details'])
            response += f"\n\n{itinerary}"
        else:
            response = "Let me know if you’d like to adjust the plan."

        # Append AI response to the conversation history
        st.session_state['conversation_history'].append({'role': 'ai', 'text': response})
        display_chat()
    else:
        st.warning("Please enter some input.")

