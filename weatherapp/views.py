from django.shortcuts import render
from django.contrib import messages
import requests
import datetime


def home(request):
    if request.method == "POST" and "city" in request.POST:
        city = request.POST["city"]
    else:
        city = "Junnar"

    API_KEY = "f81c9212e1d4e86c48524caffe6686aa"
    PARAMS = {"units": "metric", "appid": API_KEY}
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}"
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}"

    GOOGLE_API_KEY = "AIzaSyBjXG3er1OTIhhhm5-CU5ll-_ERyBqJ8Lo"
    SEARCH_ENGINE_ID = "6670f1a9d27094807"
    image_url = "https://images.pexels.com/photos/3008509/pexels-photo-3008509.jpeg?auto=compress&cs=tinysrgb&w=1600"

    try:
        image_response = requests.get(
            f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={city} city wallpaper&searchType=image&imgSize=xxlarge&num=1"
        ).json()
        if "items" in image_response:
            image_url = image_response["items"][0]["link"]
    except:
        pass

    exception_occurred = False
    alerts = []
    forecast_days = []
    forecast_temps = []
    rain_expected = False
    rain_time = None

    try:
        # Current Weather
        weather_data = requests.get(weather_url, params=PARAMS).json()
        description = weather_data["weather"][0]["description"]
        icon = weather_data["weather"][0]["icon"]
        temp = weather_data["main"]["temp"]

        # Weather Alerts
        if "alerts" in weather_data:
            alerts = weather_data["alerts"]

        # 5-Day Forecast
        forecast_data = requests.get(forecast_url, params=PARAMS).json()
        daily_data = {}

        for entry in forecast_data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(entry)

        for day, entries in list(daily_data.items())[:5]:  # Next 5 days
            temps = [item["main"]["temp"] for item in entries]
            forecast_days.append(day)
            forecast_temps.append(round(sum(temps) / len(temps), 2))

        # Rain alert logic
        for entry in forecast_data["list"]:
            if "rain" in entry["weather"][0]["main"].lower():
                rain_expected = True
                rain_time = entry["dt_txt"]
                break

    except Exception as e:
        description = "clear sky"
        icon = "01d"
        temp = 25
        city = "Junnar"
        exception_occurred = True
        messages.error(request, "Weather data not available.")

    context = {
        "description": description,
        "icon": icon,
        "temp": temp,
        "day": datetime.date.today(),
        "city": city,
        "image_url": image_url,
        "exception_occurred": exception_occurred,
        "alerts": alerts,
        "forecast": forecast_days and forecast_temps,
        "forecast_days": forecast_days,
        "forecast_temps": forecast_temps,
        "rain_expected": rain_expected,
        "rain_time": rain_time,
    }

    return render(request, "weatherapp/index.html", context)
