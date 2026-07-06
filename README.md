# 🌤️ SkyCast

### Your Window to Real-Time Weather

A premium server-rendered weather dashboard built with **Flask**,
**Jinja2**, and **custom CSS**.

## 🌟 Key Highlights

-   🌍 Automatic IP-Based User Location Detection (No JavaScript)
-   ⚡ 100% Server-Side Flask Application
-   🎨 Premium Glassmorphism UI
-   📅 7-Day Weather Forecast
-   📱 Fully Responsive
-   🚀 Ready for Render/Railway deployment

## ✨ Features

-   🌍 **Automatic User Location Detection** using server-side IP
    geolocation (approximate city, no JavaScript)
-   🔍 Live city search
-   🌡️ Current weather with feels-like, min/max temperature
-   📊 Today's highlights: humidity, pressure, wind, UV, visibility,
    sunrise/sunset, cloud cover
-   📅 7-day forecast
-   🎨 Glassmorphism UI
-   📱 Responsive design
-   ⚠️ Graceful error handling
-   🔐 Environment-variable based configuration

## 📍 Automatic User Location Detection

SkyCast detects the visitor's approximate city entirely on the
server: 1. Flask reads `request.remote_addr` 2. IP is sent to an IP
geolocation service (e.g. ipapi.co) 3. Approximate city is returned 4.
Weather loads automatically

**Advantages** - No JavaScript - No GPS - No browser permission
prompts - Fast server-side lookup

> Note: IP geolocation is approximate and localhost falls back to the
> default city.

## 🛠️ Tech Stack

-   Python
-   Flask
-   Jinja2
-   Custom CSS
-   requests
-   python-dotenv
-   Gunicorn
-   Open-Meteo API
-   IP Geolocation (ipapi.co / ip-api.com)


# 📂 Folder Structure

```
SkyCast/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── services/
│   └── weather_service.py
│
├── utils/
│   └── helpers.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── forecast.html
│   ├── settings.html
│   ├── about.html
│   ├── 404.html
│   └── 500.html
│
└── static/
    ├── css/
    │   └── style.css
    └── images/
        └── favicon.svg
```

---

## 🚀 Installation

``` bash
git clone https://github.com/your-username/skycast.git
cd skycast
python -m venv venv
```

Activate: - Windows: `venv\Scripts\activate` - Linux/macOS:
`source venv/bin/activate`

``` bash
pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

## 🌦️ Weather Data

Uses **Open-Meteo** (no API key required).

## ☁️ Deployment

Deploy on Render, Railway, PythonAnywhere, or Koyeb.

Start command:

``` bash
gunicorn app:app
```

Environment variables: - SECRET_KEY - DEFAULT_CITY - UNITS

## 🚀 Future Improvements

-   ⭐ Favorite cities
-   📍 Optional GPS-based precise location
-   🌍 Multi-language support
-   📈 Historical weather analytics
-   🌙 Light theme

## 📄 License

MIT License.

## 🙌 Credits

-   Weather: Open-Meteo
-   IP Geolocation: ipapi.co / ip-api.com

------------------------------------------------------------------------

### 👩‍💻 Developed by Pakhi Saxena

**SkyCast --- Your Window to Real-Time Weather.**
