from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import json
import random


def handle_cookies(driver):
    print("\nLooking for cookie banner...")
    time.sleep(2)
    
    cookie_texts = [
        "Sutinku",
        "Sutikti", 
        "Priimti",
        "Gerai",
        "Accept",
        "Sutinku su visais",
        "Priimti visus"
    ]
    
    for text in cookie_texts:
        try:
            button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{text}')]"))
            )
            print(f"Found cookie button: '{text}'")
            time.sleep(random.uniform(0.5, 1))
            button.click()
            print("Clicked cookie button")
            time.sleep(1)
            return True
        except:
            continue
    
    try:
        selectors = [
            "button[id*='cookie']",
            "button[class*='cookie']",
            "button[id*='consent']",
            "button[class*='consent']",
            ".cookie-accept",
            "#cookie-accept",
            "[data-testid*='cookie']",
            "[data-testid*='consent']"
        ]
        
        for selector in selectors:
            try:
                button = driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed():
                    print(f"Found cookie button with selector: {selector}")
                    time.sleep(random.uniform(0.5, 1))
                    button.click()
                    print("Clicked cookie button")
                    time.sleep(1)
                    return True
            except:
                continue
    except:
        pass
    
    print("No cookie banner found or already accepted")
    return False


def handle_verification(driver, manual_wait=False):
    print("\nLooking for verification challenge...")
    time.sleep(3)
    
    if manual_wait:
        print("\n" + "="*60)
        print("MANUAL INTERVENTION MODE")
        print("="*60)
        print("Please manually click the verification checkbox if you see one.")
        print("Waiting 15 seconds...")
        time.sleep(15)
        print("Continuing...")
        return True
    
    try:
        driver.save_screenshot("verification_before.png")
        print("Saved 'verification_before.png'")
    except:
        pass
    
    try:
        with open("verification_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved 'verification_page.html'")
    except:
        pass
    
    try:
        print("  Method 1: Searching for all checkboxes...")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        print(f"  Found {len(checkboxes)} checkbox(es)")
        
        for idx, checkbox in enumerate(checkboxes):
            try:
                if checkbox.is_displayed() and checkbox.is_enabled() and not checkbox.is_selected():
                    parent = checkbox.find_element(By.XPATH, './ancestor::*[1]')
                    context = parent.text[:100] if parent.text else "No text"
                    print(f"  Checkbox {idx+1} context: {context}")
                    
                    print(f"  Clicking checkbox {idx+1}...")
                    time.sleep(random.uniform(1, 2))
                    
                    try:
                        checkbox.click()
                    except:
                        driver.execute_script("arguments[0].click();", checkbox)
                    
                    print(f"Clicked checkbox {idx+1}")
                    time.sleep(4)
                    
                    try:
                        driver.save_screenshot("verification_after_click.png")
                        print("Saved 'verification_after_click.png'")
                    except:
                        pass
                    
                    return True
            except Exception as e:
                print(f"  Checkbox {idx+1} error: {e}")
                continue
    except Exception as e:
        print(f"  Method 1 failed: {e}")
    
    try:
        print("  Method 2: Checking iframes...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"  Found {len(iframes)} iframe(s)")
        
        for idx, iframe in enumerate(iframes):
            try:
                iframe_src = iframe.get_attribute('src') or 'no src'
                print(f"  Iframe {idx+1}: {iframe_src[:80]}")
                
                driver.switch_to.frame(iframe)
                
                checkboxes = driver.find_elements(By.CSS_SELECTOR, 
                    'input[type="checkbox"], .recaptcha-checkbox, #recaptcha-anchor, [role="checkbox"]')
                
                if checkboxes:
                    print(f"  Found {len(checkboxes)} checkbox(es) in iframe {idx+1}")
                    for cb_idx, checkbox in enumerate(checkboxes):
                        try:
                            if checkbox.is_displayed():
                                print(f"  Clicking checkbox in iframe {idx+1}...")
                                time.sleep(random.uniform(1, 2))
                                
                                try:
                                    checkbox.click()
                                except:
                                    driver.execute_script("arguments[0].click();", checkbox)
                                
                                print(f"Clicked checkbox in iframe {idx+1}")
                                driver.switch_to.default_content()
                                time.sleep(4)
                                return True
                        except:
                            continue
                
                driver.switch_to.default_content()
            except Exception as e:
                driver.switch_to.default_content()
                print(f"  Iframe {idx+1} error: {e}")
                continue
    except Exception as e:
        driver.switch_to.default_content()
        print(f"  Method 2 failed: {e}")
    
    try:
        print("  Method 3: Looking for clickable verification divs...")
        verification_selectors = [
            '[class*="challenge"]',
            '[id*="challenge"]',
            '[class*="verify"]',
            '[id*="verify"]',
            '[class*="captcha"]',
            '[id*="captcha"]',
            '[class*="checkbox"]'
        ]
        
        for selector in verification_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Found {len(elements)} element(s) with {selector}")
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"  Clicking element with {selector}...")
                            time.sleep(random.uniform(1, 2))
                            elem.click()
                            print(f"Clicked element")
                            time.sleep(4)
                            return True
            except:
                continue
    except Exception as e:
        print(f"  Method 3 failed: {e}")
    
    print("Could not automatically handle verification")
    print("Tip: Run with manual_wait=True for manual clicking")
    return False


def scrape_barbora_products(manual_verification=True):
    chrome_options = Options()
    
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--lang=lt-LT')
    # chrome_options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=chrome_options)
    
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    })
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['lt-LT', 'lt', 'en-US', 'en']})")

    base_url = "https://barbora.lt/akcijos?page={}"
    all_products = []
    page = 1
    consecutive_empty_pages = 0
    max_empty_pages = 2

    try:
        print("="*60)
        print("Starting Barbora scraper")
        print("="*60)
        print("\nStep 1: Loading homepage...")
        driver.get("https://barbora.lt")
        
        time.sleep(3)
        
        print("\nStep 2: Handling cookies...")
        handle_cookies(driver)
        
        time.sleep(2)
        
        print("\nStep 3: Handling verification...")
        if manual_verification:
            handle_verification(driver, manual_wait=True)
        else:
            handle_verification(driver, manual_wait=False)
        
        time.sleep(2)
        
        print("\nStep 4: Starting product scraping...")

        while True:
            url = base_url.format(page)
            print(f"\n{'='*60}")
            print(f"Page {page}")
            print(f"{'='*60}")
            driver.get(url)

            time.sleep(random.uniform(3, 5))

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-testid^="product-card-"]'))
                )
                print("Products loaded")
            except TimeoutException:
                print(f"Timeout on page {page}")
                
                with open(f"page_{page}_debug.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                
                try:
                    driver.save_screenshot(f"page_{page}_screenshot.png")
                except:
                    pass
                
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    break
                page += 1
                continue

            time.sleep(random.uniform(2, 3))

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(random.uniform(0.5, 1))
            driver.execute_script("window.scrollTo(0, 0);")

            products = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid^="product-card-"]')
            
            if not products:
                products = driver.find_elements(By.CSS_SELECTOR, 'li[data-cnstrc-item-name]')
            
            print(f"Found {len(products)} products")

            if not products:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    break
            else:
                consecutive_empty_pages = 0 

            new_count = 0

            for idx, p in enumerate(products):
                try:
                    product = {
                        'title': p.get_attribute('data-cnstrc-item-name'),
                        'price': p.get_attribute('data-cnstrc-item-price'),
                        'image_small': '',
                    }
                    
                    try:
                        cart_data = p.find_element(By.CSS_SELECTOR, '[data-b-for-cart]')
                        json_str = cart_data.get_attribute('data-b-for-cart')
                        if json_str:
                            data = json.loads(json_str)
                            product['image_small'] = data.get('image', '')

                    except:
                        try:
                            img = p.find_element(By.CSS_SELECTOR, 'img[src*=".png"]')
                            product['image_small'] = img.get_attribute('src')
                        except:
                            pass
                    
                    if product['title']:
                        all_products.append(product)
                        new_count += 1
                        
                        if idx == 0:
                            print(f"  {product['title'][:50]}...")
                            print(f"     {product['price']} (was {product['retail_price']})")
                
                except:
                    continue

            print(f"  Added {new_count} products (Total: {len(all_products)})")

            if new_count == 0:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    break
            else:
                consecutive_empty_pages = 0

            page += 1
            time.sleep(random.uniform(2, 4))

        if all_products:
            df = pd.DataFrame(all_products)
            df.to_csv("barbora_all_pages.csv", index=False, encoding="utf-8")
            print(f"\n{'='*60}")
            print(f"SUCCESS!")
            print(f"{'='*60}")
            print(f"Scraped {len(all_products)} total products")
            print(f"Saved to 'barbora_all_pages.csv'")
            

    
            return df
        else:
            print("\nNo products scraped!")
            return None

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        if all_products:
            pd.DataFrame(all_products).to_csv("barbora_partial.csv", index=False)
    finally:
        print("\nClosing browser in 3 seconds...")
        time.sleep(3)
        driver.quit()
        
if __name__ == "__main__":
    scrape_barbora_products(manual_verification=True)
