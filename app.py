import streamlit as st
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

def get_store_name_from_url(url):
    try:
        parts = url.split('/restaurants/')[1].split('-')
        name_parts = []
        for part in parts:
            if part.isdigit():
                break
            name_parts.append(part)
        return ' '.join(name_parts).title()
    except Exception:
        return "Unknown Store"

def scrape_single_store(url):
    offers = []
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        offer_elements = soup.select("div[data-testid^='offer-card-container']")

        if not offer_elements:
            st.warning(f"No offers found for: {url}")
        
        for el in offer_elements:
            # Extract entire text block and split logically
            all_text = el.get_text(separator='|', strip=True)
            parts = all_text.split('|')

            title = parts[0] if len(parts) > 0 else "No Title"
            description = parts[1] if len(parts) > 1 else "No Description"

            offers.append({
                "store_name": get_store_name_from_url(url),
                "store_url": url,
                "title": title,
                "description": description
            })
    except Exception as e:
        st.error(f"❌ Error scraping {url}: {e}")
    return offers

def parallel_scrape_all_stores(urls, max_threads=5):
    total = len(urls)
    all_offers = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(scrape_single_store, url): url for url in urls}
        for idx, future in enumerate(as_completed(future_to_url), start=1):
            url = future_to_url[future]
            try:
                offers = future.result()
                if offers:
                    all_offers.extend(offers)
            except Exception as e:
                st.error(f"❌ Error scraping {url}: {e}")
            progress_bar.progress(idx / total)
            status_text.text(f"Scraped {idx} of {total} URLs")

    progress_bar.empty()
    status_text.empty()
    return all_offers

def update_google_sheet(offers):
    if offers:
        st.dataframe(offers)
    else:
        st.info("No offers to display.")

st.set_page_config(page_title="Swiggy Discounts Scraper", page_icon="🍔", layout="wide")
st.title("🍔 Swiggy Discounts Scraper")

if st.button("Scrape Discounts"):
    total = len(STORE_URLS)
    st.write(f"Starting scraping 0 out of {total} URLs")
    with st.spinner("Scraping discounts from predefined stores..."):
        offers = parallel_scrape_all_stores(STORE_URLS, max_threads=5)

    if offers:
        update_google_sheet(offers)
        st.success(f"✅ {len(offers)} discounts scraped.")
    else:
        st.warning("No discounts found.")
else:
    st.write("Click the button above to start scraping discounts.")
