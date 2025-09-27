from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Point Selenium to ChromeDriver
service = Service("/Users/Pratz/bin/chromedriver")

# Launch Chrome
driver = webdriver.Chrome(service=service)
driver.get("https://www.google.com")

print("Page Title:", driver.title)  # Should print "Google"

driver.quit()
