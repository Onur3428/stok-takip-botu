from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
import sys

# Function to check stock availability (For ZARA)
def check_stock_zara(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 20)

        # 1. ÇEREZ KAPATMA
        try:
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button.click()
        except TimeoutException:
            pass 

        # 2. BEDEN LİSTESİNİ AÇMA
        try:
            # 'Sepete Ekle' veya 'Ekle' butonunu bul
            try:
                add_to_cart_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa-action='add-to-cart']")))
            except:
                add_to_cart_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ekle')]")

            # Varsa önündeki engelleri (overlay) sil
            driver.execute_script("document.querySelectorAll('.zds-backdrop').forEach(el => el.remove());")
            
            # Butona tıkla
            driver.execute_script("arguments[0].click();", add_to_cart_button)
        except Exception:
            # Buton bulunamazsa belki zaten bedenler açıktır veya stok bitiktir, devam et
            pass

        # 3. BEDENLERİ TARA
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-sizes")))
        except:
            print(">> Beden listesi görüntülenemedi (Stok tamamen bitmiş olabilir).")
            return None

        size_elements = driver.find_elements(By.CLASS_NAME, "size-selector-sizes-size")
        
        for li in size_elements:
            try:
                # Beden ismini al (Örn: "S (US S)")
                try:
                    raw_text = li.find_element(By.CSS_SELECTOR, "div[data-qa-qualifier='size-selector-sizes-size-label']").text.strip()
                except:
                    raw_text = li.text.split('\n')[0].strip()

                # --- DÜZELTME BURADA ---
                # "S (US S)" yazısını boşluktan bölüp sadece ilk kelimeyi ("S") alıyoruz.
                site_beden_temiz = raw_text.split(' ')[0] 
                # -----------------------

                # Debug için ekrana yazalım (Sorun çözüldü mü görelim)
                # print(f"   Kontrol: Site='{raw_text}' -> Temiz='{site_beden_temiz}'")

                # Karşılaştırma (Artık "S" == "S" olacak)
                if site_beden_temiz in sizes_to_check:
                    
                    button = li.find_element(By.TAG_NAME, "button")
                    status = button.get_attribute("data-qa-action")
                    
                    # Stok Kontrolü
                    if status in ["size-in-stock", "size-low-on-stock"]:
                        print(f"   >>> STOK BULUNDU! ({site_beden_temiz})")
                        return site_beden_temiz
                    else:
                        # Beden var ama stok yok
                        pass
            
            except Exception:
                continue

        return False

    except Exception as e:
        print(f"Hata: {e}")
        return None

# Diğer mağazalar (Şimdilik boş geçiyor)
def rossmannStockCheck(driver): return False
def watsonsChecker(driver): return False

def check_stock_bershka(driver, sizes_to_check):
    # Bershka için basit bir kontrol
    try:
        wait = WebDriverWait(driver, 10)
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem']")
        for btn in buttons:
            txt = btn.text.strip()
            if txt in sizes_to_check:
                cls = btn.get_attribute("class")
                if "is-disabled" not in cls:
                    return txt
    except:
        pass
    return None

def check_stock_mango(driver, sizes_to_check):
    # Mango için basit kontrol
    return None