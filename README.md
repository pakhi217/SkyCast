<div align="center">

# 🌤️ SkyCast

### Your Window to Real-Time Weather.

A premium, server-rendered weather dashboard built with **Flask, Jinja2, and hand-crafted CSS** — no JavaScript frameworks, no UI libraries, just clean Python and clean CSS.

![SkyCast Banner](static/images/banner-placeholder.png)

</div>

---

## ✨ Features

- 🔍 **Live city search** — search any city on Earth for real-time conditions
- 🌡️ **Current weather hero card** — large icon, temperature, "feels like", min/max
- 📊 **Today's Highlights** — humidity, pressure, wind speed, visibility, UV index, sunrise, sunset, cloud cover
- 📅 **7-Day Forecast** — condensed daily summaries with icons and min/max temps
- 🎨 **Dark Glassmorphism UI** — blurred glass cards, gradient headers, soft shadows
- 🧭 **Sidebar navigation** — Dashboard, Forecast, Settings, About
- ⚠️ **Graceful error handling** — friendly messages for unknown cities or API failures
- 📱 **Fully responsive** — adapts from ultra-wide monitors down to small phones
- 🖼️ **Custom 404 & 500 pages** — on-brand, not the Flask defaults
- 💫 **CSS-only animations** — fade-in cards, floating weather icons, hover transitions
- 🔐 **Secrets stay secret** — API key loaded from `.env`, never hardcoded

---

## 📸 Screenshots

> Add your own screenshots to `static/images/` and reference them here once the app is running locally.

| Dashboard | Forecast |
|---|---|
| `static/images/screenshot-dashboard.png` | `static/images/screenshot-forecast.png` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Templates | Jinja2 |
| Styling | Hand-written CSS3 (Glassmorphism) |
| HTTP Client | `requests` |
| Config | `python-dotenv` |
| Production Server | `gunicorn` |
| Weather Data | [Open-Meteo API](https://open-meteo.com/) (free, no API key required) |

No JavaScript, no React/Vue/Angular, no Bootstrap/Tailwind/jQuery — every interaction is powered by standard HTML forms and Flask routing.

---

## 📂 Folder Structure

```
SkyCast/
├── app.py                     # Flask app & routes
├── config.py                  # Centralized environment-based configuration
├── requirements.txt           # Python dependencies
├── README.md
├── .env.example                # Template for required environment variables
├── .gitignore
│
├── services/
│   └── weather_service.py     # All OpenWeatherMap API integration logic
│
├── utils/
│   └── helpers.py             # Reusable formatting/date/unit helper functions
│
├── templates/
│   ├── base.html               # Shared layout: sidebar, header, footer
│   ├── index.html              # Dashboard page (search, current weather, highlights)
│   ├── forecast.html            # Dedicated 7-day forecast page
│   ├── settings.html            # Dedicated settings page
│   ├── about.html               # Dedicated about page
│   ├── 404.html                 # Custom "not found" page
│   └── 500.html                 # Custom "server error" page
│
└── static/
    ├── css/
    │   └── style.css            # Complete hand-written glassmorphism stylesheet
    └── images/
        └── favicon.svg           # Custom SVG favicon
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/skycast.git
cd skycast
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Then open `.env` and add your OpenWeatherMap API key (see setup instructions below).

### 5. Run the app

```bash
python app.py
```

The dashboard will be available at **http://127.0.0.1:5000**.

---

## 🔑 API Setup (Open-Meteo)

Nothing to set up! SkyCast uses [Open-Meteo](https://open-meteo.com/), a free weather API that requires **no API key, no sign-up, and no credit card** for non-commercial use (up to 10,000 calls/day).

Under the hood, SkyCast makes two calls per search:
1. **Geocoding API** — resolves the city name you typed into latitude/longitude.
2. **Forecast API** — fetches current conditions and a 7-day daily forecast for those coordinates, including UV index and visibility.

Since there's no key to configure, just install the dependencies and run the app — it works immediately.

---

## ☁️ Deployment

SkyCast ships with `gunicorn` for production use.

```bash
gunicorn app:app --bind 0.0.0.0:8000
```

**Deploying to a platform (Render, Railway, Heroku-style hosts, etc.):**

1. Set the start command to `gunicorn app:app`.
2. Add `OPENWEATHER_API_KEY`, `SECRET_KEY`, `UNITS`, and `DEFAULT_CITY` as environment variables in your host's dashboard (never commit `.env`).
3. Set `FLASK_DEBUG=False` in production.

---

## 🧭 Future Improvements

- 🔎 City autocomplete using OpenWeatherMap's Geocoding API
- 🌍 Multi-language support for weather descriptions
- 📍 "Use my location" geolocation-based lookup
- 📈 Historical weather trend charts
- 🌓 Light theme toggle alongside the current dark glassmorphism theme
- ⭐ Saved/favorite cities list with persistent storage

---

## 📄 License

This project is released under the **MIT License**. You are free to use, modify, and distribute it for personal or commercial projects.

---

## 🙌 Credits

- Weather data provided by [Open-Meteo](https://open-meteo.com/) (CC BY 4.0)
- Fonts: [Manrope](https://fonts.google.com/specimen/Manrope) & [Inter](https://fonts.google.com/specimen/Inter) via Google Fonts
- Designed & built with ❤️ using Flask, Jinja2, and hand-written CSS

<div align="center">

**SkyCast** — Your Window to Real-Time Weather.
[GitHub](https://github.com/your-username/skycast)

</div>
