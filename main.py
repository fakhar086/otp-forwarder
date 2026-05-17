import os
import requests

# Zaroori configuration variables
# Production environments mein tokens ko environment variables se read karna behtar hota hai
TELEGRAM_BOT_TOKEN = "8705044326:AAG4HZjHJ0JThaMc0BCkqFJ1yakyus_JraQ"
TELEGRAM_CHAT_ID = "-1003824926404"

def send_telegram_notification(message_body):
    """
    Official Telegram Bot API ka istemal karte hue message send karne ka function.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_body,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[+] Notification successfully delivered to Telegram.")
            return True
        else:
            print(f"[-] Telegram API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection failed: {e}")
        return False

if
