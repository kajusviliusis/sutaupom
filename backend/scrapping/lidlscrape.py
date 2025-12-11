from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import csv
import re


# ============================================
# CONFIG
# ============================================

BASE_URL = "https://www.lidl.lt/c/visos-sios-savaites-akcijos/"

CATEGORY_TEXTS = [
    "Maistas, gėrimai ir buities prekės",
    "Virtuvės ir namų apyvokos prekės",
    "Sodas ir dirbtuvės",
    "Sportas ir laisvalaikis",
    "Baldai ir namų interjeras",
    "Apranga ir aksesuarai",
    "Prekės vaikams ir kūdikiams, žaislai",
]


# ============================================
# DRIVER & COOKIES
# ============================================

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # uncomment if you want headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
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
            except Exception:
                continue

        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            text = (btn.text or "").strip().lower()
            if any(word in text for word in ["priimti", "sutinku", "accept", "agree"]):
                try:
                    btn.click()
                    print("Cookie banner accepted (by text)")
                    time.sleep(1)
                    return True
                except Exception:
                    continue
    except Exception as e:
        print(f"Cookie handling error: {e}")
    return False


def safe_click(driver, element):
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


# ============================================
# CATEGORY URL DISCOVERY (the 7 circles)
# ============================================

def get_category_urls(driver):
    """
    On BASE_URL, find the 7 circles by their Lithuanian text and extract <a href>.
    """
    wait = WebDriverWait(driver, 15)
    category_links = []

    for text in CATEGORY_TEXTS:
        xpath = "//*[contains(normalize-space(), %s)]/ancestor::a[1]" % repr(text)
        try:
            link_el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            href = link_el.get_attribute("href")
            if href:
                category_links.append({"name": text, "url": href})
                print(f"Category found: '{text}' -> {href}")
            else:
                print(f"[WARN] No href for category text: {text}")
        except TimeoutException:
            print(f"[WARN] Could not locate category blob for text: {text}")

    print(f"\nTotal category URLs found: {len(category_links)}\n")
    return category_links


# ============================================
# PRODUCT COLLECTION FOR CURRENTLY VISIBLE CARDS
# ============================================

def collect_visible_products(driver, seen_ids):
    """
    Scrape all products currently visible in the DOM.
    We identify cards by classes Lidl uses:
      - div.product-grid-box
      - div.odsc-tile
      - [data-qa-label*='product-grid-box']
    Each product ID is the href of its link, else name+price.
    """
    products = []

    # gather all candidate card elements, de-duplicated by Selenium element id
    card_selectors = [
        "div.product-grid-box",
        "div.odsc-tile",
        "[data-qa-label*='product-grid-box']",
    ]
    card_ids = set()
    card_elements = []

    for sel in card_selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in elems:
                if el.id not in card_ids:
                    card_ids.add(el.id)
                    card_elements.append(el)
        except Exception:
            continue

    print(f"collect_visible_products: found {len(card_elements)} candidate cards")

    for card in card_elements:
        try:
            # ---- link + name ----
            name_text = ""
            href = ""

            # link based name (preferred)
            try:
                link = card.find_element(By.CSS_SELECTOR, "a.odsc-tile__link")
                name_text = (link.text or "").strip()
                href = link.get_attribute("href") or ""
            except Exception:
                pass

            # fallback: title element
            if not name_text:
                try:
                    title = card.find_element(By.CSS_SELECTOR, ".product-grid-box__title")
                    name_text = (title.text or "").strip()
                except Exception:
                    pass

            if not name_text:
                # if no text at all, skip this card
                continue

            # brand
            brand = ""
            try:
                brand_el = card.find_element(By.CSS_SELECTOR, ".product-grid-box__brand")
                brand = (brand_el.text or "").strip()
            except Exception:
                pass

            if brand and brand.lower() not in name_text.lower():
                full_name = f"{brand} {name_text}".strip()
            else:
                full_name = name_text.strip()

            # clean promo noise
            for junk in ["SUPERKAINA!", "SUPER KAINA", "AKCIJA!", "NAUJA!"]:
                full_name = full_name.replace(junk, "")
            full_name = " ".join(full_name.split())

            if not full_name or len(full_name) < 3:
                continue

            # ---- price ----
            price_str = ""
            try:
                price_el = card.find_element(
                    By.CSS_SELECTOR,
                    ".product-grid-box__price .ods-price__value"
                )
                price_text = (price_el.text or "").strip()
                # remove euro sign before parsing, just in case
                price_text_clean = price_text.replace("€", "")
                m = re.search(r"(\d+[.,]\d+)", price_text_clean.replace(" ", ""))
                if m:
                    price_str = m.group(1).replace(",", ".")
            except Exception:
                # last-resort: look for any '€' with a number inside the card
                try:
                    euro_els = card.find_elements(
                        By.XPATH, ".//*[contains(normalize-space(), '€')]"
                    )
                    for e in euro_els:
                        t = (e.text or "").strip()
                        if any(ch.isdigit() for ch in t):
                            t_clean = t.replace("€", "")
                            mm = re.search(r"(\d+[.,]\d+)", t_clean.replace(" ", ""))
                            if mm:
                                price_str = mm.group(1).replace(",", ".")
                                break
                except Exception:
                    pass

            if not price_str:
                # skip products without a clear price
                continue

            # ---- image ----
            img_url = "N/A"
            try:
                img_el = card.find_element(By.CSS_SELECTOR, ".odsc-image-gallery__image")
                img_url = (
                    img_el.get_attribute("src")
                    or img_el.get_attribute("data-src")
                    or img_el.get_attribute("data-lazy-src")
                    or "N/A"
                )
            except Exception:
                try:
                    img_el = card.find_element(By.CSS_SELECTOR, "img")
                    img_url = (
                        img_el.get_attribute("src")
                        or img_el.get_attribute("data-src")
                        or img_el.get_attribute("data-lazy-src")
                        or "N/A"
                    )
                except Exception:
                    img_url = "N/A"

            # ---- product ID for de-duplication ----
            if href:
                product_id = href
            else:
                product_id = f"{full_name}|{price_str}"

            if product_id in seen_ids:
                continue

            seen_ids.add(product_id)

            products.append({
                "shop_name": "Lidl",
                "product_name": full_name,
                "shelf_price": price_str,  # numeric string, no €
                "image_url": img_url,
            })

        except Exception:
            continue

    print(f"collect_visible_products: extracted {len(products)} NEW products in this pass")
    return products


# ============================================
# CATEGORY SCRAPING (incremental: 12 → load more → 12 → ...)
# ============================================

def scrape_category_incremental(driver, category_url, category_name):
    print("\n" + "=" * 60)
    print(f"SCRAPING CATEGORY: {category_name}")
    print(f"URL: {category_url}")
    print("=" * 60)

    all_products = []
    seen_ids = set()
    rounds_without_new = 0

    driver.get(category_url)
    time.sleep(3)
    handle_cookies(driver)

    # start at top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    while True:
        # 1) scrape currently visible products
        new_products = collect_visible_products(driver, seen_ids)

        if new_products:
            rounds_without_new = 0
            all_products.extend(new_products)
            print(f"Total products scraped in this category so far: {len(all_products)}")
        else:
            rounds_without_new += 1
            print(f"No new products found this round (#{rounds_without_new})")

        # 2) try to click 'Daugiau produktų' to load more products
        button_clicked = False
        try:
            buttons = driver.find_elements(
                By.XPATH, "//button[contains(., 'Daugiau produktų')]"
            )
            buttons = [b for b in buttons if b.is_displayed() and b.is_enabled()]
            if buttons:
                btn = buttons[0]
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", btn
                )
                time.sleep(0.5)
                safe_click(driver, btn)
                button_clicked = True
                print("Clicked 'Daugiau produktų' – loading next batch of products...")
                time.sleep(3)
            else:
                print("No 'Daugiau produktų' button – probably at the end of this category.")
        except Exception as e:
            print(f"Error trying to click 'Daugiau produktų': {e}")

        # 3) stop conditions
        if not button_clicked:
            # no more button, and we already scraped everything visible
            if rounds_without_new >= 1:
                print("Reached end of category; stopping.")
                break

        if rounds_without_new >= 3:
            print("No new products for 3 rounds – stopping this category.")
            break

        # small scroll to encourage new content rendering
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)

    print(f"Finished category '{category_name}'. Scraped {len(all_products)} products.")
    return all_products


# ============================================
# ALL CATEGORIES
# ============================================

def scrape_all_categories(base_url):
    driver = setup_driver()
    all_products = []

    try:
        print(f"Loading main page: {base_url}")
        driver.get(base_url)
        time.sleep(3)
        handle_cookies(driver)

        categories = get_category_urls(driver)
        if not categories:
            print("No categories found. Stopping.")
            return []

        for idx, cat in enumerate(categories, 1):
            print(f"\nCATEGORY {idx} of {len(categories)}")
            cat_products = scrape_category_incremental(driver, cat["url"], cat["name"])
            all_products.extend(cat_products)
            print(f"Running total across all categories: {len(all_products)}")
            time.sleep(2)

    except Exception as e:
        print(f"\nCritical error during scraping: {e}")
    finally:
        driver.quit()
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)

    return all_products


# ============================================
# CSV & MAIN
# ============================================

def save_to_csv(products, filename="lidl_products.csv"):
    if not products:
        print("No products to save.")
        return

    # QUOTE_ALL => every field in every row is wrapped in double quotes
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["shop_name", "product_name", "shelf_price", "image_url"])
        for p in products:
            writer.writerow([
                p["shop_name"],
                p["product_name"],
                p["shelf_price"],
                p["image_url"],
            ])

    print(f"\nSaved {len(products)} products to {filename}")


def main():
    print("\n" + "=" * 60)
    print("LIDL PRODUCT SCRAPER – LITHUANIA (incremental)")
    print("=" * 60)
    print(f"Target: {BASE_URL}\n")

    products = scrape_all_categories(BASE_URL)

    if products:
        save_to_csv(products)
        print("\n" + "=" * 60)
        print(f"FINAL RESULTS: {len(products)} total products scraped")
        print("=" * 60 + "\n")
    else:
        print("\nNo products were scraped.\n")


if __name__ == "__main__":
    main()
