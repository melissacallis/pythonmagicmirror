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
import subprocess


# Google Calendar API Scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def home(request):
    # OpenWeatherMap API details
    api_key = 'd60e365d43140a46b3afae19a3968f0e'  # Replace with your actual OpenWeatherMap API key
    latitude = 27.800583
    longitude = -97.396378

    # URLs for Current Weather and Forecast APIs
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'

    # Fetch current weather
    current_params = {
        'lat': latitude,
        'lon': longitude,
        'units': 'imperial',
        'appid': api_key
    }
    current_response = requests.get(current_weather_url, params=current_params)
    if current_response.status_code != 200:
        return render(request, 'mirror/error.html', {'error': f"Failed to fetch current weather: {current_response.text}"})

    current_data = current_response.json()
    current_weather = {
        'temp': current_data['main']['temp'],
        'weather': current_data['weather'][0]['description'],
        'icon': current_data['weather'][0]['icon'],
                   
    }
        
    # Fetch forecast data
    forecast_response = requests.get(forecast_url, params=current_params)
    if forecast_response.status_code != 200:
        return render(request, 'mirror/error.html', {'error': f"Failed to fetch forecast: {forecast_response.text}"})

    forecast_data = forecast_response.json()
    forecast_list = [
        {
            'datetime': item['dt_txt'],
            'temp': item['main']['temp'],
            'weather': item['weather'][0]['description'],
            'icon': item['weather'][0]['icon']
        }
        for item in forecast_data['list'][:5]
    ]

    # Fetch Google Calendar events
    calendar_events = get_calendar_events()

    # Pass data to the template
    context = {
        'current': current_weather,
        'forecast': forecast_list,
        'events': calendar_events  # Add events to the context
    }
    return render(request, 'mirror/home.html', context)


import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope of access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_events():
    """
    Fetches the next 10 upcoming events from the user's primary Google Calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Initiate the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Build the service
        service = build('calendar', 'v3', credentials=creds)
        # Get the current time
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        # Fetch the next 10 events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        # Return the events
        return events
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
if __name__ == '__main__':
    events = get_calendar_events()
    if not events:
        print('No upcoming events found.')
    else:
        for event in events:
            # Get the start time and summary
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            print(f"{start}: {summary}")


def launch_gui(request):
    """
    Handles the request to launch the GUI application.
    """
    try:
        # Provide the absolute path to weather_gui.py
        gui_script_path = os.path.join(
            "C:/Users/calli/OneDrive/Documents/GitHub/pythonmagicmirror/magic_mirror_docker/mirror/weather_gui.py"
        )

        # Launch the GUI application
        subprocess.Popen(["python", gui_script_path], shell=True)

        # Redirect to the home page after launching the GUI
        return redirect("home")
    except Exception as e:
        # Render an error page if launching GUI fails
        return render(request, 'mirror/error.html', {'error': f"Failed to launch GUI: {str(e)}"})


def fetch_weather():
    """
    Fetch current weather and forecast data from OpenWeatherMap API.
    """
    api_key = 'd60e365d43140a46b3afae19a3968f0'
    latitude = 27.800583
    longitude = -97.396378

    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'

    params = {'lat': latitude, 'lon': longitude, 'units': 'imperial', 'appid': api_key}
    current_response = requests.get(current_weather_url, params=params)
    forecast_response = requests.get(forecast_url, params=params)

    if current_response.status_code != 200 or forecast_response.status_code != 200:
        raise Exception("Failed to fetch weather data")

    current_data = current_response.json()
    current_weather = {
        'temp': f"{current_data['main']['temp']}°F",
        'weather': current_data['weather'][0]['description'].capitalize(),
        'icon': current_data['weather'][0]['icon']
    }

    forecast_data = forecast_response.json()
    forecast_list = [
        {
            'datetime': item['dt_txt'],
            'temp': f"{item['main']['temp']}°F",
            'weather': item['weather'][0]['description'].capitalize(),
            'icon': item['weather'][0]['icon']
        }
        for item in forecast_data['list'][:5]
    ]

    return current_weather, forecast_list

 data["results"][:10]  # Get top 10 headlines
        ]
        return articles
    except Exception as e:
        print(f"Error fetching NYTimes headlines: {e}")
        return []

def home(request):
    """
    Display the home page with NYTimes headlines.
    """
    nytimes_headlines = fetch_nytimes_headlines()
    return render(request, "mirror/home.html", {"nytimes_headlines": nytimes_headlines})

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

def create_gui():
    """
    Create a Tkinter GUI that mimics the home.html layout and displays weather data and calendar events.
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

    # Background Image
    bg_image_path = "background.jpg"  # Replace with the actual image path
    bg_image = Image.open(bg_image_path)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)

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


