from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random

def stealth_amazon_scraper(search_string):
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
    formatted_search = search_string.replace(" ", "+")
    search_url = f"https://www.amazon.in/s?k={formatted_search}"
    driver.get(search_url)
    # Let page load and scroll a bit
    time.sleep(random.uniform(3, 5))
    driver.refresh()
    time.sleep(random.uniform(2, 4))
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")

    # Extract product links using robust method
    product_links = []
    try:
        wait = WebDriverWait(driver, 10)
        anchors = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a.a-link-normal.s-link-style.a-text-normal")
        ))

        for anchor in anchors:
            href = anchor.get_attribute("href")
            if href and href not in product_links:
                product_links.append(href)
            if len(product_links) == 7:
                break
    except Exception as e:
        print("Error fetching links:", e)

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
                title = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "productTitle"))
                ).text.strip()
            except:
                title = "N/A"

            # Price
            try:
                price = driver.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
            except:
                price = "N/A"

            # Summary Review
            try:
                summary = driver.find_element(By.ID, "product-summary").text.strip()
            except:
                summary = "N/A"

            # Product Details Table
            try:
                keys = driver.find_elements(By.CSS_SELECTOR, "th.a-color-secondary.a-size-base.prodDetSectionEntry")
                values = driver.find_elements(By.CSS_SELECTOR, "td.a-size-base.prodDetAttrValue")
                details = {k.text.strip(): v.text.strip() for k, v in zip(keys, values)}
                
                if not details:
                    details = driver.find_element(By.CSS_SELECTOR,"ul.a-unordered-list.a-vertical.a-spacing-small").text.strip()

            except:
                details = {}

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