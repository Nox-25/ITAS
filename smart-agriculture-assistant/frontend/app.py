import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Smart Agriculture Assistant", page_icon="🌾", layout="wide")

st.title("🌱 Smart Agriculture Assistant")
st.markdown("An AI and IoT-Based System for Context-Aware Crop Recommendation and Monitoring")

API_URL = "http://localhost:8000"

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1892/1892751.png", width=100)
st.sidebar.title("Navigation")
pages = [
    "Dashboard Overview",
    "Live IoT Monitoring",
    "Weather Forecast",
    "AI Crop Recommendation",
    "Smart Irrigation",
    "Disease Detection",
    "Yield Prediction",
    "AI Assistant"
]
page = st.sidebar.radio("Go to", pages)

# State for Farm Selection
farm_id = st.sidebar.number_input("Current Farm ID", min_value=1, value=1)

def get_live_data(farm_id):
    try:
        curr = requests.get(f"{API_URL}/api/sensors/current/{farm_id}").json()
        weat = requests.get(f"{API_URL}/api/weather/{farm_id}").json()
        risk = requests.get(f"{API_URL}/api/risk-score/{farm_id}").json()
        return curr, weat, risk
    except:
        return None, None, None

if page == "Dashboard Overview":
    st.header(f"🚜 Farm Dashboard (Farm #{farm_id})")

    curr, weat, risk = get_live_data(farm_id)

    if curr and weat and risk:
        # Top KPIs
        col1, col2, col3, col4 = st.columns(4)

        # Determine risk color
        risk_color = "🟢 Low"
        if risk['risk_score'] > 40: risk_color = "🟠 Medium"
        if risk['risk_score'] > 70: risk_color = "🔴 High"

        col1.metric("Risk Level", risk_color, f"{risk['risk_score']}/100")
        col2.metric("Avg Temperature", f"{curr.get('temperature', '--')} °C")
        col3.metric("Soil Moisture", f"{curr.get('soil_moisture', '--')} %")
        col4.metric("Daily Rain Forecast", f"{weat.get('daily_precipitation', '--')} mm")

        st.markdown("---")

        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Recent Conditions")
            try:
                hist = requests.get(f"{API_URL}/api/sensors/latest/{farm_id}?limit=10").json()
                if hist:
                    df = pd.DataFrame(hist)
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
                    fig = px.line(df, x='timestamp', y=['temperature', 'soil_moisture'],
                                  title="Temperature & Moisture Trends", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No historical data available for chart.")

        with c2:
            st.subheader("Active Alerts")
            if risk['risk_factors']:
                for factor in risk['risk_factors']:
                    st.error(f"⚠️ {factor}")
            else:
                st.success("✅ All farm parameters are nominal.")

            st.subheader("Quick Actions")
            if st.button("Check Irrigation Need"):
                st.info("Go to 'Smart Irrigation' to run the full AI prediction.")
            if st.button("Detect Disease"):
                st.info("Go to 'Disease Detection' to upload a leaf photo.")
    else:
        st.warning("⚠️ Could not connect to backend services or no data available. Make sure the IoT Simulator and API are running.")

elif page == "Live IoT Monitoring":
    st.header("📡 Live IoT Sensors")

    placeholder = st.empty()
    while True:
        try:
            current_response = requests.get(f"{API_URL}/api/sensors/current/{farm_id}")
            history_response = requests.get(f"{API_URL}/api/sensors/latest/{farm_id}?limit=20")

            with placeholder.container():
                if current_response.status_code == 200 and current_response.json():
                    current = current_response.json()

                    st.subheader("Current Readings")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Temp", f"{current['temperature']} °C")
                    col2.metric("Hum", f"{current['humidity']} %")
                    col3.metric("Moisture", f"{current['soil_moisture']} %")
                    col4.metric("pH", f"{current['soil_ph']}")
                    col5.metric("N-P-K", f"{current['nitrogen']}-{current['phosphorus']}-{current['potassium']}")

                    st.markdown("---")

                    if history_response.status_code == 200 and history_response.json():
                        df = pd.DataFrame(history_response.json())
                        df['timestamp'] = pd.to_datetime(df['timestamp'])

                        c1, c2 = st.columns(2)
                        with c1:
                            fig1 = px.line(df, x='timestamp', y=['temperature', 'humidity'], title='Temperature & Humidity Over Time')
                            st.plotly_chart(fig1, use_container_width=True)
                        with c2:
                            fig2 = px.line(df, x='timestamp', y=['soil_moisture'], title='Soil Moisture Over Time')
                            st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No sensor data available. Please run the virtual IoT simulator.")
        except Exception as e:
            with placeholder.container():
                st.error(f"Could not reach backend for monitoring data: {e}")

        time.sleep(3)

elif page == "Weather Forecast":
    st.header("🌦️ Weather Forecast (Open-Meteo)")
    if st.button("Refresh Weather"):
        with st.spinner("Fetching data..."):
            try:
                response = requests.get(f"{API_URL}/api/weather/{farm_id}")
                if response.status_code == 200:
                    weather = response.json()

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Current Temp", f"{weather['temperature']} °C")
                    c2.metric("Humidity", f"{weather['humidity']} %")
                    c3.metric("Wind Speed", f"{weather['wind_speed']} km/h")
                    c4.metric("Cloud Cover", f"{weather['cloud_cover']} %")

                    st.subheader("Daily Forecast")
                    st.write(f"- **Max Temp:** {weather['daily_max_temp']} °C")
                    st.write(f"- **Min Temp:** {weather['daily_min_temp']} °C")
                    st.write(f"- **Total Rain Expected:** {weather['daily_precipitation']} mm")
                else:
                    st.error("Failed to fetch weather.")
            except:
                st.error("Connection error.")

elif page == "AI Crop Recommendation":
    st.header("🌾 AI Context-Aware Crop Recommendation")
    st.markdown("This uses Random Forest ML to suggest the optimal crop based on soil NPK, pH, and weather.")

    defaults = {"N": 50.0, "P": 50.0, "K": 50.0, "temperature": 25.0, "humidity": 60.0, "ph": 6.5, "rainfall": 100.0}
    try:
        curr = requests.get(f"{API_URL}/api/sensors/current/{farm_id}").json()
        weat = requests.get(f"{API_URL}/api/weather/{farm_id}").json()
        if curr:
            defaults.update({"N": curr.get("nitrogen", 50.0), "P": curr.get("phosphorus", 50.0),
                             "K": curr.get("potassium", 50.0), "ph": curr.get("soil_ph", 6.5),
                             "temperature": curr.get("temperature", 25.0), "humidity": curr.get("humidity", 60.0)})
        if weat:
            defaults["rainfall"] = float(weat.get("daily_precipitation") or 100.0)
    except:
        pass

    col1, col2 = st.columns(2)
    with col1:
        N = st.number_input("Nitrogen (N)", min_value=0.0, max_value=200.0, value=float(defaults["N"]))
        P = st.number_input("Phosphorus (P)", min_value=0.0, max_value=200.0, value=float(defaults["P"]))
        K = st.number_input("Potassium (K)", min_value=0.0, max_value=200.0, value=float(defaults["K"]))
        ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=float(defaults["ph"]))
    with col2:
        temperature = st.number_input("Temperature (°C)", min_value=-10.0, max_value=60.0, value=float(defaults["temperature"]))
        humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=float(defaults["humidity"]))
        rainfall = st.number_input("Rainfall (mm)", min_value=0.0, max_value=500.0, value=float(defaults["rainfall"]))

    if st.button("Predict Optimal Crop"):
        data = {"N": N, "P": P, "K": K, "temperature": temperature, "humidity": humidity, "ph": ph, "rainfall": rainfall}
        try:
            with st.spinner("Analyzing parameters..."):
                response = requests.post(f"{API_URL}/api/recommend-crop", json=data).json()
            st.success(f"### 🏆 Recommended Crop: {response['recommendation'].capitalize()}")
            st.write("Alternatives:", ", ".join([f"{item['crop'].capitalize()} ({item['confidence']}%)" for item in response.get("top_3", [])[1:]]))
        except:
            st.error("Error during prediction.")

elif page == "Smart Irrigation":
    st.header("💧 Smart Irrigation Prediction")

    defaults = {"moisture": 30.0, "temp": 28.0, "humidity": 65.0, "rain": 5.0}
    try:
        curr, weat, _ = get_live_data(farm_id)
        if curr:
            defaults.update({"moisture": curr.get("soil_moisture", 30.0), "temp": curr.get("temperature", 28.0), "humidity": curr.get("humidity", 65.0)})
        if weat:
            defaults["rain"] = weat.get("daily_precipitation") or 5.0
    except:
        pass

    c1, c2 = st.columns(2)
    with c1:
        m = st.number_input("Soil Moisture (%)", value=float(defaults["moisture"]))
        t = st.number_input("Temperature (°C)", value=float(defaults["temp"]))
    with c2:
        h = st.number_input("Humidity (%)", value=float(defaults["humidity"]))
        r = st.number_input("Expected Rainfall (mm)", value=float(defaults["rain"]))

    if st.button("Predict Need"):
        data = {"soil_moisture": m, "temperature": t, "humidity": h, "expected_rainfall": r}
        try:
            res = requests.post(f"{API_URL}/api/predict-irrigation", json=data).json()
            if res["irrigation_needed"]:
                st.error("### 💧 Irrigation Required")
                st.write(f"Apply approx: **{res['suggested_amount_liters_per_sqm']} Liters/m²**")
            else:
                st.success("### ✅ No Irrigation Needed")
            st.write(f"Confidence: {res['confidence']}%")
        except:
            st.error("Prediction failed.")

elif page == "Disease Detection":
    st.header("🍃 Computer Vision: Leaf Disease Detection")
    st.write("Uses a lightweight PyTorch CNN (MobileNetV2) trained on PlantVillage.")

    img = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])
    if img:
        st.image(img, width=400)
        if st.button("Analyze Image"):
            with st.spinner("Processing image via CNN..."):
                try:
                    files = {"file": (img.name, img.getvalue(), img.type)}
                    res = requests.post(f"{API_URL}/api/detect-disease", files=files).json()

                    if res['is_healthy']:
                        st.success(f"**Crop:** {res['crop']} - **Status:** {res['disease']} ({res['confidence']}%)")
                    else:
                        st.error(f"**Crop:** {res['crop']} - **Detected:** {res['disease']} ({res['confidence']}%)")
                except:
                    st.error("Error connecting to Vision API.")

elif page == "Yield Prediction":
    st.header("📈 Crop Yield ML Prediction")
    c1, c2 = st.columns(2)
    rain = c1.number_input("Total Rainfall (mm)", value=200.0)
    temp = c1.number_input("Avg Temperature (°C)", value=28.0)
    fert = c2.number_input("Fertilizer (kg/ha)", value=50.0)

    if st.button("Estimate Yield"):
        data = {"rainfall": rain, "temperature": temp, "fertilizer": fert}
        try:
            res = requests.post(f"{API_URL}/api/predict-yield", json=data).json()
            st.success(f"Expected Yield: **{res['predicted_yield_tonnes_per_hectare']} tonnes/hectare**")
            st.info(f"Range: {res['expected_range_min']} to {res['expected_range_max']} t/ha")
        except:
            st.error("Failed to estimate yield.")

elif page == "AI Assistant":
    st.header("🤖 Generative AI Assistant")
    st.markdown("Ask natural language questions about your farm conditions.")

    q = st.text_input("Ask a question:", placeholder="Why is my moisture dropping so fast?")
    if st.button("Ask"):
        try:
            with st.spinner("Generating response..."):
                res = requests.post(f"{API_URL}/api/chat", json={"farm_id": farm_id, "message": q}).json()
            st.info(f"**Assistant:** {res['reply']}")
            st.caption(f"Contextual Risk Score used: {res['risk_score']}/100")
        except:
            st.error("Failed to connect to AI engine.")
