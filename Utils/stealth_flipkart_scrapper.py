import time
import random
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import quote
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def stealth_flipkart_scrapper(search_string):
    # Setup Chrome options
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window-size=1920,1080")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Custom user-agent to mimic real browser
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
    #              "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    # options.add_argument(f'user-agent={user_agent}')

    # Initialize driver
    driver = webdriver.Chrome(options=options)
    
    stealth(driver=driver,languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,)
    
    # Remove navigator.webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Format search
    formatted_search = quote(search_string)
    search_url = f"https://www.flipkart.com/search?q={formatted_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

    driver.get(search_url)
    # Let page load and scroll a bit
    # time.sleep(random.uniform(3, 5))
    # driver.refresh()
    # time.sleep(random.uniform(2, 4))
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")

    # Extract product links using robust method
    product_links = []
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    # Extract all hrefs
    hrefs = [a['href'] for a in soup.find_all('a', href=True)]

    hrefs = Counter(hrefs)
    
    for href,count in hrefs.items():
        if count == 3 and href not in product_links:
            product_links.append(f"https://www.flipkart.com{href}")
        
        if len(product_links) == 7:
            break
    
    results = []
    # Visit each product page
    for url in product_links:
        try:
            driver.get(url)
            time.sleep(random.uniform(3, 5))

            # # Scroll to bottom slowly
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            # time.sleep(random.uniform(2, 4))

            # Title
            try:
                title =  driver.find_element(By.XPATH, "//*[contains(@class, 'VU-ZEz')]").text.strip()
            except:
                title = "N/A"

            # Price
            try:
                price = driver.find_element(By.XPATH, "//*[contains(@class, 'Nx9bqj')]").text.strip()
            except:
                price = "N/A"

            # Summary Review
            try:
                summary = driver.find_element(By.XPATH, "//*[contains(@class, '_8-rIO3')]").text.strip()
            except:
                summary = "N/A"

            # Product Details Table
            try:
                details = driver.find_element(By.XPATH, "//*[contains(@class, '_3Fm-hO')]").text.strip()
            except:
                details = ""

            results.append({
                "url": url,
                "title": title,
                "price": price,
                "summary_review": summary,
                "details": details
            })

        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    driver.quit()
    return results