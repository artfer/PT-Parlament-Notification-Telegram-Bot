import os
from dotenv import load_dotenv

# load_dotenv() will automatically search for and load variables from a .env file
# in the current directory or parent directories.
load_dotenv()

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Scraper Configuration ---
ARCHIVE_URL = os.getenv("ARCHIVE_URL")