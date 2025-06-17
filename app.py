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
selected_ipo = None
subs = 100.0  # default fallback

if live_data:
    ipo_names = [f"{name} ({sub}x HNI)" for name, sub in live_data]
    selected = st.selectbox("Select an IPO to autofill HNI subscription:", ipo_names)
    selected_ipo = live_data[ipo_names.index(selected)]
    subs = selected_ipo[1]
else:
    st.warning("Live HNI data could not be loaded. Check internet or Chittorgarh site.")

subs = st.number_input("HNI subscription (x times):", value=subs, step=1.0)
lot_range = list(range(2, 26))

results = []
for lots in lot_range:
    subset = df[df["Lots"] == lots]
    prob = subset["Probability"].mean() if not subset.empty else 1 / (lots * 10)
    capital = lots * 80000
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
