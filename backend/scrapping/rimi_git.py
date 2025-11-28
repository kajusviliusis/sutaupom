from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time
import json
import re

def setup_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    driver = webdriver.Chrome(options=options)
    if not headless:
        driver.maximize_window()
    return driver

def extract_shelf_price(product):
    try:
        price_tag = product.find_element(By.CSS_SELECTOR, "div.price-tag.card__price")
        major = price_tag.find_element(By.CSS_SELECTOR, "span").text.strip()
        cents = price_tag.find_element(By.CSS_SELECTOR, "sup").text.strip()
        if major and cents:
            return float(f"{major}.{cents}".replace(',', '.'))
    except:
        pass
    return None

def extract_price_from_text(price_text):
    if not price_text:
        return 'N/A'
    txt = price_text.replace('\xa0', ' ').replace('€', '').strip().replace(' ', '')
    matches = re.findall(r'\d+[.,]?\d*', txt)
    if not matches:
        return 'N/A'
    try:
        return float(matches[-1].replace(',', '.'))
    except:
        return 'N/A'

def scrape_page_products(driver):
    products = []
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-grid__item")))
        
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/3 * {i+1});")
            time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        product_elements = driver.find_elements(By.CSS_SELECTOR, "li.product-grid__item")

        for product in product_elements:
            try:
                product_code = product.get_attribute('data-product-code') or 'N/A'
                
                product_name = 'N/A'
                for selector in ["p.card__name", ".card__name", "[class*='name']", "h3", "h4", "p"]:
                    try:
                        text = product.find_element(By.CSS_SELECTOR, selector).text.strip()
                        if text and len(text) > 3:
                            product_name = text
                            break
                    except:
                        continue

                image_url = 'N/A'
                for selector in ["img", "img.card__image", "img[class*='product']", "img[class*='image']"]:
                    try:
                        src = product.find_element(By.CSS_SELECTOR, selector).get_attribute("src")
                        if src and len(src) > 5:
                            image_url = src
                            break
                    except:
                        continue

                shelf_price = extract_shelf_price(product)
                if not shelf_price:
                    shelf_price = 'N/A'

                if shelf_price == 'N/A':
                    try:
                        gtm_data = product.get_attribute('data-gtm-eec-product')
                        if gtm_data:
                            data = json.loads(gtm_data)
                            price_val = data.get('price')
                            if price_val is not None:
                                shelf_price = float(price_val) if isinstance(price_val, (int, float)) else extract_price_from_text(str(price_val))
                    except:
                        pass

                if shelf_price == 'N/A':
                    try:
                        data_price = product.get_attribute('data-price')
                        if data_price:
                            shelf_price = extract_price_from_text(data_price)
                    except:
                        pass

                if shelf_price == 'N/A':
                    for selector in ["span.card__price", ".price", "[class*='price']", "span[class*='Price']", ".product-price", ".product__price", "div.price", "span.price"]:
                        try:
                            price_text = product.find_element(By.CSS_SELECTOR, selector).text.strip()
                            p = extract_price_from_text(price_text)
                            if p != 'N/A':
                                shelf_price = p
                                break
                        except:
                            continue

                if product_name != 'N/A' or product_code != 'N/A':
                    products.append({
                        'shop_name': 'Rimi',
                        'product_name': product_name,
                        'shelf_price': shelf_price,
                        'image_url': image_url
                    })
            except:
                continue
    except TimeoutException:
        pass
    return products

def navigate_to_next_page(driver, current_page):
    try:
        time.sleep(2)
        for selector in ["button[aria-label*='next' i]", "a[aria-label*='next' i]", "button:has(svg):not(:disabled)", ".pagination button:last-child", ".pagination a:last-child", "button[class*='next']", "a[class*='next']", "a[rel='next']", "button[title*='Next' i]"]:
            try:
                for elem in driver.find_elements(By.CSS_SELECTOR, selector):
                    if elem.is_displayed() and elem.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                        time.sleep(1)
                        try:
                            elem.click()
                            time.sleep(4)
                            return True
                        except:
                            try:
                                driver.execute_script("arguments[0].click();", elem)
                                time.sleep(4)
                                return True
                            except:
                                continue
            except:
                continue

        try:
            current_url = driver.current_url
            if '?page=' in current_url:
                new_url = current_url.split('?page=')[0] + f'?page={current_page + 1}'
            else:
                separator = '&' if '?' in current_url else '?'
                new_url = f"{current_url}{separator}page={current_page + 1}"
            driver.get(new_url)
            time.sleep(4)
            return True
        except:
            pass
    except:
        pass
    return False

def detect_total_pages(driver):
    try:
        time.sleep(2)
        max_page = 1
        for selector in ["button[aria-label*='page']", "a[aria-label*='page']", ".pagination button", ".pagination a", "[class*='pagination'] button", "[class*='pagination'] a"]:
            try:
                for elem in driver.find_elements(By.CSS_SELECTOR, selector):
                    text = elem.text.strip()
                    if text.isdigit():
                        max_page = max(max_page, int(text))
                    aria_label = elem.get_attribute('aria-label') or ''
                    for match in re.findall(r'\d+', aria_label):
                        max_page = max(max_page, int(match))
            except:
                continue
        return max_page if max_page > 1 else None
    except:
        return None

def scrape_all_pages(url, max_pages=None, headless=True):
    driver = setup_driver(headless=headless)
    all_products = []
    try:
        driver.get(url)
        time.sleep(5)
        
        if max_pages is None:
            max_pages = detect_total_pages(driver) or 999

        for page_num in range(1, max_pages + 1):
            products = scrape_page_products(driver)
            if products:
                all_products.extend(products)
                print(f"Page: {page_num}/{max_pages if max_pages != 999 else '?'} | Total: {len(all_products)} | New: {len(products)}")
            else:
                print(f"Page {page_num}: No products, stopping.")
                break

            if page_num < max_pages and not navigate_to_next_page(driver, page_num):
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    return all_products

def save_to_csv(products, filename='rimi_products.csv'):
    if not products:
        print("No products to save!")
        return
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['shop_name', 'product_name', 'shelf_price', 'image_url'])
        writer.writeheader()
        for row in products:
            writer.writerow({
                'shop_name': row.get('shop_name', 'Rimi'),
                'product_name': row.get('product_name', 'N/A'),
                'shelf_price': '' if row.get('shelf_price') == 'N/A' else row.get('shelf_price'),
                'image_url': row.get('image_url', '')
            })
    print(f"Saved {len(products)} products to {filename}")

if __name__ == "__main__":
    url = "https://www.rimi.lt/e-parduotuve/lt/akcijos"
    products = scrape_all_pages(url, headless=True)
    if products:
        save_to_csv(products)
        print(f"\nDone! Total: {len(products)}")
    else:
        print("\nNo products scraped.")