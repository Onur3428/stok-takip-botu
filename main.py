import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scraperHelpers import check_stock_zara, check_stock_bershka, check_stock_mango

# --- AYARLAR VE LİNKLER ---
# Test linkin ve diğerleri burada
URLS_TO_CHECK = [
    {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/yun-karisimli-kazak-p05755352.html?v1=484669241"
    },
     {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/yunlu-monty-harry-lambert-for-zara-x-disney-kazak-p05755376.html?v1=459127737"
    },
     {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/straight-fit-rahat-pantolon-p03046213.html?v1=484867453"
    },
     {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/yun-straight-fit-pantolon-p06807814.html?v1=485225817"
    },
     {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/jakarli-cizgili-t-shirt-p04087380.html?v1=465255237"
    },
    
    {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/relaxed-fit-limited-edition-jean-p03991391.html?v1=464614591"
    },
    {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/basic-fermuarli-yaka-sweatshirt-p00761311.html?v1=458120097"
    },
    {
        "store": "zara",
        "url": "https://www.zara.com/tr/tr/cizgili-jakarli-gomlek---limited-edition-p06402151.html?v1=477849840" 
    }
]

# Aranan Bedenler (Test için genişlettim)
SIZES_TO_CHECK = ["S", "M", "L", "XL", "38", "40", "42"] 

# GitHub Şifreleri
BOT_API = os.environ.get("BOT_API")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    if not BOT_API or not CHAT_ID:
        print("Telegram ayarlari eksik! (GitHub Secrets kısmını kontrol et)")
        return
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
        print(">> Telegram mesaji gonderildi.")
    except Exception as e:
        print(f"Telegram hatasi: {e}")

def main():
    print("GitHub Actions (Hayalet Mod) baslatiliyor...")
    
    # --- KAMUFLAJ AYARLARI ---
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 1. Otomasyon olduğunu gizle
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 2. Gerçek bir Windows PC gibi davran (User-Agent Hilesi)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Bot olduğu anlaşılmasın diye script değerini sil
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        for item in URLS_TO_CHECK:
            url = item.get("url")
            store = item.get("store")
            print(f"------------------------------------------------")
            print(f"Kontrol ediliyor: {url}")
            
            try:
                driver.get(url)
                # Sayfanın tam yüklenmesi için bekleme (Önemli!)
                time.sleep(5) 
                
                stok_durumu = None
                
                if store == "zara":
                    stok_durumu = check_stock_zara(driver, SIZES_TO_CHECK)
                elif store == "bershka":
                    stok_durumu = check_stock_bershka(driver, SIZES_TO_CHECK)
                elif store == "mango":
                    stok_durumu = check_stock_mango(driver, SIZES_TO_CHECK)
                
                if stok_durumu:
                    mesaj = f"🚨 STOK BULUNDU! 🚨\nMağaza: {store.upper()}\nBeden: {stok_durumu}\nLink: {url}"
                    print(mesaj)
                    send_telegram_message(mesaj)
                else:
                    print(" -> Stok yok (veya beden uymadi).")
            
            except Exception as e:
                print(f"Link kontrol hatasi: {e}")
            
            # Linkler arası bekleme
            time.sleep(random.randint(3, 7))

    except Exception as e:
        print(f"Genel hata: {e}")
    finally:
        driver.quit()
        print("Islem tamamlandi.")

if __name__ == "__main__":
    main()


