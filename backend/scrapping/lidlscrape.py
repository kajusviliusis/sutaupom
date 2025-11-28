from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(40)
    return driver

def handle_cookies(driver):
    try:
        wait = WebDriverWait(driver, 8)
        selectors = [
            "button[id*='accept']",
            "button[class*='accept']",
            "button.didomi-button-highlight",
            "#onetrust-accept-btn-handler",
        ]
        for sel in selectors:
            try:
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                btn.click()
                print("Cookie banner accepted")
                time.sleep(1)
                return True
            except:
                continue

        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            text = (btn.text or "").strip().lower()
            if any(word in text for word in ['priimti', 'sutinku', 'accept', 'agree']):
                try:
                    btn.click()
                    print("Cookie banner accepted (by text)")
                    time.sleep(1)
                    return True
                except:
                    continue
    except Exception as e:
        print(f"Cookie handling: {e}")
    return False

def get_top_7_categories(driver):
    print("\n" + "="*60)
    print("EXTRACTING TOP 7 CATEGORIES")
    print("="*60)
    
    time.sleep(2)
    
    categories = []
    seen_urls = set()
    
    possible_selectors = [
        "a[href*='/c/']",
        ".category-tile a",
        "[class*='category'] a[href]",
    ]
    
    for selector in possible_selectors:
        try:
            links = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"Found {len(links)} potential links with selector: {selector}")
            
            for link in links:
                try:
                    if not link.is_displayed():
                        continue
                    
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    
                    if not href or href in seen_urls or len(text) < 3:
                        continue
                    
                    if any(x in href for x in ['login', 'account', 'cart', 'search', 'kontaktai']):
                        continue
                    
                    if '/c/' not in href:
                        continue
                    
                    y_pos = link.location.get('y', 0)
                    if y_pos > 2000:
                        continue
                    
                    categories.append({
                        "name": text,
                        "url": href
                    })
                    seen_urls.add(href)
                    
                    print(f"Category {len(categories)}: {text}")
                    
                    if len(categories) >= 7:
                        break
                        
                except Exception as e:
                    continue
            
            if len(categories) >= 7:
                break
                
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
            continue
    
    print(f"\nFound {len(categories)} categories total\n")
    return categories[:7]

def extract_visible_products(driver, already_scraped_names):
    products = []
    
    product_selectors = [
        "[id^='grid-item-']",
        "article[class*='product']",
        "[class*='product-grid'] [class*='item']",
        ".product-tile",
        "[data-product]",
        ".grid__item",
        "[class*='ProductGridBox']",
    ]
    
    product_elements = []
    for selector in product_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and len(elements) > 5:
                product_elements = elements
                break
        except:
            continue
    
    if not product_elements:
        print("No product elements found with any selector")
        return []
    
    for element in product_elements:
        try:
            product = {
                "shop_name": "Lidl",
                "product_name": "",
                "shelf_price": "",
                "image_url": ""
            }
            
            name_selectors = [
                "h3", "h2", "h1",
                "[class*='title']", 
                "[class*='name']",
                "[class*='product-name']",
                "a[class*='product']",
                ".product-title",
            ]
            for sel in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, sel)
                    name = name_elem.text.strip()
                    if name and len(name) > 2:
                        name = name.replace("SUPERKAINA!", "").strip()
                        name = name.replace("AKCIJA!", "").strip()
                        name = name.replace("NAUJA!", "").strip()
                        name = ' '.join(name.split())
                        if name:
                            product["product_name"] = name
                            break
                except:
                    continue
            
            if not product["product_name"]:
                continue
            
            if product["product_name"] in already_scraped_names:
                continue
            
            shelf_price = ""
            
            try:
                price_containers = element.find_elements(By.CSS_SELECTOR, 
                    "[class*='pricefield'], [class*='price-container'], [class*='Price']")
                
                for container in price_containers:
                    price_elements = container.find_elements(By.CSS_SELECTOR, 
                        "span, div, [class*='price'], [class*='value']")
                    
                    for price_elem in price_elements:
                        price_text = price_elem.text.strip()
                        
                        if not price_text or len(price_text) > 20:
                            continue
                        
                        if '%' in price_text:
                            continue
                        
                        if any(unit in price_text.lower() for unit in ['kg', ' l', '/kg', '/l', 'vnt', 'pac', '/vnt']):
                            continue
                        
                        if '€' in price_text and any(c.isdigit() for c in price_text):
                            if ',' in price_text or '.' in price_text:
                                shelf_price = price_text
                                break
                    
                    if shelf_price:
                        break
            except:
                pass
            
            if not shelf_price:
                try:
                    all_price_elements = element.find_elements(By.CSS_SELECTOR, "[class*='price']")
                    
                    for elem in all_price_elements:
                        text = elem.text.strip()
                        
                        if not text or len(text) > 20:
                            continue
                        if '%' in text:
                            continue
                        if any(unit in text.lower() for unit in ['kg', ' l', '/kg', '/l', 'vnt', 'pac', '/vnt']):
                            continue
                        
                        if '€' in text and any(c.isdigit() for c in text):
                            if ',' in text or '.' in text:
                                shelf_price = text
                                break
                except:
                    pass
            
            product["shelf_price"] = shelf_price.replace('€', '').strip() if shelf_price else "N/A"
            
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, "img")
                img_url = (img_elem.get_attribute("src") or 
                          img_elem.get_attribute("data-src") or
                          img_elem.get_attribute("data-lazy-src"))
                product["image_url"] = img_url if img_url else "N/A"
            except:
                product["image_url"] = "N/A"
            
            products.append(product)
            already_scraped_names.add(product["product_name"])
            
        except Exception as e:
            continue
    
    return products

def scrape_category_incremental(driver, category_url, category_name):
    print("\n" + "="*60)
    print(f"SCRAPING: {category_name}")
    print(f"URL: {category_url}")
    print("="*60)
    
    all_products = []
    already_scraped_names = set()
    
    try:
        driver.get(category_url)
        time.sleep(3)
        
        handle_cookies(driver)
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        attempts = 0
        max_attempts = 50
        no_new_products_count = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            print(f"\nLoad Cycle {attempts}")
            
            new_products = extract_visible_products(driver, already_scraped_names)
            
            if new_products:
                all_products.extend(new_products)
                print(f"Scraped {len(new_products)} NEW products")
                print(f"Total scraped so far: {len(all_products)}")
                no_new_products_count = 0
            else:
                print(f"No new products found in this cycle")
                no_new_products_count += 1
                
                if no_new_products_count >= 3:
                    print(f"No new products for {no_new_products_count} cycles - stopping")
                    break
            
            button_clicked = False
            
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                button_selectors = [
                    "//button[contains(., 'Daugiau')]",
                    "//button[contains(., 'pasiūlymų')]",
                    "//button[contains(@class, 'load-more')]",
                    "//button[contains(@class, 'Load')]",
                    "button[class*='more']",
                    "button[class*='Load']",
                ]
                
                for selector in button_selectors:
                    try:
                        if selector.startswith("//"):
                            buttons = driver.find_elements(By.XPATH, selector)
                        else:
                            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for btn in buttons:
                            try:
                                if btn.is_displayed() and btn.is_enabled():
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                    time.sleep(0.5)
                                    
                                    try:
                                        btn.click()
                                    except:
                                        driver.execute_script("arguments[0].click();", btn)
                                    
                                    button_clicked = True
                                    print("Clicked 'Daugiau pasiulymu' button - waiting for new products")
                                    time.sleep(2.5)
                                    break
                            except:
                                continue
                        
                        if button_clicked:
                            break
                            
                    except:
                        continue
                
                if not button_clicked:
                    print("No 'Daugiau pasiulymu' button found - might be at the end")
                    
                    if no_new_products_count >= 1:
                        print("All products have been loaded and scraped")
                        break
                    
            except Exception as e:
                print(f"Error finding/clicking button: {e}")
                if no_new_products_count >= 2:
                    break
        
        print(f"\n{'='*60}")
        print(f"Finished scraping {category_name}")
        print(f"Total products scraped: {len(all_products)}")
        print(f"{'='*60}\n")
        
        return all_products
        
    except Exception as e:
        print(f"Error scraping category {category_name}: {e}\n")
        return all_products

def scrape_all_categories(base_url):
    driver = setup_driver()
    all_products = []
    
    try:
        print(f"Loading main page: {base_url}")
        driver.get(base_url)
        time.sleep(3)
        
        handle_cookies(driver)
        
        categories = get_top_7_categories(driver)
        
        if not categories:
            print("No categories found")
            return []
        
        for idx, cat in enumerate(categories, 1):
            print(f"\n{'='*60}")
            print(f"CATEGORY {idx} of {len(categories)}")
            print(f"{'='*60}")
            
            cat_products = scrape_category_incremental(driver, cat["url"], cat["name"])
            all_products.extend(cat_products)
            
            print(f"Running total: {len(all_products)} products")
            
            time.sleep(2)
        
    except Exception as e:
        print(f"\nCritical error: {e}")
        
    finally:
        driver.quit()
        print("\n" + "="*60)
        print("SCRAPING COMPLETE")
        print("="*60)
    
    return all_products

def save_to_csv(products, filename="lidl_products.csv"):
    if not products:
        print("No products to save")
        return
    
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["shop_name", "product_name", "shelf_price", "image_url"])
        
        for product in products:
            writer.writerow([
                product["shop_name"],
                product["product_name"],
                product["shelf_price"],
                product["image_url"]
            ])
    
    print(f"\nSaved {len(products)} products to {filename}")

def main():
    base_url = "https://www.lidl.lt/c/visos-sios-savaites-akcijos/"
    
    print("\n" + "="*60)
    print("LIDL PRODUCT SCRAPER")
    print("="*60)
    print(f"Target: {base_url}\n")
    
    products = scrape_all_categories(base_url)
    
    if products:
        save_to_csv(products)
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS: {len(products)} total products scraped")
        print(f"{'='*60}\n")
    else:
        print("\nNo products were scraped\n")

if __name__ == "__main__":
    main()