## 🏃 Run Data Entry – Personal Running Analytics System
### Overview
- - - 

##### This project is a personal data ingestion system designed to collect and store structured running-related data from multiple sources.

The current implementation focuses on Garmin Connect data extraction.
The long-term goal is to build a growing historical dataset (stored as CSV) for experimentation, analysis, and machine learning projects.

The system is designed to evolve into a modular data pipeline that integrates:
1) Garmin health and activity data
2) Weather data
3) Calendar data

Current Scope: Garmin Extraction.

###### The system extracts the following metrics:

### 📅 Date & Time
- Date
- Day of the week

### 🧠 Recovery & Readiness
- Training Status
- Last Night HRV
- Last Night Resting Heart Rate
- Last Night Sleep Score

### 🏃 Weekly Load
- Week cumulative kilometers run

### 🏃 Today’s Run (if applicable)
- Whether a run occurred today
- Distance
- Duration
- Training load
- Aerobic effect
- Anaerobic effect
- Run start time

### 📊 4-Week Rolling Averages
- Average weekly kilometers
- Average sleep score
- Average HRV
- Average resting heart rate

### ⏱ Recency Metrics
- Days since last run
- Days since last strength training
- Days since last quality session
- Aerobic effect of last run
- Anaerobic effect of last run

### 🌍 Location & Travel
- Most recent detected country
- Whether travel occurred within the last two weeks

---

### Weather Data Extraction
The system now also integrates weather metrics from **Open-Meteo** for the user’s location, including:

#### Hourly Data (optional per hour or median of day)
- Apparent temperature  
- Rain, showers, snowfall, snow depth  
- Wind speed  
- Weather code  

#### Daily Data
- Weather code  
- Sunrise & sunset  
- Daylight duration  
- Temperature max, min, mean  
- Apparent temperature mean  
- Rain, showers, snowfall totals  
- Precipitation hours  

---

## Project Structure
code/
├─ garmin/
│ ├─ extract.py # Garmin extraction functions
│ ├─ utils.py # Utility functions for dates, calculations
│ ├─ example.py # Garmin API authentication
│
├─ weather/
│ ├─ weather_main.py # Main entry point for weather extraction
│ ├─ client.py # Open-Meteo client with caching & retry
│ ├─ parsing.py # Parsing helpers for hourly/daily weather
│ ├─ constants.py # Weather API constants
│
data/
└─ ne_110m_admin_0_countries/ # Country shapefiles for Garmin location mapping

## Credits
- Garmin extraction built on top of: [python-garminconnect](https://github.com/cyberjunky/python-garminconnect/tree/master)  
- Weather integration uses: [Open-Meteo Historical API](https://open-meteo.com/)