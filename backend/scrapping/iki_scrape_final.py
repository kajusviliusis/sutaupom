import csv
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.lastmile.lt/chain/IKI/categories/Akcijos-00sales")

csv_file = open("iki_products.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["product_name", "shelf_price", "image_url"])

products_set = set()
processed_indices = set()  
iterations = 0
total_products = 0
consecutive_no_button = 0

try:
    time.sleep(2) 
    
    while True:
        iterations += 1
        products_before = len(products_set)
        
        
        product_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='main-productCard']")
        
        
        for idx, element in enumerate(product_elements):
            if idx in processed_indices:
                continue
                
            try:
                name = element.find_element(By.CSS_SELECTOR, "span[data-testid='main-productCardTitle-text']").text.strip()
                shelf_price = element.find_element(By.CSS_SELECTOR, "span[data-testid='main-productMainPrice-text-text']").text.strip()
                img_elem = element.find_element(By.CSS_SELECTOR, "img")
                image_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                
                product_key = (name, shelf_price, image_url)
                
                if product_key not in products_set:
                    products_set.add(product_key)
                    csv_writer.writerow([name, shelf_price, image_url])
                
                processed_indices.add(idx)
            except:
                pass
        
        
        csv_file.flush()
        
        new_products = len(products_set) - products_before
        total_products = len(products_set)
        
        sys.stdout.write(f"\rIteration: {iterations} | Total: {total_products} | New this round: {new_products}")
        sys.stdout.flush()
        
        button_found = False
        try:
            buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Rodyti daugiau')]]")
            if buttons:
                button = buttons[0]
               
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", button)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", button)
                button_found = True
                consecutive_no_button = 0
                time.sleep(1) 
            else:
                consecutive_no_button += 1
        except:
            consecutive_no_button += 1
        
        
        if consecutive_no_button >= 2:
            print("\n\nNo more 'Show More' button found. Scraping complete.")
            break
        
        
        if button_found:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.3)
        
        
        if iterations % 15 == 0:
            
            current_count = len(product_elements)
            processed_indices = {i for i in processed_indices if i < current_count + 100}

except KeyboardInterrupt:
    print("\n\nStopped by user")
finally:
    print(f"\n\nScraping completed!")
    print(f"Total unique products: {total_products}")
    print(f"Total iterations: {iterations}")
    driver.quit()
    csv_file.close()
