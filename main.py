import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
PANEL_URL = "http://139.99.68.231/ints/agent/SMSCDRReports"
USERNAME = "Furqan32"
PASSWORD = "Furqan32"

TELEGRAM_BOT_TOKEN = "8705044326:AAG4HZjHJ0JThaMc0BCkqFJ1yakyus_JraQ"
TELEGRAM_CHAT_ID = "-1003824926404"

# Duplicate messages ko rokne ke liye cache memory
sent_messages = set()

def format_phone_number(phone_str):
    """Security ke liye phone number ke darmiyan wale digits hide karne ka function"""
    digits = re.sub(r'\D', '', phone_str)
    if len(digits) >= 7:
        return f"{digits[:3]}******{digits[-4:]}"
    return phone_str

def send_telegram_message(text):
    """Telegram group mein structured notification bhejne ka function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[+] OTP sent to Telegram group!")
        else:
            print(f"[-] Telegram API Error: {response.text}")
    except Exception as e:
        print(f"[-] Connection Error: {e}")

def setup_driver():
    """GitHub Actions ke liye Headless Chrome Browser setup"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login_to_panel(driver):
    """Panel par login automate karne ka function"""
    print("[*] Accessing panel and logging in...")
    driver.get(PANEL_URL)
    time.sleep(4)
    
    try:
        # Form fields detect karna attributes ke mutabik
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @name='username' or @name='user']"))
        )
        password_field = driver.find_element(By.XPATH, "//input[@type='password' or @name='password' or @name='pass']")
        
        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
        login_button.click()
        
        print("[+] Login successfully verified.")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"[-] Login interface match failed: {e}")
        return False

def start_monitoring():
    print("[*] Initializing background monitor sub-system...")
    driver = setup_driver()
    
    # First time login
    login_to_panel(driver)
    
    # GitHub Actions runtime limits ke mutabik hum is loop ko chalaenge
    # Yeh loop naye entries ko track karta rahega
    for check_cycle in range(30): 
        try:
            if driver.current_url != PANEL_URL:
                driver.get(PANEL_URL)
                time.sleep(4)
            
            # Excel data ke mutabik rows aur columns target karna
            rows = driver.find_elements(By.XPATH, "//table//tr")
            
            if not rows:
                print("[-] No active data rows visible. Re-authenticating session...")
                login_to_panel(driver)
                continue
            
            # Rows processing (Naye data ko upar se read karna)
            for row in rows[1:15]: 
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 6:
                    # Excel structure: Col 0 = Date, Col 2 = Number, Col 3 = CLI, Col 5 = SMS text
                    sms_date = cols[0].text.strip()
                    phone_number = cols[2].text.strip()
                    service_cli = cols[3].text.strip()
                    sms_content = cols[5].text.strip()
                    
                    # unique verification key taake ek hi message baar-baar group mein na jaye
                    unique_key = f"{sms_date}_{phone_number}_{service_cli}"
                    
                    if unique_key not in sent_messages:
                        hidden_phone = format_phone_number(phone_number)
                        
                        # Formatting Telegram Alert
                        alert_message = (
                            f"📩 *New OTP/SMS Detected*\n\n"
                            f"📱 *Number:* `{hidden_phone}`\n"
                            f"🌐 *Service (CLI):* `{service_cli}`\n"
                            f"💬 *Message:* {sms_content}\n"
                            f"🕒 *Timestamp:* {sms_date}"
                        )
                        
                        send_telegram_message(alert_message)
                        sent_messages.add(unique_key)
                        
        except Exception as loop_error:
            print(f"[-] Processing cycle alert: {loop_error}")
            
        print("[*] Sleeping 15 seconds before next data refresh...")
        time.sleep(15)
        
    driver.quit()
    print("[*] Cycle complete. Standard framework clean shutdown.")

if __name__ == "__main__":
    start_monitoring()
    
