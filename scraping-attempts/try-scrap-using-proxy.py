from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

PROXIES = [
    "http://userProxy:passwordProxy@addressProxy:portProxy",
    "http://userProxy:passwordProxy@addressProxy:portProxy",
    "http://userProxy:passwordProxy@addressProxy:portProxy",
]

def login_shopee():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://shopee.tw/buyer/login")
    
    input("Login ke Shopee menggunakan akun Google lalu tekan ENTER untuk melanjutkan...")
    
    cookies = driver.get_cookies()
    with open("./cookie/cookieLogin-ShopeeID.json", "wb") as f:
        pickle.dump(cookies, f)
    
    driver.quit()

def scrape_shopee_product(url):
    try:
        with open("./cookie/cookieLogin-ShopeeID.json", "rb") as f:
            cookies = pickle.load(f)
    except FileNotFoundError:
        return {"error": "Cookie file not found. Please log in first."}
    
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    response = session.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("div", {"class": "attM6y"}).text.strip() if soup.find("div", {"class": "attM6y"}) else "Tidak ditemukan"
        price = soup.find("div", {"class": "pqTWkA"}).text.strip() if soup.find("div", {"class": "pqTWkA"}) else "Tidak ditemukan"
        return {"url": url, "title": title, "price": price}
    else:
        return {"error": f"Failed to fetch page, status code: {response.status_code}"}

@app.route('/login', methods=['GET'])
def api_login():
    login_shopee()
    return jsonify({"message": "Login successful"})

@app.route('/scrape', methods=['POST'])
def api_scrape():
    data = request.get_json()
    url = data.get("url") if data else "https://shopee.tw/---i.43269385.23975514969"
    if not url:
        return jsonify({"error": "No URL provided."}), 400
    
    result = scrape_shopee_product(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5758, debug=True)
