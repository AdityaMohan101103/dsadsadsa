import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Swiggy Offers Scraper", layout="centered")

st.title("🍔 Swiggy Discounts Scraper")

url = st.text_input("Enter Swiggy restaurant URL:")

if st.button("Scrape Offers"):
    if not url:
        st.warning("Please enter a valid Swiggy restaurant URL.")
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            offers = []
            offer_blocks = soup.find_all("div", class_="sc-kbhJrz kiTfKk")

            if not offer_blocks:
                st.info("No offers found on this page.")
            else:
                for block in offer_blocks:
                    cards = block.find_all("div", {"data-testid": lambda x: x and x.startswith("offer-card-container-")})
                    for card in cards:
                        offer_text = card.find("div", class_="sc-aXZVg hsuIwO")
                        code_text = card.find("div", class_="sc-aXZVg foYDCM")

                        offer = offer_text.get_text(strip=True) if offer_text else "N/A"
                        code = code_text.get_text(strip=True) if code_text else "N/A"

                        offers.append({"Offer": offer, "Code": code})

                st.success(f"Found {len(offers)} offer(s):")
                for i, offer in enumerate(offers, 1):
                    st.markdown(f"**{i}. {offer['Offer']}**  \n`{offer['Code']}`")

        except requests.RequestException as e:
            st.error(f"Error fetching the page: {e}")
