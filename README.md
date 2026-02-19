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