from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
import json
import re

def setup_driver():
    """Setup Chrome driver with options"""
    options = webdriver.ChromeOptions()
    # Uncomment to run without browser window
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def extract_shelf_price(product):
    """Extract the actual shelf price from the price-tag element"""
    try:
        # Look for the price-tag card__price element (works for both regular and discounted)
        price_tag = product.find_element(By.CSS_SELECTOR, "div.price-tag.card__price")
        
        # Get the main number (span)
        major = price_tag.find_element(By.CSS_SELECTOR, "span").text.strip()
        
        # Get the cents/superscript (sup)
        cents = price_tag.find_element(By.CSS_SELECTOR, "sup").text.strip()
        
        # Combine them: "1" + "75" = "1.75"
        if major and cents:
            price_str = f"{major}.{cents}".replace(',', '.')
            return float(price_str)
    except Exception:
        pass
    
    return None

def extract_per_unit_price(product):
    """Extract the per-kg/per-unit price from card__price-per"""
    try:
        # Look specifically for card__price-per paragraph
        per_unit_elem = product.find_element(By.CSS_SELECTOR, "p.card__price-per")
        per_unit_text = per_unit_elem.text.strip()
        
        # Extract number from "17,50 €/kg" or "2,83 €/kg"
        matches = re.findall(r'\d+[.,]\d+', per_unit_text)
        if matches:
            price_str = matches[0].replace(',', '.')
            return float(price_str)
    except Exception:
        pass
    
    return None

def extract_price_from_text(price_text):
    """Normalize price text and extract a float (fallback method)"""
    if not price_text:
        return 'N/A'
    txt = price_text.replace('\xa0', ' ').replace('€', '').strip()
    txt = txt.replace(' ', '')
    matches = re.findall(r'\d+[.,]?\d*', txt)
    if not matches:
        return 'N/A'
    candidate = matches[-1].replace(',', '.')
    try:
        return float(candidate)
    except:
        return 'N/A'

def scroll_and_wait(driver):
    """Scroll page and wait for content to load"""
    print("  Scrolling to load products...")
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3 * {});".format(i+1))
        time.sleep(1)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def scrape_page_products(driver):
    """Scrape all products from current page"""
    products = []
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-grid__item"))
        )
        
        scroll_and_wait(driver)
        
        product_elements = driver.find_elements(By.CSS_SELECTOR, "li.product-grid__item")
        print(f"  Found {len(product_elements)} products")
        
        for idx, product in enumerate(product_elements):
            try:
                product_code = product.get_attribute('data-product-code') or 'N/A'
                product_name = 'N/A'
                name_selectors = [
                    "p.card__name",
                    ".card__name",
                    "[class*='name']",
                    "h3", "h4", "p"
                ]
                for selector in name_selectors:
                    try:
                        name_elem = product.find_element(By.CSS_SELECTOR, selector)
                        text = name_elem.text.strip()
                        if text and len(text) > 3:
                            product_name = text
                            break
                    except Exception:
                        continue
                
                # ==== IMAGE URL EXTRACTION ====
                image_url = 'N/A'
                try:
                    img_selectors = [
                        "img",
                        "img.card__image",
                        "img[class*='product']",
                        "img[class*='image']"
                    ]
                    for selector in img_selectors:
                        try:
                            img_elem = product.find_element(By.CSS_SELECTOR, selector)
                            src = img_elem.get_attribute("src")
                            if src and len(src) > 5:
                                image_url = src
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
                # ================================

                # ==== PRICE EXTRACTION (FIXED) ====
                shelf_price = 'N/A'
                per_unit_price = 'N/A'
                
                # Method 1: Try the price-tag element (works for ALL products)
                price = extract_shelf_price(product)
                if price:
                    shelf_price = price
                    print(f"    Product {idx+1}: Found shelf price: €{shelf_price}")
                
                # Method 2: Fallback to GTM data if price-tag method fails
                if shelf_price == 'N/A':
                    try:
                        gtm_data = product.get_attribute('data-gtm-eec-product')
                        if gtm_data:
                            try:
                                data = json.loads(gtm_data)
                                price_val = data.get('price', None)
                                if price_val is not None:
                                    if isinstance(price_val, (int, float)):
                                        shelf_price = float(price_val)
                                    else:
                                        shelf_price = extract_price_from_text(str(price_val))
                                    if shelf_price != 'N/A':
                                        print(f"    Product {idx+1}: Found shelf price in GTM: €{shelf_price}")
                            except Exception:
                                pass
                    except Exception:
                        pass
                
                # Always try to get the per-unit price (€/kg)
                per_unit = extract_per_unit_price(product)
                if per_unit:
                    per_unit_price = per_unit
                    print(f"    Product {idx+1}: Found per-unit price: €{per_unit_price}/kg")
                
                if shelf_price == 'N/A':
                    try:
                        data_price = product.get_attribute('data-price')
                        if data_price:
                            p = extract_price_from_text(data_price)
                            if p != 'N/A':
                                shelf_price = p
                    except Exception:
                        pass
                
                if shelf_price == 'N/A':
                    price_selectors = [
                        "span.card__price",
                        ".price",
                        "[class*='price']",
                        "span[class*='Price']",
                        ".product-price", 
                        ".product__price",
                        "div.price", 
                        "span.price"
                    ]
                    for selector in price_selectors:
                        try:
                            price_elem = product.find_element(By.CSS_SELECTOR, selector)
                            price_text = price_elem.text.strip()
                            p = extract_price_from_text(price_text)
                            if p != 'N/A':
                                shelf_price = p
                                break
                        except Exception:
                            continue
                # ====================================
                
                if product_name != 'N/A' or product_code != 'N/A':
                    products.append({
                        'product_code': product_code,
                        'product_name': product_name,
                        'shelf_price': shelf_price,
                        'per_unit_price': per_unit_price,
                        'image_url': image_url
                    })
                    
                    if idx < 3:
                        print(f"    Sample product {idx+1}:")
                        print(f"      Code: {product_code}")
                        print(f"      Name: {product_name}")
                        print(f"      Shelf Price: €{shelf_price}")
                        print(f"      Per Unit: €{per_unit_price}/kg")
                        print(f"      Image: {image_url}")
                        
            except Exception as e:
                print(f"    Error on product {idx+1}: {repr(e)}")
                continue
    
    except TimeoutException:
        print("  ⚠ Timeout waiting for products")
    
    return products

def navigate_to_next_page(driver, current_page):
    """Navigate to next page"""
    try:
        print(f"  Looking for next page button...")
        time.sleep(2)
        next_selectors = [
            "button[aria-label*='next' i]",
            "a[aria-label*='next' i]",
            "button:has(svg):not(:disabled)",
            ".pagination button:last-child",
            ".pagination a:last-child",
            "button[class*='next']",
            "a[class*='next']",
            "a[rel='next']",
            "button[title*='Next' i]"
        ]
        for selector in next_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                        time.sleep(1)
                        try:
                            elem.click()
                            print(f"  ✓ Clicked next button")
                            time.sleep(4)
                            return True
                        except Exception:
                            try:
                                driver.execute_script("arguments[0].click();", elem)
                                print(f"  ✓ Clicked next button (JS)")
                                time.sleep(4)
                                return True
                            except Exception:
                                continue
            except Exception:
                continue
        
        try:
            current_url = driver.current_url
            if '?page=' in current_url:
                base = current_url.split('?page=')[0]
                new_url = base + f'?page={current_page + 1}'
            else:
                separator = '&' if '?' in current_url else '?'
                new_url = f"{current_url}{separator}page={current_page + 1}"
            print(f"  Trying URL navigation: {new_url}")
            driver.get(new_url)
            time.sleep(4)
            return True
        except Exception as e:
            print(f"  ⚠ URL navigation failed: {e}")
        return False
    except Exception as e:
        print(f"  ⚠ Error navigating: {e}")
        return False

def scrape_all_pages(url, max_pages=81):
    """Scrape all pages"""
    driver = setup_driver()
    all_products = []
    
    try:
        print(f"\nOpening: {url}")
        driver.get(url)
        time.sleep(5)
        
        for page_num in range(1, max_pages + 1):
            print(f"\n{'='*60}")
            print(f"PAGE {page_num}/{max_pages}")
            print(f"{'='*60}")
            
            products = scrape_page_products(driver)
            if products:
                all_products.extend(products)
                print(f"  ✓ Scraped {len(products)} products")
                print(f"  📊 Total so far: {len(all_products)} products")
            else:
                print(f"  ⚠ No products found on this page!")
            
            if page_num < max_pages:
                if not navigate_to_next_page(driver, page_num):
                    print(f"\n  ⚠ Failed to navigate. Stopping at page {page_num}")
                    break
            else:
                print(f"\n  ✓ Completed all {max_pages} pages!")
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing browser...")
        driver.quit()
    
    return all_products

def save_to_csv(products, filename='rimi_products.csv'):
    """Save to CSV"""
    if not products:
        print("\n❌ No products to save!")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['product_name', 'shelf_price', 'per_unit_price', 'image_url'])
        writer.writeheader()
        for row in products:
            out_row = {
                'product_name': row.get('product_name', 'N/A'),
                'shelf_price': '' if row.get('shelf_price') == 'N/A' else row.get('shelf_price'),
                'per_unit_price': '' if row.get('per_unit_price') == 'N/A' else row.get('per_unit_price'),
                'image_url': row.get('image_url', '')
            }
            writer.writerow(out_row)
    
    print(f"\n✅ Saved {len(products)} products to {filename}")

if __name__ == "__main__":
    url = "https://www.rimi.lt/e-parduotuve/lt/akcijos"
    test_pages = 146
    
    print("=" * 60)
    print("RIMI PRODUCT SCRAPER (Updated with shelf + per-unit prices)")
    print("=" * 60)
    print(f"\n⚠ TESTING MODE: Scraping {test_pages} pages first")
    print("Change test_pages variable to scrape more pages")
    print("=" * 60)
    
    products = scrape_all_pages(url, max_pages=test_pages)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total products: {len(products)}")
    
    if products:
        print("\nFirst 5 products:")
        for p in products[:5]:
            print(f"\n  Code: {p['product_code']}")
            print(f"  Name: {p['product_name']}")
            print(f"  Shelf Price: €{p['shelf_price']}")
            print(f"  Per Unit: €{p['per_unit_price']}/kg")
            print(f"  Image: {p['image_url']}")
        
        save_to_csv(products)
    
    print("\n✅ Done!")