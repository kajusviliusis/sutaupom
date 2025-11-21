import csv
import time
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from db_utils_sqlite import save_product_record


# --- Chrome setup su fallback į atskirą profilį ---
def setup_driver(use_profile=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option('prefs', {
        'profile.managed_default_content_settings.images': 2,
        'profile.default_content_setting_values.notifications': 2,
    })

    if use_profile:
        print("🧠 Naudojamas atskiras Chrome profilis (be konfliktų)")
        options.add_argument("user-data-dir=/Users/zem_simon/Documents/backend/chrome_profile")
    else:
        print("🟢 Naudojamas headless režimas")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(1.5)
    return driver


def scrape_barbora(driver):
    driver.get("https://www.barbora.lt/akcijos")
    print("🌍 Atidarytas Barbora puslapis, laukiama produktų...")

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".b-product, .b-product--inner, .b-product--wrap"))
    )
    products = driver.find_elements(By.CSS_SELECTOR, ".b-product, .b-product--inner, .b-product--wrap")

    scraped = []
    for p in products:
        try:
            name = p.find_element(By.CSS_SELECTOR, ".b-product-title").text.strip()
            price_text = p.find_element(By.CSS_SELECTOR, ".b-product-price-current").text.strip()
            price = float(price_text.replace("€", "").replace(",", ".").strip())

            try:
                discount_text = p.find_element(By.CSS_SELECTOR, ".b-product-price-old").text.strip()
                discount_price = float(discount_text.replace("€", "").replace(",", ".").strip())
            except:
                discount_price = None

            img = p.find_element(By.TAG_NAME, "img").get_attribute("src")

            scraped.append({
                "name": name,
                "price": price,
                "discount_price": discount_price,
                "image_url": img
            })

            # ✅ Įrašas į SQLite DB
            save_product_record(
                name=name,
                price=price,
                discount_price=discount_price,
                image_url=img,
                store_name="Barbora"
            )

            print(f"✅ {name}")

        except Exception as e:
            print(f"⚠️ Klaida skaitant produktą: {e}")

    return scraped

if __name__ == "__main__":
    try:
        # --- 1 bandymas: headless ---
        driver = setup_driver(use_profile=False)
        try:
            products = scrape_barbora(driver)
        except TimeoutException:
            print("\n⚠️ Produktų nepavyko gauti — bandome su atskiru Chrome profiliu...")
            driver.quit()

            # --- 2 bandymas: su profiliu ---
            driver = setup_driver(use_profile=True)
            products = scrape_barbora(driver)

        driver.quit()

        if products:
            with open("barbora_all_pages.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["name", "price", "discount_price", "image_url"])
                writer.writeheader()
                writer.writerows(products)
            print(f"💾 Išsaugota {len(products)} produktų į CSV ir DB ✅")
        else:
            print("❌ Nepavyko rasti produktų.")

    except Exception as e:
        print(f"❌ Kritinė klaida: {e}")