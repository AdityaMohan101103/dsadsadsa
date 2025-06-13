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

# Set Streamlit config
st.set_page_config(page_title="🍔 Swiggy Offers", layout="centered")

# Add custom CSS for styling and animations
st.markdown("""
    <style>
        body {
            background-color: #fafafa;
        }
        .offer-box {
            background: linear-gradient(145deg, #ffffff, #f0f0f0);
            border-radius: 20px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: slideIn 0.5s ease forwards;
            transition: transform 0.3s ease;
        }
        .offer-box:hover {
            transform: scale(1.03);
        }
        .outlet-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-top: 2rem;
            color: #333;
        }
        @keyframes slideIn {
            from {opacity: 0; transform: translateX(-50px);}
            to {opacity: 1; transform: translateX(0);}
        }
        .offer-text {
            font-size: 1.1rem;
            color: #444;
        }
        .logo {
            font-size: 3rem;
            text-align: center;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# UI header
st.markdown('<div class="logo">🍔</div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Swiggy Outlet-wise Offers Scraper</h1>", unsafe_allow_html=True)
st.write("Scraping predefined Swiggy restaurant URLs...")

# Set up Selenium without webdriver_manager
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Railway Chrome path
driver_path = "/usr/bin/chromedriver"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

data = []
for idx, url in enumerate(STORE_URLS):
    driver.get(url)
    time.sleep(5)

    try:
        outlet_name = driver.find_element(By.CLASS_NAME, "oypwP").text
    except:
        outlet_name = "Unknown Outlet"

    st.markdown(f'<div class="outlet-title">🏪 {outlet_name}</div>', unsafe_allow_html=True)

    offers = []
    offer_blocks = driver.find_elements(By.CLASS_NAME, "gPgEKT")
    for block in offer_blocks:
        try:
            title = block.find_element(By.CLASS_NAME, "hsuIwO").text
            code = block.find_element(By.CLASS_NAME, "foYDCM").text
            full_offer = f"{title}<br><strong>USE {code}</strong>"
            offers.append(full_offer)
        except:
            continue

    if offers:
        for i, offer in enumerate(offers):
            delay = i * 0.15
            st.markdown(
                f'<div class="offer-box" style="animation-delay: {delay:.2f}s;"><div class="offer-text">{offer}</div></div>',
                unsafe_allow_html=True
            )
            data.append([outlet_name, url, offer.replace("<br>", " ").replace("<strong>", "").replace("</strong>", "")])
    else:
        st.markdown("<div class='offer-box'><div class='offer-text'>No offers found.</div></div>", unsafe_allow_html=True)
        data.append([outlet_name, url, "No offers"])

driver.quit()

# Write CSV
csv_filename = "swiggy_offers.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Outlet Name", "URL", "Offer"])
    writer.writerows(data)

# Download button
with open(csv_filename, "rb") as f:
    st.download_button("📥 Download All Offers as CSV", f, file_name="swiggy_offers.csv", mime="text/csv")
