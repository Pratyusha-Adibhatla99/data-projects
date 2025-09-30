from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time

# Your get_driver function
def get_driver():
    options = Options()
    options.add_argument("--headless")  # Comment out to see browser
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# Initialize driver
driver = get_driver()
url = "https://www.rentcafe.com/apartments-for-rent/us/ny/buffalo/"
driver.get(url)

# Wait for listings to load
time.sleep(5)

# Parse page
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Open CSV to save data
with open("zillow.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Address", "Beds", "Rent", "Link"])

    # Loop through listings
    for listing in soup.find_all("li", class_="listing-details"):
        name_tag = listing.find("h2", class_="listing-name")
        address_tag = listing.find("span", class_="listing-address")
        beds_tag = listing.find("td", class_="data-beds")
        rent_tag = listing.find("td", class_="data-rent")
        link_tag = listing.find("a", href=True)

        if name_tag and address_tag and beds_tag and rent_tag and link_tag:
            name = name_tag.get_text(strip=True)
            address = address_tag.get_text(strip=True)
            beds = beds_tag.get_text(strip=True)
            rent = rent_tag.get_text(strip=True)
            link = link_tag["href"]

            writer.writerow([name, address, beds, rent, link])

print("Scraping complete. Data saved to zillow.csv")
