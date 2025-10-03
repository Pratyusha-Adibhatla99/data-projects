import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_apartments(max_listings=400):
    base_url = "https://www.apartments.com/buffalo-ny/"
    driver = get_driver()
    wait = WebDriverWait(driver, 15)

    listings = []
    current_page = 1

    while len(listings) < max_listings:
        url = f"{base_url}{current_page}/"
        print(f"Page {current_page}: Loading listings...")
        driver.get(url)

        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.placard')))
        except TimeoutException:
            print("Timeout waiting for listings")
            break

        cards = driver.find_elements(By.CSS_SELECTOR, '.placard')
        print(f"Found {len(cards)} cards on page {current_page}")

        for card in cards:
            if len(listings) >= max_listings:
                break
            try:
                title = card.find_element(By.CSS_SELECTOR, '.property-title').text
            except:
                title = "No title"
            try:
                price = card.find_element(By.CSS_SELECTOR, '.property-pricing').text
            except:
                price = "No price"
            try:
                address = card.find_element(By.CSS_SELECTOR, '.property-address').text
            except:
                address = "No address"
            try:
                beds = card.find_element(By.CSS_SELECTOR, '.property-beds').text
            except:
                beds = "No beds info"
            try:
                link = card.find_element(By.CSS_SELECTOR, 'a.property-link').get_attribute('href')
            except:
                link = "No link"

            listings.append({
                "Title": title,
                "Price": price,
                "Address": address,
                "Beds": beds,
                "URL": link
            })

        # Check if next page exists
        try:
            pagination = driver.find_element(By.CSS_SELECTOR, '.paging')
            next_page = pagination.find_elements(By.CSS_SELECTOR, 'a[data-page]')
            if not next_page or current_page >= len(next_page):
                print("No more page numbers found, scraping finished.")
                break
        except:
            print("Pagination not found, scraping finished.")
            break

        current_page += 1
        time.sleep(2)  # Small delay to avoid being blocked

    driver.quit()
    return listings

if __name__ == "__main__":
    os.makedirs('./data', exist_ok=True)
    scraped_listings = scrape_apartments(max_listings=400)
    if scraped_listings:
        df = pd.DataFrame(scraped_listings)
        csv_path = './data/apartments.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Scraped {len(scraped_listings)} listings and saved to {csv_path}")
    else:
        print("No listings scraped.")
