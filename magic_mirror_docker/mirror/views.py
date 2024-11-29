
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
import datetime
import random
import sys
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf

import yfinance as yf


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
    calendar_events = fetch_calendar_events()

    # Fetch NY Times headlines
    nytimes_headlines = fetch_nytimes_headlines()
     # Default stock tickers
    stock_tickers = ["AAPL", "GOOGL", "MSFT", "MMLP"]
    

    stock_data = []
    for ticker in stock_tickers:
        data = get_yahoo_stock_data(ticker)
        if data:
            stock_data.append(data)
    print(f"Stock data passed to template: {stock_data}")

    # Fetch stock data
    #stock_data = [get_stock_data(ticker) for ticker in stock_tickers]

    
    # Pass data to the template
    context = {
        'current': current_weather,
        'forecast': forecast_list,
        'events': calendar_events,
        'nytimes_headlines': nytimes_headlines,
        'zen_saying': get_zen_saying(),
        "stocks": stock_data,
        }  # Add NY Times headlines to the
    
    return render(request, 'mirror/home.html', context)



def get_yahoo_stock_data(ticker):
    """
    Fetch and print all raw stock data from the Yahoo Finance API for debugging.
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        # Print the entire raw response to the terminal for debugging
        print(f"Raw data fetched for {ticker}:")
        for key, value in stock_info.items():
            print(f"{key}: {value}")

        # Example of extracting specific fields (you can customize these as needed)
        stock_data = {
            "symbol": stock_info.get("symbol", ticker),
            "price": stock_info.get("currentPrice"),
            "currency": stock_info.get("currency", "N/A"),
            "fifty_two_week_high": stock_info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": stock_info.get("fiftyTwoWeekLow"),
            "fifty_two_week_change": stock_info.get("52WeekChange"),
            
        }

        return stock_data
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None
    
def fetch_full_stock_data_raw(ticker):
    stock = yf.Ticker(ticker)
    print(f"Raw object for {ticker}: {stock}")
    print(f"Methods available: {dir(stock)}")

   




def get_zen_saying():
    sayings = [
"Feelings are just visitors. Let them come and go.",
"Don’t fight with your thoughts; just observe them and they will dissolve.",
"The mind loves to create problems, but it also loves to invent solutions.",
"Be the sky, not the clouds.",
"Happiness is your nature. It is not wrong to desire it. What is wrong is seeking it outside when it is inside.",
    ]
    return random.choice(sayings)
    
        
 # Define the scope of access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
    print(f"Current weather response: {current_response.json()}")
    print(f"NY Times headlines: {fetch_nytimes_headlines()}")


    return current_weather, forecast_list



def format_event_datetime(event_datetime):
    """Split event_datetime into date and time."""
    try:
        print(f"Raw event_datetime input: {event_datetime}")  # Debugging input
        if 'T' in event_datetime:  # Check if it contains both date and time
            date_part, time_part = event_datetime.split('T')
            time_part = time_part.split('-')[0]  # Remove timezone info if present
            return date_part, time_part  # Return date and time separately
        else:
            return event_datetime, None  # Return only date if no time is present
    except Exception as e:
        print(f"Error formatting datetime: {e}")
        return "Invalid Date", "Invalid Time"


def fetch_calendar_events():
    # Mocked Google Calendar data for demonstration
    events = [
        {"start": {"dateTime": "2024-11-29T19:00:00-06:00", "timeZone": "America/Chicago"}, "summary": "Time to take medicine"},
        {"start": {"date": "2024-12-01"}, "summary": "Doctor's appointment"},
    ]

    formatted_events = []
    for event in events:
        event_datetime = event["start"].get("dateTime", event["start"].get("date", ""))
        date_part, time_part = format_event_datetime(event_datetime)  # Split into date and time
        formatted_events.append({
            "date": date_part,
            "time": time_part,
            "summary": event["summary"],
        })

    print(f"Formatted events: {formatted_events}")  # Debugging formatted output
    return formatted_events

    
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




