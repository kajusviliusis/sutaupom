from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import json
import re
import time

def setup_driver():
    options = webdriver.ChromeOptions()
    for arg in ['--headless', '--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled', 
                '--disable-gpu', '--disable-extensions', '--disable-logging', '--log-level=3',
                '--disable-images', '--blink-settings=imagesEnabled=false',
                'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36']:
        options.add_argument(arg)
    
    prefs = {
        'profile.managed_default_content_settings.images': 2,
        'profile.default_content_setting_values.notifications': 2,
    }
    options.add_experimental_option('prefs', prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # nelaukia visu resursu uzkrovimo
    options.page_load_strategy = 'eager' 
    
    driver = webdriver.Chrome(options=options)
    #kol atsiras elementas
    driver.implicitly_wait(1.5)
    return driver

def extract_price(text):
    if not text: return 'N/A'
    matches = re.findall(r'\d+[.,]\d+', str(text).replace('\xa0', '').replace('€', ''))
    return float(matches[-1].replace(',', '.')) if matches else 'N/A'

def scrape_page_products(driver):
    try:
        #8 sekundes laukiame kol pasikraus produktai
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-grid__item")))
        
        # lazy loading pagreitina
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.4)
        
        products = []
        product_elements = driver.find_elements(By.CSS_SELECTOR, "li.product-grid__item")
        
        for product in product_elements:
            try:
                
                try:
                    data = json.loads(product.get_attribute('data-gtm-eec-product'))
                    name = data.get('name', 'N/A')
                    price = float(data.get('price', 'N/A'))
                    
    
                    per_unit = 'N/A'
                    try:
                        per_unit = extract_price(product.find_element(By.CSS_SELECTOR, "p.card__price-per").text)
                    except: pass
                    
                    img = 'N/A'
                    try:
                        elem = product.find_element(By.CSS_SELECTOR, "img")
                        img = elem.get_attribute("src") or elem.get_attribute("data-src") or 'N/A'
                        if img and img.endswith('.svg'): img = 'N/A'
                    except: pass
                    
                    if name != 'N/A' and len(name) > 3:
                        products.append({
                            'product_name': name,
                            'shelf_price': price,
                            'per_unit_price': per_unit,
                            'image_url': img
                        })
                        continue
                except:
                    pass
                
                #DOM - document object model
                name = 'N/A'
                for sel in ["p.card__name", ".card__name", "[class*='name']"]:
                    try:
                        txt = product.find_element(By.CSS_SELECTOR, sel).text.strip()
                        if len(txt) > 3:
                            name = txt
                            break
                    except: pass
                
                if name == 'N/A': continue
                
                price = 'N/A'
                try:
                    tag = product.find_element(By.CSS_SELECTOR, "div.price-tag.card__price")
                    major = tag.find_element(By.CSS_SELECTOR, "span").text.strip()
                    cents = tag.find_element(By.CSS_SELECTOR, "sup").text.strip()
                    price = float(f"{major}.{cents}".replace(',', '.'))
                except:
                    for sel in ["span.card__price", ".price", "[class*='price']"]:
                        try:
                            price = extract_price(product.find_element(By.CSS_SELECTOR, sel).text)
                            if price != 'N/A': break
                        except: pass
                
             
                per_unit = 'N/A'
                try:
                    per_unit = extract_price(product.find_element(By.CSS_SELECTOR, "p.card__price-per").text)
                except: pass
                
                
                img = 'N/A'
                try:
                    elem = product.find_element(By.CSS_SELECTOR, "img")
                    img = elem.get_attribute("src") or elem.get_attribute("data-src") or 'N/A'
                    if img and img.endswith('.svg'): img = 'N/A'
                except: pass
                
                products.append({
                    'product_name': name,
                    'shelf_price': price,
                    'per_unit_price': per_unit,
                    'image_url': img
                })
            except: continue
        
        return products if products else None
    except TimeoutException:
        return None

def scrape_all_pages(url, max_pages=None):
    driver = setup_driver()
    all_products, page, empty_count = [], 1, 0
    
    try:
        driver.get(url)
        time.sleep(1)
        
        while not (max_pages and page > max_pages):
            products = scrape_page_products(driver)
            
            if not products:
                empty_count += 1
                if empty_count >= 2: break
            else:
                empty_count = 0
                all_products.extend(products)
                print(f"\rPage {page}: {len(products)} products | Total: {len(all_products)}", end='', flush=True)
            
            page += 1
            if max_pages and page > max_pages: break
            
            next_url = f"{url}{'&' if '?' in url else '?'}page={page}"
            driver.get(next_url)
            time.sleep(0.8)
        
        print(f"\n✓ Completed: {page-1} pages, {len(all_products)} products")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        driver.quit()
    
    return all_products

def save_to_csv(products, filename='rimi_products.csv'):
    if not products:
        print("✗ No products to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['product_name', 'shelf_price', 'per_unit_price', 'image_url'])
        writer.writeheader()
        writer.writerows([{k: '' if v == 'N/A' else v for k, v in p.items()} for p in products])
    
    print(f"✓ Saved to {filename}")

if __name__ == "__main__":
    products = scrape_all_pages("https://www.rimi.lt/e-parduotuve/lt/akcijos")
    if products: save_to_csv(products)
    print("Done!")