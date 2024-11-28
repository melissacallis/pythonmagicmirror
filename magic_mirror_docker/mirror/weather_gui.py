import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime  
import os 
import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
from django.shortcuts import redirect, render
import requests
import subprocess# Import datetime for current time and date

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def fetch_weather():
    """
    Fetch current weather and forecast data from OpenWeatherMap API.
    """
    api_key = 'd60e365d43140a46b3afae19a3968f0e'  # Replace with your actual API key
    latitude = 27.800583
    longitude = -97.396378

    # URLs for Current Weather and Forecast APIs
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'

    # Fetch current weather
    params = {
        'lat': latitude,
        'lon': longitude,
        'units': 'imperial',
        'appid': api_key
    }
    current_response = requests.get(current_weather_url, params=params)
    forecast_response = requests.get(forecast_url, params=params)

    if current_response.status_code != 200 or forecast_response.status_code != 200:
        raise Exception("Failed to fetch weather data")

    # Parse current weather
    current_data = current_response.json()
    current_weather = {
        'temp': f"{current_data['main']['temp']}°F",
        'weather': current_data['weather'][0]['description'].capitalize(),
        'icon': current_data['weather'][0]['icon']
    }

    # Parse forecast data
    forecast_data = forecast_response.json()
    forecast_list = [
        {
            'datetime': item['dt_txt'],
            'temp': f"{item['main']['temp']}°F",
            'weather': item['weather'][0]['description'].capitalize(),
            'icon': item['weather'][0]['icon']
        }
        for item in forecast_data['list'][:5]  # First 5 entries (15 hours)
    ]

    return current_weather, forecast_list

def fetch_calendar_events():
    """
    Fetch Google Calendar events using the Calendar API.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return [
        {
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'summary': event.get('summary', 'No Title')
        }
        for event in events
    ]
    
def fetch_nytimes_headlines():
    """
    Fetch the latest NY Times headlines using the Top Stories API.
        """
    NYTIMES_API_KEY = "aJPG3CwEfz7Aeq73ItKUWxlHo2OiA2Yp"  # Replace with your actual API key
    NYTIMES_API_URL = "https://api.nytimes.com/svc/topstories/v2/home.json"
        
    try:
        # Send a GET request to the NY Times Top Stories API
        response = requests.get(NYTIMES_API_URL, params={"api-key": NYTIMES_API_KEY})
        response.raise_for_status()  # Raise an error for HTTP response codes 4xx/5xx
        data = response.json()
            
            # Extract and return the top 10 headlines
        return [
            {"title": article["title"], "url": article["url"]}
            for article in data.get("results", [])[:10]
        ]
    except requests.exceptions.RequestException as req_err:
        print(f"Request error fetching NY Times headlines: {req_err}")
    except KeyError as key_err:
        print(f"Key error processing NY Times data: {key_err}")
    except Exception as e:
        print(f"Unexpected error fetching NY Times headlines: {e}")
        
    return []

def create_gui():
    """
    Create a Tkinter GUI that displays weather data and Google Calendar events.
    """
    # Fetch weather and calendar data
    try:
        current_weather, forecast_list = fetch_weather()
        calendar_events = fetch_calendar_events()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Initialize Tkinter root window
    root = tk.Tk()
    root.title("Magic Mirror GUI")
    root.geometry("1024x768")
    root.configure(bg="black")

    # Transparent frame colors
    frame_color = "#D3D3D3"
    header_color = "#444444"
    text_color = "white"

    # Title
    title = tk.Label(root, text="Magic Mirror Dashboard", font=("Arial", 24, "bold"), bg=header_color, fg=text_color)
    title.pack(pady=10)

    # Forecast Section (Top Center)
    forecast_frame = tk.Frame(root, bg=frame_color)
    forecast_frame.pack(pady=10)
    tk.Label(forecast_frame, text="5-Day Forecast", font=("Arial", 18, "bold"), bg=header_color, fg=text_color).pack()

    forecast_cards = tk.Frame(forecast_frame, bg=frame_color)
    forecast_cards.pack()

    for forecast in forecast_list:
        card = tk.Frame(forecast_cards, bg=frame_color)
        card.pack(side="left", padx=5, pady=5)
        tk.Label(card, text=forecast['datetime'], font=("Arial", 12), bg=frame_color, fg="black").pack()
        tk.Label(card, text=f"Temp: {forecast['temp']}", font=("Arial", 12), bg=frame_color, fg="black").pack()
        tk.Label(card, text=forecast['weather'], font=("Arial", 12), bg=frame_color, fg="black").pack()

    # Left-Aligned Column
    column_frame = tk.Frame(root, bg=frame_color)
    column_frame.pack(side="left", padx=10, pady=10, fill="y")

    # Current Weather
    weather_frame = tk.Frame(column_frame, bg=frame_color)
    weather_frame.pack(fill="x", pady=5)
    tk.Label(weather_frame, text="Current Weather", font=("Arial", 14, "bold"), bg=header_color, fg=text_color).pack()
    tk.Label(weather_frame, text=f"Temp: {current_weather['temp']}", font=("Arial", 12), bg=frame_color, fg="black").pack()
    tk.Label(weather_frame, text=current_weather['weather'], font=("Arial", 12), bg=frame_color, fg="black").pack()

    # Current Time and Date
    time_frame = tk.Frame(column_frame, bg=frame_color)
    time_frame.pack(fill="x", pady=5)
    tk.Label(time_frame, text="Current Time and Date", font=("Arial", 14, "bold"), bg=header_color, fg=text_color).pack()

    now = datetime.now()
    tk.Label(time_frame, text=now.strftime("%I:%M %p"), font=("Arial", 12), bg=frame_color, fg="black").pack()
    tk.Label(time_frame, text=now.strftime("%A, %B %d, %Y"), font=("Arial", 12), bg=frame_color, fg="black").pack()

    # Calendar Events
    events_frame = tk.Frame(column_frame, bg=frame_color)
    events_frame.pack(fill="x", pady=5)
    tk.Label(events_frame, text="Upcoming Events", font=("Arial", 14, "bold"), bg=header_color, fg=text_color).pack()

    for event in calendar_events:
        tk.Label(events_frame, text=f"{event['start']} - {event['summary']}", font=("Arial", 12), bg=frame_color, fg="black").pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()