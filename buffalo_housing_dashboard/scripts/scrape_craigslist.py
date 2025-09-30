# scripts/scrape_craigslist.py

import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scrape_craigslist(url="https://buffalo.craigslist.org/search/apa", output_file="data/craigslist.csv"):
    # --- Initialize Selenium driver ---
    options = Options()
    options.add_argument("--headless")  # run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(3)

    print("🔄 Scrolling to load all listings...")

    # --- Robust infinite scroll ---
    previous_count = 0
    scroll_pause = 2  # seconds to wait for new listings

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        listings = driver.find_elements(By.CSS_SELECTOR, "div.cl-search-result")
        current_count = len(listings)
        print(f"Current listings loaded: {current_count}")

        if current_count == previous_count:
            break  # no new listings loaded
        previous_count = current_count

    print(f"✅ Total listings loaded: {len(listings)}")

    # --- Scrape data ---
    all_data = []
    for listing in listings:
        try:
            url = listing.find_element(By.CSS_SELECTOR, "a.posting-title").get_attribute("href")
        except:
            url = None
        try:
            price = listing.find_element(By.CSS_SELECTOR, ".priceinfo").text
        except:
            price = None
        try:
            bedrooms = listing.find_element(By.CSS_SELECTOR, ".post-bedrooms").text
        except:
            bedrooms = None
        try:
            location_text = listing.find_element(By.CSS_SELECTOR, ".meta").text
            # Use last word as area name
            area_name = location_text.split()[-1] if location_text else None
        except:
            location_text = None
            area_name = None

        # Set Title to area name
        title = area_name if area_name else "Apartment"

        all_data.append([title, price, bedrooms, location_text, url])

    driver.quit()

    # --- Save to CSV ---
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "Bedrooms", "Location", "URL"])
        writer.writerows(all_data)

    print(f"✅ Scraped {len(all_data)} listings and saved to {output_file}")


if __name__ == "__main__":
    scrape_craigslist()
