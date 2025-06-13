import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
#dewfwfwefewfwe
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import csv

STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
]

st.set_page_config(page_title="Swiggy Outlet-wise Offers Scraper", layout="centered")
st.title("🍔 Swiggy Outlet-wise Offers Scraper")
st.write("Launching browser... Please wait...")

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

all_data = []

for index, url in enumerate(STORE_URLS):
    driver.get(url)
    time.sleep(5)

    try:
        outlet_elem = driver.find_element(By.CSS_SELECTOR, ".sc-bvgPty .sc-aXZVg.kYaBqd")
        outlet_name = outlet_elem.text.strip()
    except NoSuchElementException:
        outlet_name = "Unknown Outlet"

    try:
        offer_container = driver.find_element(By.CSS_SELECTOR, ".sc-kbhJrz")
        offers_raw = offer_container.find_elements(By.CSS_SELECTOR, "[data-testid^='offer-card-container']")
        offers = []
        for card in offers_raw:
            try:
                lines = card.text.split("\n")
                text = lines[0] if lines else ""
                code = lines[1] if len(lines) > 1 else ""
                offers.append(f"{text}\nUSE {code}" if code else text)
            except:
                continue
    except NoSuchElementException:
        offers = []

    all_data.append((url, outlet_name, offers))

    delay = round(index * 0.15, 2)
    st.markdown(f"""
    <style>
    @keyframes slideIn {{
      from {{ opacity: 0; transform: translateX(-20px); }}
      to {{ opacity: 1; transform: translateX(0); }}
    }}
    .outlet-box-{index} {{
        background-color: #e0f7fa;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 16px;
        border: 1px solid #b2ebf2;
        animation: slideIn 0.5s ease {delay}s forwards;
        opacity: 0;
        transition: transform 0.3s ease;
    }}
    .outlet-box-{index}:hover {{
        background-color: #b2ebf2;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        transform: scale(1.02);
    }}
    .outlet-link {{
        color: #0077cc;
        text-decoration: none;
        transition: color 0.2s ease;
    }}
    .outlet-link:hover {{
        color: #004a99;
        text-decoration: underline;
    }}
    </style>

    <div class="outlet-box-{index}">
      <h4 style='color:#000000; display: flex; align-items: center; gap: 10px;'>
        <img src="https://upload.wikimedia.org/wikipedia/en/1/12/Swiggy_logo.svg" width="24" height="24" style="vertical-align: middle;">
        <u>{outlet_name}</u>
      </h4>
      <p style='font-size:14px;color:#333;'>🔗 <a class="outlet-link" href="{url}" target="_blank">{url}</a></p>
    </div>
    """, unsafe_allow_html=True)

    if offers:
        for offer in offers:
            st.markdown(f"<li>{offer}</li>", unsafe_allow_html=True)
    else:
        st.write("No offers found.")

driver.quit()

# Save to CSV
with open("swiggy_offers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Outlet Name", "URL", "Offer"])
    for url, outlet_name, offers in all_data:
        if offers:
            writer.writerow([outlet_name, url, offers[0]])
            for offer in offers[1:]:
                writer.writerow(["", "", offer])
        else:
            writer.writerow([outlet_name, url, "No offers"])

st.success("✅ CSV exported as swiggy_offers.csv")
