import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
    # Add more URLs as needed
]

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

def create_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_single_store(url, headless=True):
    offers = []
    driver = None
    try:
        driver = create_driver(headless=headless)
        driver.get(url)

        wait = WebDriverWait(driver, 20)

        # Scroll down to bottom to force lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # wait for potential lazy loading

        # Wait for offers container presence
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid^='offer-card-container']")))

        offer_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-testid^='offer-card-container']")
        st.write(f"DEBUG: Found {len(offer_elements)} offer elements on {url}")

        if not offer_elements:
            st.warning(f"No offer elements found for {url}. The page layout or selectors might have changed.")

        for el in offer_elements:
            try:
                title_element = el.find_element(By.CSS_SELECTOR, "div.sc-aXZVg.hsuIwO")
                desc_element = el.find_element(By.CSS_SELECTOR, "div.sc-aXZVg.foYDCM")
                title = title_element.text.strip() if title_element else "No Title"
                desc = desc_element.text.strip() if desc_element else "No Description"
            except Exception:
                title = "No Title"
                desc = "No Description"

            offers.append({
                "store_name": get_store_name_from_url(url),
                "store_url": url,
                "title": title,
                "description": desc
            })
    except TimeoutException:
        st.error(f"❌ Timeout while loading offers on {url}")
    except WebDriverException as e:
        st.error(f"❌ Selenium WebDriver error on {url}: {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error scraping {url}: {e}")
    finally:
        if driver:
            driver.quit()
    return offers

def parallel_scrape_all_stores(urls, max_threads=1, headless=True):
    # Reduced max_threads due to Selenium resource usage
    total = len(urls)
    all_offers = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(scrape_single_store, url, headless): url for url in urls}
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
    st.info("Google Sheet update feature not implemented. Showing data below.")
    st.dataframe(offers)

st.set_page_config(page_title="Swiggy Discounts Scraper - Debug", page_icon="🍔", layout="wide")
st.title("🍔 Swiggy Discounts Scraper - Debug")

headless_toggle = st.checkbox("Run browser headless (uncheck to show browser window)", value=True)

if st.button("Scrape Discounts"):
    total = len(STORE_URLS)
    st.write(f"Starting scraping 0 out of {total} URLs")
    with st.spinner("Scraping discounts from predefined stores... (this might take a while)"):
        offers = parallel_scrape_all_stores(STORE_URLS, max_threads=1, headless=headless_toggle)

    if offers:
        update_google_sheet(offers)
        st.success(f"✅ {len(offers)} discounts scraped.")
    else:
        st.warning("No discounts found.")
else:
    st.write("Click the button above to start scraping discounts.")

