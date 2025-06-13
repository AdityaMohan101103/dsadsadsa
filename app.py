import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

st.set_page_config(page_title="Swiggy Discounts Scraper", layout="centered")
st.title("🍔 Swiggy Discounts Scraper")

url = st.text_input("Enter Swiggy restaurant URL:")

if st.button("Scrape Offers"):
    if not url:
        st.warning("Please enter a valid Swiggy restaurant URL.")
    else:
        st.info("Scraping offers... Please wait...")

        # Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        options.binary_location = "/usr/bin/chromium"

        try:
            # Initialize Chrome driver
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(5)  # Wait for JS content to load

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
                st.success(f"Found {len(offers)} offer(s):")
                for i, offer in enumerate(offers, 1):
                    st.markdown(f"**{i}. {offer['Offer']}**  \n`{offer['Code']}`")
            else:
                st.info("No offers found on this page.")

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            driver.quit()
