import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Predefined list of Swiggy restaurant URLs
STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
]

st.set_page_config(page_title="Swiggy Offers Multi-Scraper", layout="centered")
st.title("🍔 Swiggy Outlet-wise Offers Scraper")

if st.button("Scrape Offers from All Outlets"):
    st.info("Launching browser... Please wait...")

    # Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.binary_location = "/usr/bin/chromium"

    try:
        driver = webdriver.Chrome(options=options)

        results = []

        for url in STORE_URLS:
            st.markdown(f"### 🏪 Scraping: [Open]({url})")
            driver.get(url)
            time.sleep(5)

            offers = []
            offer_containers = driver.find_elements(By.CLASS_NAME, "sc-kbhJrz")

            for container in offer_containers:
                cards = container.find_elements(By.XPATH, ".//div[starts-with(@data-testid, 'offer-card-container-')]")
                for card in cards:
                    try:
                        offer = card.find_element(By.CLASS_NAME, "hsuIwO").text
                        code = card.find_element(By.CLASS_NAME, "foYDCM").text
                        offers.append({"Offer": offer, "Code": code})
                    except:
                        continue

            if offers:
                for i, offer in enumerate(offers, 1):
                    st.markdown(f"**{i}. {offer['Offer']}**  \n`{offer['Code']}`")
            else:
                st.markdown("*No offers found.*")

            st.markdown("---")

    except Exception as e:
        st.error(f"Error: {e}")

    finally:
        driver.quit()
