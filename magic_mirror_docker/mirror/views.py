import requests  # Import requests for making HTTP requests
import subprocess
from django.shortcuts import redirect, render
from PIL import Image, ImageTk  # Import for GUI-related tasks
import os

def home(request):
    # OpenWeatherMap API details
    api_key = 'd60e365d43140a46b3afae19a3968f0e'# Replace with your actual OpenWeatherMap 
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
        'icon': current_data['weather'][0]['icon']
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

    # Pass data to the template
    context = {
        'current': current_weather,
        'forecast': forecast_list
    }
    return render(request, 'mirror/home.html', context)

def launch_gui(request):
    """
    Handles the request to launch the GUI application.
    """
    try:
        # Use the correct absolute path to weather_gui.py
        gui_script_path = os.path.join(
            "C:/Users/calli/OneDrive/Documents/GitHub/pythonmagicmirror/magic_mirror_docker/mirror/weather_gui.py"
        )

        # Launch the GUI application
        subprocess.Popen(["python", gui_script_path], shell=True)

        # Redirect to home page
        return redirect("home")
    except Exception as e:
        # Render error page if launching GUI fails
        return render(request, 'mirror/error.html', {'error': f"Failed to launch GUI: {str(e)}"})
