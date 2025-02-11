from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import json
from selenium import webdriver

def scrape_shopee(url):
    option = webdriver.ChromeOptions()
    option.add_argument('--headless') 
    option.add_argument('--disable-blink-features=AutomationControlled') 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    driver.set_window_size(1920, 1080)

    try:
        # driver.get("https://shopee.co.id/login")
        driver.get("https://shopee.tw/buyer/login")
        time.sleep(5)

        with open("./cookie/cookieLogin-ShopeeID.json", "r") as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = 'Lax'
            if 'secure' not in cookie:
                cookie['secure'] = True
            driver.add_cookie(cookie)

        driver.refresh()
        time.sleep(5)

    except Exception as e:
        print(f"Gagal melakukan login: {e}")
        driver.quit()
        return []

    results = []
    try:
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for area in soup.find_all('div', class_="flex card jNRWxO"):
            title = area.find("div", {"class": "attM6y"}).text.strip() if area.find("div", {"class": "attM6y"}) else "Tidak ditemukan"
            price = area.find("div", {"class": "pqTWkA"}).text.strip() if area.find("div", {"class": "pqTWkA"}) else "Tidak ditemukan"

            results.append({
                "url": url,
                "judul": title,
                "harga": price,
            })
        else:
            print("Section produk tidak ditemukan!")

    except Exception as e:
        print(f"Gagal scraping: {e}")

    driver.quit()
    return results

if __name__ == '__main__':
    # target_url = "https://shopee.co.id/product/551837787/12327628126"
    target_url = "https://shopee.tw/---i.43269385.23975514969"
    hasil_scraping = scrape_shopee(target_url)

    with open("./open-ai/hasil-shopee.json", "w", encoding='utf-8') as f:
        json.dump(hasil_scraping, f, indent=4, ensure_ascii=False)

    print("Scraping dan penyimpanan berhasil!")
