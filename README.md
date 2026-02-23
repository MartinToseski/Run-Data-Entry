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
│ ├─ extract.py\
│ ├─ utils.py\
│ ├─ example.py\
│ ├─ data/\
│ │ └─ ne_110m_admin_0_countries/\
│\
├─ weather/\
│ ├─ weather_main.py\
│ ├─ client.py\
│ ├─ parsing.py\
│ ├─ constants.py\
│\
├─ calendar/\
│ ├─ calendar_main.py\
│ ├─ client.py\
│ ├─ parsing.py\
│ ├─ constants.py