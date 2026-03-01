# 🏃 Run Data Entry – Personal Running Analytics System

## Overview
This project is a personal data ingestion system designed to collect and store structured running-related data from multiple sources.

The goal is to build a growing historical dataset (stored as CSV) for experimentation, longitudinal analysis, and future machine learning projects.

The system is structured as a modular data pipeline integrating:

1. Garmin health and activity data  
2. Weather data (Open-Meteo)  
3. Google Calendar data  

Each module is independently responsible for extracting and structuring its respective data.

---

# Current Capabilities

## 🟦 Garmin Data Extraction
Provides structured running, recovery, and location metrics.

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

## 🌤 Weather Data Extraction (Open-Meteo)
Weather data is fetched using the location coordinates extracted from Garmin.

### Hourly Data (run-hour specific or daily median)
- Apparent temperature  
- Rain  
- Showers  
- Snowfall  
- Snow depth  
- Wind speed  
- Weather code  

### Daily Aggregates
- Weather code  
- Sunrise & sunset  
- Daylight duration  
- Temperature (max / min / mean)  
- Apparent temperature mean  
- Rain / showers / snowfall totals  
- Precipitation hours  

---

## 📅 Google Calendar Data Extraction
Calendar data is used to quantify daily cognitive and time-load context.

### Daily Metrics
- Total class hours  
- Total work/meeting hours  
- Morning activity (before 10am)  
- Evening activity (after 5pm)  
- Gym availability (KTU gym) 

### Upcoming Load
- Presence of deadlines within the next 3 days  
  (Detected via keyword filtering in event summaries)

---

# Project Structure
code/\
├─ garmin/\
│ ├─ extract.py &emsp;&emsp;&emsp;&emsp;# Garmin extraction functions\
│ ├─ utils.py &emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;# Utility functions for dates and calculations\  
│ ├─ client.py &emsp;&emsp;&emsp;&emsp;&nbsp; # Garmin API authentication\
│ ├─ data/ &emsp;&emsp;\
│ │ └─ 
│\
├─ weather/\
│ ├─ weather_main.py &emsp;# Weather extraction entry point\
│ ├─ client.py &emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp; # Open-Meteo API client with caching & retry\
│ ├─ parsing.py &emsp;&emsp;&emsp;&nbsp;&nbsp;&nbsp;# Parsing helpers for hourly/daily weather\
│ ├─ constants.py &emsp;&emsp;&nbsp;&nbsp; # API constants\
│\
├─ calendar/\
│ ├─ calendar_main.py &nbsp; # Calendar extraction entry point\
│ ├─ client.py &emsp;&emsp;&emsp;&emsp;&nbsp; # Google Calendar API client & authentication\
│ ├─ parsing.py &emsp;&emsp;&emsp;&nbsp; # Parsing & processing helpers\
│ ├─ constants.py &emsp;&emsp;&nbsp; # Calendar constants\
│\
├─ pipeline/\
│ ├─ run_pipeline.py &emsp; # Runs the full data pipeline\
│ ├─ aggregator.py &emsp;&nbsp;&nbsp; # Combines Garmin, Weather, Calendar data\
│ ├─ schema.py &emsp;&emsp;&nbsp;&nbsp;&nbsp; # Final schema for CSV storage\
│ ├─ storage.py &emsp;&emsp;&nbsp;&nbsp;&nbsp;&nbsp; # Handles CSV persistence\
data/\
├─ running_dataset.csv &emsp;&emsp;&emsp;&emsp;&emsp;&nbsp; # Aggregated CSV dataset\
├─ ne_110m_admin_0_countries &emsp; # Country shapefiles for location mapping\