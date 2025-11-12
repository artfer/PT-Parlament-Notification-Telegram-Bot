import requests
import logging
from ..config import settings

def send_telegram_message(message: str):
    """Sends a message to the specified Telegram chat via the bot."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logging.error("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in environment variables.")
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info("Successfully sent message to Telegram.")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send message to Telegram: {e}")
        return False