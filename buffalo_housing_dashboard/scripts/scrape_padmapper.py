from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os


def scrape_padmapper(url, max_listings=200, max_wait=20):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")  # Uncomment to run headless
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, max_wait)

    results = []
    seen_addresses = set()
    page = 1

    while len(results) < max_listings:
        page_url = f"{url}?page={page}"
        driver.get(page_url)
        time.sleep(5)  # wait for JS to load

        try:
            listings = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//div[contains(@class,'ListItemFull_listItemFull')]")
            ))
        except:
            print(f"⚠️ No listings found on page {page}. Stopping.")
            break

        for l in listings:
            try:
                addr_elem = l.find_element(By.XPATH, ".//div[contains(@class,'ListItemFull_address')]//a")
                address = addr_elem.text.strip()
                link = addr_elem.get_attribute("href").strip()
            except:
                address = ""
                link = ""

            try:
                price = l.find_element(By.XPATH, ".//div[contains(@class,'ListItemFull_price')]//span").text.strip()
            except:
                price = ""

            try:
                details = l.find_element(By.XPATH, ".//div[contains(@class,'ListItemFull_info__phfgd')]").text.strip()
                # Parse bedrooms and area
                bedrooms = ""
                area = ""
                if "Bedrooms" in details:
                    parts = details.split("Bedrooms")
                    bedrooms = parts[0].strip() + " Bedrooms"
                    area = parts[1].replace("·", "").strip()
                else:
                    area = details.strip()
            except:
                bedrooms = ""
                area = ""

            if address and address not in seen_addresses:
                seen_addresses.add(address)
                results.append({
                    "address": address,
                    "price": price,
                    "bedrooms": bedrooms,
                    "area": area,
                    "url": link
                })

        print(f"🔎 Page {page}: collected {len(results)} listings total.")

        if len(results) >= max_listings:
            break

        page += 1

    driver.quit()
    return results[:max_listings]


if __name__ == "__main__":
    url = "https://www.padmapper.com/apartments/buffalo-ny"
    data = scrape_padmapper(url, max_listings=200)
    print(f"✅ Scraped {len(data)} listings")

    os.makedirs("./data", exist_ok=True)

    output_file = "./data/padmapper.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["address", "price", "bedrooms", "area", "url"])
        writer.writeheader()
        writer.writerows(data)

    print(f"💾 Saved {len(data)} listings to {output_file}")
