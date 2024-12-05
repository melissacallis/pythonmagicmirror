
import requests

from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
from django.shortcuts import redirect, render
import requests
import random
import sys
import isodate
import yfinance as yf

import http.client
import json

import http.client
import json


# Google Calendar API Scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def home(request):
    # OpenWeatherMap API details
    api_key = os.getenv("API_KEY_WEATHER")  # Replace with your actual OpenWeatherMap API key
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
    
    zen_saying = get_zen_saying()

    # Fetch NY Times headlines
    nytimes_headlines = fetch_nytimes_headlines()
    
     # Default stock tickers
    stock_tickers = ["AAPL", "GOOGL", "MSFT", "MMLP"]
    

    stock_data = []
    for ticker in stock_tickers:
        data = get_yahoo_stock_data(ticker)
        if data:
            stock_data.append(data)
    #print(f"Stock data passed to template: {stock_data}")

    # Fetch sports-headline data
    #stock_data = [get_stock_data(ticker) for ticker in stock_tickers]

    sports_headlines= fetch_sports_headlines()
    
    # Pass data to the template
    # Fetch YouTube Shorts
    youtube_shorts = fetch_youtube_shorts()
    
        
    context = {
        'current': current_weather,
        'forecast': forecast_list,
        'events': calendar_events,
        'nytimes_headlines': nytimes_headlines,
        'zen_saying': get_zen_saying(),
        "stocks": stock_data,
        "youtube_shorts": youtube_shorts,
        'sports_headlines': sports_headlines,
        
        }  # Add NY Times headlines to the
    
   
    

    
    return render(request, 'mirror/home.html', context)

def get_zen_saying():
    sayings = [
"Feelings are just visitors. Let them come and go.",
"Don’t fight with your thoughts; just observe them and they will dissolve.",
"The mind loves to create problems, but it also loves to invent solutions.",
"Be the sky, not the clouds.",
"Happiness is your nature. It is not wrong to desire it. What is wrong is seeking it outside when it is inside.",
    ]
    return random.choice(sayings)

import http.client
import json

def fetch_sports_headlines():
    """Fetch sports headlines from the NFL API."""
    conn = http.client.HTTPSConnection("nfl-football-api.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "ffda10e22cmshcb6236d6bc8f365p1b8b5djsn88764eb5fd75",
        'x-rapidapi-host': "nfl-football-api.p.rapidapi.com"
    }

    try:
        conn.request("GET", "/nfl-single-news?id=40342801", headers=headers)
        res = conn.getresponse()
        data = res.read()

        # Decode JSON response
        articles = json.loads(data.decode("utf-8"))

        headlines = []
        # Process the main headlines
        for article in articles.get('headlines', []):
            headline = article.get('title', 'No headline available')
            description = article.get('description', '')
            image_url = article.get('images', [{}])[0].get('url', '') if article.get('images') else ''
            web_url = article.get('links', {}).get('web', {}).get('href', '#')

            if image_url:  # Ensure main headline has an image
                headlines.append({
                    'headline': headline,
                    'description': description,
                    'image_url': image_url,
                    'web_url': web_url,
                })

            # Process related articles
            for related in article.get('related', []):
                related_headline = related.get('title', 'No related headline available')
                related_image_url = related.get('images', [{}])[0].get('url', '') if related.get('images') else ''
                related_web_url = related.get('links', {}).get('web', {}).get('href', '#')

                if related_image_url:  # Ensure related article has an image
                    headlines.append({
                        'headline': related_headline,
                        'description': '',
                        'image_url': related_image_url,
                        'web_url': related_web_url,
                    })

        print("Processed headlines for template:", headlines)
        return headlines
    except Exception as e:
        print(f"Error fetching sports headlines: {e}")
        return []

    
    
def get_yahoo_stock_data(ticker):
    """
    Fetch and print all raw stock data from the Yahoo Finance API for debugging.
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        # Print the entire raw response to the terminal for debugging
        #print(f"Raw data fetched for {ticker}:")
        #for key, value in stock_info.items():
         #   print(f"{key}: {value}")

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
        #print(f"Error fetching stock data for {ticker}: {e}")
        return None
    
def fetch_full_stock_data_raw(ticker):
    stock = yf.Ticker(ticker)
    #print(f"Raw object for {ticker}: {stock}")
    #print(f"Methods available: {dir(stock)}")

   
def fetch_weather():
    """
    Fetch current weather and forecast data from OpenWeatherMap API.
    """
    api_key = os.getenv("API_KEY_WEATHER")
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
    """
    Safely splits event_datetime into date and time, handling potential timezone offsets.
    """
    try:
        if 'T' in event_datetime:  # If `dateTime` includes a time part
            date_part, time_part = event_datetime.split('T')
            time_part = time_part.split('+')[0].split('-')[0]  # Remove timezone offset if present
            return date_part, time_part
        else:  # If only `date` is present
            return event_datetime, None  # Return only date
    except Exception as e:
        print(f"Error formatting datetime: {e}")
        return "Invalid Date", "Invalid Time"


def fetch_calendar_events():
    """
    Fetch upcoming Google Calendar events and format their date and time fields.
    """
    # Replace the mock data with the actual API call as shown below:
    try:
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
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        print(f"Raw events: {events}")
        
        formatted_events = []
        for event in events:
            event_datetime = event['start'].get('dateTime', event['start'].get('date', ''))
            date_part, time_part = format_event_datetime(event_datetime)
            formatted_events.append({
                "date": date_part,
                "time": time_part,
                "summary": event.get("summary", "No Title"),
            })
            
        return formatted_events

    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []

    
def fetch_nytimes_headlines():
    """
    Fetch the latest NY Times headlines using the Top Stories API.
    """
    NYTIMES_API_KEY = os.getenv("NYTIMES_API_KEY")
    NYTIMES_API_URL = "https://api.nytimes.com/svc/topstories/v2/home.json"

    try:
        response = requests.get(NYTIMES_API_URL, params={"api-key": NYTIMES_API_KEY})
        response.raise_for_status()
        data = response.json()

        # Extract and handle multimedia data
        headlines = []
        for article in data.get("results", [])[:10]:
            # Check if multimedia exists
            if article.get("multimedia"):
                # Look for 'superJumbo' format
                image_url = next(
                    (media["url"] for media in article["multimedia"] if media["format"] == "Super Jumbo"),
                    None
                )
                # If 'superJumbo' not found, fallback to first image
                if not image_url:
                    image_url = article["multimedia"][0]["url"]
            else:
                # Use a placeholder if no multimedia is available
                image_url = "https://via.placeholder.com/800x400?text=No+Image+Available"

            # Append the processed headline data
            headlines.append({
                "title": article.get("title", "No Title"),
                "abstract": article.get("abstract", ""),
                "url": article.get("url", "#"),
                "image_url": image_url,
            })

        return headlines
    except Exception as e:
        print(f"Error fetching NY Times headlines: {e}")
        return []

       





def fetch_youtube_shorts():
    """
    Fetch the top two sports-related YouTube Shorts.
    """
    
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    if not API_KEY:
        print("YouTube API key not found in environment variables.")
        return []

    # Build the YouTube API client
    youtube = build("youtube", "v3", developerKey=API_KEY)

    # Define search parameters
    search_params = {
        "part": "snippet",
        "maxResults": 10,  # Fetch more results to filter later
        "q": "sports #shorts",  # Include "sports" keyword and Shorts hashtag
        "type": "video",
        "videoDuration": "any",  # Fetch videos of any length
        "order": "viewCount",    # Order by view count
        "safeSearch": "moderate" # Safe search filter
    }

    try:
        # Fetch search results
        response = youtube.search().list(**search_params).execute()
        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]

        # Fetch video details for duration and filtering
        videos_response = youtube.videos().list(
            part="snippet,contentDetails",
            id=",".join(video_ids)
        ).execute()

        shorts = []
        for video in videos_response.get("items", []):
            duration = video["contentDetails"]["duration"]
            snippet = video["snippet"]
            duration_seconds = isodate.parse_duration(duration).total_seconds()

            # Filter for videos less than or equal to 60 seconds
            if duration_seconds <= 60:
                shorts.append({
                    "video_id": video["id"],
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "thumbnail_url": snippet["thumbnails"]["high"]["url"],
                    "video_url": f"https://www.youtube.com/watch?v={video['id']}"
                })

            # Stop when we have 2 Shorts
            if len(shorts) == 2:
                break

        return shorts

    except Exception as e:
        print(f"Error fetching YouTube Shorts: {e}")
        return []

    except Exception as e:
        print(f"Error fetching YouTube Shorts: {e}")
        return []

# Arlo credentials (store securely in environment variables)
ARLO_USERNAME = os.getenv("ARLO_USERNAME")  # Replace with your Arlo username
ARLO_PASSWORD = os.getenv("ARLO_PASSWORD")  # Replace with your Arlo password

