import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- Function to get real-time HNI subscription data from Chittorgarh using pandas fallback ---
def get_live_hni_subscription():
    try:
        url = "https://www.chittorgarh.com/report/latest-sme-ipo-subscription-live/85/"
        tables = pd.read_html(url)
        df = tables[0]
        ipo_data = []
        for _, row in df.iterrows():
            try:
                ipo_data.append((row["IPO Name"], float(row["NII"].split()[0])))
            except:
                continue
        return ipo_data
    except:
        return []

# --- Function to get GMP data ---
def get_dummy_gmp_data():
    return {
        "Delta Autocorp": 45,
        "Rikhav Securities": 25,
        "CapitalNumbers": 60
    }

# --- Function to map probability to confidence zone ---
def confidence_zone(prob):
    if prob >= 0.5:
        return "🟢 High"
    elif prob >= 0.2:
        return "🟡 Medium"
    elif prob > 0:
        return "🔴 Low"
    else:
        return "⚪ None"

# --- Streamlit App ---
st.title("📊 SME IPO HNI Allotment Predictor")

# Show live IPO list
st.subheader("Live SME IPOs")
live_data = get_live_hni_subscription()
gmp_data = get_dummy_gmp_data()
selected_ipo = None
subs = 100.0

if live_data:
    ipo_names = [f"{name} ({sub}x HNI)" for name, sub in live_data]
    selected = st.selectbox("Select an IPO to autofill HNI subscription:", ipo_names)
    selected_ipo = live_data[ipo_names.index(selected)]
    selected_name = selected_ipo[0]
    subs = selected_ipo[1]
    st.markdown(f"**GMP:** ₹{gmp_data.get(selected_name, 'N/A')}")
else:
    st.warning("Live HNI data could not be loaded. Check internet or Chittorgarh site.")
    selected_name = ""

subs = st.number_input("HNI subscription (x times):", value=subs, step=1.0)
user_capital = st.number_input("Your investment capital (₹):", value=500000, step=10000)
lot_range = list(range(2, 26))

st.markdown("---")

# --- Dynamic Prediction ---
st.subheader(f"Est. Allotment Odds for: {selected_name}")

results = []
for lots in lot_range:
    capital = lots * 80000
    if capital > user_capital:
        continue
    base_factor = 2.5
    expected_applicants = subs * base_factor * lots
    prob = min(1.0, 1 / expected_applicants)
    expected_shares = prob * 200
    efficiency = capital / expected_shares if expected_shares else None
    zone = confidence_zone(prob)

    results.append({
        "Lots Applied": lots,
        "Est. Allotment %": round(prob * 100, 2),
        "Confidence": zone,
        "Capital (₹)": capital,
        "Expected Shares": round(expected_shares, 2),
        "₹ per Expected Share": round(efficiency, 2) if efficiency else None
    })

out_df = pd.DataFrame(results)
st.dataframe(out_df.style.format({"Capital (₹)": "₹{:,.0f}", "₹ per Expected Share": "₹{:,.0f}"}))

# --- OCR/BoA Section Disabled ---
st.subheader("📂 BoA Image Upload (Disabled on Streamlit Cloud)")
st.info("Due to platform limitations, image upload + OCR is disabled here. Run locally to use it.")

# Historical returns section
st.subheader("Historical IPO Listing Gains")
st.markdown("Here’s a sample of past IPO listing gains to understand trends:")
historical = pd.DataFrame({
    "IPO": ["Delta Autocorp", "Rikhav Securities", "CapitalNumbers"],
    "Issue Price": [40, 45, 90],
    "Listing Price": [62, 56, 132],
    "Listing Gain %": [55.0, 24.4, 46.7]
})
st.dataframe(historical)
