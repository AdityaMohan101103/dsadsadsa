import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

st.set_page_config(page_title="Swiggy Offers Scraper", layout="centered")
st.title("🍔 Swiggy Discounts Scraper")

url = st.text_input("Enter Swiggy restaurant URL:")

if st.button("Scrape Offers"):
    if not url:
        st.warning("Please enter a valid Swiggy restaurant URL.")
    else:
        st.info("Scraping offers... Please wait.")

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            driver.get(url)
            time.sleep(5)  # Let the page fully load

            offers = []

            offer_container = driver.find_elements(By.CLASS_NAME, "sc-kbhJrz")
            if not offer_container:
                st.info("No offers found on this page.")
            else:
                cards = offer_container[0].find_elements(By.XPATH, ".//div[starts-with(@data-testid, 'offer-card-container-')]")
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
                    st.info("No offers found in the offer container.")

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            driver.quit()
