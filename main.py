import os
import requests

# Sensitive data ko environment variables se read karna secure practice ha
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")

def send_alert(message_text):
    """
    Official Telegram Bot API ke zariye structured alert send karne ka function.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[+] Notification sent successfully.")
            return True
        else:
            print(f"[-] API Error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection Error: {e}")
        return False

if __name__ == "__main__":
    # Test message
    send_alert("⚠️ *System Alert:* Test notification structure.")
    
