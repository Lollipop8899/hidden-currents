import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import pydeck as pdk
from datetime import datetime

st.set_page_config(page_title="Hidden Currents", page_icon="🌊", layout="wide")

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "YOUR_REAL_API_KEY"

# -----------------------------
# BEACH COORDINATES
# -----------------------------
BEACH_COORDS = {
    "Santa Monica": (34.0195, -118.4912),
    "Manhattan Beach": (33.8847, -118.4109),
    "Huntington Beach": (33.6595, -117.9988),
    "Malibu": (34.0259, -118.7798),
    "Laguna Beach": (33.5427, -117.7854),
    "Newport Beach": (33.6017, -117.9298),
    "Hermosa Beach": (33.8622, -118.3995),
    "Redondo Beach": (33.8492, -118.3884),
    "Venice Beach": (33.9850, -118.4695),
    "Dockweiler Beach": (33.9397, -118.4404),
    "Zuma Beach": (34.0207, -118.8318),
    "El Porto": (33.9006, -118.4220),
    "Seal Beach": (33.7414, -118.1048),
    "Seal Beach Pier": (33.7387, -118.1049),
    "Bolsa Chica": (33.6936, -118.0478),
    "Crystal Cove": (33.5669, -117.8332),
    "Dana Point": (33.4669, -117.6981),
    "Salt Creek Beach": (33.4750, -117.7215),
    "San Clemente Pier": (33.4178, -117.6210),
    "Trestles": (33.3843, -117.5931),
}

# -----------------------------
# FALLBACK SAMPLE DATA
# -----------------------------
BEACH_DATA = {
    "Santa Monica": {
        "tide": "Outgoing",
        "wave_height_ft": 1.8,
        "wave_period_s": 11,
        "wind": "Offshore",
        "rip_advisory": "Moderate",
    },
    "Manhattan Beach": {
        "tide": "Incoming",
        "wave_height_ft": 2.4,
        "wave_period_s": 8,
        "wind": "Onshore",
        "rip_advisory": "Low",
    },
    "Huntington Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 3.1,
        "wave_period_s": 12,
        "wind": "Crossshore",
        "rip_advisory": "High",
    },
    "Malibu": {
        "tide": "Incoming",
        "wave_height_ft": 1.2,
        "wave_period_s": 9,
        "wind": "Offshore",
        "rip_advisory": "Low",
    },
    "Laguna Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 2.0,
        "wave_period_s": 10,
        "wind": "Offshore",
        "rip_advisory": "Moderate",
    },
    "Newport Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 2.7,
        "wave_period_s": 11,
        "wind": "Crossshore",
        "rip_advisory": "High",
    },
    "Hermosa Beach": {
        "tide": "Incoming",
        "wave_height_ft": 2.1,
        "wave_period_s": 9,
        "wind": "Onshore",
        "rip_advisory": "Moderate",
    },
    "Redondo Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 1.9,
        "wave_period_s": 10,
        "wind": "Offshore",
        "rip_advisory": "Moderate",
    },
    "Venice Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 2.2,
        "wave_period_s": 10,
        "wind": "Crossshore",
        "rip_advisory": "Moderate",
    },
    "Dockweiler Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 2.3,
        "wave_period_s": 9,
        "wind": "Onshore",
        "rip_advisory": "Moderate",
    },
    "Zuma Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 3.4,
        "wave_period_s": 12,
        "wind": "Crossshore",
        "rip_advisory": "High",
    },
    "El Porto": {
        "tide": "Outgoing",
        "wave_height_ft": 3.0,
        "wave_period_s": 11,
        "wind": "Crossshore",
        "rip_advisory": "High",
    },
    "Seal Beach": {
        "tide": "Incoming",
        "wave_height_ft": 1.7,
        "wave_period_s": 8,
        "wind": "Onshore",
        "rip_advisory": "Low",
    },
    "Seal Beach Pier": {
        "tide": "Outgoing",
        "wave_height_ft": 2.0,
        "wave_period_s": 10,
        "wind": "Offshore",
        "rip_advisory": "Moderate",
    },
    "Bolsa Chica": {
        "tide": "Incoming",
        "wave_height_ft": 2.0,
        "wave_period_s": 9,
        "wind": "Crossshore",
        "rip_advisory": "Moderate",
    },
    "Crystal Cove": {
        "tide": "Outgoing",
        "wave_height_ft": 1.8,
        "wave_period_s": 10,
        "wind": "Offshore",
        "rip_advisory": "Moderate",
    },
    "Dana Point": {
        "tide": "Incoming",
        "wave_height_ft": 1.3,
        "wave_period_s": 8,
        "wind": "Onshore",
        "rip_advisory": "Low",
    },
    "Salt Creek Beach": {
        "tide": "Outgoing",
        "wave_height_ft": 3.2,
        "wave_period_s": 11,
        "wind": "Crossshore",
        "rip_advisory": "High",
    },
    "San Clemente Pier": {
        "tide": "Outgoing",
        "wave_height_ft": 2.1,
        "wave_period_s": 10,
        "wind": "Offshore",
        "rip_advisory": "Moderate",
    },
    "Trestles": {
        "tide": "Outgoing",
        "wave_height_ft": 3.5,
        "wave_period_s": 12,
        "wind": "Crossshore",
        "rip_advisory": "High",
    },
}

# -----------------------------
# LOAD HISTORICAL DATASET
# -----------------------------
@st.cache_data
def load_rip_history() -> pd.DataFrame:
    try:
        df = pd.read_csv("rip_current_history.csv")
        required_cols = {
            "beach",
            "historical_risk",
            "last_incident_note",
            "risk_multiplier",
        }
        missing = required_cols - set(df.columns)
        if missing:
            st.warning(f"rip_current_history.csv is missing columns: {missing}. Historical layer disabled.")
            return pd.DataFrame()
        return df
    except FileNotFoundError:
        st.warning("rip_current_history.csv not found. Historical layer disabled.")
        return pd.DataFrame()

RIP_HISTORY_DF = load_rip_history()

def get_history_row(beach: str):
    if RIP_HISTORY_DF.empty:
        return None
    rows = RIP_HISTORY_DF[RIP_HISTORY_DF["beach"] == beach]
    if rows.empty:
        return None
    return rows.iloc[0]

# -----------------------------
# API HELPERS
# -----------------------------
def classify_wind(speed: float) -> str:
    if speed < 5:
        return "Offshore"
    if speed < 10:
        return "Crossshore"
    return "Onshore"

def advisory_from_wave(wave_height_ft: float) -> str:
    if wave_height_ft >= 3:
        return "High"
    if wave_height_ft >= 2:
        return "Moderate"
    return "Low"

def extract_hour(hour: dict) -> dict:
    wave_height_m = hour["waveHeight"]["noaa"]
    wave_period_s = hour["wavePeriod"]["noaa"]
    wind_speed = hour["windSpeed"]["noaa"]

    wave_height_ft = round(wave_height_m * 3.28084, 2)

    return {
        "wave_height_ft": wave_height_ft,
        "wave_period_s": wave_period_s,
        "wind": classify_wind(wind_speed),
        "tide": "Outgoing",  # placeholder until tide API is added
        "rip_advisory": advisory_from_wave(wave_height_ft),
    }

def get_real_and_predicted_data(lat: float, lng: float):
    url = (
        f"https://api.stormglass.io/v2/weather/point"
        f"?lat={lat}&lng={lng}&params=waveHeight,wavePeriod,windSpeed"
    )
    headers = {"Authorization": API_KEY}

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    payload = response.json()

    hours = payload["hours"]
    if not hours:
        raise ValueError("No hourly data returned from API")

    current_data = extract_hour(hours[0])
    predicted_data = extract_hour(hours[min(3, len(hours) - 1)])

    return current_data, predicted_data

# -----------------------------
# RISK HELPERS
# -----------------------------
def historical_score_from_label(label: str) -> int:
    mapping = {
        "Low": 30,
        "Moderate": 55,
        "High": 80,
        "Unknown": 40,
    }
    return mapping.get(label, 40)

def risk_color(level: str) -> str:
    if level == "HIGH":
        return "#d9534f"
    if level == "MODERATE":
        return "#f0ad4e"
    return "#5cb85c"

def risk_rgb(level: str):
    if level == "HIGH":
        return [217, 83, 79]
    if level == "MODERATE":
        return [240, 173, 78]
    return [92, 184, 92]

# -----------------------------
# RISK ENGINE
# -----------------------------
def compute_risk(data: dict, user_mode: str, beach: str):
    score = 0
    reasons = []
    contributions = {
        "Tide": 0,
        "Wave": 0,
        "Wind": 0,
        "Advisory": 0,
        "History": 0,
        "User Mode": 0,
    }

    if data["tide"] == "Outgoing":
        score += 30
        contributions["Tide"] += 30
        reasons.append("Outgoing tide increases offshore pull and can strengthen rip current risk.")

    if data["wave_height_ft"] <= 2.0 and data["wave_period_s"] >= 10:
        score += 20
        contributions["Wave"] += 20
        reasons.append("Small waves with longer periods can create deceptively calm-looking but unstable conditions.")
    elif data["wave_height_ft"] > 2.5:
        score += 15
        contributions["Wave"] += 15
        reasons.append("Higher wave energy can increase break instability and current risk.")

    if data["wind"] == "Offshore":
        score += 15
        contributions["Wind"] += 15
        reasons.append("Offshore wind can flatten the surface appearance while dangerous currents remain active.")
    elif data["wind"] == "Crossshore":
        score += 10
        contributions["Wind"] += 10
        reasons.append("Crossshore wind may contribute to unstable surface behavior and current patterns.")

    if data["rip_advisory"] == "High":
        score += 30
        contributions["Advisory"] += 30
        reasons.append("Current wave conditions suggest elevated rip-current danger.")
    elif data["rip_advisory"] == "Moderate":
        score += 15
        contributions["Advisory"] += 15
        reasons.append("Moderate conditions may become unsafe, especially for beginners.")

    history_row = get_history_row(beach)
    history_note = None
    historical_risk = "Unknown"

    if history_row is not None:
        multiplier = float(history_row["risk_multiplier"])
        historical_risk = str(history_row["historical_risk"])
        history_note = str(history_row["last_incident_note"])

        baseline_adjustment = int(round((score * (multiplier - 1.0)) * 0.6))

        if historical_risk == "High":
            baseline_adjustment += 5
        elif historical_risk == "Moderate":
            baseline_adjustment += 2

        if baseline_adjustment > 0:
            score += baseline_adjustment
            contributions["History"] += baseline_adjustment
            reasons.append(f"Historical beach data suggests elevated baseline risk at {beach}.")

    if user_mode == "Tourist/Beginner":
        score += 15
        contributions["User Mode"] += 15
        reasons.append("Beginner mode increases caution because unfamiliar beaches are more likely to be misread.")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
        summary = "Surface may look calm, but hidden current conditions are elevated."
        if user_mode == "Tourist/Beginner":
            advice = [
                "Avoid entering without lifeguard supervision.",
                "Not recommended for beginner surfers, children, or unfamiliar swimmers.",
                "Stay near monitored areas and ask local lifeguards before entering.",
            ]
        else:
            advice = [
                "Use extreme caution and stay near lifeguard-monitored areas.",
                "Reassess entry points before entering the water.",
                "Do not rely on surface calm alone.",
            ]
    elif score >= 40:
        level = "MODERATE"
        summary = "Some conditions may look manageable, but hidden risk factors are present."
        if user_mode == "Tourist/Beginner":
            advice = [
                "Use caution and prefer shallow, monitored areas.",
                "Do not enter if you are unfamiliar with the beach.",
                "Check with a lifeguard before entering.",
            ]
        else:
            advice = [
                "Use caution and monitor changing conditions.",
                "Evaluate break patterns and current behavior before entering.",
                "Stay alert for shifting water conditions.",
            ]
    else:
        level = "LOW"
        summary = "Current conditions appear relatively safer, but caution is still important."
        if user_mode == "Tourist/Beginner":
            advice = [
                "Conditions are relatively safer, but remain near monitored areas.",
                "Unfamiliar beaches may still carry hidden risk.",
                "Check posted warnings before entering.",
            ]
        else:
            advice = [
                "Conditions appear manageable, but continue monitoring the water.",
                "Stay aware of shifting tides and surf conditions.",
                "Use local knowledge when possible.",
            ]

    return score, level, summary, reasons, advice, contributions, historical_risk, history_note

# -----------------------------
# MAP DATA
# -----------------------------
def get_all_beach_risks(user_mode: str) -> pd.DataFrame:
    rows = []

    for beach, (lat, lng) in BEACH_COORDS.items():
        try:
            current_data, _ = get_real_and_predicted_data(lat, lng)
            source = "Live API"
        except Exception:
            current_data = BEACH_DATA[beach]
            source = "Fallback"

        score, level, summary, reasons, advice, contributions, historical_risk, history_note = compute_risk(
            current_data, user_mode, beach
        )

        historical_score = historical_score_from_label(historical_risk)
        if score > historical_score:
            comparison = "Above baseline"
        elif score < historical_score:
            comparison = "Below baseline"
        else:
            comparison = "Near baseline"

        rows.append({
            "beach": beach,
            "lat": lat,
            "lon": lng,
            "score": score,
            "level": level,
            "historical_risk": historical_risk,
            "historical_score": historical_score,
            "comparison": comparison,
            "source": source,
            "color": risk_rgb(level),
        })

    return pd.DataFrame(rows)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Learn", "Saved"])

st.sidebar.markdown("---")
user_mode = st.sidebar.selectbox("User Mode", ["Tourist/Beginner", "Experienced"])
st.sidebar.caption("Hidden Currents MVP")
st.sidebar.caption("A beach safety app for calm-looking but dangerous water")

# -----------------------------
# HOME PAGE
# -----------------------------
if page == "Home":
    st.markdown("""
    <h1 style='text-align: center;'>🌊 Hidden Currents</h1>
    <p style='text-align: center; font-size:18px; color:gray;'>
    See what the surface hides
    </p>
    """, unsafe_allow_html=True)

    beach = st.selectbox("Choose a beach", list(BEACH_COORDS.keys()))
    lat, lng = BEACH_COORDS[beach]

    try:
        current_data, predicted_data = get_real_and_predicted_data(lat, lng)
        using_live_data = True
    except Exception as e:
        st.warning(f"Live data unavailable. Using sample data. Error: {e}")
        current_data = BEACH_DATA[beach]
        predicted_data = BEACH_DATA[beach]
        using_live_data = False

    score, level, summary, reasons, advice, contributions, historical_risk, history_note = compute_risk(
        current_data, user_mode, beach
    )
    pred_score, pred_level, pred_summary, _, _, _, _, _ = compute_risk(
        predicted_data, user_mode, beach
    )

    color = risk_color(level)
    pred_color = risk_color(pred_level)

    top1, top2 = st.columns([1, 1])

    with top1:
        if using_live_data:
            st.success("🟢 Live Data Connected")
        else:
            st.warning("🟡 Using Sample Data")

    with top2:
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption(f"Mode: {user_mode}")

    st.markdown("## Risk Overview")
    st.caption("Compare current conditions with the projected short-term risk trend")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="
            padding:22px 24px;
            border-radius:18px;
            background-color:{color}18;
            border:1px solid {color};
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
            min-height:180px;
            color:#111827;
        ">
            <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:10px;">
                Live Risk Now
            </div>
            <div style="font-size:34px; font-weight:800; color:{color}; line-height:1.1; margin-bottom:8px;">
                {level}
            </div>
            <div style="font-size:16px; color:#111827; margin-bottom:10px;">
                <b>Score:</b> {score}/100
            </div>
            <div style="font-size:15px; color:#374151; line-height:1.5;">
                {summary}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            padding:22px 24px;
            border-radius:18px;
            background-color:{pred_color}18;
            border:1px solid {pred_color};
            box-shadow:0 4px 12px rgba(0,0,0,0.05);
            min-height:180px;
            color:#111827;
        ">
            <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:10px;">
                Predicted Risk (3 Hours)
            </div>
            <div style="font-size:34px; font-weight:800; color:{pred_color}; line-height:1.1; margin-bottom:8px;">
                {pred_level}
            </div>
            <div style="font-size:16px; color:#111827; margin-bottom:10px;">
                <b>Score:</b> {pred_score}/100
            </div>
            <div style="font-size:15px; color:#374151; line-height:1.5;">
                {pred_summary}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if pred_score > score:
        st.warning("Risk is expected to increase over the next few hours.")
    elif pred_score < score:
        st.success("Risk is expected to decrease over the next few hours.")
    else:
        st.info("Risk is expected to remain relatively stable over the next few hours.")

    st.markdown("## Conditions Overview")
    st.caption("Live environmental signals and longer-term beach risk context")

    cond1, cond2 = st.columns(2)

    with cond1:
        st.markdown(f"""
        <div style="
            padding:18px 20px;
            border-radius:16px;
            background-color:#f8f9fa;
            border:1px solid #e5e7eb;
            color:#1f2937;
            box-shadow:0 2px 8px rgba(0,0,0,0.04);
            min-height:150px;
        ">
            <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:12px;">
                Ocean Conditions
            </div>
            <div style="margin-bottom:10px; color:#1f2937;">🌊 <b>Tide:</b> {current_data['tide']}</div>
            <div style="margin-bottom:10px; color:#1f2937;">🌊 <b>Wave Height:</b> {current_data['wave_height_ft']} ft</div>
            <div style="color:#1f2937;">🌊 <b>Period:</b> {current_data['wave_period_s']} s</div>
        </div>
        """, unsafe_allow_html=True)

    with cond2:
        st.markdown(f"""
        <div style="
            padding:18px 20px;
            border-radius:16px;
            background-color:#f8f9fa;
            border:1px solid #e5e7eb;
            color:#1f2937;
            box-shadow:0 2px 8px rgba(0,0,0,0.04);
            min-height:150px;
        ">
            <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:12px;">
                Risk Context
            </div>
            <div style="margin-bottom:10px; color:#1f2937;">🌬 <b>Wind:</b> {current_data['wind']}</div>
            <div style="margin-bottom:10px; color:#1f2937;">⚠️ <b>Advisory:</b> {current_data['rip_advisory']}</div>
            <div style="color:#1f2937;">📚 <b>Historical Risk:</b> {historical_risk}</div>
        </div>
        """, unsafe_allow_html=True)

    if history_note:
        st.markdown(f"""
        <div style="
            margin-top:12px;
            padding:14px 16px;
            border-radius:12px;
            background-color:#fff8e1;
            border-left:5px solid #f0ad4e;
            color:#1f2937;
            box-shadow:0 2px 8px rgba(0,0,0,0.03);
        ">
            <span style="font-weight:700; color:#92400e;">Historical Note:</span>
            <span style="color:#1f2937;"> {history_note}</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Why is this beach historically risky?"):
            st.write(history_note)

            if historical_risk == "High":
                st.write("This beach has a stronger long-term hazard profile, so the model applies a more cautious baseline adjustment.")
            elif historical_risk == "Moderate":
                st.write("This beach shows recurring risk patterns under certain conditions, so the model adds a moderate baseline adjustment.")
            elif historical_risk == "Low":
                st.write("This beach has a relatively lower historical hazard profile, but current conditions can still create danger.")
            else:
                st.write("No detailed historical classification is currently available for this beach.")

    st.markdown("### 🚨 Safety Guidance")
    for item in advice:
        st.error(item)

    st.markdown("---")

    st.markdown("### Risk Factor Contribution")
    factor_df = pd.DataFrame({
        "Factor": list(contributions.keys()),
        "Contribution": list(contributions.values())
    })

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(factor_df["Factor"], factor_df["Contribution"])
    ax.set_ylabel("Risk Contribution")
    ax.set_title("How different factors influence today's risk")
    st.pyplot(fig)

    st.markdown("---")
    st.markdown("### Live vs Historical Risk Comparison")

    historical_score = historical_score_from_label(historical_risk)

    compare_df = pd.DataFrame({
        "Risk Type": ["Live Risk", "Predicted Risk", "Historical Baseline"],
        "Score": [score, pred_score, historical_score]
    })

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(compare_df["Risk Type"], compare_df["Score"])
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Risk Score")
    ax2.set_title("Comparing Current, Predicted, and Historical Risk")
    st.pyplot(fig2)

    if score > historical_score:
        st.info("Current conditions are more dangerous than this beach's usual historical baseline.")
    elif score < historical_score:
        st.info("Current conditions are lower than this beach's historical baseline risk.")
    else:
        st.info("Current conditions are close to this beach's historical baseline risk.")

    st.markdown("---")
    st.markdown("## Beach Risk Map")
    st.caption("Color-coded coastal risk across nearby beaches based on current conditions, historical baseline, and user mode")

    map_df = get_all_beach_risks(user_mode)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[lon, lat]',
        get_color='color',
        get_radius=900,
        pickable=True,
        opacity=0.85,
        stroked=True,
        filled=True,
        line_width_min_pixels=1,
        get_line_color=[255, 255, 255],
    )

    view_state = pdk.ViewState(
        latitude=33.9,
        longitude=-118.2,
        zoom=8,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": """
            <div style="font-family:Arial; font-size:13px;">
                <b>{beach}</b><br/>
                Risk: <b>{level}</b><br/>
                Score: <b>{score}</b><br/>
                Historical: <b>{historical_risk}</b><br/>
                Comparison: <b>{comparison}</b><br/>
                Source: <b>{source}</b>
            </div>
            """
        }
    )

    st.pydeck_chart(deck)

    st.markdown("""
    <div style="
        display:flex;
        gap:18px;
        align-items:center;
        margin-top:8px;
        margin-bottom:8px;
        font-size:14px;
        color:#374151;
    ">
        <div><span style="display:inline-block;width:12px;height:12px;background:#d9534f;border-radius:50%;margin-right:6px;"></span>High Risk</div>
        <div><span style="display:inline-block;width:12px;height:12px;background:#f0ad4e;border-radius:50%;margin-right:6px;"></span>Moderate Risk</div>
        <div><span style="display:inline-block;width:12px;height:12px;background:#5cb85c;border-radius:50%;margin-right:6px;"></span>Low Risk</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Nearby Beach Risk Summary")

    display_df = map_df[["beach", "level", "score", "historical_risk", "comparison", "source"]].copy()
    display_df["level"] = display_df["level"].map({
        "HIGH": "🔴 HIGH",
        "MODERATE": "🟡 MODERATE",
        "LOW": "🟢 LOW",
    })

    st.dataframe(display_df, use_container_width=True)

# -----------------------------
# LEARN PAGE
# -----------------------------
elif page == "Learn":
    st.title("📘 Learn")
    st.subheader("Why calm water can still be dangerous")

    st.markdown("## 🌊 What is a rip current?")
    st.info(
        "A rip current is a strong, narrow flow of water moving away from shore. "
        "It can pull swimmers away even when the surface looks calm."
    )

    st.markdown("## ⚠️ Why calm water can be dangerous")
    st.write("""
    - Smooth-looking water may hide rip channels  
    - Fewer breaking waves do not always mean safer conditions  
    - Surface appearance does not always reflect underwater movement  
    - Unfamiliar beaches are often misread by visitors and beginners  
    """)

    st.markdown("## 🧭 What should you do?")
    st.warning("""
    - Stay calm  
    - Do not swim directly against the current  
    - Swim parallel to shore  
    - Float if needed and signal for help  
    """)

    st.markdown("## 👥 Who should be extra careful?")
    st.write("""
    - Tourists unfamiliar with the beach  
    - Beginner surfers  
    - Children and families  
    - Anyone relying only on surface appearance  
    """)

# -----------------------------
# SAVED PAGE
# -----------------------------
elif page == "Saved":
    st.title("⭐ Saved Beaches")
    st.subheader("Quick view of saved beach conditions")

    saved = ["Santa Monica", "Manhattan Beach", "Huntington Beach", "Zuma Beach"]

    for beach in saved:
        data = BEACH_DATA.get(beach, list(BEACH_DATA.values())[0])
        score, level, summary, reasons, advice, contributions, historical_risk, history_note = compute_risk(
            data, user_mode, beach
        )

        st.markdown(
            f"""
            <div style="padding:16px;margin-bottom:12px;border-radius:14px;background-color:{risk_color(level)}15;border:1px solid {risk_color(level)};">
                <h4 style="margin-bottom:4px;">{beach}</h4>
                <p style="margin:0;"><b>{level}</b> — Score: {score}/100</p>
                <p style="margin-top:6px;">{summary}</p>
                <p style="margin-top:6px;">Historical Risk: {historical_risk}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.dataframe(styled_df, use_container_width=True)

# -----------------------------
# LEARN PAGE
# -----------------------------
elif page == "Learn":
    st.title("📘 Learn")
    st.subheader("Why calm water can still be dangerous")

    st.markdown("## 🌊 What is a rip current?")
    st.info(
        "A rip current is a strong, narrow flow of water moving away from shore. "
        "It can pull swimmers away even when the surface looks calm."
    )

    st.markdown("## ⚠️ Why calm water can be dangerous")
    st.write("""
    - Smooth-looking water may hide rip channels  
    - Fewer breaking waves do not always mean safer conditions  
    - Surface appearance does not always reflect underwater movement  
    - Unfamiliar beaches are often misread by visitors and beginners  
    """)

    st.markdown("## 🧭 What should you do?")
    st.warning("""
    - Stay calm  
    - Do not swim directly against the current  
    - Swim parallel to shore  
    - Float if needed and signal for help  
    """)

    st.markdown("## 👥 Who should be extra careful?")
    st.write("""
    - Tourists unfamiliar with the beach  
    - Beginner surfers  
    - Children and families  
    - Anyone relying only on surface appearance  
    """)

# -----------------------------
# SAVED PAGE
# -----------------------------
elif page == "Saved":
    st.title("⭐ Saved Beaches")
    st.subheader("Quick view of saved beach conditions")

    saved = ["Santa Monica", "Manhattan Beach", "Huntington Beach", "Zuma Beach"]

    for beach in saved:
        data = BEACH_DATA.get(beach, list(BEACH_DATA.values())[0])
        score, level, summary, reasons, advice, contributions, historical_risk, history_note = compute_risk(
            data, user_mode, beach
        )

        st.markdown(
            f"""
            <div style="padding:16px;margin-bottom:12px;border-radius:14px;background-color:{risk_color(level)}15;border:1px solid {risk_color(level)};">
                <h4 style="margin-bottom:4px;">{beach}</h4>
                <p style="margin:0;"><b>{level}</b> — Score: {score}/100</p>
                <p style="margin-top:6px;">{summary}</p>
                <p style="margin-top:6px;">Historical Risk: {historical_risk}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
