# Hidden Currents

**Hidden Currents** is a data-driven beach safety app that identifies hidden ocean risk in calm-looking conditions.

It was inspired by a surfing accident in deceptively calm water and built to help **tourists, beginners, and families** make safer decisions before entering unfamiliar beaches.

## What it does

- Uses **live ocean data** from the Stormglass API
- Estimates **current risk** and **predicted risk** for the next few hours
- Adjusts risk based on **historical rip-current patterns**
- Supports **different user modes**
  - Tourist/Beginner
  - Experienced
- Shows a **color-coded beach map**
- Explains *why* a beach may be risky, not just *that* it is risky

## Why this project matters

Rip currents are dangerous partly because they are often misunderstood.

Water that looks calm can still be unsafe. Many tourists and beginner swimmers rely on surface appearance, but hidden current systems can create dangerous conditions underneath.

This project translates complex environmental data into **simple, explainable guidance**.

## Features

- **Live Risk Now** based on real-time wave and wind conditions
- **Predicted Risk (3 Hours)** to show near-future changes
- **Historical Risk Layer** using a beach-level rip-current dataset
- **Risk Explanation Engine** with factor-by-factor contribution
- **Safety Guidance** tailored to user experience level
- **Interactive Map** with red / yellow / green beach markers

## Tech Stack

- Python
- Streamlit
- Pandas
- Matplotlib
- PyDeck
- Requests
- Stormglass API

## Files

- `app.py` — main Streamlit app
- `rip_current_history.csv` — historical beach risk dataset
- `requirements.txt` — Python dependencies

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
