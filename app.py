
import json
import os
import random
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


st.set_page_config(
    page_title="Smart Agriculture Monitoring",
    page_icon="🌱",
    layout="wide"
)


# ---------------- FIREBASE CONNECTION ----------------

def connect_firebase():

    if not firebase_admin._apps:

        key_path = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )

        if key_path:
            firebase_cred = credentials.Certificate(key_path)

        else:
            firebase_info = json.loads(
                st.secrets["firebase_credentials"]
            )
            firebase_cred = credentials.Certificate(firebase_info)

        firebase_admin.initialize_app(firebase_cred)

    return firestore.client()


try:
    db = connect_firebase()

except Exception as error:
    st.error("Firebase connection failed.")
    st.code(str(error))
    st.stop()


# ---------------- FIRESTORE DATA ----------------

def add_sensor_reading(timestamp, soil, temperature, humidity, light):

    reading = {
        "timestamp": timestamp,
        "soil_moisture": soil,
        "temperature": temperature,
        "humidity": humidity,
        "light_intensity": light
    }

    db.collection("sensor_readings").add(reading)


def get_readings():

    documents = db.collection("sensor_readings").stream()

    records = []

    for document in documents:
        records.append(document.to_dict())

    data = pd.DataFrame(records)

    if data.empty:
        return data

    required_columns = [
        "timestamp",
        "soil_moisture",
        "temperature",
        "humidity",
        "light_intensity"
    ]

    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    # Convert every timestamp to a common UTC timezone
    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        format="mixed",
        errors="coerce",
        utc=True
    )

    for column in required_columns[1:]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna(subset=required_columns)

    data = data.sort_values("timestamp")

    return data


# ---------------- SENSOR SIMULATION ----------------

def generate_sensor_reading():

    add_sensor_reading(
        datetime.now(timezone.utc).isoformat(),
        round(random.uniform(10, 80), 2),
        round(random.uniform(20, 45), 2),
        round(random.uniform(30, 90), 2),
        round(random.uniform(1000, 10000), 2)
    )


def generate_sample_data():

    for i in range(24):

        timestamp = (
            datetime.now(timezone.utc)
            - timedelta(hours=23 - i)
        ).isoformat()

        add_sensor_reading(
            timestamp,
            round(random.uniform(10, 80), 2),
            round(random.uniform(20, 45), 2),
            round(random.uniform(30, 90), 2),
            round(random.uniform(1000, 10000), 2)
        )


# ---------------- SIDEBAR ----------------

st.sidebar.title("Farm Control")

st.sidebar.write("Project: Smart Agriculture")
st.sidebar.write("Database: Firebase Firestore")
st.sidebar.write("Mode: MQTT Sensor Monitoring")

if st.sidebar.button("Generate New Sensor Reading"):
    generate_sensor_reading()
    st.rerun()

if st.sidebar.button("Generate 24 Hours Sample Data"):
    generate_sample_data()
    st.rerun()

if st.sidebar.button("Refresh Dashboard"):
    st.rerun()


# ---------------- MAIN DASHBOARD ----------------

st.title("🌱 Smart Agriculture Monitoring System")

st.subheader(
    "Real-Time Sensor Monitoring and Analytics Dashboard"
)

st.info(
    "Sensor readings are received through MQTT, stored in "
    "Firebase Firestore, and displayed on this dashboard. "
    "Use Refresh Dashboard to fetch the latest readings."
)

data = get_readings()

if data.empty:
    st.warning("No sensor readings available yet.")
    st.stop()


# ---------------- LATEST READINGS ----------------

latest = data.iloc[-1]

st.header("Live Sensor Readings")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Soil Moisture",
    f"{latest['soil_moisture']:.2f}%"
)

col2.metric(
    "Temperature",
    f"{latest['temperature']:.2f} °C"
)

col3.metric(
    "Humidity",
    f"{latest['humidity']:.2f}%"
)

col4.metric(
    "Light Intensity",
    f"{latest['light_intensity']:.2f} Lux"
)


# ---------------- ALERTS ----------------

st.header("Farm Alerts")

alerts = []

if latest["soil_moisture"] < 25:
    alerts.append(
        "Low soil moisture! Irrigation is required."
    )

if latest["temperature"] > 40:
    alerts.append(
        "High temperature detected!"
    )

if alerts:
    for alert in alerts:
        st.error(alert)
else:
    st.success(
        "No critical alerts. Farm conditions are normal."
    )


# ---------------- CROP HEALTH ----------------

st.header("Crop Health Indicator")

if (
    latest["soil_moisture"] < 25
    or latest["temperature"] > 40
):
    st.warning(
        "Crop condition requires attention."
    )
else:
    st.success(
        "Crop conditions are currently within the alert limits."
    )


# ---------------- SENSOR TRENDS ----------------

st.header("Real-Time Sensor Trends")

chart_data = data.tail(100)

fig1 = px.line(
    chart_data,
    x="timestamp",
    y="soil_moisture",
    title="Soil Moisture Trend (%)"
)

st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(
    chart_data,
    x="timestamp",
    y="temperature",
    title="Temperature Trend (°C)"
)

st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(
    chart_data,
    x="timestamp",
    y="humidity",
    title="Humidity Trend (%)"
)

st.plotly_chart(fig3, use_container_width=True)

fig4 = px.line(
    chart_data,
    x="timestamp",
    y="light_intensity",
    title="Light Intensity Trend (Lux)"
)

st.plotly_chart(fig4, use_container_width=True)


# ---------------- HOURLY ANALYTICS ----------------

st.header("Hourly Analytics Report")

hourly_data = data.copy()

hourly_data["hour"] = (
    hourly_data["timestamp"].dt.floor("h")
)

hourly_report = hourly_data.groupby("hour").agg(
    Average_Soil_Moisture=("soil_moisture", "mean"),
    Average_Temperature=("temperature", "mean"),
    Average_Humidity=("humidity", "mean"),
    Average_Light_Intensity=("light_intensity", "mean")
).reset_index()

st.dataframe(
    hourly_report,
    use_container_width=True
)


# ---------------- DAILY ANALYTICS ----------------

st.header("Daily Analytics Report")

daily_data = data.copy()

daily_data["date"] = (
    daily_data["timestamp"].dt.date
)

daily_report = daily_data.groupby("date").agg(
    Average_Soil_Moisture=("soil_moisture", "mean"),
    Average_Temperature=("temperature", "mean"),
    Average_Humidity=("humidity", "mean"),
    Average_Light_Intensity=("light_intensity", "mean")
).reset_index()

st.dataframe(
    daily_report,
    use_container_width=True
)

csv_data = daily_report.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Daily Analytics Report",
    data=csv_data,
    file_name="daily_agriculture_report.csv",
    mime="text/csv"
)


# ---------------- STORED SENSOR READINGS ----------------

st.header("Stored Sensor Readings")

st.dataframe(
    data.sort_values(
        "timestamp",
        ascending=False
    ),
    use_container_width=True
)

st.caption(
    "Smart Agriculture Monitoring System | "
    "Academic IoT and Cloud Analytics Prototype"
)
