import subprocess
import time

print("🚀 Paleidžiamas Rimi scraperis...")
subprocess.run(["python3", "rimi_scrape_kodas.py"])
time.sleep(2)

print("\n🚀 Paleidžiamas Barbora scraperis...")
subprocess.run(["python3", "barborascrape.py"])

print("\n✅ Abu scraperiai baigė darbą.")