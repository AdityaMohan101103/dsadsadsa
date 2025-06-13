import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv

# Swiggy store URLs
STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
]

st.set_page_config(page_title="🍔 Swiggy Offers", layout="centered")

# Stylish CSS
st.markdown("""
    <style>
        body {
            background-color: #f6f9fc;
            font-family: 'Segoe UI', sans-serif;
        }
        .center-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 600;
            color: #333;
        }
        .subtext {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .download-btn {
            display: flex;
            justify-content: center;
            margin-top: 2rem;
        }
        .stSlider > div {
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="center-title">🍔 Swiggy Outlet Offers Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Scraping offers from predefined Swiggy restaurant URLs...</div>', unsafe_allow_html=True)

# Chrome options setup
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

data = []
progress = st.slider("Scraping Progress", 0, len(STORE_URLS), 0, disabled=True, label_visibility="visible")
progress_slot = st.empty()

for idx, url in enumerate(STORE_URLS):
    driver.get(url)
    time.sleep(5)

    try:
        outlet_name = driver.find_element(By.CLASS_NAME, "oypwP").text
    except:
        outlet_name = "Unknown Outlet"

    offers = []
    offer_blocks = driver.find_elements(By.CLASS_NAME, "gPgEKT")
    for block in offer_blocks:
        try:
            title = block.find_element(By.CLASS_NAME, "hsuIwO").text
            code = block.find_element(By.CLASS_NAME, "foYDCM").text
            full_offer = f"{title} - USE {code}"
            offers.append(full_offer)
        except:
            continue

    if not offers:
        offers = ["No offers"]

    for offer in offers:
        data.append([outlet_name, url, offer])

    progress_slot.slider("Scraping Progress", 0, len(STORE_URLS), idx + 1, disabled=True)

driver.quit()

# Write CSV
csv_filename = "swiggy_offers.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Outlet Name", "URL", "Offer"])
    writer.writerows(data)

# Download CSV
st.markdown('<div class="download-btn">', unsafe_allow_html=True)
with open(csv_filename, "rb") as f:
    st.download_button("📥 Download All Offers as CSV", f, file_name="swiggy_offers.csv", mime="text/csv")
st.markdown('</div>', unsafe_allow_html=True)
