from flask import Flask
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from waitress import serve


app = Flask(__name__)

# ---------- CONFIG ----------
URL = "https://prisma-sprachzentrum.com/telc-deutsch-b2/"
SELECTORS = {
    "date_dropdown": "select#form-field-prufungsdatum"
}
TOKEN = "8241226867:AAEyXdRWnoBLulfgD_u7IyhOMN1H6c-4co0"
CHAT_ID = "1900853158"

# ---------- FUNCTIONS ----------
def make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
        print("📨 Telegram message sent.")
    except Exception as e:
        print("❌ Failed to send Telegram message:", e)

def is_date_available(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["date_dropdown"])))
        dropdown = Select(driver.find_element(By.CSS_SELECTOR, SELECTORS["date_dropdown"]))
        options = [o for o in dropdown.options if o.get_attribute("value").strip()]
        return len(options) > 0
    except Exception as e:
        print("Dropdown check error:", e)
        return False

# ---------- FLASK ROUTE ----------
@app.route("/checkPrisma")
def check_exam_date():
    driver = make_driver()
    driver.get(URL)
    driver.refresh()

    if is_date_available(driver):
        send_telegram_message("📅 ف Prisma تم العثور على تاريخ امتحان B2! سارع بالتسجيل الآن ✅")
        driver.quit()
        return "✅ Date found and Telegram message sent."
    else:
        driver.quit()
        return "⏳ No date available."

serve(app, host="0.0.0.0", port=8080)
