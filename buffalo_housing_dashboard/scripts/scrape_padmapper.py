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
import re


def scrape_padmapper(url, max_listings=400, max_wait=20):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, max_wait)

    results = []
    seen_addresses = set()
    page = 1

    while len(results) < max_listings:
        page_url = f"{url}?page={page}"
        driver.get(page_url)
        time.sleep(5)

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

            # extract bedrooms and area separately
            bedrooms, area = "", ""
            try:
                details = l.find_element(By.XPATH, ".//div[contains(@class,'ListItemFull_info__phfgd')]").text.strip()

                # Case 1: "1–2 Bedrooms Apartments · Riverside Park, Buffalo"
                match = re.match(r"(.*?)Bedrooms?.*·(.*)", details)
                if match:
                    bedrooms = match.group(1).strip()
                    area = match.group(2).strip()

                # Case 2: "Studio Apartment · Delaware - West Ferry, Buffalo"
                elif "Studio" in details and "·" in details:
                    parts = details.split("·")
                    bedrooms = parts[0].replace("Apartment", "").strip()
                    area = parts[1].strip()

                else:
                    # fallback: just store details if pattern not matched
                    area = details.strip()
            except:
                pass

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
    data = scrape_padmapper(url, max_listings=400)
    print(f"✅ Scraped {len(data)} listings")

    os.makedirs("./data", exist_ok=True)
    output_file = "./data/padmapper.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["address", "price", "bedrooms", "area", "url"])
        writer.writeheader()
        writer.writerows(data)

    print(f"💾 Saved {len(data)} listings to {output_file}")
