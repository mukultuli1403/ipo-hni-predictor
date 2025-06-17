import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- Function to get real-time HNI subscription data from Chittorgarh ---
def get_live_hni_subscription():
    try:
        url = "https://www.chittorgarh.com/report/latest-sme-ipo-subscription-live/85/"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")

        ipo_data = []
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 6:
                ipo_name = cols[0].get_text(strip=True)
                hni_subscription = cols[2].get_text(strip=True)
                if hni_subscription.replace('.', '', 1).isdigit():
                    ipo_data.append((ipo_name, float(hni_subscription)))
        return ipo_data
    except Exception as e:
        return []

# --- Function to get GMP data from IPOWatch (placeholder using static sample) ---
def get_dummy_gmp_data():
    return {
        "Delta Autocorp": 45,
        "Rikhav Securities": 25,
        "CapitalNumbers": 60
    }

# --- Load training data ---
data = [
    {"IPO": "Delta Autocorp", "Lots": 2, "Applicants": 43, "Ratio": "1:43"},
    {"IPO": "Delta Autocorp", "Lots": 10, "Applicants": 6, "Ratio": "1:2"},
    {"IPO": "Rikhav Securities", "Lots": 2, "Applicants": 122, "Ratio": "1:122"},
    {"IPO": "Rikhav Securities", "Lots": 10, "Applicants": 6, "Ratio": "1:5"},
    {"IPO": "CapitalNumbers", "Lots": 2, "Applicants": 110, "Ratio": "1:110"},
    {"IPO": "CapitalNumbers", "Lots": 10, "Applicants": 6, "Ratio": "1:6"}
]
df = pd.DataFrame(data)
df["Probability"] = df["Ratio"].apply(lambda x: round(eval(x.replace(":", "/")), 4))

# --- Streamlit App ---
st.title("📊 SME IPO HNI Allotment Predictor")

# Show live IPO list
st.subheader("Live SME IPOs")
live_data = get_live_hni_subscription()
gmp_data = get_dummy_gmp_data()
selected_ipo = None
subs = 100.0  # default fallback

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

# Filter historical data for selected IPO
ipo_df = df[df["IPO"] == selected_name]
if not ipo_df.empty:
    st.subheader(f"Prediction for: {selected_name}")
    results = []
    for lots in lot_range:
        capital = lots * 80000
        if capital > user_capital:
            continue
        subset = ipo_df[ipo_df["Lots"] == lots]
        prob = subset["Probability"].mean() if not subset.empty else 1 / (lots * 10)
        expected_shares = prob * 200
        efficiency = capital / expected_shares if expected_shares else None

        results.append({
            "Lots Applied": lots,
            "Est. Allotment %": round(prob * 100, 2),
            "Capital (₹)": capital,
            "Expected Shares": round(expected_shares, 2),
            "₹ per Expected Share": round(efficiency, 2) if efficiency else None
        })

    out_df = pd.DataFrame(results)
    st.dataframe(out_df.style.format({"Capital (₹)": "₹{:,.0f}", "₹ per Expected Share": "₹{:,.0f}"}))
else:
    st.warning(f"No historical allotment data available yet for **{selected_name}**. Please check back later.")

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
