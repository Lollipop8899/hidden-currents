import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

API_KEY = "YOUR_API_KEY_HERE"

def get_real_data(lat, lng):
    url = f"https://api.stormglass.io/v2/weather/point?lat={lat}&lng={lng}&params=waveHeight,wavePeriod,windSpeed"

    headers = {
        'Authorization': API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    current = data['hours'][0]

    return {
        "wave_height_ft": round(current['waveHeight']['noaa'] * 3.28, 2),
        "wave_period_s": current['wavePeriod']['noaa'],
        "wind": "Offshore" if current['windSpeed']['noaa'] < 5 else "Onshore",
        "tide": "Outgoing",   # placeholder
        "rip_advisory": "Moderate"  # placeholder
    }
st.set_page_config(page_title="Hidden Currents", page_icon="🌊", layout="wide")

# -----------------------------
# Sample beach data (MVP)
# Later you can replace this with API data
# -----------------------------
BEACH_COORDS = {
    "Santa Monica": (34.0195, -118.4912),
    "Manhattan Beach": (33.8847, -118.4109),
    "Huntington Beach": (33.6595, -117.9988),
    "Malibu": (34.0259, -118.7798),
    "Laguna Beach": (33.5427, -117.7854),
}

# -----------------------------
# Risk engine (rule-based MVP)
# -----------------------------
def compute_risk(data: dict):
    score = 0
    reasons = []
    contributions = {
        "Tide": 0,
        "Wave": 0,
        "Wind": 0,
        "Advisory": 0,
    }

    # Tide
    if data["tide"] == "Outgoing":
        score += 30
        contributions["Tide"] += 30
        reasons.append("Outgoing tide increases offshore pull and can strengthen rip current risk.")

    # Wave height + period
    if data["wave_height_ft"] <= 2.0 and data["wave_period_s"] >= 10:
        score += 20
        contributions["Wave"] += 20
        reasons.append("Relatively small waves with longer periods can create deceptively calm-looking but unstable conditions.")
    elif data["wave_height_ft"] > 2.5:
        score += 15
        contributions["Wave"] += 15
        reasons.append("Higher wave energy can increase break instability and current risk.")

    # Wind
    if data["wind"] == "Offshore":
        score += 15
        contributions["Wind"] += 15
        reasons.append("Offshore wind can flatten the surface appearance while dangerous currents remain active.")
    elif data["wind"] == "Crossshore":
        score += 10
        contributions["Wind"] += 10
        reasons.append("Crossshore wind may contribute to unstable surface behavior and current patterns.")

    # Advisory
    if data["rip_advisory"] == "High":
        score += 30
        contributions["Advisory"] += 30
        reasons.append("Official advisory indicates elevated rip current danger.")
    elif data["rip_advisory"] == "Moderate":
        score += 15
        contributions["Advisory"] += 15
        reasons.append("Moderate advisory suggests conditions may become unsafe, especially for beginners.")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
        summary = "Surface may look calm, but hidden current conditions are elevated."
        advice = [
            "Avoid entering the water without lifeguard supervision.",
            "Not recommended for beginner surfers or children.",
            "Stay near monitored areas and ask local lifeguards before entering."
        ]
    elif score >= 40:
        level = "MODERATE"
        summary = "Some conditions may look manageable, but hidden risk factors are present."
        advice = [
            "Use caution and check local conditions before entering.",
            "Beginners should stay in shallow, monitored areas.",
            "Do not assume calm-looking water is low risk."
        ]
    else:
        level = "LOW"
        summary = "Current conditions appear relatively safer, but caution is still important."
        advice = [
            "Continue checking lifeguard guidance.",
            "Stay aware of changing tides and surf conditions.",
            "Unfamiliar beaches may still carry hidden risk."
        ]

    return score, level, summary, reasons, advice, contributions


def risk_color(level: str) -> str:
    if level == "HIGH":
        return "#d9534f"
    if level == "MODERATE":
        return "#f0ad4e"
    return "#5cb85c"


# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Learn", "Saved"])

st.sidebar.markdown("---")
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

    beach = st.selectbox("Choose a beach", list(BEACH_DATA.keys()))
    lat, lng = BEACH_COORDS[beach]
    data = get_real_data(lat, lng)

    score, level, summary, reasons, advice, contributions = compute_risk(data)

    # Main risk card
    color = risk_color(level)

    st.markdown(f"""
    <div style="
        padding:25px;
        border-radius:20px;
        background: linear-gradient(135deg, {color}20, white);
        border: 1px solid {color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    ">
        <h2 style="color:{color}; margin-bottom:5px;">{beach}</h2>
        <h1 style="color:{color}; margin:0;">{level}</h1>
        <h3>Risk Score: {score}/100</h3>
        <p style="font-size:18px;"><b>{summary}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Conditions")
    st.markdown(f"""
    - 🌊 Tide: **{data['tide']}**
    - 🌊 Wave Height: **{data['wave_height_ft']} ft**
    - 🌊 Period: **{data['wave_period_s']} s**
    - 🌬 Wind: **{data['wind']}**
    - ⚠️ Advisory: **{data['rip_advisory']}**
    """)

    st.markdown("---")

    # Why risky
    with st.expander("Why is this risky?"):
        for reason in reasons:
            st.write(f"- {reason}")

    # Safety advice
    st.markdown("### 🚨 Safety Guidance")
    for item in advice:
        st.error(item)

    st.markdown("---")

    # Visualization
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
    st.caption("MVP note: this version uses a rule-based model with sample beach data. Later versions can connect to live wave, tide, and weather APIs.")

# -----------------------------
# LEARN PAGE
# -----------------------------
elif page == "Learn":
    st.title("📘 Learn")
    st.subheader("Why calm water can still be dangerous")

    st.markdown("## 🌊 What is a rip current?")
    st.info("A rip current is a strong, narrow flow of water moving away from shore.")

    st.markdown("## ⚠️ Why calm water can be dangerous")
    st.write("""
    - Smooth-looking water may hide rip channels  
    - Fewer waves does NOT mean safer conditions  
    - Surface ≠ system  
    """)

    st.markdown("## 🧭 What should you do?")
    st.warning("""
    - Stay calm  
    - Do NOT swim directly against the current  
    - Swim parallel to shore  
    - Signal for help if needed  
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

    saved = ["Santa Monica", "Manhattan Beach", "Huntington Beach"]

    for beach in saved:
       lat, lng = BEACH_COORDS[beach]
    data = get_real_data(lat, lng)
        score, level, summary, reasons, advice, contributions = compute_risk(data)

        st.markdown(
            f"""
            <div style="padding:16px;margin-bottom:12px;border-radius:14px;background-color:{risk_color(level)}15;border:1px solid {risk_color(level)};">
                <h4 style="margin-bottom:4px;">{beach}</h4>
                <p style="margin:0;"><b>{level}</b> — Score: {score}/100</p>
                <p style="margin-top:6px;">{summary}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
import requests

API_KEY = "YOUR_API_KEY"

def get_real_data(lat, lng):
    url = f"https://api.stormglass.io/v2/weather/point?lat={lat}&lng={lng}&params=waveHeight,wavePeriod,windSpeed"

    headers = {
        'Authorization': API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    current = data['hours'][0]

    return {
        "wave_height_ft": round(current['waveHeight']['noaa'] * 3.28, 2),
        "wave_period_s": current['wavePeriod']['noaa'],
        "wind": "Offshore" if current['windSpeed']['noaa'] < 5 else "Onshore",
        "tide": "Outgoing",  # placeholder for now
        "rip_advisory": "Moderate"  # placeholder
    }
    BEACH_COORDS = {
    "Santa Monica": (34.0195, -118.4912),
    "Manhattan Beach": (33.8847, -118.4109),
}
