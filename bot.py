iimport time
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

TELEGRAM_BOT_TOKEN = "8705044326:AAEH-TgpgisDF_hqZmlHQH5Oo4hBK6aVVqY"
TELEGRAM_CHAT_ID = "-1003824926404"

# Duplicate check karne ke liye set
sent_messages = set()

def format_phone_number(phone_str):
    """Phone number ke pehle 3 aur akhri 4 digits dikhayega"""
    digits = re.sub(r'\D', '', phone_str)
    if len(digits) >= 7:
        return f"{digits[:3]}******{digits[-4:]}"
    return phone_str

def send_telegram_message(text):
    """Telegram par message bhejne ka function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[+] Message sent to Telegram!")
        else:
            print(f"[-] Telegram Error: {response.text}")
    except Exception as e:
        print(f"[-] Request failed: {e}")

def setup_driver():
    """Selenium WebDriver setup"""
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Background me chalne ke liye
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login_to_panel(driver):
    """Panel par login karne ka function"""
    print("[*] Panel open ho raha ha aur login kiya ja raha ha...")
    driver.get(PANEL_URL)
    time.sleep(3)
    
    try:
        # Input fields dhoondna (Agar login fields ke ID/Name alag hain to inko change kiya ja sakta ha)
        # Yeh common attributes `name="username"` aur `name="password"` ke mutabik hain
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @name='username' or @name='user']"))
        )
        password_field = driver.find_element(By.XPATH, "//input[@type='password' or @name='password' or @name='pass']")
        
        # Details enter karna
        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        
        # Login button dhund kar click karna
        login_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
        login_button.click()
        
        print("[+] Login successfully completed!")
        time.sleep(4) # Redirect hone ka wait
        return True
    except Exception as e:
        print(f"[-] Login failed: {e}. Ho sakta ha page direct khul gaya ho ya input fields ke name alag hon.")
        return False

def scrape_panel():
    print("[*] Bot start ho raha ha...")
    driver = setup_driver()
    
    # Pehle login karenge
    login_to_panel(driver)
    
    try:
        while True:
            try:
                # Direct target page par jana agar login ke baad redirect na hua ho
                if driver.current_url != PANEL_URL:
                    driver.get(PANEL_URL)
                    time.sleep(3)
                
                # HTML Table se data nikalna
                rows = driver.find_elements(By.XPATH, "//table//tr")
                
                if not rows:
                    # Agar session expire ho jaye aur wapas login page aa jaye
                    print("[-] Data nahi mila, ho sakta ha session expire ho gaya ho. Re-logging in...")
                    login_to_panel(driver)
                    continue
                
                for row in rows[1:]: # Header row chor kar
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 3:
                        msg_time = cols[0].text.strip()
                        phone_num = cols[1].text.strip()
                        otp_msg = cols[2].text.strip()
                        
                        # Unique ID duplicate roknay k liye
                        msg_id = f"{msg_time}_{phone_num}"
                        
                        if msg_id not in sent_messages:
                            formatted_phone = format_phone_number(phone_num)
                            
                            tg_text = (
                                f"📩 *New OTP Received*\n\n"
                                f"📱 *Number:* `{formatted_phone}`\n"
                                f"💬 *Message:* {otp_msg}\n"
                                f"🕒 *Time:* {msg_time}"
                            )
                            
                            send_telegram_message(tg_text)
                            sent_messages.add(msg_id)
                            
            except Exception as e:
                print(f"[-] Loop error: {e}")
                
            print("[*] Waiting 10 seconds for next check...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("[*] Bot stopped.")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_panel()


