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

st.markdown(
    "<h1 style='text-align: center;'>🍔 Swiggy Outlet-wise Offers Scraper</h1>", 
    unsafe_allow_html=True
)

st.markdown("---")
st.write("Scraping offers from predefined Swiggy URLs...")

# Set up Selenium without webdriver_manager
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Manually set the ChromeDriver path (assuming it's preinstalled on Railway)
driver_path = "/usr/bin/chromedriver"

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

data = []

for url in STORE_URLS:
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
            offers.append(f"{title}\nUSE {code}")
        except:
            continue

    if offers:
        st.markdown(f"### 🏪 {outlet_name}")
        for offer in offers:
            st.markdown(f"- {offer}")
    else:
        st.markdown(f"### 🏪 {outlet_name}")
        st.write("No offers found.")

    for offer in offers:
        data.append([outlet_name, url, offer])

driver.quit()

# Save to CSV
csv_filename = "swiggy_offers.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Outlet Name", "URL", "Offer"])
    writer.writerows(data)

with open(csv_filename, "rb") as f:
    st.download_button("📥 Download CSV", f, file_name="swiggy_offers.csv")

