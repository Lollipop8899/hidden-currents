# Hidden Currents

**Hidden Currents** is a data-driven beach safety app that detects hidden ocean risk in calm-looking conditions.

Inspired by a surfing incident in deceptively calm water, this project helps **tourists, beginners, and families** make safer decisions before entering unfamiliar beaches.

---

## What it does

Hidden Currents analyzes ocean conditions and translates them into simple, explainable safety guidance.

It combines:

- 🌊 **Live ocean data** (wave height, period, wind)
- 🔮 **Short-term prediction** (next 3 hours)
- 📚 **Historical beach-risk layer**
- 👤 **User mode (beginner vs experienced)**

The result is a system that identifies when water may *look safe but behave dangerously*.

---

## Why this project matters

Rip currents are dangerous not just because they exist—but because they are often misunderstood.

Water that appears calm can still contain strong outgoing currents.  
Many people—especially tourists and beginners—rely on surface appearance to judge safety.

This project focuses on:

> **Making hidden environmental risk visible and understandable.**

---

## Project Goal

Hidden Currents is designed to move beyond raw data and provide **interpretable risk insights**.

The system integrates:

- real-time environmental signals
- near-term predictions
- long-term hazard patterns

A key feature is the **historical beach-risk layer**, built from a curated dataset, which adjusts real-time risk estimates using long-term exposure patterns.

The goal is not just to detect risk, but to:

> **help users understand why risk exists—and act accordingly.**

---

## Features

- **Live Risk Score**
  - Based on real-time ocean conditions

- **Predicted Risk (3 Hours)**
  - Detects short-term changes in risk

- **Historical Risk Adjustment**
  - Incorporates long-term hazard patterns

- **User Mode**
  - Tourist / Beginner → more conservative
  - Experienced → more context-based

- **Explainable Risk Engine**
  - Shows contributing factors (tide, wave, wind)

- **Safety Guidance**
  - Actionable advice based on risk level

- **Interactive Map**
  - Color-coded beach risk (red / yellow / green)

---

## Model Explanation

Hidden Currents uses a **multi-layer risk model** rather than a single metric.

### 1. Real-Time Environmental Layer

The model processes:
- wave height
- wave period
- wind speed
- inferred tide behavior

These factors determine immediate surface and subsurface conditions.

---

### 2. Short-Term Prediction Layer

Using hourly forecast data, the system compares:

- current conditions
- conditions ~3 hours ahead

This allows detection of:
- rising risk (e.g., tide change)
- stabilizing conditions
- persistent hazard

---

### 3. Historical Risk Layer

A curated dataset provides:

- historical risk classification per beach
- known hazard patterns
- baseline multipliers

This layer adjusts the model to account for:

> beaches that are consistently more dangerous than they appear.

---

### 4. User Sensitivity Layer

The model adapts based on user type:

- **Tourist / Beginner**
  - Increased risk sensitivity
  - More conservative recommendations

- **Experienced**
  - Reduced adjustment
  - More context-driven interpretation

---

### 5. Final Risk Output

The final score is computed by combining:

- environmental conditions
- predicted changes
- historical baseline
- user sensitivity

Output includes:

- risk level (Low / Moderate / High)
- numeric score
- explanation of contributing factors
- safety guidance

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Matplotlib
- PyDeck
- Requests
- Stormglass API

---

## Files

- `app.py` — main application
- `rip_current_history.csv` — historical dataset
- `requirements.txt` — dependencies

---

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
