import os
import sys
import logging
import requests

# Production applications mein telemetry logs generate karna standard practice hai
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Configuration keys ko secure environment variables mein manage kiya jata hai
API_KEY = os.getenv("NOTIF_BOT_TOKEN", "8705044326:AAG4HZjHJ0JThaMc0BCkqFJ1yakyus_JraQ")
RECIPIENT_ID = os.getenv("NOTIF_CHAT_ID", "-1003824926404")

def check_environment():
    """Zaroori authorization tokens ki presence confirm karne ka function."""
    if not API_KEY or ":" not in API_KEY:
        logging.error("Configuration Fault: API_KEY setup is incorrect or missing.")
        return False
    if not RECIPIENT_ID:
        logging.error("Configuration Fault: RECIPIENT_ID identifier is absent.")
        return False
    return True

def dispatch_telemetry(log_title, log_body):
    """
    Structured notifications ko secure REST API calls ke zariye 
    designated recipient channels par push karne ka function.
    """
    if not check_environment():
        return False

    endpoint_url = f"https://api.telegram.org/bot{API_KEY}/sendMessage"
    
    # Safe aur clean message delivery formatting
    compiled_text = (
        f"📋 *{log_title}*\n"
        f"=========================\n"
        f"{log_body}"
    )
    
    http_payload = {
        "chat_id": RECIPIENT_ID,
        "text": compiled_text,
        "parse_mode": "Markdown"
    }
    
    try:
        # Runtime network delays se bachne ke liye standard timeout rule lagana zaroori hai
        response = requests.post(endpoint_url, json=http_payload, timeout=10)
        
        if response.status_code == 200:
            logging.info("Network Sync: Data packet delivered to the messaging gateway.")
            return True
        else:
            logging.warning(f"Gateway Alert: Server returned non-200 status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as network_error:
        logging.error(f"Hardware Link Exception: Socket transaction failure: {network_error}")
        return False

if __name__ == "__main__":
    logging.info("Initializing production communication pipeline framework...")
    
    # Generic template execution tracing ke liye
    test_title = "Data Synchronization Node Status"
    test_body = (
        "🔹 *Node Instance:* Secure-Auth-Router-01\n"
        "🔹 *State Verification:* DISPATCH_READY\n"
        "🔹 *Encryption Layer:* TLS Session Active"
    )
    
    success = dispatch_telemetry(test_title, test_body)
    if success:
        logging.info("Diagnostics Routine: Connection integration passed successfully.")
    else:
        logging.error("Diagnostics Routine: Boundary communication check failed.")
        
