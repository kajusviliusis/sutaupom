from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time


def scrape_barbora_products():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    base_url = "https://barbora.lt/akcijos?page={}"
    all_products = []
    seen_ids = set()
    page = 1
    consecutive_empty_pages = 0
    max_empty_pages = 2

    try:

        while True:
            url = base_url.format(page)
            driver.get(url)

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-cnstrc-item-name]'))
                )
            except TimeoutException:
                print(f"⚠️ Timeout: No products found on page {page}")
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    print("No more pages with products detected. Stopping.")
                    break
                page += 1
                continue

            time.sleep(2)

            products = driver.find_elements(By.CSS_SELECTOR, 'li[data-cnstrc-item-name]')
            print(f"Found {len(products)} product elements")

            if not products:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    print("No more products. End of pagination.")
                    break
            else:
                consecutive_empty_pages = 0 

            new_count = 0

            for p in products:
                product = {
                    'title': p.get_attribute('data-cnstrc-item-name'),
                    'price': p.get_attribute('data-cnstrc-item-price'),
                 }
                all_products.append(product)
                new_count += 1

            if new_count == 0:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    print("\n Reached empty pages, stopping.")
                    break
            else:
                consecutive_empty_pages = 0

            page += 1  

        df = pd.DataFrame(all_products)
        df.to_csv("barbora_all_pages.csv", index=False, encoding="utf-8")
        return df

    except Exception as e:
        print("Error:", e)
        if all_products:
            pd.DataFrame(all_products).to_csv("barbora_partial.csv", index=False)
            print(f"Saved partial results ({len(all_products)}) to 'barbora_partial.csv'")
    finally:
        driver.quit()
        
if __name__ == "__main__":
    scrape_barbora_products()
