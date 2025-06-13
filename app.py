import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Predefined Swiggy outlet URLs
STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
]

st.set_page_config(page_title="Swiggy Offers Scraper", layout="centered")
st.title("🍔 Swiggy Outlet-wise Offers Scraper")

if st.button("Scrape Offers from All Outlets"):
    st.info("Launching browser... Please wait...")

    # Chrome options for headless browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.binary_location = "/usr/bin/chromium"

    all_offers = []

    try:
        driver = webdriver.Chrome(options=options)

        for url in STORE_URLS:
            driver.get(url)
            time.sleep(5)

            # Extract outlet name reliably
            try:
                outlet_label = driver.find_element(By.XPATH, '//div[text()="Outlet"]')
                outlet_name_elem = outlet_label.find_element(By.XPATH, './following-sibling::div')
                outlet_name = outlet_name_elem.text.strip()
            except:
                outlet_name = "Unknown Outlet"

            st.markdown(f"### 🏪 {outlet_name}")

            offer_containers = driver.find_elements(By.CLASS_NAME, "sc-kbhJrz")
            offers_found = False

            for container in offer_containers:
                cards = container.find_elements(By.XPATH, './/div[starts-with(@data-testid, "offer-card-container-")]')
                for card in cards:
                    try:
                        offer = card.find_element(By.CLASS_NAME, "hsuIwO").text
                        code = card.find_element(By.CLASS_NAME, "foYDCM").text
                        all_offers.append({
                            "Outlet": outlet_name,
                            "Offer": offer,
                            "Code": code,
                            "URL": url
                        })
                        st.markdown(f"**- {offer}**  \n`{code}`")
                        offers_found = True
                    except:
                        continue

            if not offers_found:
                st.markdown("*No offers found.*")

            st.markdown("---")

    except Exception as e:
        st.error(f"Error occurred: {e}")

    finally:
        driver.quit()

    # Show downloadable CSV
    if all_offers:
        df = pd.DataFrame(all_offers)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV of All Offers",
            data=csv,
            file_name="swiggy_offers.csv",
            mime='text/csv'
        )
    else:
        st.warning("No offers found for any outlet.")
