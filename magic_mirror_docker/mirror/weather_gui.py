import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime  # Import datetime for current time and date

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

def create_gui():
    """
    Create a Tkinter GUI that mimics the home.html layout and displays weather data.
    """
    # Fetch weather data
    try:
        current_weather, forecast_list = fetch_weather()
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return

    # Initialize Tkinter root window
    root = tk.Tk()
    root.title("Weather GUI")
    root.geometry("800x600")
    root.configure(bg="#808080")  # Grey background

    # Simulated Transparency: Light grey for boxes
    box_color = "#b3b3b3"  # Blended grey (approx. 25% transparent effect)

    # Title
    title = tk.Label(root, text="Magic Mirror - Weather", font=("Arial", 20, "bold"), bg="#808080", fg="white")
    title.pack(pady=10)

    # Current Time and Date
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")  # Format time as HH:MM AM/PM
    current_date = now.strftime("%A, %B %d, %Y")  # Format date as Day, Month DD, YYYY
    time_date_frame = tk.Frame(root, bg=box_color)
    time_date_frame.pack(pady=10, padx=20, fill="x")

    time_label = tk.Label(
        time_date_frame,
        text=f"Time: {current_time}",
        font=("Arial", 14),
        bg=box_color,
        fg="white"
    )
    time_label.pack(side="left", padx=10, pady=10)

    date_label = tk.Label(
        time_date_frame,
        text=f"Date: {current_date}",
        font=("Arial", 14),
        bg=box_color,
        fg="white"
    )
    date_label.pack(side="left", padx=10, pady=10)

    # Current Weather Section
    current_frame = tk.Frame(root, bg=box_color)
    current_frame.pack(pady=10, padx=20, fill="x")
    
    # Current Weather Icon
    icon_url = f"http://openweathermap.org/img/wn/{current_weather['icon']}@2x.png"
    icon_response = requests.get(icon_url, stream=True)
    icon_image = Image.open(icon_response.raw)
    icon_photo = ImageTk.PhotoImage(icon_image)

    icon_label = tk.Label(current_frame, image=icon_photo, bg=box_color)
    icon_label.image = icon_photo  # Keep reference to avoid garbage collection
    icon_label.pack(side="left", padx=10, pady=10)

    # Current Weather Info
    weather_info = tk.Label(
        current_frame,
        text=f"Temperature: {current_weather['temp']}\nCondition: {current_weather['weather']}",
        font=("Arial", 14),
        bg=box_color,
        fg="white",
        justify="left"
    )
    weather_info.pack(side="left", padx=10, pady=10)

    # Forecast Section
    forecast_title = tk.Label(root, text="3-Hour Forecast (Next 15 Hours)", font=("Arial", 16, "bold"), bg="#808080", fg="white")
    forecast_title.pack(pady=10)

    forecast_frame = tk.Frame(root, bg="#808080")
    forecast_frame.pack(pady=10, padx=20)

    for forecast in forecast_list:
        # Forecast Card
        card = tk.Frame(forecast_frame, bg=box_color)
        card.pack(side="left", padx=10, pady=10, fill="y")

        # Forecast Icon
        icon_url = f"http://openweathermap.org/img/wn/{forecast['icon']}@2x.png"
        icon_response = requests.get(icon_url, stream=True)
        icon_image = Image.open(icon_response.raw)
        icon_photo = ImageTk.PhotoImage(icon_image)

        icon_label = tk.Label(card, image=icon_photo, bg=box_color)
        icon_label.image = icon_photo  # Keep reference to avoid garbage collection
        icon_label.pack(pady=5)

        # Forecast Info
        forecast_info = tk.Label(
            card,
            text=f"{forecast['datetime']}\n{forecast['temp']}\n{forecast['weather']}",
            font=("Arial", 12),
            bg=box_color,
            fg="white",
            justify="center"
        )
        forecast_info.pack(pady=5)

    # Run Tkinter Main Loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()