import os
import sys
import logging
import requests

# Production applications mein telemetry logging standard practice hai
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Configuration ko secure secrets storage ya env variables mein rakha jata hai
API_TOKEN = os.getenv("APP_TELEGRAM_TOKEN", "8705044326:AAG4HZjHJ0JThaMc0BCkqFJ1yakyus_JraQ")
CHANNEL_ID = os.getenv("APP_TARGET_CHANNEL", "-1003824926404")

def validate_configuration():
    """Zaroori configuration values ki presence check karne ka function."""
    if not API_TOKEN or ":" not in API_TOKEN:
        logging.error("Invalid or missing TELEGRAM_BOT_TOKEN.")
        return False
    if not CHANNEL_ID:
        logging.error("Missing TELEGRAM_CHAT_ID.")
        return False
    return True

def emit_notification(event_title, event_details):
    """
    Official Webhook / REST endpoints par POST request submit karne ka function.
    """
    if not validate_configuration():
        return False

    request_url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    
    # Payload structure setting
    formatted_msg = (
        f"🚨 *{event_title}*\n"
        f"-------------------------\n"
        f"{event_details}"
    )
    
    post_body = {
        "chat_id": CHANNEL_ID,
        "text": formatted_msg,
        "parse_mode": "Markdown"
    }
    
    try:
        # Timeout set karna zaroori hai taake cloud runs system network delay se crash na hon
        response = requests.post(request_url, json=post_body, timeout=10)
        
        if response.status_code == 200:
            logging.INFO("Application event payload pushed successfully.")
            return True
        else:
            logging.warning(f"Target API responded with error code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as network_exception:
        logging.error(f"Network interaction error: {network_exception}")
        return False

if __name__ == "__main__":
    logging.info("Starting standard log processor verification...")
    
    # Mock system metrics data structure
    title = "System Event Notification"
    details = (
        "🔹 *Component:* Data-Gateway\n"
        "🔹 *Status:* Verification Pending\n"
        "🕒 *Log Timestamp:* 2026-05-17 21:40:00"
    )
    
    # Execution block
    emit_notification(title, details)
    
