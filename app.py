import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
]

st.set_page_config(page_title="Swiggy Offers Scraper", layout="centered")
st.markdown("<h1 style='text-align: center;'>🍔 Swiggy Offers Scraper</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Get outlet-wise discounts with one click 💸</h4>", unsafe_allow_html=True)
st.markdown("---")

if st.button("🚀 Scrape Offers from All Outlets"):
    st.info("Launching browser... Please wait...")

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

            # Extract outlet name
            try:
                outlet_label = driver.find_element(By.XPATH, '//div[text()="Outlet"]')
                outlet_name_elem = outlet_label.find_element(By.XPATH, './following-sibling::div')
                outlet_name = outlet_name_elem.text.strip()
            except:
                outlet_name = "Unknown Outlet"

            st.markdown(f"""<div style="background-color:#f9f9f9;padding:15px;border-radius:10px;margin-bottom:10px;">
            <h4>🏪 <u>{outlet_name}</u></h4><p style='font-size:14px;'>🔗 <a href="{url}" target="_blank">{url}</a></p>""", unsafe_allow_html=True)

            offer_containers = driver.find_elements(By.CLASS_NAME, "sc-kbhJrz")
            offers = []

            for container in offer_containers:
                cards = container.find_elements(By.XPATH, './/div[starts-with(@data-testid, "offer-card-container-")]')
                for card in cards:
                    try:
                        offer = card.find_element(By.CLASS_NAME, "hsuIwO").text
                        code = card.find_element(By.CLASS_NAME, "foYDCM").text
                        offers.append((offer, code))
                        st.markdown(f"<div style='padding-left:10px;'>✅ <b>{offer}</b><br><code>{code}</code></div>", unsafe_allow_html=True)
                    except:
                        continue

            if not offers:
                st.markdown("<div style='color:red;'>❌ No offers found.</div>", unsafe_allow_html=True)
                all_offers.append({
                    "Outlet": outlet_name,
                    "URL": url,
                    "Offer": "No offers found",
                    "Code": ""
                })
            else:
                for i, (offer, code) in enumerate(offers):
                    all_offers.append({
                        "Outlet": outlet_name if i == 0 else "",
                        "URL": url if i == 0 else "",
                        "Offer": offer,
                        "Code": code
                    })

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("----")

    except Exception as e:
        st.error(f"❗ Error occurred: {e}")
    finally:
        driver.quit()

    if all_offers:
        df = pd.DataFrame(all_offers)
        csv = df.to_csv(index=False).encode('utf-8')
        st.success("🎉 Offers fetched successfully!")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="swiggy_offers_clean.csv",
            mime='text/csv'
        )
    else:
        st.warning("⚠️ No offers found for any outlet.")
